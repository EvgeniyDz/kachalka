from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.analytics import (
    ExerciseProgressPointRead,
    MuscleGroupFrequencyRead,
    PersonalRecordRead,
    WeeklyVolumeRead,
)
from app.services.analytics import (
    list_exercise_progress,
    list_frequent_muscle_groups,
    list_latest_records,
    list_weekly_volume,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get(
    "/exercises/{exercise_id}/progress",
    response_model=list[ExerciseProgressPointRead],
)
async def get_exercise_progress(
    exercise_id: int,
    session: DbSession,
) -> list[ExerciseProgressPointRead]:
    """Return progress points for one exercise."""

    return await list_exercise_progress(session, exercise_id)


@router.get("/weekly-volume", response_model=list[WeeklyVolumeRead])
async def get_weekly_volume(session: DbSession) -> list[WeeklyVolumeRead]:
    """Return weekly training volume."""

    return await list_weekly_volume(session)


@router.get("/records", response_model=list[PersonalRecordRead])
async def get_latest_records(
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[PersonalRecordRead]:
    """Return latest personal records."""

    return await list_latest_records(session, locale, limit)


@router.get("/muscle-groups/frequency", response_model=list[MuscleGroupFrequencyRead])
async def get_muscle_group_frequency(
    session: DbSession,
    locale: str = Query(default="uk", min_length=2, max_length=8),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[MuscleGroupFrequencyRead]:
    """Return most frequently trained muscle groups."""

    return await list_frequent_muscle_groups(session, locale, limit)