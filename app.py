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


# Create the application instance
# This is what gets imported when other modules do "from app import app"
# It's also what gunicorn or other WSGI servers will use to run the application
app = create_app()


# This block only runs if this file is executed directly (not imported)
# It's a common Python pattern: if __name__ == '__main__'
# This allows us to run the app with: python app.py
# But it won't run if we import this module from another file
if __name__ == '__main__':
    # Run the Flask development server
    # host="0.0.0.0" means the server will be accessible from any network interface
    # port=8080 is the port number the server will listen on
    # Note: This is only for development! In production, use gunicorn or similar
    app.run(host="0.0.0.0", port=8080)
