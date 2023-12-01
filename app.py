from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_mail import Message, Mail
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from dotenv import load_dotenv
import os
import stripe

load_dotenv()

app =Flask(__name__,
            static_url_path='',
            static_folder='public')

stripe.api_key = 'sk_test_51OIaagFn9mbqMEffBXHysIy5wlS80JE1gv6gA0I1sqBeeYF4wgM1cyLPocJ1QHb3IUpi144vH7WXikDDujhaZBvp00PEppd3LJ'
STRIPE_PUBLIC_KEY = 'pk_test_51OIaagFn9mbqMEffZaiYD7IXCl0pPnnJSMTqlrTnPRq3E1B4MDE6SzkZKkxqsP2llY235EKYVKSlZOgdHK6A6oWB00g5wMLkkG'
STRIPE_SECRET_KEY = "sk_test_51OIaagFn9mbqMEffBXHysIy5wlS80JE1gv6gA0I1sqBeeYF4wgM1cyLPocJ1QHb3IUpi144vH7WXikDDujhaZBvp00PEppd3LJ"
STRIPE_WEBHOOK_SECRET = "whsec_28bf38ec3a12f91111a4a923d96543592c15bf74ec1a802a45253ddeda9c3646"

YOUR_DOMAIN2 = 'http://localhost:5000'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config['SECRET_KEY'] = 'super secret key'
app.config["SESSION_TYPE"] = "filesystem"

app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '3134450fcbf405'
app.config['MAIL_PASSWORD'] = 'a564b6ae708430'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

Session(app)
mail =Mail(app)


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

        error_name = "Try another username, please"
        error_password = "passwords don't match" 

        #confirma la contraseña
        if password != confirmation:
            return render_template("registro.html", errorP=error_password)
        
        row = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(row) != 0:
            return render_template("registro.html", errorN=error_name,)
        
        else:
            #se agrega el nuevo usario
            db.execute('INSERT INTO users(username, email, password) VALUES (?, ?, ?)', username, email, password)
            return redirect("/login")
    else:
         return render_template("registro.html")
        


@app.route("/login", methods=["GET", "POST"])
def log_ing():

    session.clear()
    
    error = "Invalid credentials"

    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
       

        if not username or not password:
            return render_template("login.html", error=error)
        

        rows = db.execute('SELECT * FROM users WHERE username = (?)', username)

        if len(rows) == 0:
            return render_template("login.html", error=error)

        if  rows[0]["password"] != request.form.get("password"):
            return render_template("login.html", error=error)
        
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


# Stripe
@app.route('/create-checkout-session', methods=["POST"])
def create_checkout_session():
    if request.method == "POST":
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                            "price_data": {
                                "currency": 'usd',
                                "product_data": {
                                    "name": 'Taskmaster',
                                },
                                "unit_amount": 5000
                            },
                            "quantity": 1,
                        },
                ],
                metadata={
                        "product_id": 2,
                        "user_id": 3,
                        "quantity": 1
                    },
                mode="payment",
                success_url=YOUR_DOMAIN2 + '/',
                cancel_url=YOUR_DOMAIN2 + '/',
            )
           
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, code=303)


@app.route("/webhooks/stripe/", methods=["POST"])
def webhooks():
    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)

    try:
        event = stripe.Webhook.construct_event(
            payload, received_sig, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        print("Error while decoding event!")
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError:
        print("Invalid signature!")
        return "Bad signature", 400

    print(
        "GG"
    )

    return "", 200