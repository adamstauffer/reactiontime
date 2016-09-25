from flask import (
    current_app, g, request, redirect, url_for, render_template, flash, abort,
)
from flask.ext.babel import gettext
from flask.ext.login import login_required, current_user
from app.user.models import User
from ..timetrial import timetrial
import flask_sijax


class SijaxHandler(object):
    """A container class for all Sijax handlers.
    Grouping all Sijax handler functions in a class
    (or a Python module) allows them all to be registered with
    a single line of code.
    """

    @staticmethod
    def save_time(obj_response, reaction_time):
        current_best_time = current_user.best_time

        if not current_best_time or reaction_time < current_best_time:
            current_user.best_time = reaction_time
            current_user.update()
            obj_response.html('#best_time', str(reaction_time))


@flask_sijax.route(timetrial, '/')
@login_required
def index():
    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    # Regular (non-Sijax request) - render the page template
    return render_template('timetrial.html')
