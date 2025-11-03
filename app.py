from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import resend
import mysql.connector
import MySQLdb
from werkzeug.security import check_password_hash
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)


cursor = db.cursor()

resend.api_key = os.getenv("RESEND_API_KEY")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        loginEmail = request.form.get('loginEmail')
        passwordEmail = request.form.get('loginPassword')

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM person WHERE email = %s", (loginEmail,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], passwordEmail):
            session['admin_logged_in'] = True
            session['admin_email'] = loginEmail
            return redirect(url_for('admin'))  # <-- redirect istället för render_template
        else:
            flash("Fel email eller lösenord!")

    return render_template('login.html')


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
