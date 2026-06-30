from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Exercise, ExerciseTranslation, MuscleGroup, MuscleGroupTranslation
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseListRead,
    ExerciseRead,
    MuscleGroupRead,
    TranslationRead,
)


def pick_translation(
    translations: list[ExerciseTranslation | MuscleGroupTranslation],
    locale: str,
) -> ExerciseTranslation | MuscleGroupTranslation | None:
    """Pick the requested translation, falling back to Ukrainian and then first available."""

    by_locale = {translation.locale: translation for translation in translations}
    return by_locale.get(locale) or by_locale.get("uk") or next(iter(translations), None)


def read_translation(translation: ExerciseTranslation | MuscleGroupTranslation) -> TranslationRead:
    """Convert a translation ORM object into an API schema."""

    return TranslationRead(
        locale=translation.locale,
        name=translation.name,
        description=getattr(translation, "description", None),
    )


def read_muscle_group(muscle_group: MuscleGroup, locale: str) -> MuscleGroupRead:
    """Convert a muscle group ORM object into a localized API schema."""

    selected = pick_translation(muscle_group.translations, locale)
    return MuscleGroupRead(
        id=muscle_group.id,
        code=muscle_group.code,
        name=selected.name if selected else muscle_group.code,
        translations=[read_translation(translation) for translation in muscle_group.translations],
    )


def read_exercise(exercise: Exercise, locale: str) -> ExerciseRead:
    """Convert an exercise ORM object into a localized API schema."""

    selected = pick_translation(exercise.translations, locale)
    return ExerciseRead(
        id=exercise.id,
        code=exercise.code,
        name=selected.name if selected else exercise.code,
        description=getattr(selected, "description", None) if selected else None,
        equipment=exercise.equipment,
        is_custom=exercise.is_custom,
        muscle_group=read_muscle_group(exercise.muscle_group, locale),
        translations=[read_translation(translation) for translation in exercise.translations],
    )


async def list_muscle_groups(session: AsyncSession, locale: str) -> list[MuscleGroupRead]:
    """Return all muscle groups with localized display names."""

    statement = (
        select(MuscleGroup)
        .options(selectinload(MuscleGroup.translations))
        .order_by(MuscleGroup.code)
    )
    result = await session.scalars(statement)
    return [read_muscle_group(muscle_group, locale) for muscle_group in result]


async def list_exercises(
    session: AsyncSession,
    locale: str,
    muscle_group_code: str | None = None,
    search: str | None = None,
    include_custom: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> ExerciseListRead:
    """Return a paginated exercise catalog with optional filters."""

    statement = select(Exercise).options(
        selectinload(Exercise.translations),
        selectinload(Exercise.muscle_group).selectinload(MuscleGroup.translations),
    )
    count_statement = select(func.count(func.distinct(Exercise.id)))

    if muscle_group_code is not None:
        statement = statement.join(Exercise.muscle_group).where(
            MuscleGroup.code == muscle_group_code
        )
        count_statement = count_statement.join(Exercise.muscle_group).where(
            MuscleGroup.code == muscle_group_code
        )

    if search:
        statement = statement.join(Exercise.translations).where(
            ExerciseTranslation.name.ilike(f"%{search}%")
        )
        count_statement = count_statement.join(Exercise.translations).where(
            ExerciseTranslation.name.ilike(f"%{search}%")
        )

    if not include_custom:
        statement = statement.where(Exercise.is_custom.is_(False))
        count_statement = count_statement.where(Exercise.is_custom.is_(False))

    total = await session.scalar(count_statement)
    statement = statement.distinct().order_by(Exercise.code).limit(limit).offset(offset)
    result = await session.scalars(statement)
    exercises = result.unique().all()

    return ExerciseListRead(
        items=[read_exercise(exercise, locale) for exercise in exercises],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


async def get_muscle_group_by_code(session: AsyncSession, code: str) -> MuscleGroup | None:
    """Find a muscle group by its stable code."""

    return await session.scalar(select(MuscleGroup).where(MuscleGroup.code == code))


async def get_exercise_by_id(session: AsyncSession, exercise_id: int) -> Exercise | None:
    """Find an exercise with all relations needed by the API response."""

    statement = (
        select(Exercise)
        .where(Exercise.id == exercise_id)
        .options(
            selectinload(Exercise.translations),
            selectinload(Exercise.muscle_group).selectinload(MuscleGroup.translations),
        )
    )
    return await session.scalar(statement)


async def create_exercise(
    session: AsyncSession,
    payload: ExerciseCreate,
    locale: str,
) -> ExerciseRead:
    """Create a custom exercise and return it in the requested locale."""

    muscle_group = await get_muscle_group_by_code(session, payload.muscle_group_code)
    if muscle_group is None:
        raise ValueError("muscle_group_not_found")

    exercise = Exercise(
        code=payload.code or f"custom_{uuid4().hex[:12]}",
        muscle_group_id=muscle_group.id,
        equipment=payload.equipment,
        is_custom=True,
    )
    session.add(exercise)
    await session.flush()

    for translation in payload.translations:
        session.add(
            ExerciseTranslation(
                exercise_id=exercise.id,
                locale=translation.locale,
                name=translation.name,
                description=translation.description,
            )
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ValueError("exercise_conflict") from exc

    created = await get_exercise_by_id(session, exercise.id)
    if created is None:
        raise RuntimeError("created_exercise_not_found")
    return read_exercise(created, locale)


async def update_exercise(
    session: AsyncSession,
    exercise: Exercise,
    payload: dict,
    locale: str,
) -> ExerciseRead:
    """Update a custom exercise and its translations."""

    if payload.get("muscle_group_code") is not None:
        muscle_group = await get_muscle_group_by_code(session, payload["muscle_group_code"])
        if muscle_group is None:
            raise ValueError("muscle_group_not_found")
        exercise.muscle_group_id = muscle_group.id

    if "equipment" in payload:
        exercise.equipment = payload["equipment"]

    if payload.get("translations") is not None:
        existing = {translation.locale: translation for translation in exercise.translations}
        for translation in payload["translations"]:
            current = existing.get(translation["locale"])
            if current is None:
                session.add(
                    ExerciseTranslation(
                        exercise_id=exercise.id,
                        locale=translation["locale"],
                        name=translation["name"],
                        description=translation.get("description"),
                    )
                )
            else:
                current.name = translation["name"]
                current.description = translation.get("description")

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ValueError("exercise_conflict") from exc

    updated = await get_exercise_by_id(session, exercise.id)
    if updated is None:
        raise RuntimeError("updated_exercise_not_found")
    return read_exercise(updated, locale)


async def delete_exercise(session: AsyncSession, exercise: Exercise) -> None:
    """Delete a custom exercise."""

    await session.delete(exercise)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ValueError("exercise_in_use") from exc