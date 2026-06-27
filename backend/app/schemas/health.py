from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response contract for the API health endpoint."""

    status: Literal["ok"]
    service: str
    environment: str
