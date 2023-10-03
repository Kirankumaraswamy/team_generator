from fastapi import FastAPI, Depends, HTTPException, Path, Body
from app import models, schemas, crud, dependencies
from app.database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Team generator")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/heartbeat")
async def hearbeat():
    return "random team generator app is up and running."

@app.post("/player")
async def add_player(player: schemas.Player, db: Session = Depends(get_db)):
    db_player = crud.player_by_user_name(db=db, user_name=player.user_name)
    if db_player:
        raise HTTPException(status_code=400, detail="Player with same user name already exists.")
    return crud.add_player(db=db, player=player)

@app.get("/player")
async def get_player(user_name: str, db: Session = Depends(get_db)):
    player = crud.player_by_user_name(db=db, user_name=user_name)
    if not player:
        raise HTTPException(status_code=404, detail="Player with given user name doesn't exist in database.")
    return player
@app.get("/players")
async def get_players(db: Session = Depends(get_db)):
    players = crud.get_players(db=db)
    return players

@app.post("/game", response_model=schemas.Game)
async def create_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    db_game = crud.game_by_name(db=db, name=game.name)
    if db_game:
        raise HTTPException(status_code=400, detail="Game with same name already exists.")
    players = []
    for user_name in game.players:
        user = crud.player_by_user_name(db=db, user_name=user_name)
        if user_name not in players:
            players.append(user_name)
        else:
            raise HTTPException(status_code=400, detail=f"Player with user name {user_name} exists multiple times.")
        if not user:
            raise HTTPException(status_code=400, detail=f"Player with user name {user_name} doesn't exists.")
    game = crud.create_game(db=db, game=game)
    return game

@app.get("/games")
async def get_games(db: Session = Depends(get_db)):
    games = crud.get_games(db=db)
    return games

@app.get("/game/{game_name}", response_model=schemas.Game)
def get_game(game_name: str, db: Session = Depends(get_db)):
    game = crud.game_by_name(db=db, name=game_name)
    if not game:
        raise HTTPException(status_code=404, detail="Game with given name doesn't exist in database.")
    return game

@app.post("/round/{game_name}", response_model=schemas.Round)
def create_round(game_name: str,
                 round: schemas.RoundCreate = Body(), db: Session = Depends(get_db)):
    game = crud.game_by_name(db=db, name=game_name)
    if not game:
        raise HTTPException(status_code=404, detail="Game with given name doesn't exist in database.")

    if len(game.players) < int(round.total_teams):
        raise HTTPException(status_code=400, detail="Number of teams can't be greater than the number of players in the game.")

    game_round = crud.get_round(db=db, game_id=game.id, round_name=round.round_name)
    if game_round:
        raise HTTPException(status_code=400, detail="Round names has to be unique in a game.")

    if round.shuffle:
        teams = []
        # if the user is sending team names already then use it
        if round.team_names:
            teams = round.team_names
        for i in range(int(round.total_teams)):
            if i >= len(teams):
                teams.append("Team" + str(i + 1))
        teams = teams[:round.total_teams]
        round.team_names = teams
    db_round = crud.add_round(db=db, game=game, round=round)
    return db_round

@app.get("/round/{game_name}/{round_name}", response_model=schemas.Round)
def get_round(game_name: str, round_name: str = Path(), db: Session = Depends(get_db)):
    game = crud.game_by_name(db=db, name=game_name)
    if not game:
        raise HTTPException(status_code=404, detail="Game with given name doesn't exist in database.")
    game_round = crud.get_round(db=db, game_id=game.id, round_name=round_name)
    if not game_round:
        raise HTTPException(status_code=404, detail="Round with given round name doesn't exist for the game.")
    print(game_round.teams)
    return game_round

@app.post("/score/{game_name}/{round_name}")
async def add_score(game_name: str,
                    round_name: str = Path(), body: schemas.Score = Body(description="JSON object with keys as team names and values as the scores"), db: Session = Depends(get_db)):
    game = crud.game_by_name(db=db, name=game_name)
    if not game:
        raise HTTPException(status_code=404, detail="Game with given name doesn't exist in database.")

    game_round = crud.get_round(db=db, game_id=game.id, round_name=round_name)
    if not game_round:
        raise HTTPException(status_code=404, detail="Round with given name doesn't exist in the game.")

    teams = crud.get_teams(db=db, game_id=game.id, round_name=round_name)
    score_items = body.scores
    team_names = [team.name for team in teams ]
    provided_team_names = []

    if len(team_names) != len(score_items):
        raise HTTPException(status_code=400, detail=f"Please specify score for all teams participating. {team_names}")

    for item in score_items:
        team_name = item.team_name
        provided_team_names.append(team_name)
        print(team_name, team_names)
        if team_name not in team_names:
            raise HTTPException(status_code=404, detail=f"Team with name {team_name} doesn't exist in the game round.")

    if len(set(team_names) - set(provided_team_names)) > 0:
        raise HTTPException(status_code=400, detail=f"{set(team_names) - set(provided_team_names)} score missing.")

    crud.add_score(db=db, game_id=game.id, round_name=round_name, score_items=score_items)
    return "Scores added."

@app.get("/scores/{game_name}")
async def get_player_scores(game_name: str, db: Session = Depends(get_db)):
    game = crud.game_by_name(db=db, name=game_name)
    if not game:
        raise HTTPException(status_code=404, detail="Game with given name doesn't exist in database.")

    score_sheet = crud.compute_scores(db=db, game_id=game.id)

    # Sort the dictionary by values in ascending order
    sorted_score_sheet = dict(sorted(score_sheet.items(), key=lambda item: item[1], reverse=True))

    return sorted_score_sheet




@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    error_code = exc.status_code
    error_message = exc.detail
    # print("Error :", error_code, " ", error_message)
    response = JSONResponse(
        status_code=error_code, content={"detail": error_message}
    )
    return response