from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.exercise import Exercise


class MuscleGroup(Base):
    """A stable muscle group used to categorize exercises."""

    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    translations: Mapped[list["MuscleGroupTranslation"]] = relationship(
        back_populates="muscle_group",
        cascade="all, delete-orphan",
    )
    exercises: Mapped[list["Exercise"]] = relationship(back_populates="muscle_group")


class MuscleGroupTranslation(Base):
    """Localized display name for a muscle group."""

    __tablename__ = "muscle_group_translations"
    __table_args__ = (UniqueConstraint("muscle_group_id", "locale", name="uq_muscle_group_locale"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_groups.id", ondelete="CASCADE"))
    locale: Mapped[str] = mapped_column(String(8), index=True)
    name: Mapped[str] = mapped_column(String(120))

    muscle_group: Mapped[MuscleGroup] = relationship(back_populates="translations")
