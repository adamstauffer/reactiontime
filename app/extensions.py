from flask.ext.login import LoginManager
lm = LoginManager()

from flask.ext.restless import APIManager
api = APIManager()

from flask.ext.heroku import Heroku
heroku = Heroku()

from flask.ext.travis import Travis
travis = Travis()

from flask.ext.mail import Mail
mail = Mail()

from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

from flask.ext.bcrypt import Bcrypt
bcrypt = Bcrypt()

from celery import Celery
celery = Celery()

from flask.ext.assets import Environment
assets = Environment()

from flask.ext.babel import Babel
babel = Babel()

from flask_moment import Moment
moment = Moment()
