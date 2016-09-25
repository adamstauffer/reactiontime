from flask_wtf import Form
from flask.ext.babel import gettext
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.user.models import User
from app.games.models import Game


class CreateGameForm(Form):
    player2 = QuerySelectField(
        gettext('Select a player to battle or leave blank to auto-queue'),
        query_factory=lambda: User.get_active_users(),
        allow_blank=True, get_label="username"
    )

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
