from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Session = sessionmaker()

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    conference = Column(String)
    players = relationship('Player')
    schedule = relationship('Game')


class Player(Base):
    __tablename__ = 'players'

    unique_id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(Integer)
    position = Column(String)
    height = Column(String)
    weight = Column(Integer)
    year = Column(String)
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship('Team', back_populates='players')


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    date = Column(String)
    home_team_id = Column(Integer, ForeignKey('home_team.id'))
    home_team = relationship('Team', back_populates='schedule')
    home_team_score = Column(Integer)
    away_team_id = Column(Integer, ForeignKey('away_team.id'))
    away_team = relationship('Team', back_populates='schedule')
    away_team_score = Column(Integer)
    plays = relationship('Play')

class Play(Base):
    __tablename__ = 'plays'

    unique_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship('Game', back_populates='plays')
    play_id = Column(Integer)
    timestamp = Column(String)
    actor = Column(String)
    action = Column(String)
    assistant = Column(String)
    result_score = Column(String)
