from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.exercise import Exercise
    from app.models.workout import ExerciseSet, Workout


class PersonalRecord(Base):
    """Best known result for an exercise and record type."""

    __tablename__ = "personal_records"
    __table_args__ = (
        UniqueConstraint("exercise_id", "record_type", name="uq_exercise_record_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    workout_id: Mapped[int | None] = mapped_column(ForeignKey("workouts.id", ondelete="SET NULL"))
    exercise_set_id: Mapped[int | None] = mapped_column(
        ForeignKey("exercise_sets.id", ondelete="SET NULL")
    )
    record_type: Mapped[str] = mapped_column(String(40), index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exercise: Mapped["Exercise"] = relationship(back_populates="personal_records")
    workout: Mapped["Workout | None"] = relationship()
    exercise_set: Mapped["ExerciseSet | None"] = relationship()
