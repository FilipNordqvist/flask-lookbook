"""Configuration management for the Flask application."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    
    # Database configuration
    MYSQL_HOST = os.getenv("MYSQLHOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQLPORT", 3306))
    MYSQL_USER = os.getenv("MYSQLUSER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQLDATABASE", "test")
    
    # Email configuration
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "info@nordqvist.tech")
    EMAIL_TO = os.getenv("EMAIL_TO", "info@nordqvist.tech")
    
    # Session configuration
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    @staticmethod
    def get_db_config():
        """Get database configuration as dictionary."""
        return {
            "host": Config.MYSQL_HOST,
            "port": Config.MYSQL_PORT,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
            "database": Config.MYSQL_DATABASE,
        }
    
    @staticmethod
    def validate():
        """Validate that required configuration is present."""
        required_vars = ["FLASK_SECRET_KEY"]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

