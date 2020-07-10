import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bluefrog.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/destinations")
@login_required
def destinations():
    return render_template("destinations.html")

@app.route("/destination")
@login_required
def destination():
    return render_template("destination.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return render_template("login.html", warning = 0)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", warning = 1)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return render_template("login.html", warning = 2)
        elif not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", warning = 3)


        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Registration process:
        name = request.form.get("nickname")
        email = request.form.get("email")
        password = request.form.get("password")
        confPassword = request.form.get("confPassword")
        print(name, email, password, confPassword)

        # Check if name and email address are both provided
        if not name:
            return render_template("register.html", warning = 0)
        elif not email:
            return render_template("register.html", warning = 4)
        elif not password:
            return render_template("register.html", warning = 3)

        # Check if chosen passwords are identical
        elif password != confPassword:
            return render_template("register.html", warning = 1)

        # Check if the username is already taken
        rows = db.execute("SELECT * FROM users WHERE email = :email", email = email)
        if len(rows) > 0:
            return render_template("register.html", warning = 2)
        # If the username is not taken, hash the password, insert user into users table
        else:
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users (name, email, hash) VALUES (?,?,?)", name, email, hash)

        #session["user_id"] = rows[0]["id"]
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        return render_template("add.html", message = 0)
        #TODO
    else:
        return render_template("add.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
