"""
Configuration management for the Flask application.

This module centralizes all configuration settings. Instead of scattering configuration
throughout the codebase, we keep it all in one place. This makes it easier to:
- See all configuration options at a glance
- Change settings without hunting through multiple files
- Have different configurations for different environments (dev, test, production)

We use environment variables to store sensitive information like passwords and API keys.
This is a security best practice - never hardcode secrets in your code!

IMPORTANT: We use @property decorators instead of class attributes to ensure
environment variables are read fresh each time they're accessed. This is critical
for testing, where environment variables might be set after the config module is imported.
If we used class attributes, they would be evaluated once at import time and cache
the values, making them stale in tests.

To make class-level access work (like Config.SECRET_KEY), we use __getattr__ on the
class itself to delegate property access to a singleton instance.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
# The .env file should be in the project root and should NOT be committed to git
# It contains sensitive information like database passwords and API keys
load_dotenv()


class ConfigMeta(type):
    """
    Metaclass for Config to enable class-level property access.

    In Python, __getattr__ on a class doesn't work the way you might expect.
    To make class-level attribute access work (like Config.SECRET_KEY), we need
    to use a metaclass. The metaclass's __getattr__ is called when accessing
    attributes on the class itself.

    This allows Config.SECRET_KEY to work even though SECRET_KEY is a property
    (which normally only works on instances).
    """

    def __getattribute__(cls, name):
        """
        Allow class-level access to properties (e.g., Config.SECRET_KEY).

        This method intercepts ALL attribute access on the Config class.
        If the attribute is a property descriptor, we access it through
        the singleton instance to get the actual value.
        """
        # First, try to get the attribute normally
        attr = super().__getattribute__(name)

        # If it's a property descriptor, access it through an instance
        if isinstance(attr, property):
            # Get or create the singleton instance
            if cls._instance is None:
                cls._instance = cls()
            # Access the property through the instance to get the actual value
            return getattr(cls._instance, name)

        # Otherwise, return the attribute as-is
        return attr


class Config(metaclass=ConfigMeta):
    """
    Base configuration class.

    This class holds all configuration settings for the application.
    We use a class instead of a dictionary because:
    1. It's easier to organize related settings
    2. We can add methods (like validate() and get_db_config())
    3. It's more Pythonic and easier to extend later

    All settings are read from environment variables using os.getenv().
    The second parameter to os.getenv() is the default value if the variable doesn't exist.

    IMPORTANT: We use @property decorators to ensure environment variables are
    read fresh each time they're accessed, not cached at import time. This is
    essential for testing where environment variables are set after module import.

    Class-level access (like Config.SECRET_KEY) works through the ConfigMeta
    metaclass's __getattr__ method, which delegates to a singleton instance.
    """

    # Singleton instance - created once, used for all property access
    _instance = None

    def __new__(cls):
        """
        Create a singleton instance.

        This ensures only one Config instance exists, which is important
        for consistency. However, we also support class-level access.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def SECRET_KEY(self):
        """
        Secret key for Flask sessions and CSRF protection.

        This MUST be set in your .env file - Flask needs this to sign cookies securely.
        Using @property ensures this is read fresh from the environment each time,
        not cached at import time.
        """
        return os.getenv("FLASK_SECRET_KEY")

    @property
    def MYSQL_HOST(self):
        """Database server address."""
        return os.getenv("MYSQLHOST", "localhost")

    @property
    def MYSQL_PORT(self):
        """Database port (3306 is MySQL default)."""
        return int(os.getenv("MYSQLPORT", 3306))

    @property
    def MYSQL_USER(self):
        """Database username."""
        return os.getenv("MYSQLUSER", "root")

    @property
    def MYSQL_PASSWORD(self):
        """Database password."""
        return os.getenv("MYSQLPASSWORD", "")

    @property
    def MYSQL_DATABASE(self):
        """Name of the database to use."""
        return os.getenv("MYSQLDATABASE", "test")

    @property
    def BASE_DOMAIN(self):
        """
        Base domain for the application.

        This is used to construct default email addresses and can be used
        for other domain-related configuration. Set BASE_DOMAIN environment
        variable to customize (e.g., BASE_DOMAIN=example.com).
        Defaults to "nordqvist.tech" if not set.
        """
        return os.getenv("BASE_DOMAIN", "nordqvist.tech")

    @property
    def RESEND_API_KEY(self):
        """API key for Resend email service."""
        return os.getenv("RESEND_API_KEY")

    @property
    def EMAIL_FROM(self):
        """
        Sender email address.

        If EMAIL_FROM environment variable is set, it will be used directly.
        Otherwise, it defaults to "info@{BASE_DOMAIN}" where BASE_DOMAIN
        comes from the BASE_DOMAIN environment variable (or "nordqvist.tech").
        """
        # Check if EMAIL_FROM is explicitly set
        explicit_email = os.getenv("EMAIL_FROM")
        if explicit_email:
            return explicit_email
        # Otherwise, construct from base domain
        return f"info@{self.BASE_DOMAIN}"

    @property
    def EMAIL_TO(self):
        """
        Recipient email address.

        If EMAIL_TO environment variable is set, it will be used directly.
        Otherwise, it defaults to "info@{BASE_DOMAIN}" where BASE_DOMAIN
        comes from the BASE_DOMAIN environment variable (or "nordqvist.tech").
        """
        # Check if EMAIL_TO is explicitly set
        explicit_email = os.getenv("EMAIL_TO")
        if explicit_email:
            return explicit_email
        # Otherwise, construct from base domain
        return f"info@{self.BASE_DOMAIN}"

    @property
    def SESSION_COOKIE_SECURE(self):
        """
        Only send cookies over HTTPS connections.

        Set this to "true" in production when you have SSL/HTTPS enabled.
        In development, you can leave it as "false" to work with http://localhost
        """
        return os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"

    @property
    def SESSION_COOKIE_HTTPONLY(self):
        """
        Prevents JavaScript from accessing the cookie.

        This protects against XSS (Cross-Site Scripting) attacks.
        Always set this to True for security.
        """
        return True

    @property
    def SESSION_COOKIE_SAMESITE(self):
        """
        Controls when cookies are sent with cross-site requests.

        "Lax" is a good default - it allows cookies on normal navigation but blocks them
        on cross-site POST requests, which helps prevent CSRF attacks.
        """
        return "Lax"

    @classmethod
    def get_db_config(cls):
        """
        Get database configuration as a dictionary.

        This method returns all database settings in a format that mysql.connector expects.
        We use a method instead of just accessing the attributes directly because:
        1. It keeps the database connection code cleaner
        2. We could add validation or transformation logic here if needed
        3. It's a common pattern in Flask applications

        Note: Since we're using properties, we access them through the singleton instance.
        This method works as both a classmethod (Config.get_db_config()) and can be
        called on an instance.

        Returns:
            dict: A dictionary with database connection parameters
        """
        # Get the singleton instance to access properties
        instance = cls._instance if cls._instance is not None else cls()
        return {
            "host": instance.MYSQL_HOST,
            "port": instance.MYSQL_PORT,
            "user": instance.MYSQL_USER,
            "password": instance.MYSQL_PASSWORD,
            "database": instance.MYSQL_DATABASE,
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

        Note: This method reads directly from os.getenv() to ensure it checks
        the current environment variable values, not cached class attributes.

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
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


# Initialize the singleton instance
# This ensures the instance exists for class-level property access
Config._instance = Config()
