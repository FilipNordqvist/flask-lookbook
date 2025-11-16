"""Authentication routes."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_user_by_email, create_user, user_exists
from utils import login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not email.strip():
            flash("Please enter a valid email address.")
            return render_template('login.html')

        email = email.strip()

        try:
            user = get_user_by_email(email)

            if user and check_password_hash(user.get('password', ''), password):
                session['admin_logged_in'] = True
                session['admin_email'] = email
                flash("Login successful!")
                return redirect(url_for('main.admin'))
            else:
                flash("Wrong email or password!")
        except Exception as e:
            flash("An error occurred during login. Please try again.")
            # In production, log the error instead of exposing it

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Handle user registration (admin only)."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_repeat = request.form.get('password_repeat', '').strip()

        if not email:
            flash("Please enter a valid email address.")
            return render_template('register.html')
        
        if not password or not password_repeat:
            flash("Please enter the password twice.")
            return render_template('register.html')
        
        if password != password_repeat:
            flash("Passwords do not match!")
            return render_template('register.html')
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return render_template('register.html')

        try:
            if user_exists(email):
                flash("Email address is already registered.")
                return render_template('register.html')

            hashed_password = generate_password_hash(password)
            create_user(email, hashed_password)

            flash("Registration successful! You can now log in.")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("An error occurred during registration. Please try again.")
            # In production, log the error instead of exposing it

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for('main.home'))

