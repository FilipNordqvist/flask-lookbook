"""
Main application routes.

This module contains the main public-facing routes for the application:
- Home page (/)
- Inspiration page (/inspiration)
- About page (/about)
- Admin dashboard (/admin) - requires login

These are simpler routes that mostly just display pages. They don't do
much processing - they just render templates.
"""
from flask import Blueprint, render_template
from utils import login_required

# Create a Blueprint for main application routes
# Blueprints help organize routes - think of them as "modules" for your routes
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """
    Home page route.
    
    This is the root URL of the website (just /). When someone visits
    the base URL of your site, this function runs.
    
    Returns:
        str: Rendered HTML from the index.html template
    """
    # render_template() finds the template file (in the templates/ folder)
    # and renders it to HTML, which is sent to the user's browser
    return render_template('index.html')


@main_bp.route('/inspiration')
def inspiration():
    """
    Inspiration page route.
    
    This displays a gallery or collection of inspirational content.
    """
    # Render the inspiration template
    return render_template("inspiration.html")


@main_bp.route('/about')
def about():
    """
    About page route.
    
    This typically displays information about the company or website.
    """
    # Render the about template
    return render_template('about.html')


@main_bp.route('/admin')
@login_required  # This decorator protects the route - requires login
def admin():
    """
    Admin dashboard route.
    
    This page is protected by @login_required, which means:
    1. If the user is not logged in, they'll be redirected to the login page
    2. If they are logged in, they'll see the admin dashboard
    
    The @login_required decorator runs BEFORE this function, so by the time
    we get here, we know the user is authenticated.
    """
    # Render the admin template
    # Since @login_required already checked authentication, we can safely
    # show admin content here
    return render_template('admin.html')
