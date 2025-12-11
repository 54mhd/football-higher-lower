from typing import List, Literal

from pydantic import BaseModel, Field


class PlayerOut(BaseModel):
    id: int
    name: str
    image_url: str
    stat_value: int


class RandomPlayersResponse(BaseModel):
    players: List[PlayerOut]


class VerifyRequest(BaseModel):
    player_left_id: int = Field(..., ge=1)
    player_right_id: int = Field(..., ge=1)
    guess: Literal["left", "right"]


class VerifyResponse(BaseModel):
    correct: bool
    left_value: int
    right_value: int


class HealthResponse(BaseModel):
    status: str
