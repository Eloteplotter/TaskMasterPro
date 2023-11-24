from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

app =Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db = SQL("sqlite:///block.db")

db.execute('CREATE TABLE users (id INTEGER, name TEXT NOT NULL, password TEXT NOT NULL) PRIMARY KEY(id)')

db.execute('CREATE TABLE blocks (id_block INTEGER, user_id INTEGER, name_block TEXT NOT NULL, star_date TIME(no se xd ), finish_date TIME(no se x2))')

@app.route("/")
def index():
    if not session.get("id"):
        return redirect("/login")
    notas = db.execute("select * from block where id_users = ?" ,session["id"])
    return render_template("index.html" , notas = notas)


@app.route("/", methods= ["GET", "POST"])
def log_ing():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    else:
        name == request.form.get("name")
        password = request.form.get("password")

        if not name or not password:
            pass

        rows = db.execule('SELECT name, password FROM users WHERE name = (?)', name)

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return "Invalid password or username"

        session("user_id") = rows[0]["id"]
        
        return redirect("/")



