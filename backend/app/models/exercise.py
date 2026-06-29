from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.muscle_group import MuscleGroup
    from app.models.record import PersonalRecord
    from app.models.workout import WorkoutExercise


class Exercise(Base):
    """An exercise from the default catalog or created by the user."""

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id", ondelete="RESTRICT")
    )
    equipment: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    muscle_group: Mapped["MuscleGroup"] = relationship(back_populates="exercises")
    translations: Mapped[list["ExerciseTranslation"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workout_exercises: Mapped[list["WorkoutExercise"]] = relationship(back_populates="exercise")
    personal_records: Mapped[list["PersonalRecord"]] = relationship(back_populates="exercise")


class ExerciseTranslation(Base):
    """Localized exercise name and optional description."""

    __tablename__ = "exercise_translations"
    __table_args__ = (UniqueConstraint("exercise_id", "locale", name="uq_exercise_locale"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    locale: Mapped[str] = mapped_column(String(8), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    exercise: Mapped[Exercise] = relationship(back_populates="translations")
