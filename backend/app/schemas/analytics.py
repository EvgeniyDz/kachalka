from __future__ import annotations

from datetime import date as Date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.exercise import ExerciseRead, MuscleGroupRead


class ExerciseProgressPointRead(BaseModel):
    """One set-level progress point for an exercise."""

    workout_id: int
    workout_date: Date
    exercise_set_id: int
    set_number: int
    weight: Decimal | None = None
    reps: int | None = None
    volume: Decimal | None = None
    estimated_1rm: Decimal | None = None


class WeeklyVolumeRead(BaseModel):
    """Training volume aggregated by ISO week."""

    week_start: Date
    volume: Decimal = Field(ge=0)
    workout_count: int = Field(ge=0)


class PersonalRecordRead(BaseModel):
    """Personal record returned by the API."""

    id: int
    record_type: str
    value: Decimal
    workout_id: int | None = None
    exercise_set_id: int | None = None
    exercise: ExerciseRead


class MuscleGroupFrequencyRead(BaseModel):
    """How often a muscle group appears in workout history."""

    muscle_group: MuscleGroupRead
    exercise_count: int = Field(ge=0)