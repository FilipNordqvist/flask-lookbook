"""
Configuration management for the Flask application.

This module centralizes all configuration settings. Instead of scattering configuration
throughout the codebase, we keep it all in one place. This makes it easier to:
- See all configuration options at a glance
- Change settings without hunting through multiple files
- Have different configurations for different environments (dev, test, production)

We use environment variables to store sensitive information like passwords and API keys.
This is a security best practice - never hardcode secrets in your code!
"""
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
# The .env file should be in the project root and should NOT be committed to git
# It contains sensitive information like database passwords and API keys
load_dotenv()


class Config:
    """
    Base configuration class.
    
    This class holds all configuration settings for the application.
    We use a class instead of a dictionary because:
    1. It's easier to organize related settings
    2. We can add methods (like validate() and get_db_config())
    3. It's more Pythonic and easier to extend later
    
    All settings are read from environment variables using os.getenv().
    The second parameter to os.getenv() is the default value if the variable doesn't exist.
    """
    
    # Secret key for Flask sessions and CSRF protection
    # This MUST be set in your .env file - Flask needs this to sign cookies securely
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    
    # Database configuration
    # These settings tell the application how to connect to the MySQL database
    MYSQL_HOST = os.getenv("MYSQLHOST", "localhost")  # Database server address
    MYSQL_PORT = int(os.getenv("MYSQLPORT", 3306))    # Database port (3306 is MySQL default)
    MYSQL_USER = os.getenv("MYSQLUSER", "root")       # Database username
    MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD", "")   # Database password
    MYSQL_DATABASE = os.getenv("MYSQLDATABASE", "test")  # Name of the database to use
    
    # Email configuration
    # These are for the Resend email service (used to send contact form emails)
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")  # API key for Resend service
    EMAIL_FROM = os.getenv("EMAIL_FROM", "info@nordqvist.tech")  # Sender email address
    EMAIL_TO = os.getenv("EMAIL_TO", "info@nordqvist.tech")      # Recipient email address
    
    # Session configuration
    # These settings control how Flask handles session cookies (cookies that remember logged-in users)
    
    # SESSION_COOKIE_SECURE: Only send cookies over HTTPS connections
    # Set this to "true" in production when you have SSL/HTTPS enabled
    # In development, you can leave it as "false" to work with http://localhost
    # The .lower() == "true" converts the string to a boolean
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    
    # SESSION_COOKIE_HTTPONLY: Prevents JavaScript from accessing the cookie
    # This protects against XSS (Cross-Site Scripting) attacks
    # Always set this to True for security
    SESSION_COOKIE_HTTPONLY = True
    
    # SESSION_COOKIE_SAMESITE: Controls when cookies are sent with cross-site requests
    # "Lax" is a good default - it allows cookies on normal navigation but blocks them
    # on cross-site POST requests, which helps prevent CSRF attacks
    SESSION_COOKIE_SAMESITE = "Lax"
    
    @staticmethod
    def get_db_config():
        """
        Get database configuration as a dictionary.
        
        This method returns all database settings in a format that mysql.connector expects.
        We use a method instead of just accessing the attributes directly because:
        1. It keeps the database connection code cleaner
        2. We could add validation or transformation logic here if needed
        3. It's a common pattern in Flask applications
        
        Returns:
            dict: A dictionary with database connection parameters
        """
        return {
            "host": Config.MYSQL_HOST,
            "port": Config.MYSQL_PORT,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
            "database": Config.MYSQL_DATABASE,
        }
    
    @staticmethod
    def validate():
        """
        Validate that required configuration is present.
        
        This method checks that all required environment variables are set.
        We call this when the application starts up, so we fail fast if something
        is misconfigured rather than discovering it later when trying to use it.
        
        The @staticmethod decorator means this method doesn't need an instance
        of the Config class to be called - you can call it like: Config.validate()
        
        Raises:
            ValueError: If any required environment variables are missing
        """
        # List of environment variable names that MUST be set
        required_vars = ["FLASK_SECRET_KEY"]
        
        # List comprehension: create a list of variables that are missing
        # os.getenv(var) returns None if the variable doesn't exist
        # "if not os.getenv(var)" checks if the variable is None or empty
        missing = [var for var in required_vars if not os.getenv(var)]
        
        # If any variables are missing, raise an error with a helpful message
        if missing:
            # f-string: a way to format strings in Python (Python 3.6+)
            # f"...{variable}..." inserts the variable value into the string
            # ', '.join(missing) joins the list items with commas and spaces
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
