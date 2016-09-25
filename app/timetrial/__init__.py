from flask import Blueprint

timetrial = Blueprint('timetrial', __name__, template_folder='templates')

import views
