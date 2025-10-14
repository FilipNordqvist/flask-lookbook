
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_mail import Mail, Message
import os
from flask import request, redirect, url_for

app = Flask(__name__)
mail = Mail(app)

load_dotenv()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/clothes')
def clothes():
    return render_template("clothes.html")

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

    msg = Message(
        'New message from webshop',
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = message
    mail.send(msg)
    return redirect(url_for('contact'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
