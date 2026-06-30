from datetime import date
from types import SimpleNamespace

from app.main import app
from app.services.workouts import read_workout


def test_workout_routes_are_registered_in_openapi() -> None:
    """Workout CRUD API is exposed in the FastAPI schema."""

    paths = app.openapi()["paths"]

    assert "/api/v1/workouts" in paths
    assert "/api/v1/workouts/{workout_id}" in paths


def test_workout_list_route_has_pagination_contract() -> None:
    """Workout history exposes limit/offset pagination in OpenAPI."""

    operation = app.openapi()["paths"]["/api/v1/workouts"]["get"]
    parameter_names = {parameter["name"] for parameter in operation["parameters"]}

    assert {"limit", "offset"}.issubset(parameter_names)
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/WorkoutListRead"
    )


def test_read_workout_localizes_nested_exercise() -> None:
    """Workout details reuse exercise localization for nested exercise data."""

    muscle_group = SimpleNamespace(
        id=1,
        code="chest",
        translations=[
            SimpleNamespace(locale="uk", name="Груди"),
            SimpleNamespace(locale="en", name="Chest"),
        ],
    )
    exercise = SimpleNamespace(
        id=10,
        code="bench_press",
        equipment="barbell",
        is_custom=False,
        muscle_group=muscle_group,
        translations=[
            SimpleNamespace(locale="uk", name="Жим лежачи", description=None),
            SimpleNamespace(locale="en", name="Bench press", description=None),
        ],
    )
    workout = SimpleNamespace(
        id=1,
        date=date(2026, 6, 30),
        title="Push day",
        notes=None,
        exercises=[
            SimpleNamespace(
                id=100,
                order_index=0,
                notes=None,
                exercise=exercise,
                sets=[
                    SimpleNamespace(
                        id=1000,
                        set_number=1,
                        weight=80,
                        reps=8,
                        rpe=8,
                        notes=None,
                    )
                ],
            )
        ],
    )

    result = read_workout(workout, "en")

    assert result.title == "Push day"
    assert result.exercises[0].exercise.name == "Bench press"
    assert result.exercises[0].sets[0].reps == 8