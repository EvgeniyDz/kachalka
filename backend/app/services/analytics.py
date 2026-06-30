from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Exercise,
    ExerciseSet,
    MuscleGroup,
    PersonalRecord,
    Workout,
    WorkoutExercise,
)
from app.schemas.analytics import (
    ExerciseProgressPointRead,
    MuscleGroupFrequencyRead,
    PersonalRecordRead,
    WeeklyVolumeRead,
)
from app.services.exercises import read_exercise, read_muscle_group

MAX_WEIGHT = "max_weight"
MAX_VOLUME = "max_volume"
MAX_REPS = "max_reps"
ESTIMATED_1RM = "estimated_1rm"
RECORD_TYPES = (MAX_WEIGHT, MAX_VOLUME, MAX_REPS, ESTIMATED_1RM)


@dataclass(frozen=True)
class RecordCandidate:
    exercise_id: int
    workout_id: int
    exercise_set_id: int
    record_type: str
    value: Decimal


def quantize_decimal(value: Decimal) -> Decimal:
    """Normalize calculated values to the DB scale used by personal records."""

    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_volume(weight: Decimal | None, reps: int | None) -> Decimal | None:
    """Return set volume: weight multiplied by reps."""

    if weight is None or reps is None:
        return None
    return quantize_decimal(weight * Decimal(reps))


def calculate_estimated_1rm(weight: Decimal | None, reps: int | None) -> Decimal | None:
    """Return estimated one-rep max using the Epley formula."""

    if weight is None or reps is None or reps <= 0:
        return None
    return quantize_decimal(weight * (Decimal(1) + Decimal(reps) / Decimal(30)))


def build_record_candidates(workout: Workout) -> list[RecordCandidate]:
    """Build all possible personal-record candidates from a workout."""

    candidates: list[RecordCandidate] = []

    for workout_exercise in workout.exercises:
        for exercise_set in workout_exercise.sets:
            if exercise_set.weight is not None:
                candidates.append(
                    RecordCandidate(
                        exercise_id=workout_exercise.exercise_id,
                        workout_id=workout.id,
                        exercise_set_id=exercise_set.id,
                        record_type=MAX_WEIGHT,
                        value=quantize_decimal(exercise_set.weight),
                    )
                )

            if exercise_set.reps is not None:
                candidates.append(
                    RecordCandidate(
                        exercise_id=workout_exercise.exercise_id,
                        workout_id=workout.id,
                        exercise_set_id=exercise_set.id,
                        record_type=MAX_REPS,
                        value=Decimal(exercise_set.reps),
                    )
                )

            volume = calculate_volume(exercise_set.weight, exercise_set.reps)
            if volume is not None:
                candidates.append(
                    RecordCandidate(
                        exercise_id=workout_exercise.exercise_id,
                        workout_id=workout.id,
                        exercise_set_id=exercise_set.id,
                        record_type=MAX_VOLUME,
                        value=volume,
                    )
                )

            estimated_1rm = calculate_estimated_1rm(exercise_set.weight, exercise_set.reps)
            if estimated_1rm is not None:
                candidates.append(
                    RecordCandidate(
                        exercise_id=workout_exercise.exercise_id,
                        workout_id=workout.id,
                        exercise_set_id=exercise_set.id,
                        record_type=ESTIMATED_1RM,
                        value=estimated_1rm,
                    )
                )

    return candidates


async def recalculate_personal_records(session: AsyncSession) -> None:
    """Rebuild personal records from all workouts."""

    await session.execute(PersonalRecord.__table__.delete())

    statement = select(Workout).options(
        selectinload(Workout.exercises).selectinload(WorkoutExercise.sets)
    )
    workouts = await session.scalars(statement)
    best: dict[tuple[int, str], RecordCandidate] = {}

    for workout in workouts:
        for candidate in build_record_candidates(workout):
            key = (candidate.exercise_id, candidate.record_type)
            current = best.get(key)
            if current is None or candidate.value > current.value:
                best[key] = candidate

    session.add_all(
        PersonalRecord(
            exercise_id=candidate.exercise_id,
            workout_id=candidate.workout_id,
            exercise_set_id=candidate.exercise_set_id,
            record_type=candidate.record_type,
            value=candidate.value,
        )
        for candidate in best.values()
    )


async def list_exercise_progress(
    session: AsyncSession,
    exercise_id: int,
) -> list[ExerciseProgressPointRead]:
    """Return set-level progress points for one exercise."""

    statement = (
        select(Workout, WorkoutExercise, ExerciseSet)
        .join(WorkoutExercise, WorkoutExercise.workout_id == Workout.id)
        .join(ExerciseSet, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .where(WorkoutExercise.exercise_id == exercise_id)
        .order_by(Workout.date, Workout.id, WorkoutExercise.order_index, ExerciseSet.set_number)
    )
    rows = await session.execute(statement)

    return [
        ExerciseProgressPointRead(
            workout_id=workout.id,
            workout_date=workout.date,
            exercise_set_id=exercise_set.id,
            set_number=exercise_set.set_number,
            weight=exercise_set.weight,
            reps=exercise_set.reps,
            volume=calculate_volume(exercise_set.weight, exercise_set.reps),
            estimated_1rm=calculate_estimated_1rm(exercise_set.weight, exercise_set.reps),
        )
        for workout, _, exercise_set in rows
    ]


async def list_weekly_volume(session: AsyncSession) -> list[WeeklyVolumeRead]:
    """Return training volume grouped by ISO week."""

    statement = select(Workout).options(
        selectinload(Workout.exercises).selectinload(WorkoutExercise.sets)
    )
    workouts = await session.scalars(statement)
    volume_by_week: dict[date, Decimal] = defaultdict(lambda: Decimal("0.00"))
    workout_ids_by_week: dict[date, set[int]] = defaultdict(set)

    for workout in workouts:
        week_start = workout.date - timedelta(days=workout.date.weekday())
        workout_ids_by_week[week_start].add(workout.id)
        for workout_exercise in workout.exercises:
            for exercise_set in workout_exercise.sets:
                volume = calculate_volume(exercise_set.weight, exercise_set.reps)
                if volume is not None:
                    volume_by_week[week_start] += volume

    return [
        WeeklyVolumeRead(
            week_start=week_start,
            volume=quantize_decimal(volume_by_week[week_start]),
            workout_count=len(workout_ids_by_week[week_start]),
        )
        for week_start in sorted(workout_ids_by_week)
    ]


async def list_latest_records(
    session: AsyncSession,
    locale: str,
    limit: int = 10,
) -> list[PersonalRecordRead]:
    """Return latest personal records."""

    statement = (
        select(PersonalRecord)
        .options(
            selectinload(PersonalRecord.exercise).selectinload(Exercise.translations),
            selectinload(PersonalRecord.exercise)
            .selectinload(Exercise.muscle_group)
            .selectinload(MuscleGroup.translations),
        )
        .order_by(PersonalRecord.created_at.desc(), PersonalRecord.id.desc())
        .limit(limit)
    )
    records = await session.scalars(statement)

    return [
        PersonalRecordRead(
            id=record.id,
            record_type=record.record_type,
            value=record.value,
            workout_id=record.workout_id,
            exercise_set_id=record.exercise_set_id,
            exercise=read_exercise(record.exercise, locale),
        )
        for record in records
    ]


async def list_frequent_muscle_groups(
    session: AsyncSession,
    locale: str,
    limit: int = 10,
) -> list[MuscleGroupFrequencyRead]:
    """Return the most frequently trained muscle groups."""

    statement = (
        select(MuscleGroup, Exercise, WorkoutExercise)
        .join(Exercise, Exercise.muscle_group_id == MuscleGroup.id)
        .join(WorkoutExercise, WorkoutExercise.exercise_id == Exercise.id)
        .options(selectinload(MuscleGroup.translations))
    )
    rows = await session.execute(statement)
    counts: dict[int, int] = defaultdict(int)
    groups: dict[int, MuscleGroup] = {}

    for muscle_group, _, _ in rows:
        counts[muscle_group.id] += 1
        groups[muscle_group.id] = muscle_group

    sorted_group_ids = sorted(counts, key=lambda group_id: counts[group_id], reverse=True)[:limit]
    return [
        MuscleGroupFrequencyRead(
            muscle_group=read_muscle_group(groups[group_id], locale),
            exercise_count=counts[group_id],
        )
        for group_id in sorted_group_ids
    ]