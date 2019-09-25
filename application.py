import os
import requests

from flask import Flask, session, render_template, url_for, redirect, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bootstrap import Bootstrap
from flask_scss import Scss
from flask_nav.elements import Navbar, View
from flask_nav import Nav
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "s2nASV5kfWKOVxbPruzJkg", "isbns": "9781632168146"})

nav = Nav()


@nav.navigation()
def mynavbar():
    return Navbar(
        '',
        View('Home', 'index'),
        View('Profile', 'profile'),
        View('Log In', 'login'),
        View('Sign Up', 'signup'),
        View('Log Out', 'logout')
    )

app = Flask(__name__)
Bootstrap(app)
Scss(app, static_dir='static', asset_dir='assets')
nav.init_app(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "secretkey"
Session(app)

# Enable this flag only in development since it can have performance and security implications
app.config['DEBUG'] = True

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

login_manager = LoginManager()
login_manager.init_app(app)

#from .models import User

#@login_manager.user_loader
#def load_user(user_id):
#    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


@app.route("/")
def index():
    books_basic = db.execute("SELECT isbn, title, author, year FROM books")
    books = res.json()["books"]
    return render_template("index.html", books=books, books_basic=books_basic)


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/login")
def login():
    return render_template("login.html")


#@app.route("/login", methods=['POST'])
#def login_post():


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup", methods=['POST'])
def signup_post():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user:
        flash("Email address already exists")
        return redirect(url_for("app.login"))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method="sha256"))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("app.login"))


@app.route("/logout")
def logout():
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)
