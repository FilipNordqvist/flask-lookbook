"""
Database utilities with proper connection management.

This module handles all database operations. It uses context managers to ensure
that database connections are always properly closed, even if an error occurs.

Context managers are a Python feature that automatically handle setup and cleanup.
They're perfect for resources like database connections that need to be closed.
The "with" statement uses context managers - you've probably seen it with files:
    with open('file.txt') as f:
        # use f
    # f is automatically closed here, even if an error occurred

We use context managers here to ensure:
1. Connections are always closed (prevents connection leaks)
2. Transactions are rolled back on errors (keeps data consistent)
3. Errors are handled properly (doesn't mask the original error)
"""

import logging
import mysql.connector
from mysql.connector import Error as MySQLError
from contextlib import contextmanager
from config import Config

# Set up a logger for this module
# Logging helps us track errors and debug issues in production
# Each module can have its own logger, which makes it easy to filter logs
logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.

    This function is a context manager - you use it with the "with" statement:
        with get_db_connection() as conn:
            # use conn here
        # conn is automatically closed here

    The @contextmanager decorator from contextlib makes this function work
    as a context manager. The "yield" statement is where execution pauses
    and returns control to the code using the context manager.

    This ensures proper cleanup and error handling:
    - Connections are always closed, even if an error occurs
    - Transactions are committed if everything succeeds
    - Transactions are rolled back if an error occurs

    Yields:
        mysql.connector.connection: A MySQL database connection object

    Raises:
        MySQLError: Any MySQL database error that occurs during operations
    """
    conn = None  # Initialize to None so we can check if connection was created

    try:
        # Create a connection to the MySQL database
        # **Config.get_db_config() unpacks the dictionary returned by get_db_config()
        # This is equivalent to: connect(host="...", port=..., user="...", etc.)
        conn = mysql.connector.connect(**Config.get_db_config())

        # Yield the connection - this is where execution pauses
        # Code using "with get_db_connection() as conn:" will execute here
        # When that code block finishes, execution continues after the yield
        yield conn

        # If we get here, everything succeeded - commit the transaction
        # A transaction is a group of database operations that should all succeed or all fail
        # commit() makes the changes permanent in the database
        conn.commit()

    except MySQLError:
        # If any database error occurred, we need to rollback the transaction
        # This undoes any changes that were made, keeping the database consistent
        # We catch MySQLError specifically (not generic Exception) to avoid masking
        # unexpected errors like KeyboardInterrupt or SystemExit, which should propagate
        if conn:
            try:
                # Try to rollback the transaction
                conn.rollback()
            except MySQLError as rollback_error:
                # If rollback itself fails, we log the error but don't let it
                # mask the original error. This is important - we want to know about
                # the original problem (like a failed INSERT), not just that rollback failed.
                # However, rollback failures are serious and should be logged, as they
                # could indicate database connection issues or corruption.
                logger.error(
                    "Failed to rollback transaction: %s",
                    rollback_error,
                    exc_info=True,  # Include full traceback in the log
                )

        # Re-raise the original exception
        # Using bare "raise" (not "raise e") preserves the full traceback,
        # which makes debugging much easier
        raise  # Preserve original exception and traceback

    finally:
        # The finally block ALWAYS runs, whether there was an error or not
        # This ensures the connection is always closed, preventing connection leaks
        if conn and conn.is_connected():
            # Close the connection to free up database resources
            # Database servers have a limit on how many connections they can handle
            # If we don't close connections, we'll eventually run out
            conn.close()


@contextmanager
def get_db_cursor(dictionary=False):
    """
    Context manager for database cursors.

    A cursor is an object that lets you execute SQL queries and get results.
    This function automatically handles both the connection AND the cursor,
    making it even easier to use.

    The dictionary parameter controls the format of query results:
    - dictionary=False: Results are tuples (row[0], row[1], row[2], ...)
    - dictionary=True: Results are dictionaries (row['email'], row['password'], ...)
    Dictionary format is usually easier to work with.

    Args:
        dictionary (bool): If True, return results as dictionaries instead of tuples

    Yields:
        mysql.connector.cursor: A database cursor object

    Example:
        with get_db_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()  # Returns a dict like {'id': 1, 'name': 'John'}
    """
    # Use the connection context manager to get a connection
    # This ensures the connection is properly managed
    with get_db_connection() as conn:
        # Create a cursor from the connection
        # The dictionary parameter controls result format (see docstring above)
        cursor = conn.cursor(dictionary=dictionary)

        try:
            # Yield the cursor - code using this context manager executes here
            yield cursor
        finally:
            # Always close the cursor when done
            # Cursors also consume resources and should be closed
            cursor.close()


def get_user_by_email(email):
    """
    Get a user from the database by their email address.

    This is a helper function that wraps a common database operation.
    Instead of writing the same SQL query in multiple places, we write it once here.
    This follows the DRY (Don't Repeat Yourself) principle.

    Args:
        email (str): The email address to search for

    Returns:
        dict or None: User data as a dictionary if found, None if not found

    Example:
        user = get_user_by_email('user@example.com')
        if user:
            print(user['email'])  # Access fields like a dictionary
    """
    # Use the cursor context manager - it handles connection and cursor cleanup
    # dictionary=True means results will be dictionaries, not tuples
    with get_db_cursor(dictionary=True) as cursor:
        # Execute a SQL SELECT query
        # The %s is a placeholder that gets replaced with the email value
        # Using placeholders (parameterized queries) prevents SQL injection attacks
        # NEVER build SQL queries by concatenating strings with user input!
        cursor.execute("SELECT * FROM person WHERE email = %s", (email,))

        # fetchone() gets the first row from the query results
        # Returns None if no rows were found
        return cursor.fetchone()


def create_user(email, hashed_password):
    """
    Create a new user in the database.

    This function inserts a new user record into the database.
    The password should already be hashed (using werkzeug.security.generate_password_hash)
    before calling this function - NEVER store plain text passwords!

    Args:
        email (str): The user's email address
        hashed_password (str): The password hash (not the plain text password!)

    Example:
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('my_password')
        create_user('user@example.com', password_hash)
    """
    # Use the cursor context manager
    with get_db_cursor() as cursor:
        # Execute an INSERT query to add a new user
        # The %s placeholders are replaced with the email and hashed_password values
        # The parentheses around (email, hashed_password) make it a tuple
        # MySQL connector expects a tuple or list for the parameter values
        cursor.execute(
            "INSERT INTO person (email, password) VALUES (%s, %s)",
            (email, hashed_password),
        )
        # The connection context manager will automatically commit when this function completes


def user_exists(email):
    """
    Check if a user with the given email already exists in the database.

    This is useful for validation - you might want to check if an email
    is already registered before trying to create a new account.

    Args:
        email (str): The email address to check

    Returns:
        bool: True if a user with this email exists, False otherwise

    Example:
        if user_exists('user@example.com'):
            print("Email already registered!")
        else:
            print("Email is available")
    """
    # Get the user (if they exist)
    user = get_user_by_email(email)

    # Return True if user is not None, False if user is None
    # In Python, None is "falsy", so we can use it directly in a boolean context
    return user is not None


def create_images_table():
    """
    Create the images table if it doesn't exist.

    This function creates a table to store metadata about images uploaded to R2.
    The table stores:
    - id: Primary key (auto-increment)
    - filename: The unique filename in R2
    - r2_key: The full path/key in R2 (e.g., "inspiration/uuid.jpg")
    - url: The public URL to access the image
    - alt_text: Optional alt text for accessibility
    - created_at: Timestamp when the image was uploaded
    - is_active: Whether the image should be displayed (allows soft deletion)

    This function is idempotent - it can be called multiple times safely.
    If the table already exists, it won't create a duplicate.
    """
    with get_db_cursor() as cursor:
        # Create the images table
        # IF NOT EXISTS ensures this is idempotent (safe to call multiple times)
        # AUTO_INCREMENT means the id will automatically increment for each new row
        # DEFAULT CURRENT_TIMESTAMP sets created_at to the current time when a row is inserted
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                r2_key VARCHAR(500) NOT NULL UNIQUE,
                url VARCHAR(1000) NOT NULL,
                alt_text VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_is_active (is_active),
                INDEX idx_created_at (created_at)
            )
            """
        )
        # The connection context manager will commit automatically


def add_image(filename, r2_key, url, alt_text=None):
    """
    Add an image record to the database.

    This function stores metadata about an uploaded image. The actual file
    is stored in Cloudflare R2, but we store the metadata (filename, URL, etc.)
    in the database so we can query and display images efficiently.

    Args:
        filename (str): The unique filename (e.g., "uuid.jpg")
        r2_key (str): The full path/key in R2 (e.g., "inspiration/uuid.jpg")
        url (str): The public URL to access the image
        alt_text (str, optional): Alt text for accessibility (default: None)

    Returns:
        int: The ID of the newly created image record

    Example:
        image_id = add_image(
            filename="abc123.jpg",
            r2_key="inspiration/abc123.jpg",
            url="https://example.com/inspiration/abc123.jpg",
            alt_text="Beautiful interior design"
        )
    """
    with get_db_cursor() as cursor:
        # Insert the image metadata into the database
        cursor.execute(
            """
            INSERT INTO images (filename, r2_key, url, alt_text)
            VALUES (%s, %s, %s, %s)
            """,
            (filename, r2_key, url, alt_text),
        )
        # Get the ID of the newly inserted row
        # LAST_INSERT_ID() returns the auto-increment ID from the last INSERT
        cursor.execute("SELECT LAST_INSERT_ID() as id")
        result = cursor.fetchone()
        return result[0] if result else None


def get_all_active_images():
    """
    Get all active images from the database.

    Returns only images where is_active is TRUE. This allows soft deletion -
    we can hide images without actually deleting them from R2 or the database.

    Returns:
        list: A list of dictionaries, each containing image data
              (id, filename, r2_key, url, alt_text, created_at, is_active)

    Example:
        images = get_all_active_images()
        for image in images:
            print(f"Image URL: {image['url']}")
    """
    with get_db_cursor(dictionary=True) as cursor:
        # Select all active images, ordered by creation date (newest first)
        cursor.execute(
            """
            SELECT id, filename, r2_key, url, alt_text, created_at, is_active
            FROM images
            WHERE is_active = TRUE
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


def get_image_by_id(image_id):
    """
    Get a single image by its ID.

    Args:
        image_id (int): The ID of the image to retrieve

    Returns:
        dict or None: Image data as a dictionary if found, None if not found
    """
    with get_db_cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT id, filename, r2_key, url, alt_text, created_at, is_active
            FROM images
            WHERE id = %s
            """,
            (image_id,),
        )
        return cursor.fetchone()


def deactivate_image(image_id):
    """
    Soft delete an image by setting is_active to FALSE.

    This doesn't actually delete the image from R2 or the database - it just
    marks it as inactive so it won't be displayed. This is useful because:
    1. We can restore images later if needed
    2. We keep a history of what was uploaded
    3. We don't need to delete from R2 immediately (can be done later)

    Args:
        image_id (int): The ID of the image to deactivate

    Returns:
        bool: True if the image was found and deactivated, False otherwise
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            UPDATE images
            SET is_active = FALSE
            WHERE id = %s
            """,
            (image_id,),
        )
        # cursor.rowcount tells us how many rows were affected
        # If it's 0, the image wasn't found
        return cursor.rowcount > 0


def delete_image(image_id):
    """
    Permanently delete an image record from the database.

    WARNING: This only deletes the database record, not the file from R2.
    You should call delete_file_from_r2() separately if you want to remove
    the file from R2 as well.

    Args:
        image_id (int): The ID of the image to delete

    Returns:
        bool: True if the image was found and deleted, False otherwise
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM images
            WHERE id = %s
            """,
            (image_id,),
        )
        return cursor.rowcount > 0
