"""
Main application routes.

This module contains the main public-facing routes for the application:
- Home page (/)
- Inspiration page (/inspiration)
- About page (/about)
- Admin dashboard (/admin) - requires login
- File upload (/admin/upload) - requires login
- Image management (/admin/images) - requires login
- Delete image (/admin/images/<id>/delete) - requires login

These routes handle both displaying pages and processing file uploads.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import login_required
from database import (
    create_images_table,
    add_image,
    get_all_active_images,
    get_image_by_id,
    delete_image,
    get_db_cursor,
)
from .media_handler import upload_file_to_r2, delete_file_from_r2

# Create a Blueprint for main application routes
# Blueprints help organize routes - think of them as "modules" for your routes
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
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
    return render_template("index.html")


@main_bp.route("/inspiration")
def inspiration():
    """
    Inspiration page route.

    This displays a gallery of images uploaded to Cloudflare R2.
    Images are fetched from the database and displayed in a responsive grid.
    """
    # Ensure the images table exists (idempotent - safe to call multiple times)
    create_images_table()

    # Get all active images from the database
    # These are images that have been uploaded and are marked as active
    images = get_all_active_images()

    # Pass the images to the template so it can display them
    return render_template("inspiration.html", images=images)


@main_bp.route("/about")
def about():
    """
    About page route.

    This typically displays information about the company or website.
    """
    # Render the about template
    return render_template("about.html")


@main_bp.route("/admin")
@login_required  # This decorator protects the route - requires login
def admin():
    """
    Admin dashboard route.

    This page is protected by @login_required, which means:
    1. If the user is not logged in, they'll be redirected to the login page
    2. If they are logged in, they'll see the admin dashboard

    The @login_required decorator runs BEFORE this function, so by the time
    we get here, we know the user is authenticated.

    The admin page displays:
    - A form to upload new images to Cloudflare R2
    - A list of all uploaded images with options to delete them
    """
    # Ensure the images table exists
    create_images_table()

    # Get all images (including inactive ones) for the admin view
    # Admins should see all images, not just active ones
    with get_db_cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT id, filename, r2_key, url, alt_text, created_at, is_active
            FROM images
            ORDER BY created_at DESC
            """
        )
        all_images = cursor.fetchall()

    # Render the admin template with the list of images
    return render_template("admin.html", images=all_images)


@main_bp.route("/admin/upload", methods=["POST"])
@login_required
def upload_image():
    """
    Handle file upload to Cloudflare R2.

    This route processes file uploads from the admin page. It:
    1. Validates the file was provided
    2. Uploads the file to Cloudflare R2
    3. Stores metadata in the database
    4. Redirects back to admin page with success/error message

    The route only accepts POST requests (file uploads must use POST).
    """
    # Check if a file was provided in the request
    if "file" not in request.files:
        flash("No file provided", "error")
        return redirect(url_for("main.admin"))

    file = request.files["file"]

    # Check if file was actually selected (filename is not empty)
    if file.filename == "":
        flash("No file selected", "error")
        return redirect(url_for("main.admin"))

    # Get optional alt text from the form
    alt_text = request.form.get("alt_text", "").strip()
    # If alt_text is empty, set it to None (database allows NULL)
    if not alt_text:
        alt_text = None

    # Ensure the images table exists
    create_images_table()

    # Upload the file to Cloudflare R2
    # upload_file_to_r2 returns a dict with 'success', 'url', 'filename', etc.
    result = upload_file_to_r2(file, folder="inspiration")

    if not result["success"]:
        # If upload failed, show error message and redirect
        flash(f"Upload failed: {result.get('error', 'Unknown error')}", "error")
        return redirect(url_for("main.admin"))

    # If upload succeeded, store metadata in the database
    try:
        add_image(
            filename=result["filename"],
            r2_key=result["r2_key"],
            url=result["url"],
            alt_text=alt_text,
        )
        flash("Image uploaded successfully!", "success")
    except Exception as e:
        # If database insert failed, we should ideally delete from R2 too
        # But for now, just log the error and show a message
        # The file is in R2 but not in the database, which is inconsistent
        flash(f"Upload succeeded but failed to save metadata: {str(e)}", "error")

    return redirect(url_for("main.admin"))


@main_bp.route("/admin/images/<int:image_id>/delete", methods=["POST"])
@login_required
def delete_image_route(image_id):
    """
    Delete an image (both from database and R2).

    This route handles image deletion. It:
    1. Gets the image record from the database
    2. Deletes the file from Cloudflare R2
    3. Deletes the record from the database
    4. Redirects back to admin page

    Args:
        image_id (int): The ID of the image to delete
    """
    # Get the image record to find the R2 key
    image = get_image_by_id(image_id)

    if not image:
        flash("Image not found", "error")
        return redirect(url_for("main.admin"))

    # Try to delete from R2 first
    # Even if this fails, we'll still delete from database
    # (the file might already be gone, or R2 might be temporarily unavailable)
    delete_result = delete_file_from_r2(image["r2_key"])
    if not delete_result["success"]:
        # Log the error but continue with database deletion
        flash(
            f"Warning: Could not delete from R2: {delete_result.get('error', 'Unknown error')}",
            "warning",
        )

    # Delete from database
    if delete_image(image_id):
        flash("Image deleted successfully", "success")
    else:
        flash("Failed to delete image from database", "error")

    return redirect(url_for("main.admin"))
