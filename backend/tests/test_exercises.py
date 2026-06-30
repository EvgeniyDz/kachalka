from types import SimpleNamespace

from app.main import app
from app.services.exercises import read_exercise


def test_exercise_routes_are_registered_in_openapi() -> None:
    """The exercise catalog API is exposed in the FastAPI schema."""

    paths = app.openapi()["paths"]

    assert "/api/v1/exercises" in paths
    assert "/api/v1/exercises/{exercise_id}" in paths
    assert "/api/v1/muscle-groups" in paths


def test_exercise_list_route_has_pagination_contract() -> None:
    """Exercise lists expose limit/offset pagination in OpenAPI."""

    operation = app.openapi()["paths"]["/api/v1/exercises"]["get"]
    parameter_names = {parameter["name"] for parameter in operation["parameters"]}

    assert {"limit", "offset"}.issubset(parameter_names)
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ExerciseListRead"
    )


def test_read_exercise_uses_requested_locale_and_fallback() -> None:
    """Exercise API output selects the requested locale with Ukrainian fallback."""

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
            SimpleNamespace(locale="en", name="Bench press", description="Classic press"),
        ],
    )

    english = read_exercise(exercise, "en")
    unknown_locale = read_exercise(exercise, "pl")

    assert english.name == "Bench press"
    assert english.description == "Classic press"
    assert english.muscle_group.name == "Chest"
    assert unknown_locale.name == "Жим лежачи"
    assert unknown_locale.muscle_group.name == "Груди"