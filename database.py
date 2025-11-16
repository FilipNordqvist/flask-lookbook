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
import mysql.connector
from contextlib import contextmanager
from config import Config


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
        Exception: Any exception that occurs during database operations
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
        
    except Exception:
        # If any error occurred, we need to rollback the transaction
        # This undoes any changes that were made, keeping the database consistent
        if conn:
            try:
                # Try to rollback the transaction
                conn.rollback()
            except Exception:
                # If rollback itself fails, we catch that error but don't let it
                # mask the original error. This is important - we want to know about
                # the original problem (like a failed INSERT), not just that rollback failed.
                # The "pass" statement means "do nothing" - we're intentionally ignoring
                # the rollback error so the original error can be raised below.
                pass
        
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
            (email, hashed_password)
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
