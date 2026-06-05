from pydantic import BaseModel


class Character(BaseModel):
    id: str
    name: str
    alignment: str
    image_url: str
    intelligence: int
    strength: int
    speed: int
    durability: int
    power: int
    combat: int
    powers_text: str


class BattleRequest(BaseModel):
    team_a: list[str]
    team_b: list[str]


class BattleResponse(BaseModel):
    story: list[str]
    winner: str
    score_a: int
    score_b: int
    team_a: list[Character]
    team_b: list[Character]


class HealthResponse(BaseModel):
    status: str
