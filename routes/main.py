"""Main application routes."""
from flask import Blueprint, render_template
from utils import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Home page."""
    return render_template('index.html')


@main_bp.route('/inspiration')
def inspiration():
    """Inspiration page."""
    return render_template("inspiration.html")


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@main_bp.route('/admin')
@login_required
def admin():
    """Admin dashboard."""
    return render_template('admin.html')

