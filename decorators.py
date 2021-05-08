from functools import wraps
from flask import request, redirect, url_for, abort
from flask_login import current_user


def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.get_id() is None:
            return redirect(url_for('login', next=request.url))
        elif current_user.id != 1:
            return abort(403,description="Forbidden, Access Denied")
        return function(*args,**kwargs)
    return wrapper_function