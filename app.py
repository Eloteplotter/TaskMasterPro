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
app.config['SECRET_KEY'] = 'super secret key'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
            return "algo"
        
        row = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(row) != 0:
            return "eso significa que hay otro usuario con el mismo username"
        
        else:
            #se agrega el nuevo usario
            db.execute('INSERT INTO users(username, email, password) VALUES (?, ?, ?)', username, email, password)
            return redirect("/login")
    else:
         return render_template("registro.html")
        


@app.route("/login", methods=["GET", "POST"])
def log_ing():

    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
       

        if not username or not password:
            pass #por el momentoo, idea que ponga un mensaje en rojo que no coinciden las contra o algo asi

        rows = db.execute('SELECT * FROM users WHERE username = (?)', username)
        print(rows)

        if  check_password_hash(rows[0]["password"], request.form.get("password")):
            return "aqui un mensaje donde diga la contra o el username es erroneo"

        session["user_id"] = rows[0]["id"] 

        return redirect("/")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
 
    user_id = session.get("user_id")
    blocks = db.execute("SELECT * FROM block WHERE user_id = ?", user_id)

    return render_template("index.html" , blocks = blocks)



@app.route("/edit", methods=["POST"])
@login_required
def edit():
    
    title = request.form.get("editTitle")
    descripcion = request.form.get("editDescripcion")
    tiempo_inicio = request.form.get("editTiempo_inicio")
    tiempo_final = request.form.get("editTiempo_final")
    id = request.form.get("id")
    
    print(title, descripcion, tiempo_inicio, tiempo_final, id)

    db.execute("UPDATE block SET titulo = ?, descripcion = ?, tiempo_inicio = ?, tiempo_final = ? WHERE id = ?", 
                title, descripcion, tiempo_inicio, tiempo_final, id)
    
    return redirect("/")



@app.route("/add", methods=["POST"])
@login_required
def add():
    user_id = session.get("user_id")
    title = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    tiempo_inicio = request.form.get("tiempo_inicio")
    tiempo_final = request.form.get("tiempo_final")

    db.execute('INSERT INTO block (titulo, descripcion, user_id, tiempo_inicio, tiempo_final) VALUES (?, ?, ?, ?, ?)',
               title, descripcion, user_id, tiempo_inicio, tiempo_final,)
   
    return redirect("/")
    


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    

    id_nota = request.form.get("id_nota")
    db.execute('DELETE FROM block WHERE id = ?', id_nota)

    return redirect("/")

@app.route("/logout")
@login_required
def logout():

     session.clear()
     return redirect("/")
