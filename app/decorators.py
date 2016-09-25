from functools import wraps

from flask import abort

from flask_login import current_user


def admin_required(fn):
    """Only allow administrators to access the view."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return fn(*args, **kwargs)
    return decorated_function
