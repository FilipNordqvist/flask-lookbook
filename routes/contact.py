"""Contact form routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import resend
from config import Config
from markupsafe import escape, Markup

contact_bp = Blueprint('contact', __name__)

# Initialize resend
resend.api_key = Config.RESEND_API_KEY


@contact_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')


@contact_bp.route('/send', methods=['POST'])
def send_email():
    """Handle contact form submission."""
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    phone = request.form.get('phone', '').strip()
    name = request.form.get('name', '').strip()

    if not email or not message:
        flash("Email and message are required.")
        return redirect(url_for('contact.contact'))

    # Validate email format (basic check)
    if '@' not in email or '.' not in email.split('@')[-1]:
        flash("Please enter a valid email address.")
        return redirect(url_for('contact.contact'))

    try:
        # Escape user input to prevent HTML injection
        safe_email = escape(email)
        safe_phone = escape(phone) if phone else "Not provided"
        safe_name = escape(name) if name else "Not provided"
        safe_message = escape(message)

        # Create HTML email with escaped content
        # Use Markup('<br>') to prevent escaping of the replacement string
        safe_message_with_breaks = safe_message.replace(chr(10), Markup('<br>'))
        
        html_content = f"""
        <p><b>From:</b> {safe_name} ({safe_email})</p>
        <p><b>Phone:</b> {safe_phone}</p>
        <p><b>Message:</b></p>
        <p>{safe_message_with_breaks}</p>
        """

        resend.Emails.send({
            "from": Config.EMAIL_FROM,
            "to": Config.EMAIL_TO,
            "reply_to": email,
            "subject": "New message from HNF webshop",
            "html": html_content
        })
        
        flash("Thank you! Your message has been sent successfully.")
        return redirect(url_for('contact.contact'))
    except Exception as e:
        # Log error in production, show user-friendly message
        flash("Sorry, an error occurred while sending your message. Please try again later.")
        return redirect(url_for('contact.contact'))

