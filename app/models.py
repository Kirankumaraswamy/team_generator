from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, PrimaryKeyConstraint, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created = Column(DateTime(timezone=True), server_default=func.now())

    players = relationship('GamePlayer', back_populates='game')
    rounds = relationship('Round', back_populates='game')

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    created = Column(DateTime(timezone=True), server_default=func.now())

    games = relationship('GamePlayer', back_populates='player')

class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    round_name = Column(String)
    round_number = Column(Integer)
    shuffle = Column(Boolean)
    created = Column(DateTime(timezone=True), server_default=func.now())

    game = relationship('Game', back_populates='rounds')
    teams = relationship('Team', back_populates='round')

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("rounds.id"))
    name = Column(String, index=True)
    created = Column(DateTime(timezone=True), server_default=func.now())

    round = relationship('Round', back_populates='teams')
    players = relationship('PlayerTeam', back_populates='team')

class GamePlayer(Base):
    __tablename__ = "games_players"

    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    created = Column(DateTime(timezone=True), server_default=func.now())

    player = relationship('Player', back_populates='games')
    game = relationship('Game', back_populates='players')

    __table_args__ = (
        PrimaryKeyConstraint('player_id', 'game_id'),
    )

class PlayerTeam(Base):
    __tablename__ = "players_teams"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    created = Column(DateTime(timezone=True), server_default=func.now())

    player = relationship('Player')
    team = relationship('Team', back_populates='players')

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("rounds.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    score = Column(Integer)
    created = Column(DateTime(timezone=True), server_default=func.now())