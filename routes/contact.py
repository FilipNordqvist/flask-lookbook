"""
Contact form routes.

This module handles the contact form - allowing visitors to send messages
to the website owner via email.

Security note: We use HTML escaping to prevent XSS (Cross-Site Scripting) attacks.
XSS attacks happen when malicious code is injected into web pages. By escaping
user input, we convert dangerous characters (like < and >) into safe HTML entities
(like &lt; and &gt;), preventing the browser from executing any malicious code.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import resend
from config import Config
from markupsafe import escape, Markup

# Create a Blueprint for contact-related routes
contact_bp = Blueprint('contact', __name__)

# NOTE: We do NOT set resend.api_key at module level here.
# Setting it at module import time would cause issues because:
# 1. In tests, environment variables might not be set when the module is imported
# 2. Config.RESEND_API_KEY might be None at import time
# 3. The API key should be set lazily when actually needed (in the send_email route)
# We set resend.api_key inside the send_email() function right before using it


@contact_bp.route('/contact')
def contact():
    """
    Contact page route.
    
    This displays the contact form where users can enter their information
    and send a message.
    """
    # Render the contact form template
    return render_template('contact.html')


@contact_bp.route('/send', methods=['POST'])
def send_email():
    """
    Handle contact form submission.
    
    This route processes the contact form when it's submitted. It:
    1. Validates the input (email, message, etc.)
    2. Escapes user input to prevent XSS attacks
    3. Sends an email using the Resend service
    4. Shows a success or error message
    
    Security: We escape all user input before putting it in HTML to prevent
    XSS (Cross-Site Scripting) attacks. This converts dangerous characters
    like <script> into safe text that won't execute.
    """
    # Get form data and clean it up
    # .strip() removes whitespace from the beginning and end
    # The second argument to .get() is the default value if the field is missing
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    phone = request.form.get('phone', '').strip()
    name = request.form.get('name', '').strip()

    # Validate required fields
    # Email and message are required - check if they're not empty
    if not email or not message:
        flash("Email and message are required.")
        # Redirect back to the contact page so they can try again
        return redirect(url_for('contact.contact'))

    # Basic email validation
    # Check if email contains @ and has a domain (something after the @)
    # This is a simple check - in production, you might want more robust validation
    # email.split('@') splits the email at the @ symbol
    # [-1] gets the last part (the domain part)
    # We check if there's a dot in the domain (like .com, .org, etc.)
    if '@' not in email or '.' not in email.split('@')[-1]:
        flash("Please enter a valid email address.")
        return redirect(url_for('contact.contact'))

    # Use try/except to handle errors gracefully
    try:
        # CRITICAL SECURITY STEP: Escape all user input!
        # escape() converts dangerous HTML characters into safe text
        # For example: <script> becomes &lt;script&gt;
        # This prevents XSS (Cross-Site Scripting) attacks where malicious
        # code could be injected into the email and executed
        safe_email = escape(email)
        safe_phone = escape(phone) if phone else "Not provided"
        safe_name = escape(name) if name else "Not provided"
        safe_message = escape(message)

        # Convert newlines in the message to HTML line breaks
        # chr(10) is the newline character (\n)
        # We want to replace newlines with <br> tags so they display correctly in HTML
        # However, MarkupSafe's escape() function returns a Markup object
        # When you call .replace() on a Markup object, it escapes the replacement string too
        # So we use Markup('<br>') to tell it that <br> is safe HTML that shouldn't be escaped
        safe_message_with_breaks = safe_message.replace(chr(10), Markup('<br>'))
        
        # Create the HTML content for the email
        # We use an f-string (f"...") to insert variables into the string
        # The {variable} syntax inserts the variable value
        html_content = f"""
        <p><b>From:</b> {safe_name} ({safe_email})</p>
        <p><b>Phone:</b> {safe_phone}</p>
        <p><b>Message:</b></p>
        <p>{safe_message_with_breaks}</p>
        """

        # Set the Resend API key right before using it
        # We do this here (not at module level) because:
        # 1. Environment variables might not be set at import time (especially in tests)
        # 2. This ensures we always have the latest value from Config
        # 3. Lazy initialization prevents issues with test discovery
        resend.api_key = Config.RESEND_API_KEY

        # Send the email using the Resend service
        # resend.Emails.send() is the API call to send an email
        resend.Emails.send({
            "from": Config.EMAIL_FROM,      # Who the email is from
            "to": Config.EMAIL_TO,          # Who receives the email
            "reply_to": email,              # Where replies should go (the person who filled the form)
            "subject": "New message from HNF webshop",  # Email subject line
            "html": html_content            # The email body in HTML format
        })
        
        # Show success message
        flash("Thank you! Your message has been sent successfully.")
        # Redirect back to the contact page
        return redirect(url_for('contact.contact'))
        
    except Exception as e:
        # If something goes wrong (like email service is down), handle it gracefully
        # We don't show the actual error to the user - that could reveal
        # sensitive information or confuse them
        flash("Sorry, an error occurred while sending your message. Please try again later.")
        # In production, you would log the actual error (e) here for debugging
        # but not show it to the user
        return redirect(url_for('contact.contact'))
