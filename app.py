import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
import resend, mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "port": int(os.getenv("MYSQLPORT", 3306)),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),
    "database": os.getenv("MYSQLDATABASE", "test")
}

db = mysql.connector.connect(**DB_CONFIG)

cursor = db.cursor()

resend.api_key = os.getenv("RESEND_API_KEY")


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not email.strip():
            flash("Please enter a valid email address.")
            return render_template('login.html')

        email = email.strip()

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user.get('password', ''), password):
            session['admin_logged_in'] = True
            session['admin_email'] = email
            return render_template('admin.html')

        else:
            flash("Wrong email or password!")

    return render_template('login.html')

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET','POST'])
@login_required
def register():
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
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            flash("Email address is already registered.")
            cursor.close()
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO person (email, password) VALUES (%s, %s)", (email, hashed_password))
        db.commit()
        cursor.close()

        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/inspiration')
def clothes():
    return render_template("inspiration.html")

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
    phone = request.form.get('phone')

    if not email or not message:
        return "Email and message required", 400

    try:
        r = resend.Emails.send({
            "from": "info@nordqvist.tech",
            "to": "info@nordqvist.tech",
            "reply_to": email,
            "subject": "New message from HNF webshop",
            "html": f"<p><b>From:</b> {email}</p><p><b>Tel:</b> {phone}</p><p><b>Meddalande:</b><br> {message}</p>"
        })
        return redirect(url_for('contact'))
    except Exception as e:
        return f"An error occurred: {e}", 500
       
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
