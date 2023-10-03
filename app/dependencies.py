from app import database, schemas, crud
from sqlalchemy.orm import Session
def get_game_names(db: Session):
    game_names = []
    games = crud.get_games(db)
    for game in games:
        game_names.append(game.name)
    print(game_names)
    return game_names
