from flask import Flask

app = Flask(__name__)

@app.route("/")
def about():
    return "<p>My first flask app!</p>"