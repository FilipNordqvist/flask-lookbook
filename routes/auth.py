"""
Authentication routes.

This module handles user authentication: login, registration, and logout.
Authentication is the process of verifying who a user is (like checking
a username and password).

Flask routes are functions that handle HTTP requests. When someone visits
a URL like /login, Flask calls the corresponding route function.

HTTP methods:
- GET: Used to retrieve data (like showing a page)
- POST: Used to submit data (like submitting a form)
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_user_by_email, create_user, user_exists
from utils import login_required

# Create a Blueprint for authentication routes
# Blueprints are Flask's way of organizing routes into groups
# The first argument is the blueprint name, used in url_for()
# The second argument is __name__, which tells Flask where to find templates
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    This route handles both displaying the login form (GET) and processing
    the login form submission (POST). This is a common pattern in Flask.
    
    When a user successfully logs in, we store their login status in the session.
    The session is like a temporary storage that persists across multiple requests
    from the same user. It's stored in a cookie on the user's browser.
    """
    # Check if this is a POST request (form submission)
    # request.method tells us which HTTP method was used
    if request.method == 'POST':
        # Get form data from the request
        # request.form is a dictionary-like object containing form data
        # .get() returns None if the key doesn't exist (safer than [] which raises KeyError)
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate the email - check if it exists and isn't just whitespace
        # .strip() removes leading and trailing whitespace
        # "not email or not email.strip()" checks if email is None, empty, or only whitespace
        if not email or not email.strip():
            # flash() stores a message that will be shown to the user on the next page
            # These messages are typically displayed at the top of the page
            flash("Please enter a valid email address.")
            # Return the login page again so they can try again
            return render_template('login.html')

        # Clean up the email by removing whitespace
        email = email.strip()

        # Use try/except to handle any database errors gracefully
        try:
            # Look up the user in the database by their email
            user = get_user_by_email(email)

            # Check if user exists AND password is correct
            # check_password_hash() compares a plain text password with a hashed password
            # We hash passwords so even if someone steals our database, they can't see
            # the actual passwords. Hashing is one-way - you can't reverse it.
            # user.get('password', '') gets the password from the user dict, or '' if not found
            if user and check_password_hash(user.get('password', ''), password):
                # Login successful! Store login status in the session
                # session is a dictionary-like object that persists across requests
                # It's stored in a cookie on the user's browser
                session['admin_logged_in'] = True
                session['admin_email'] = email  # Store email for later use
                
                # Show a success message
                flash("Login successful!")
                
                # Redirect to the admin page
                # redirect() sends an HTTP redirect response
                # url_for() generates the URL for a route by its function name
                # 'main.admin' means the 'admin' function in the 'main' blueprint
                return redirect(url_for('main.admin'))
            else:
                # Either user doesn't exist or password is wrong
                # Don't tell them which one - that would help attackers
                flash("Wrong email or password!")
        except Exception as e:
            # If something goes wrong (like database error), show a friendly message
            # We don't show the actual error to the user - that could reveal
            # sensitive information about our system
            flash("An error occurred during login. Please try again.")
            # In production, you would log the actual error here for debugging
            # but not show it to the user

    # If this is a GET request, or if login failed, show the login form
    # render_template() finds the template file and renders it to HTML
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required  # This decorator requires the user to be logged in
def register():
    """
    Handle user registration (admin only).
    
    This route is protected by @login_required, which means only logged-in
    users (admins) can access it. This prevents random people from creating accounts.
    
    The registration process:
    1. Validate the input (email, password, etc.)
    2. Check if email is already registered
    3. Hash the password (never store plain text passwords!)
    4. Save the user to the database
    """
    # Check if this is a form submission
    if request.method == 'POST':
        # Get and clean form data
        # The second argument to .get() is the default value if the key doesn't exist
        # .strip() removes whitespace from the beginning and end
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_repeat = request.form.get('password_repeat', '').strip()

        # Validate email - check if it's not empty
        if not email:
            flash("Please enter a valid email address.")
            return render_template('register.html')
        
        # Validate that both password fields are filled
        if not password or not password_repeat:
            flash("Please enter the password twice.")
            return render_template('register.html')
        
        # Check if passwords match
        # This is important - we ask users to type their password twice to make
        # sure they didn't make a typo
        if password != password_repeat:
            flash("Passwords do not match!")
            return render_template('register.html')
        
        # Check password length - enforce minimum security requirements
        # len() returns the length of a string
        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return render_template('register.html')

        # Use try/except to handle database errors
        try:
            # Check if this email is already registered
            # We don't want duplicate accounts with the same email
            if user_exists(email):
                flash("Email address is already registered.")
                return render_template('register.html')

            # Hash the password before storing it
            # generate_password_hash() creates a secure hash that can't be reversed
            # Even if someone steals our database, they can't see the actual passwords
            # This is a security best practice - NEVER store plain text passwords!
            hashed_password = generate_password_hash(password)
            
            # Create the user in the database
            create_user(email, hashed_password)

            # Show success message and redirect to login page
            flash("Registration successful! You can now log in.")
            return redirect(url_for('auth.login'))
        except Exception as e:
            # Handle any errors (like database connection issues)
            flash("An error occurred during registration. Please try again.")
            # In production, log the error for debugging

    # If this is a GET request, show the registration form
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """
    Handle user logout.
    
    Logging out clears the session, which removes the user's login status.
    After logout, they'll need to log in again to access protected pages.
    """
    # Clear all session data
    # This removes 'admin_logged_in' and any other session variables
    session.clear()
    
    # Show a confirmation message
    flash("You have been logged out successfully.")
    
    # Redirect to the home page
    return redirect(url_for('main.home'))
