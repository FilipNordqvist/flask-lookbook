
from dotenv import load_dotenv
from flask import Flask, render_template
import os
from flask import request, redirect, url_for
import resend

app = Flask(__name__)
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/inspiration')
def clothes():
    return render_template("inspiration.html")

@app.route('/clothes/tshirts')
def tshirts():
    return render_template('tshirts.html')

@app.route('/clothes/hoodie')
def hoodie():
    return render_template('hoodie.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send', methods=['POST'])
def send_email():
    email = request.form.get('email')
    message = request.form.get('message')

    if not email or not message:
        return "Email and message required", 400

    try:
        r = resend.Emails.send({
            "from": "info@nordqvist.tech",
            "to": "info@nordqvist.tech",
            "reply_to": email,
            "subject": "New message from HNF webshop",
            "html": f"<p><b>From:</b> {email}</p><p>{message}</p>"
        })
        print("✅ Resend response:", r)
        return redirect(url_for('contact'))
    except Exception as e:
        import traceback
        print("❌ Error from Resend:", e)
        traceback.print_exc()
        return f"Failed to send email: {e}", 500
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
