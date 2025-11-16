"""Database utilities with proper connection management."""
import mysql.connector
from contextlib import contextmanager
from config import Config


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures proper cleanup and error handling.
    """
    conn = None
    try:
        conn = mysql.connector.connect(**Config.get_db_config())
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn and conn.is_connected():
            conn.close()


@contextmanager
def get_db_cursor(dictionary=False):
    """
    Context manager for database cursors.
    Automatically handles connection and cursor cleanup.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
        finally:
            cursor.close()


def get_user_by_email(email):
    """Get user by email address."""
    with get_db_cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
        return cursor.fetchone()


def create_user(email, hashed_password):
    """Create a new user in the database."""
    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO person (email, password) VALUES (%s, %s)",
            (email, hashed_password)
        )


def user_exists(email):
    """Check if a user with the given email exists."""
    user = get_user_by_email(email)
    return user is not None

