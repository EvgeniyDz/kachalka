from __future__ import annotations

from datetime import date as Date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exercise import ExerciseRead


class ExerciseSetInput(BaseModel):
    """Payload for one performed set."""

    set_number: int | None = Field(default=None, ge=1)
    weight: Decimal | None = Field(default=None, ge=0, max_digits=7, decimal_places=2)
    reps: int | None = Field(default=None, ge=0)
    rpe: Decimal | None = Field(default=None, ge=0, le=10, max_digits=3, decimal_places=1)
    notes: str | None = None


class WorkoutExerciseInput(BaseModel):
    """Payload for one exercise inside a workout."""

    exercise_id: int = Field(ge=1)
    order_index: int | None = Field(default=None, ge=0)
    notes: str | None = None
    sets: list[ExerciseSetInput] = Field(default_factory=list)


class WorkoutCreate(BaseModel):
    """Payload for creating a workout."""

    date: Date
    title: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    exercises: list[WorkoutExerciseInput] = Field(default_factory=list)


class WorkoutUpdate(BaseModel):
    """Payload for editing a workout."""

    model_config = ConfigDict(extra="forbid")

    date: Date | None = None
    title: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    exercises: list[WorkoutExerciseInput] | None = None


class ExerciseSetRead(BaseModel):
    """Set returned by the API."""

    id: int
    set_number: int
    weight: Decimal | None = None
    reps: int | None = None
    rpe: Decimal | None = None
    notes: str | None = None


class WorkoutExerciseRead(BaseModel):
    """Exercise block returned by the API."""

    id: int
    order_index: int
    notes: str | None = None
    exercise: ExerciseRead
    sets: list[ExerciseSetRead]


class WorkoutRead(BaseModel):
    """Detailed workout returned by the API."""

    id: int
    date: Date
    title: str | None = None
    notes: str | None = None
    exercises: list[WorkoutExerciseRead]


class WorkoutSummaryRead(BaseModel):
    """Compact workout item for history lists."""

    id: int
    date: Date
    title: str | None = None
    notes: str | None = None
    exercise_count: int
    set_count: int


class WorkoutListRead(BaseModel):
    """Paginated workout history response."""

    items: list[WorkoutSummaryRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)