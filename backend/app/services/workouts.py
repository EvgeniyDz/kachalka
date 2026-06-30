from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Exercise, ExerciseSet, MuscleGroup, Workout, WorkoutExercise
from app.schemas.workout import (
    ExerciseSetInput,
    ExerciseSetRead,
    WorkoutCreate,
    WorkoutExerciseInput,
    WorkoutExerciseRead,
    WorkoutListRead,
    WorkoutRead,
    WorkoutSummaryRead,
    WorkoutUpdate,
)
from app.services.exercises import read_exercise


def read_set(exercise_set: ExerciseSet) -> ExerciseSetRead:
    """Convert a set ORM object into an API schema."""

    return ExerciseSetRead(
        id=exercise_set.id,
        set_number=exercise_set.set_number,
        weight=exercise_set.weight,
        reps=exercise_set.reps,
        rpe=exercise_set.rpe,
        notes=exercise_set.notes,
    )


def read_workout_exercise(
    workout_exercise: WorkoutExercise,
    locale: str,
) -> WorkoutExerciseRead:
    """Convert a workout exercise ORM object into an API schema."""

    return WorkoutExerciseRead(
        id=workout_exercise.id,
        order_index=workout_exercise.order_index,
        notes=workout_exercise.notes,
        exercise=read_exercise(workout_exercise.exercise, locale),
        sets=[read_set(exercise_set) for exercise_set in workout_exercise.sets],
    )


def read_workout(workout: Workout, locale: str) -> WorkoutRead:
    """Convert a workout ORM object into a detailed API schema."""

    return WorkoutRead(
        id=workout.id,
        date=workout.date,
        title=workout.title,
        notes=workout.notes,
        exercises=[
            read_workout_exercise(workout_exercise, locale)
            for workout_exercise in workout.exercises
        ],
    )


def read_workout_summary(workout: Workout) -> WorkoutSummaryRead:
    """Convert a workout ORM object into a compact history item."""

    return WorkoutSummaryRead(
        id=workout.id,
        date=workout.date,
        title=workout.title,
        notes=workout.notes,
        exercise_count=len(workout.exercises),
        set_count=sum(len(workout_exercise.sets) for workout_exercise in workout.exercises),
    )


def build_exercise_set(payload: ExerciseSetInput, fallback_number: int) -> ExerciseSet:
    """Build a set ORM object from API input."""

    return ExerciseSet(
        set_number=payload.set_number or fallback_number,
        weight=payload.weight,
        reps=payload.reps,
        rpe=payload.rpe,
        notes=payload.notes,
    )


def build_workout_exercise(
    payload: WorkoutExerciseInput,
    fallback_order: int,
) -> WorkoutExercise:
    """Build a workout exercise ORM object with nested sets."""

    return WorkoutExercise(
        exercise_id=payload.exercise_id,
        order_index=payload.order_index if payload.order_index is not None else fallback_order,
        notes=payload.notes,
        sets=[
            build_exercise_set(exercise_set, index)
            for index, exercise_set in enumerate(payload.sets, start=1)
        ],
    )


def replace_workout_exercises(
    workout: Workout,
    exercises: list[WorkoutExerciseInput],
) -> None:
    """Replace nested workout exercises and sets."""

    workout.exercises = [
        build_workout_exercise(workout_exercise, index)
        for index, workout_exercise in enumerate(exercises)
    ]


async def ensure_exercises_exist(
    session: AsyncSession,
    exercises: list[WorkoutExerciseInput],
) -> None:
    """Validate that every referenced exercise exists."""

    exercise_ids = {workout_exercise.exercise_id for workout_exercise in exercises}
    if not exercise_ids:
        return

    statement = select(Exercise.id).where(Exercise.id.in_(exercise_ids))
    found_ids = set(await session.scalars(statement))
    if found_ids != exercise_ids:
        raise ValueError("exercise_not_found")


async def list_workouts(
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    date_from: date | None = None,
    date_to: date | None = None,
) -> WorkoutListRead:
    """Return paginated workout history."""

    statement = select(Workout).options(
        selectinload(Workout.exercises).selectinload(WorkoutExercise.sets)
    )
    count_statement = select(func.count(Workout.id))

    if date_from is not None:
        statement = statement.where(Workout.date >= date_from)
        count_statement = count_statement.where(Workout.date >= date_from)

    if date_to is not None:
        statement = statement.where(Workout.date <= date_to)
        count_statement = count_statement.where(Workout.date <= date_to)

    total = await session.scalar(count_statement)
    statement = (
        statement.order_by(Workout.date.desc(), Workout.id.desc()).limit(limit).offset(offset)
    )
    result = await session.scalars(statement)

    return WorkoutListRead(
        items=[read_workout_summary(workout) for workout in result],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


async def get_workout_by_id(session: AsyncSession, workout_id: int) -> Workout | None:
    """Find a workout with all nested data needed for the API response."""

    statement = (
        select(Workout)
        .where(Workout.id == workout_id)
        .options(
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.exercise)
            .selectinload(Exercise.translations),
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.exercise)
            .selectinload(Exercise.muscle_group)
            .selectinload(MuscleGroup.translations),
            selectinload(Workout.exercises).selectinload(WorkoutExercise.sets),
        )
    )
    return await session.scalar(statement)


async def create_workout(
    session: AsyncSession,
    payload: WorkoutCreate,
    locale: str,
) -> WorkoutRead:
    """Create a workout with nested exercises and sets."""

    await ensure_exercises_exist(session, payload.exercises)
    workout = Workout(date=payload.date, title=payload.title, notes=payload.notes)
    replace_workout_exercises(workout, payload.exercises)
    session.add(workout)
    await session.commit()

    created = await get_workout_by_id(session, workout.id)
    if created is None:
        raise RuntimeError("created_workout_not_found")
    return read_workout(created, locale)


async def update_workout(
    session: AsyncSession,
    workout: Workout,
    payload: WorkoutUpdate,
    locale: str,
) -> WorkoutRead:
    """Update a workout and optionally replace nested exercises and sets."""

    update_data = payload.model_dump(exclude_unset=True)

    if "date" in update_data:
        workout.date = update_data["date"]
    if "title" in update_data:
        workout.title = update_data["title"]
    if "notes" in update_data:
        workout.notes = update_data["notes"]
    if payload.exercises is not None:
        await ensure_exercises_exist(session, payload.exercises)
        replace_workout_exercises(workout, payload.exercises)

    await session.commit()

    updated = await get_workout_by_id(session, workout.id)
    if updated is None:
        raise RuntimeError("updated_workout_not_found")
    return read_workout(updated, locale)


async def delete_workout(session: AsyncSession, workout: Workout) -> None:
    """Delete a workout with nested exercises and sets."""

    await session.delete(workout)
    await session.commit()