"""
Utility functions and decorators.

This module contains helper functions that are used throughout the application.
Decorators are a powerful Python feature that let you modify or extend the behavior
of functions without changing their code.

A decorator is a function that takes another function as input and returns a
modified version of that function. In Flask, decorators are commonly used for:
- Authentication checks (like login_required)
- Logging
- Caching
- Rate limiting
- And more!

The @ symbol is Python's syntax for applying a decorator to a function.
"""

from functools import wraps
from flask import redirect, url_for, session


def login_required(f):
    """
    Decorator to require login for a route.

    This decorator checks if a user is logged in before allowing them to access
    a route. If they're not logged in, it redirects them to the login page.

    How decorators work:
    1. When you put @login_required above a function, Python calls login_required()
       with that function as an argument
    2. login_required() returns a new function (decorated_function)
    3. When someone calls the original function, they're actually calling
       decorated_function, which checks login status first

    The @wraps decorator preserves the original function's metadata (name, docstring, etc.)
    This is important for debugging and for Flask's routing system.

    Args:
        f: The function being decorated (the route handler)

    Returns:
        function: A new function that checks login status before calling the original

    Example usage:
        @app.route('/admin')
        @login_required  # This decorator runs before the route function
        def admin():
            return "Admin page"

        # Now if someone tries to access /admin without being logged in,
        # they'll be redirected to the login page automatically
    """

    @wraps(f)  # Preserves the original function's name and metadata
    def decorated_function(*args, **kwargs):
        """
        The wrapper function that actually gets called.

        *args and **kwargs allow this function to accept any arguments
        that the original function might have. This makes the decorator
        work with any route function, regardless of its parameters.

        *args = positional arguments (like regular function parameters)
        **kwargs = keyword arguments (like name=value parameters)
        """
        # Check if the user is logged in
        # session is a Flask object that stores data for the current user
        # It works like a dictionary - you can store and retrieve values
        # 'admin_logged_in' is a key we set when the user successfully logs in
        # .get() returns None if the key doesn't exist (user not logged in)
        if not session.get("admin_logged_in"):
            # User is not logged in - redirect them to the login page
            # redirect() sends an HTTP redirect response to the browser
            # url_for() generates the URL for a route by its function name
            # This is better than hardcoding '/login' because if we rename the route,
            # url_for will still work
            return redirect(url_for("auth.login"))

        # User is logged in - call the original function with all its arguments
        # *args unpacks positional arguments, **kwargs unpacks keyword arguments
        # This passes all arguments through to the original function unchanged
        return f(*args, **kwargs)

    # Return the decorated function
    # When someone uses @login_required, this is what replaces their original function
    return decorated_function
