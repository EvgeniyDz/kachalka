from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.exercise import Exercise


class Workout(Base):
    """A single training session."""

    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order_index",
    )


class WorkoutExercise(Base):
    """A chosen exercise inside a workout."""

    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "order_index", name="uq_workout_exercise_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"))
    order_index: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    workout: Mapped[Workout] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(back_populates="workout_exercises")
    sets: Mapped[list["ExerciseSet"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="ExerciseSet.set_number",
    )


class ExerciseSet(Base):
    """One completed set for a workout exercise."""

    __tablename__ = "exercise_sets"
    __table_args__ = (UniqueConstraint("workout_exercise_id", "set_number", name="uq_set_number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE")
    )
    set_number: Mapped[int] = mapped_column(Integer)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rpe: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    workout_exercise: Mapped[WorkoutExercise] = relationship(back_populates="sets")
