"""Create initial Kachalka domain schema.

Revision ID: 202606270001
Revises:
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202606270001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_column(name: str) -> sa.Column:
    """Return a timezone-aware timestamp column with a database default."""

    return sa.Column(
        name,
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def upgrade() -> None:
    """Create the first set of domain tables."""

    op.create_table(
        "muscle_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        timestamp_column("created_at"),
        timestamp_column("updated_at"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_muscle_groups_code"), "muscle_groups", ["code"])

    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        timestamp_column("created_at"),
        timestamp_column("updated_at"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workouts_date"), "workouts", ["date"])

    op.create_table(
        "muscle_group_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("muscle_group_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ["muscle_group_id"],
            ["muscle_groups.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("muscle_group_id", "locale", name="uq_muscle_group_locale"),
    )
    op.create_index(
        op.f("ix_muscle_group_translations_locale"),
        "muscle_group_translations",
        ["locale"],
    )

    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("muscle_group_id", sa.Integer(), nullable=False),
        sa.Column("equipment", sa.String(length=80), nullable=True),
        sa.Column("is_custom", sa.Boolean(), server_default="false", nullable=False),
        timestamp_column("created_at"),
        timestamp_column("updated_at"),
        sa.ForeignKeyConstraint(
            ["muscle_group_id"],
            ["muscle_groups.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_exercises_code"), "exercises", ["code"])

    op.create_table(
        "exercise_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exercise_id", "locale", name="uq_exercise_locale"),
    )
    op.create_index(
        op.f("ix_exercise_translations_locale"),
        "exercise_translations",
        ["locale"],
    )

    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["workout_id"], ["workouts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workout_id", "order_index", name="uq_workout_exercise_order"),
    )

    op.create_table(
        "exercise_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("rpe", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["workout_exercise_id"],
            ["workout_exercises.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workout_exercise_id", "set_number", name="uq_set_number"),
    )

    op.create_table(
        "personal_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("workout_id", sa.Integer(), nullable=True),
        sa.Column("exercise_set_id", sa.Integer(), nullable=True),
        sa.Column("record_type", sa.String(length=40), nullable=False),
        sa.Column("value", sa.Numeric(precision=10, scale=2), nullable=False),
        timestamp_column("created_at"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["exercise_set_id"],
            ["exercise_sets.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["workout_id"], ["workouts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exercise_id", "record_type", name="uq_exercise_record_type"),
    )
    op.create_index(
        op.f("ix_personal_records_record_type"),
        "personal_records",
        ["record_type"],
    )


def downgrade() -> None:
    """Drop the initial domain tables in dependency order."""

    op.drop_index(op.f("ix_personal_records_record_type"), table_name="personal_records")
    op.drop_table("personal_records")
    op.drop_table("exercise_sets")
    op.drop_table("workout_exercises")
    op.drop_index(op.f("ix_exercise_translations_locale"), table_name="exercise_translations")
    op.drop_table("exercise_translations")
    op.drop_index(op.f("ix_exercises_code"), table_name="exercises")
    op.drop_table("exercises")
    op.drop_index(
        op.f("ix_muscle_group_translations_locale"),
        table_name="muscle_group_translations",
    )
    op.drop_table("muscle_group_translations")
    op.drop_index(op.f("ix_workouts_date"), table_name="workouts")
    op.drop_table("workouts")
    op.drop_index(op.f("ix_muscle_groups_code"), table_name="muscle_groups")
    op.drop_table("muscle_groups")
