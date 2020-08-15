import os

#from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required, lookup, usd

# For image upload define folders etc.
UPLOAD_FOLDER = '/Users/laurent/programming/finalproject/final/static/images/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def upload_file(iata, place):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = UPLOAD_FOLDER + iata + '/' + place
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path, filename))


# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
#db = SQL("sqlite:///bluefrog.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mybluefrog")
def mybluefrog():
    user_id = session["user_id"]
    #print(user_id)
    myPlaces = db.execute("SELECT destination, title, description, name FROM places JOIN authors ON places.id = authors.place_id JOIN destinations ON destinations.id = places.dest_id JOIN users ON users.id = authors.user_id WHERE authors.user_id = :user_id ORDER BY destination, title", user_id = user_id)
    print(myPlaces)
    return render_template("mybluefrog.html", myPlaces = myPlaces)


@app.route("/start/<message>")
@login_required
def start(message):
    message = int(message)
    return render_template("start.html", message = message)


@app.route("/destinations")
@login_required
def destinations():
    # Get all the destinations from the database
    destinations = db.execute("SELECT * FROM destinations")
    # Create an empty destination dictionary
    dest_list = dict()
    for destination in destinations:
        dest_list.update({destination["destination"]:destination["iata"]})
    return render_template("destinations.html", dest_list = dest_list)

@app.route("/destination/<iata>")
@login_required
def destination(iata):
    destination = db.execute("SELECT * FROM destinations WHERE iata = :iata", iata = iata)
    dest_id = destination[0]["id"]
    place_list = db.execute("SELECT id, title, url, description FROM places WHERE dest_id = :dest_id", dest_id = dest_id)
    #print(place_list)
    return render_template("destination.html", place_list = place_list, iata = iata)

@app.route("/place/<int:place_id>")
@login_required
def place(place_id):
    place = db.execute("SELECT * FROM places WHERE id = :place_id", place_id = place_id)
    dest_id = int(place[0]["dest_id"])
    iata = db.execute("SELECT iata FROM destinations WHERE id = :dest_id", dest_id = dest_id)
    iata = iata[0]["iata"]
    image_path = "/Users/laurent/programming/finalproject/final/static/images/" + iata + '/' + str(place_id)

    if os.path.exists(image_path):
        for image in os.listdir(image_path):
            path = iata + '/' + str(place_id) + '/' + image

            image_path = path
    else:
        image_path = None

    return render_template("place.html", place = place, iata = iata, image_path = image_path)


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
        return redirect(url_for('start', message=0))

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

        # Get all the parameters from the add form
        title = request.form.get("title")
        destination = request.form.get("destination")
        public = request.form.get("public")
        url = request.form.get("url")
        description = request.form.get("description")
        author = session["user_id"]
        categories = [request.form.get("category1"), request.form.get("category2")]

        # Split the destination into IATA code and plain text destination
        destination_list = destination.split(" - ")
        iata = destination_list[0].upper()
        destination = destination_list[1]

        # Insert values into the database:
        # Check if destination is already in the database
        rows = db.execute("SELECT * FROM destinations WHERE iata = :iata", iata = iata)
        # If not in the database:
        if len(rows) == 0:
            # Add the destination to the database (into the destinations table)
            db.execute("INSERT INTO destinations (iata, destination) VALUES (?,?)", iata, destination)

        # Query the destinations table for the selected destination
        dest_id = db.execute("SELECT id FROM destinations WHERE iata = :iata", iata = iata)
        dest_id = dest_id[0]["id"]
        # Add the place
        db.execute("INSERT INTO places (title, dest_id, url, public, description, timestamp) VALUES(?,?,?,?,?,CURRENT_TIMESTAMP)", title, dest_id, url, public, description)
        # Add the author
        place_id = db.execute("SELECT MAX(id) FROM places")
        place_id = place_id[0]["MAX(id)"]
        db.execute("INSERT INTO authors (user_id, place_id) VALUES (?,?)", author, place_id)
        # Add the categories
        for category in categories:
            db.execute("INSERT INTO categories (place_id, category) VALUES (?,?)", place_id, category)

        # Add the image if any
        place = str(place_id)
        upload_file(iata, place)

        return redirect(url_for('start', message=1))

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
