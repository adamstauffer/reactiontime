from flask_login import current_user
from app.extensions import cache, bcrypt
from app.database import db
from app.user.models import User
import datetime
import enum


class GameState(enum.Enum):
    COMPLETED = 0
    PENDING = 1


class GameOutcome(enum.Enum):
    PLAYER1 = 0
    PLAYER2 = 1
    TIE = 2
    NO_CONTEST = 3


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_ts = db.Column(db.DateTime(timezone=True),
            server_default=db.func.current_timestamp(),)
    updated_ts = db.Column(db.DateTime(timezone=True),
            onupdate=db.func.current_timestamp(),)
    player1 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    player2 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    player1_time = db.Column(db.Float(default=None))
    player2_time = db.Column(db.Float(default=None))
    state = db.Column(db.Integer)
    outcome = db.Column(db.Integer)

    def __init__(self, player1, player2=None):
        self.player1 = player1.id
        self.player2 = player2.id if player2 else None
        self.created_ts = datetime.datetime.now()
        self.state = GameState.PENDING

    def __repr__(self):
        return '<Game %s>' % self.id

    @classmethod
    def user_games(cls):
        games = cls.query.filter(db.or_(
            cls.player1 == current_user.id,
            cls.player2 == current_user.id)).order_by(
            cls.created_ts.desc()).all()
        return games

    def get_player1(self):
        player1 = User.query.filter_by(id=self.player1).first()
        return player1 if player1 else None

    def get_player2(self):
        player2 = User.query.filter_by(id=self.player2).first()
        return player2 if player2 else None

    def get_opponent(self):
        if self.player2 is None:
            return None
        if current_user.id == self.player1:
            opponent_id = self.player2
        if current_user.id == self.player2:
            opponent_id = self.player1
        opponent = User.query.filter_by(id=opponent_id).first()
        return opponent

    def get_opponent_time(self):
        opponent_time = None
        if current_user.id == self.player1:
            opponent_time = self.player2_time
        if current_user.id == self.player2:
            opponent_time = self.player1_time
        return opponent_time

    def get_player_time(self):
        player_time = None
        if current_user.id == self.player1:
            player_time = self.player1_time
        if current_user.id == self.player2:
            player_time = self.player2_time
        return player_time

    def get_state(self):
        if self.state == GameState.COMPLETED:
            return "Completed"
        return "Pending"

    def get_outcome(self):
        if (self.outcome == GameOutcome.PLAYER1 and
                current_user.id == self.player1) or (
                self.outcome == GameOutcome.PLAYER2 and
                current_user.id == self.player2):
            return "Win"
        if (self.outcome == GameOutcome.PLAYER2 and
                current_user.id != self.player2) or (
                self.outcome == GameOutcome.PLAYER1 and
                current_user.id != self.player1):
            return "Loss"
        if self.outcome == GameOutcome.TIE:
            return "Tied!"
        if self.outcome == GameOutcome.NO_CONTEST:
            return "No contest!"
        return None
