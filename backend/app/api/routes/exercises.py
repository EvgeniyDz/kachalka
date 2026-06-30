from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseListRead,
    ExerciseRead,
    ExerciseUpdate,
    MuscleGroupRead,
)
from app.services.exercises import (
    create_exercise,
    delete_exercise,
    get_exercise_by_id,
    list_exercises,
    list_muscle_groups,
    update_exercise,
)

router = APIRouter(tags=["Exercises"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/muscle-groups", response_model=list[MuscleGroupRead])
async def get_muscle_groups(
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
) -> list[MuscleGroupRead]:
    """Return muscle groups for exercise filters and forms."""

    return await list_muscle_groups(session, locale)


@router.get("/exercises", response_model=ExerciseListRead)
async def get_exercises(
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
    muscle_group_code: str | None = Query(default=None, min_length=1, max_length=80),
    search: str | None = Query(default=None, min_length=1, max_length=160),
    include_custom: bool = True,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ExerciseListRead:
    """Return the paginated exercise catalog with optional filtering."""

    return await list_exercises(
        session,
        locale,
        muscle_group_code,
        search,
        include_custom,
        limit,
        offset,
    )


@router.post("/exercises", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
async def post_exercise(
    payload: ExerciseCreate,
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
) -> ExerciseRead:
    """Create a custom exercise."""

    try:
        return await create_exercise(session, payload, locale)
    except ValueError as exc:
        if str(exc) == "muscle_group_not_found":
            raise HTTPException(status_code=404, detail="Muscle group not found") from exc
        if str(exc) == "exercise_conflict":
            raise HTTPException(
                status_code=409,
                detail="Exercise code or translation already exists",
            ) from exc
        raise


@router.patch("/exercises/{exercise_id}", response_model=ExerciseRead)
async def patch_exercise(
    exercise_id: int,
    payload: ExerciseUpdate,
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
) -> ExerciseRead:
    """Edit a custom exercise."""

    exercise = await get_exercise_by_id(session, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if not exercise.is_custom:
        raise HTTPException(status_code=403, detail="Seed exercises cannot be edited")

    try:
        return await update_exercise(
            session,
            exercise,
            payload.model_dump(exclude_unset=True),
            locale,
        )
    except ValueError as exc:
        if str(exc) == "muscle_group_not_found":
            raise HTTPException(status_code=404, detail="Muscle group not found") from exc
        if str(exc) == "exercise_conflict":
            raise HTTPException(
                status_code=409,
                detail="Exercise update conflicts with existing data",
            ) from exc
        raise


@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_exercise(
    exercise_id: int,
    session: DbSession,
) -> Response:
    """Delete a custom exercise."""

    exercise = await get_exercise_by_id(session, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if not exercise.is_custom:
        raise HTTPException(status_code=403, detail="Seed exercises cannot be deleted")

    try:
        await delete_exercise(session, exercise)
    except ValueError as exc:
        if str(exc) == "exercise_in_use":
            raise HTTPException(
                status_code=409,
                detail="Exercise is already used in workouts",
            ) from exc
        raise

    return Response(status_code=status.HTTP_204_NO_CONTENT)