from sqlalchemy.orm import Session
import random
from sqlalchemy import and_, desc, select, func
from app import models, schemas
from typing import List

def add_player(db: Session, player: schemas.Player):
    player = models.Player(user_name=player.user_name)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()

def player_by_user_name(db: Session, user_name: str):
    return db.query(models.Player).filter(models.Player.user_name == user_name).first()

def game_by_name(db: Session, name: str):
    return db.query(models.Game).filter(models.Game.name == name).first()

def create_game(db: Session, game: schemas.Game):
    db_game = models.Game(name=game.name)
    db.add(db_game)

    db.commit()
    db.refresh(db_game)

    for user_name in game.players:
        db_player = db.query(models.Player).filter(models.Player.user_name == user_name).first()
        if db_player:
            db_game_player = models.GamePlayer(game_id=db_game.id, player_id=db_player.id)
            db.add(db_game_player)

    db.commit()
    return db_game

def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Game).offset(skip).limit(limit).all()

def add_round(db: Session, game: models.Game, round: schemas.RoundCreate):
    db_rounds = get_rounds(db=db, game_id=game.id)

    round_number = len(db_rounds) + 1
    db_round = models.Round(game_id=game.id, round_name=round.round_name, round_number=round_number, shuffle=round.shuffle)
    db.add(db_round)
    db.commit()
    db.refresh(db_round)

    db_teams = []

    if round_number == 1 or round.shuffle:
        players = game.players
        random.shuffle(players)
        for team in round.team_names:
            db_team = models.Team(round_id=db_round.id, name=team)
            db.add(db_team)
            db.commit()
            db.refresh(db_team)
            db_teams.append(db_team)

        for index, db_player in enumerate(players):
            db_team = db_teams[index % len(db_teams)]
            db_player_team = models.PlayerTeam(team_id=db_team.id, player_id=db_player.player_id)
            db.add(db_player_team)
        db.commit()
    else:
        last_round = db_rounds[0]
        print(last_round.teams)
        for last_round_team in last_round.teams:
            # use same team names created in last round
            db_team = models.Team(round_id=db_round.id, name=last_round_team.name)
            db.add(db_team)
            db.commit()
            db.refresh(db_team)
            db_teams.append(db_team)
            # put the player in same team as in last round
            team_players = db.query(models.PlayerTeam).filter(models.PlayerTeam.team_id == last_round_team.id).all()
            for team_player in team_players:
                player_id = team_player.player_id
                db_player_team = models.PlayerTeam(team_id=db_team.id, player_id=player_id)
                db.add(db_player_team)

        db.commit()
    return db_round

def get_round(db: Session, game_id: int, round_name: str):
    return db.query(models.Round).filter(and_(models.Round.game_id == game_id, models.Round.round_name == round_name)).first()

def get_rounds(db: Session, game_id: int):
    return db.query(models.Round).filter(and_(models.Round.game_id == game_id)).order_by(desc(models.Round.created)).all()
def get_team(db: Session, game_id: int, round_name: str, team_name: str):
    teams = get_teams(db=db, game_id=game_id, round_name=round_name)
    for team in teams:
        if team.name == team_name:
            return team
    return None

def get_teams(db: Session, game_id: int, round_name: str):
    db_round = get_round(db=db, game_id=game_id, round_name=round_name)
    teams = db.query(models.Team).filter(models.Team.round_id == db_round.id).all()
    return teams

def add_score(db: Session, game_id: int, round_name: str, score_items: List[schemas.ScoreItem]):
    round_id = get_round(db=db, game_id=game_id, round_name=round_name).id
    for score_item in score_items:
        team_id = get_team(db=db, game_id=game_id, round_name=round_name, team_name=score_item.team_name).id
        db_score = db.query(models.Score).filter(and_(models.Score.round_id == round_id, models.Score.team_id == team_id)).first()
        if db_score:
            db_score.score = score_item.score
        else:
            db_score = models.Score(round_id=round_id, team_id=team_id, score=score_item.score)
            db.add(db_score)
        db.commit()


def compute_scores(db: Session, game_id: int):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    players = game.players
    player_scores = {}
    db_rounds = get_rounds(db=db, game_id=game.id)

    for player in players:
        score = 0
        player_name = db.query(models.Player).filter(models.Player.id == player.player_id).first().user_name
        join_results = db.query(models.Round, models.Team, models.PlayerTeam).join(models.Round, models.Round.id == models.Team.round_id).join(
            models.PlayerTeam, models.PlayerTeam.team_id == models.Team.id).filter(and_(models.Round.game_id == game_id, models.PlayerTeam.player_id == player.player_id)).all()
        for result in join_results:
            #print(round_team)

            db_score = db.query(models.Score).filter(models.Score.team_id==result[1].id).first()
            if db_score:
                score += db_score.score
        player_scores[player_name] = score
    return player_scores