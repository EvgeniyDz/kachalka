from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.main import app
from app.services.analytics import (
    ESTIMATED_1RM,
    MAX_REPS,
    MAX_VOLUME,
    MAX_WEIGHT,
    build_record_candidates,
    calculate_estimated_1rm,
    calculate_volume,
)


def test_analytics_routes_are_registered_in_openapi() -> None:
    """Analytics endpoints are exposed in the FastAPI schema."""

    paths = app.openapi()["paths"]

    assert "/api/v1/analytics/exercises/{exercise_id}/progress" in paths
    assert "/api/v1/analytics/weekly-volume" in paths
    assert "/api/v1/analytics/records" in paths
    assert "/api/v1/analytics/muscle-groups/frequency" in paths


def test_volume_and_estimated_1rm_calculations() -> None:
    """Analytics formulas use Decimal math and round to two decimals."""

    assert calculate_volume(Decimal("82.50"), 6) == Decimal("495.00")
    assert calculate_estimated_1rm(Decimal("82.50"), 6) == Decimal("99.00")
    assert calculate_volume(None, 6) is None
    assert calculate_estimated_1rm(Decimal("82.50"), 0) is None


def test_build_record_candidates_for_workout_set() -> None:
    """A set can produce all supported personal-record candidate types."""

    exercise_set = SimpleNamespace(
        id=1000,
        weight=Decimal("82.50"),
        reps=6,
    )
    workout_exercise = SimpleNamespace(
        exercise_id=10,
        sets=[exercise_set],
    )
    workout = SimpleNamespace(
        id=1,
        date=date(2026, 6, 30),
        exercises=[workout_exercise],
    )

    candidates = build_record_candidates(workout)
    values_by_type = {candidate.record_type: candidate.value for candidate in candidates}

    assert values_by_type[MAX_WEIGHT] == Decimal("82.50")
    assert values_by_type[MAX_REPS] == Decimal("6")
    assert values_by_type[MAX_VOLUME] == Decimal("495.00")
    assert values_by_type[ESTIMATED_1RM] == Decimal("99.00")