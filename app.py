from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

app =Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


db = SQL("sqlite:///block.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods= ["GET", "POST"])
def login():
    return render_template("login.html")