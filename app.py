from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from dotenv import load_dotenv

load_dotenv()

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

@app.route("/registro", methods=["GET", "POST"])
def registro():
    
    if request.method == "POST":
         username = request.form.get("username")
         email = request.form.get("email")
         password = request.form.get("password")
         confirmation = request.form.get("confirmation")
         #confirma la contrase;a 
         if password != confirmation:
             return "hola"
        
         #se agrega el nuevo usario
         db.execute('INSERT INTO users username, email, password VALUES (?, ?, ?)', username, email, generate_password_hash(password))
         return redirect ("login.html")
    else:
         return redirect ("registro.html")
        


@app.route("/", methods=["GET", "POST"])
def log_ing():

     session.clear()

     if request.method == "GET":
         return render_template("login.html")

     else:
         name = request.form.get("name")
         password = request.form.get("password")
         user_id = session["user_id"]

         if not name or not password:
             pass #por el momentoo, idea que ponga un mensaje en rojo que no coinciden las contra, supongo que que js 

         session["user_id"] = rows[0]["id"] 

         rows = db.execute('SELECT name, password FROM users WHERE name = (?)', name)

         if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
             return #aqui un mensaje donde diga la contra o el username es erroneo 

     return redirect("/")


@app.route("/index", methods=["GET", "POST"])
def index():
    if not session.get("id"):
        return redirect("/login")
    
    blocks = db.execute("SElECT * FROM block WHERE id_users = ? GROUP BY titulo" ,session["id"])
    return render_template("index.html" , blocks = blocks)

@app.route("/edit", methods=["POST"])
def edit():
   
     title = request.form.get("titulo")
     nota = request.form.get("nota")
     start_time = request.form.get("star_time")
     finish_time = request.form.get("finish_time")

     db.execute("INSERT INTO block(titulo, descripcion, user_id, tiempo_inicio, tiempo_final) VALUES(?, ?, ?, ?, ?)", 
                title, nota, session["id"], start_time, finish_time)
    
     return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
   
     id = request.form.get("id_nota")
     db.execute('DELETE * FROM block WHERE id = ?', id)

@app.route("/logout")
def logout():

     session.clear()
     return redirect("/")



@app.route("/login", methods= ["GET", "POST"])
def login():
    return render_template("login.html")