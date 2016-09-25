from flask import request, redirect, url_for, render_template, flash, g, abort
from flask_login import current_user
from flask.ext.babel import gettext
from flask.ext.login import login_required
from app.database import db
from app.user.models import User
from app.games.forms import CreateGameForm
from app.games.models import Game, GameOutcome, GameState
import flask_sijax

from ..games import games


class SijaxHandler(object):
    """A container class for all Sijax handlers.
    Grouping all Sijax handler functions in a class
    (or a Python module) allows them all to be registered with
    a single line of code.
    """

    @staticmethod
    def save_time(obj_response, reaction_time, game_id):
        # much dark mojo...

        game = Game.query.filter_by(id=game_id).first()
        if not game:
            return redirect(url_for('games.index'))

        if game.player1 == current_user.id and game.player1_time is None:
            game.player1_time = reaction_time
        if game.player2 == current_user.id and game.player2_time is None:
            game.player2_time = reaction_time

        opponent_time = game.get_opponent_time()

        if opponent_time is not None:
            if game.player1_time < game.player2_time:
                game.outcome = GameOutcome.PLAYER1
            if game.player1_time > game.player2_time:
                game.outcome = GameOutcome.PLAYER2
            if game.player1_time == game.player2_time:
                game.outcome = GameOutcome.TIE

        if game.outcome is not None:
            game.state = GameState.COMPLETED
            obj_response.html('#game_status', 'Completed')
            obj_response.attr('#game_status', 'class', 'label label-success')

        db.session.commit()

        outcome = game.get_outcome()

        if outcome == 'Win':
            obj_response.html('#game_result', 'You won!')
        if outcome == 'Loss':
            obj_response.html('#game_result', 'You lost!')
        if outcome == 'Tied!':
            obj_response.html('#game_result', 'It was a tie!')
        if outcome is None:
            obj_response.html(
                '#game_result', 'Still waiting for opponent, check back later')

        current_best_time = current_user.best_time
        if not current_best_time or reaction_time < current_best_time:
            current_user.best_time = reaction_time
            current_user.update()
            flash(gettext('You got a new best time!'), 'success')


@games.route('/', methods=['GET'])
@login_required
def index():
    games = Game.user_games()
    return render_template('games.html', games=games)


@games.route('/create', methods=['GET', 'POST'])
@login_required
def create_game():
    form = CreateGameForm()
    if form.validate_on_submit():
        game = Game(
            player1=current_user,
            player2=form.player2.data)
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('games.index'))
    return render_template('create_game_modal.html', form=form)


@flask_sijax.route(games, '/play/<int:game_id>')
@login_required
def play_game(game_id):
    game = Game.query.filter_by(id=game_id).first_or_404()

    if game.player1 != current_user.id and game.player2 != current_user.id:
        return render_template('not_user_game.html', game=game)

    if game.state == GameState.COMPLETED or (
            game.state == GameState.PENDING and
            game.get_player_time() is not None):
        return render_template('game_already_played.html', game=game)

    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    return render_template('play_game.html', game=game)
