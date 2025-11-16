"""Flask application factory."""
from flask import Flask
from config import Config
from routes.auth import auth_bp
from routes.main import main_bp
from routes.contact import contact_bp


def create_app():
    """Create and configure the Flask application."""
    # Validate configuration
    Config.validate()
    
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY
    
    # Configure session cookies
    app.config['SESSION_COOKIE_SECURE'] = Config.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
