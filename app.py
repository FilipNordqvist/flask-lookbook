"""
Flask application factory.

This file uses the "Application Factory" pattern, which is a best practice in Flask.
Instead of creating the app directly, we create a function that returns a configured
Flask application. This makes it easier to:
- Test the application (you can create multiple app instances)
- Configure the app differently for different environments (dev, test, production)
- Use the app with different WSGI servers (like gunicorn)

The __name__ variable is a special Python variable that contains the name of the
current module. Flask uses this to know where to find templates and static files.
"""
from flask import Flask
from config import Config
from routes.auth import auth_bp
from routes.main import main_bp
from routes.contact import contact_bp


def create_app():
    """
    Create and configure the Flask application.
    
    This function is called the "Application Factory" because it creates (manufactures)
    a Flask application instance. This is a common pattern in Flask applications.
    
    Returns:
        Flask: A configured Flask application instance
    """
    # Validate configuration before creating the app
    # This ensures we fail fast if required environment variables are missing
    # rather than discovering the problem later when trying to use them
    Config.validate()
    
    # Create a Flask application instance
    # __name__ tells Flask where to find templates, static files, etc.
    app = Flask(__name__)
    
    # Set the secret key for the application
    # The secret key is used to sign session cookies and other security-related things
    # NEVER commit the actual secret key to version control - always use environment variables!
    app.secret_key = Config.SECRET_KEY
    
    # Configure session cookies for security
    # These settings help protect against common web vulnerabilities:
    # - SESSION_COOKIE_SECURE: Only send cookies over HTTPS (set to True in production)
    # - SESSION_COOKIE_HTTPONLY: Prevents JavaScript from accessing cookies (XSS protection)
    # - SESSION_COOKIE_SAMESITE: Helps prevent CSRF attacks
    app.config['SESSION_COOKIE_SECURE'] = Config.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
    
    # Register blueprints
    # Blueprints are Flask's way of organizing routes into separate modules
    # Think of them as "mini-applications" that can be registered with the main app
    # This keeps our code organized and makes it easier to maintain
    app.register_blueprint(auth_bp)      # Authentication routes (login, register, logout)
    app.register_blueprint(main_bp)      # Main application routes (home, about, etc.)
    app.register_blueprint(contact_bp)   # Contact form routes
    
    return app


# Lazy application initialization
# We don't create the app immediately at import time because:
# 1. Test discovery (pytest) imports modules before setting up environment variables
# 2. This would cause Config.validate() to fail if FLASK_SECRET_KEY isn't set yet
# 
# Instead, we use a lazy initialization pattern: the app is only created when
# it's actually accessed. This allows:
# - Test fixtures to set environment variables before app creation
# - Gunicorn and other WSGI servers to still access app:app (they access it at runtime)
# - Import-time operations to succeed without requiring environment variables
_app_instance = None


def _get_app():
    """
    Get or create the Flask application instance (lazy initialization).
    
    This function creates the app on first access, not at import time.
    This is important for:
    - Test discovery: pytest imports modules before setting env vars
    - Development: allows importing app.py without all env vars set
    - Production: gunicorn accesses app at runtime, so it works fine
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = create_app()
    return _app_instance


# For WSGI servers (gunicorn, uwsgi, etc.) and direct imports
# We provide 'app' as a property-like accessor
# When gunicorn does 'from app import app', it gets this object
# When it accesses app (at runtime), it triggers _get_app() which creates the instance
class _LazyApp:
    """
    Lazy app accessor for WSGI servers.
    
    This class allows 'app' to be accessed like a normal variable, but
    actually creates the Flask instance only when first accessed. This defers
    Config.validate() until runtime, allowing test discovery to work.
    """
    def __getattr__(self, name):
        """Delegate all attribute access to the actual Flask app instance."""
        return getattr(_get_app(), name)
    
    def __call__(self, *args, **kwargs):
        """Allow app to be called as a WSGI application."""
        return _get_app()(*args, **kwargs)


# Create the lazy app accessor
# This allows: from app import app (works for gunicorn, tests, etc.)
# The actual Flask instance is created on first access
app = _LazyApp()


# This block only runs if this file is executed directly (not imported)
# It's a common Python pattern: if __name__ == '__main__'
# This allows us to run the app with: python app.py
# But it won't run if we import this module from another file
if __name__ == '__main__':
    # Run the Flask development server
    # host="0.0.0.0" means the server will be accessible from any network interface
    # port=8080 is the port number the server will listen on
    # Note: This is only for development! In production, use gunicorn or similar
    # Accessing app.run() triggers lazy initialization via __getattr__
    app.run(host="0.0.0.0", port=8080)
