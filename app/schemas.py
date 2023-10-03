from pydantic import BaseModel, Field
from typing import List, Union
from datetime import datetime
from pydantic_settings import BaseSettings
class AppSettings(BaseSettings):
    postgres_user:str = Field("", description="Postgres User name")
    postgres_password :str = Field("", description="Postgres User name")
    postgres_db:str = Field("", description="Postgres User name")
    postgres_host:str = Field("", description="Postgres User name")

    class Config:
        env_file = "../env"
class Player(BaseModel):
    user_name: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_name": "Jon"
            }
        }
    }

class GameBase(BaseModel):
    name: str

class GameCreate(GameBase):
    players: List[str]  # List of player IDs

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Game1",
                "players": ["Jon", "sam", "Bill"]
            }
        }
    }

class RoundBase(BaseModel):
    name: str

class CreateTeam(BaseModel):
    teams: List[Union[str, None]] = None
    total_teams: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "teams": ["team1", "team2"],
                "total_teams": 2,
            }
        }
    }

class GamePlayer(BaseModel):
    player: Player
    class Config:
        orm_mode = True

class PlayerTeam(BaseModel):
    player: Player

    class Config:
        orm_mode = True

class Team(BaseModel):
    name: str

    players: list[PlayerTeam]

    class Config:
        orm_mode = True


class Round(BaseModel):
    round_name: str
    round_number: int
    shuffle: bool = False
    teams: list[Team]
    created: datetime
    class Config:
        orm_mode = True

class Game(GameBase):
    id: int
    rounds: list[Round] = []
    players: list[GamePlayer] = []
    created: datetime
    class Config:
        orm_mode = True

class RoundCreate(BaseModel):
    team_names: List[Union[str, None]] = None
    total_teams: int = 2
    round_name: str
    shuffle: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "round_name": "round1",
                "total_teams": 2,
                "shuffle": False,
                "team_names": ["team1", "team2"],
            }
        }
    }

class ScoreItem(BaseModel):
    team_name: str
    score: int
class Score(BaseModel):
    scores: List[ScoreItem]

    model_config = {
        "json_schema_extra": {
            "example": {
                "scores": [
                    {"team_name": "Team1", "score": 30},
                    {"team_name": "Team2", "score": 20},
                ]
            }
        }
    }



