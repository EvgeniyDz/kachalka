from pydantic import BaseModel, ConfigDict, Field


class TranslationInput(BaseModel):
    """Localized text supplied by the API client."""

    locale: str = Field(min_length=2, max_length=8)
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None


class TranslationRead(BaseModel):
    """Localized text returned by the API."""

    locale: str
    name: str
    description: str | None = None


class MuscleGroupRead(BaseModel):
    """Muscle group displayed in the requested locale."""

    id: int
    code: str
    name: str
    translations: list[TranslationRead]


class ExerciseRead(BaseModel):
    """Exercise catalog item displayed in the requested locale."""

    id: int
    code: str
    name: str
    description: str | None = None
    equipment: str | None = None
    is_custom: bool
    muscle_group: MuscleGroupRead
    translations: list[TranslationRead]


class ExerciseListRead(BaseModel):
    """Paginated exercise catalog response."""

    items: list[ExerciseRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class ExerciseCreate(BaseModel):
    """Payload for creating a custom exercise."""

    code: str | None = Field(default=None, pattern=r"^[a-z0-9_]+$", max_length=100)
    muscle_group_code: str = Field(min_length=1, max_length=80)
    equipment: str | None = Field(default=None, max_length=80)
    translations: list[TranslationInput] = Field(min_length=1)


class ExerciseUpdate(BaseModel):
    """Payload for editing a custom exercise."""

    model_config = ConfigDict(extra="forbid")

    muscle_group_code: str | None = Field(default=None, min_length=1, max_length=80)
    equipment: str | None = Field(default=None, max_length=80)
    translations: list[TranslationInput] | None = None