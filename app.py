#import os
#from dotenv import load_dotenv
from flask import Flask, render_template
#from flask_mail import Mail, Message

app = Flask(__name__)

#load_dotenv()

""" app.secret_key = os.getenv("SECRET_KEY")

print("Hemlig nyckel:", app.secret_key)

app.secret_key = os.getenv("SECRET_KEY")

app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app) """

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
