from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.workout import WorkoutCreate, WorkoutListRead, WorkoutRead, WorkoutUpdate
from app.services.workouts import (
    create_workout,
    delete_workout,
    get_workout_by_id,
    list_workouts,
    read_workout,
    update_workout,
)

router = APIRouter(tags=["Workouts"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/workouts", response_model=WorkoutListRead)
async def get_workouts(
    session: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    date_from: date | None = None,
    date_to: date | None = None,
) -> WorkoutListRead:
    """Return paginated workout history."""

    return await list_workouts(session, limit, offset, date_from, date_to)


@router.get("/workouts/{workout_id}", response_model=WorkoutRead)
async def get_workout(
    workout_id: int,
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
) -> WorkoutRead:
    """Return workout details."""

    workout = await get_workout_by_id(session, workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return read_workout(workout, locale)


@router.post("/workouts", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
async def post_workout(
    payload: WorkoutCreate,
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
) -> WorkoutRead:
    """Create a workout."""

    try:
        return await create_workout(session, payload, locale)
    except ValueError as exc:
        if str(exc) == "exercise_not_found":
            raise HTTPException(status_code=404, detail="Exercise not found") from exc
        raise


@router.patch("/workouts/{workout_id}", response_model=WorkoutRead)
async def patch_workout(
    workout_id: int,
    payload: WorkoutUpdate,
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
) -> WorkoutRead:
    """Edit a workout."""

    workout = await get_workout_by_id(session, workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    try:
        return await update_workout(session, workout, payload, locale)
    except ValueError as exc:
        if str(exc) == "exercise_not_found":
            raise HTTPException(status_code=404, detail="Exercise not found") from exc
        raise


@router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_workout(
    workout_id: int,
    session: DbSession,
) -> Response:
    """Delete a workout."""

    workout = await get_workout_by_id(session, workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    await delete_workout(session, workout)
    return Response(status_code=status.HTTP_204_NO_CONTENT)