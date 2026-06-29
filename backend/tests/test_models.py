from app import models
from app.db.base import Base


def test_domain_models_are_registered_in_metadata() -> None:
    """All roadmap tables are attached to SQLAlchemy metadata."""

    expected_tables = {
        "exercise_sets",
        "exercise_translations",
        "exercises",
        "muscle_group_translations",
        "muscle_groups",
        "personal_records",
        "workout_exercises",
        "workouts",
    }

    assert expected_tables.issubset(Base.metadata.tables)
    assert models.Exercise.__tablename__ == "exercises"
