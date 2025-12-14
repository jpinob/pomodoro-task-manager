"""
Helper functions for the Pomodoro Task Manager.

This module contains utility functions like login_required decorator.
"""

from functools import wraps
from flask import redirect, session, url_for


def login_required(f):
    """
    Decorator to require login for routes.

    Args:
        f: The function to wrap.

    Returns:
        The wrapped function that checks for authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
