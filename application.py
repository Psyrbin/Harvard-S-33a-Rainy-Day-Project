import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import json
import datetime
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/add_user", methods=['POST'])
def add_user():
    name = request.form.get("name")
    password = request.form.get("password")
    password_conf = request.form.get("password_conf")

    if password != password_conf:
        return render_template("error.html", message="Passwords don't match")
    if db.execute('SELECT * FROM users WHERE name = :name', {'name': name}).rowcount != 0:
        return render_template('error.html', message='User with this name already exists. Please try another.')

    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name, "password": password})
    db.commit()
    return render_template("add_user.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get("password")

        if db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).rowcount == 0:
            return render_template("error.html", message="Username is incorrect")

        user = db.execute("SELECT * FROM users WHERE name = :name AND password = :password", {"name": name, "password": password})
        if user.rowcount == 0:
            return render_template("error.html", message="Wrong password")
        db.commit()
    
        session['user_id'] = user.fetchone().id

    return render_template("search.html")

@app.route("/search_results", methods=['POST'])
def search_results():
    zipcode = request.form.get('zip')
    city = request.form.get('city')
    zipcode = '%' + zipcode + '%'
    city = '%' + city.upper() + '%'

    cities = db.execute('SELECT zip, city FROM zips WHERE zip LIKE :zip AND city LIKE :city', {'zip':zipcode, 'city':city}).fetchall()
    db.commit()
    return render_template("search_results.html", cities=cities)

@app.route("/<string:zipcode>", methods=['GET', 'POST'])
def city(zipcode):
    location = db.execute('SELECT * FROM zips WHERE zip = :zip', {'zip': zipcode})
    if location.rowcount == 0:
        return render_template('error.html', message='Location not found')

    if request.method == 'POST':
        if db.execute('SELECT * FROM checkins WHERE user_id = :id', {'id': session['user_id']}).rowcount != 0:
            return render_template('error.html', message='You already checked in for this location')
        user = db.execute('SELECT * FROM users where id = :id', {'id': session['user_id']}).fetchone()
        comment = request.form.get('comment')
        db.execute('INSERT INTO checkins (user_id, location_id, comment) VALUES (:uid, :lid, :comment)',{'uid': user.id, 'lid': zipcode, 'comment': comment})

    location = location.fetchone()
    checkins = db.execute('SELECT name, comment FROM users, checkins WHERE users.id = user_id AND location_id = :zip', {'zip': zipcode})
    checkin_num = checkins.rowcount
    comments = checkins.fetchall()

    logged_in = True
    if session.get('user_id') == None:
        logged_in = False


    weather = requests.get(f'https://api.darksky.net/forecast/41028ca0915330153e43860a3a0d9423/{location.latitude},{location.longitude}').json()['currently']
    weather['time'] = datetime.datetime.fromtimestamp(int(weather['time']))
    weather['humidity'] = round(weather['humidity'] * 100)

    commented = False
    if logged_in and db.execute('SELECT * FROM checkins WHERE user_id = :uid', {'uid': session['user_id']}).rowcount != 0:
        commented=True
    db.commit()

    return render_template("location.html", location=location, comments=comments, checkin_num=checkin_num, weather=weather, logged_in=logged_in, commented=commented)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

@app.route("/api/<string:zipcode>")
def api(zipcode):
    location = db.execute('SELECT * FROM zips WHERE zip = :zip', {'zip': zipcode})
    if location.rowcount == 0:
        return jsonify({"error": "Location not found"}), 404

    location = location.fetchone()
    checkin_num = db.execute('SELECT * FROM checkins WHERE location_id = :zip', {'zip': zipcode}).rowcount
    db.commit()
    return jsonify({
            "place_name": location.city,
            "state": location.state,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "zip": location.zip,
            "population": location.population,
            "check_ins": checkin_num
    })