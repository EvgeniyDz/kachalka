import asyncio
from dataclasses import dataclass

from sqlalchemy import select

from app.db.session import AsyncSessionFactory
from app.models import Exercise, ExerciseTranslation, MuscleGroup, MuscleGroupTranslation


@dataclass(frozen=True)
class MuscleGroupSeed:
    code: str
    names: dict[str, str]


@dataclass(frozen=True)
class ExerciseSeed:
    code: str
    muscle_group_code: str
    equipment: str
    names: dict[str, str]


MUSCLE_GROUPS = [
    MuscleGroupSeed("chest", {"uk": "Груди", "en": "Chest"}),
    MuscleGroupSeed("back", {"uk": "Спина", "en": "Back"}),
    MuscleGroupSeed("legs", {"uk": "Ноги", "en": "Legs"}),
    MuscleGroupSeed("shoulders", {"uk": "Плечі", "en": "Shoulders"}),
    MuscleGroupSeed("biceps", {"uk": "Біцепс", "en": "Biceps"}),
    MuscleGroupSeed("triceps", {"uk": "Трицепс", "en": "Triceps"}),
    MuscleGroupSeed("core", {"uk": "Прес", "en": "Core"}),
]

EXERCISES = [
    ExerciseSeed("bench_press", "chest", "barbell", {"uk": "Жим лежачи", "en": "Bench press"}),
    ExerciseSeed(
        "squat",
        "legs",
        "barbell",
        {"uk": "Присідання зі штангою", "en": "Barbell squat"},
    ),
    ExerciseSeed("deadlift", "back", "barbell", {"uk": "Станова тяга", "en": "Deadlift"}),
    ExerciseSeed(
        "overhead_press",
        "shoulders",
        "barbell",
        {"uk": "Жим штанги стоячи", "en": "Overhead press"},
    ),
    ExerciseSeed("pull_up", "back", "bodyweight", {"uk": "Підтягування", "en": "Pull-up"}),
    ExerciseSeed(
        "barbell_row",
        "back",
        "barbell",
        {"uk": "Тяга штанги в нахилі", "en": "Barbell row"},
    ),
    ExerciseSeed(
        "lat_pulldown",
        "back",
        "cable",
        {"uk": "Тяга верхнього блока", "en": "Lat pulldown"},
    ),
    ExerciseSeed("leg_press", "legs", "machine", {"uk": "Жим ногами", "en": "Leg press"}),
    ExerciseSeed(
        "dumbbell_curl",
        "biceps",
        "dumbbell",
        {"uk": "Згинання рук з гантелями", "en": "Dumbbell curl"},
    ),
    ExerciseSeed(
        "triceps_pushdown",
        "triceps",
        "cable",
        {"uk": "Розгинання рук на блоці", "en": "Triceps pushdown"},
    ),
    ExerciseSeed("plank", "core", "bodyweight", {"uk": "Планка", "en": "Plank"}),
    ExerciseSeed(
        "romanian_deadlift",
        "legs",
        "barbell",
        {"uk": "Румунська тяга", "en": "Romanian deadlift"},
    ),
]


async def seed_database() -> None:
    """Insert the default exercise catalog without duplicating existing rows."""

    async with AsyncSessionFactory() as session:
        muscle_groups: dict[str, MuscleGroup] = {}

        for item in MUSCLE_GROUPS:
            muscle_group = await session.scalar(
                select(MuscleGroup).where(MuscleGroup.code == item.code)
            )
            if muscle_group is None:
                muscle_group = MuscleGroup(code=item.code)
                session.add(muscle_group)
                await session.flush()

            for locale, name in item.names.items():
                translation = await session.scalar(
                    select(MuscleGroupTranslation).where(
                        MuscleGroupTranslation.muscle_group_id == muscle_group.id,
                        MuscleGroupTranslation.locale == locale,
                    )
                )
                if translation is None:
                    session.add(
                        MuscleGroupTranslation(
                            muscle_group_id=muscle_group.id,
                            locale=locale,
                            name=name,
                        )
                    )

            muscle_groups[item.code] = muscle_group

        for item in EXERCISES:
            exercise = await session.scalar(select(Exercise).where(Exercise.code == item.code))
            if exercise is None:
                exercise = Exercise(
                    code=item.code,
                    muscle_group_id=muscle_groups[item.muscle_group_code].id,
                    equipment=item.equipment,
                    is_custom=False,
                )
                session.add(exercise)
                await session.flush()

            for locale, name in item.names.items():
                translation = await session.scalar(
                    select(ExerciseTranslation).where(
                        ExerciseTranslation.exercise_id == exercise.id,
                        ExerciseTranslation.locale == locale,
                    )
                )
                if translation is None:
                    session.add(
                        ExerciseTranslation(
                            exercise_id=exercise.id,
                            locale=locale,
                            name=name,
                        )
                    )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_database())