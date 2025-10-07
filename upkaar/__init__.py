from flask import (
    Flask, render_template, send_file,
    request, flash, session, redirect, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
import os
from . import database


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    database.init_app(app)

    @app.route('/')
    def hello():
        return render_template("index.html")

    @app.route('/favicon.ico')
    def favicon():
        return send_file("static/favicon.ico")

    @app.route('/db')
    def _db():
        data = (database.get_db()["users"].find())
        return render_template("db.html", data=data)

    @app.route('/signup', methods=("GET", "POST"))
    def signup():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            try:
                assert username, "Username is required"
                assert password, "Username is required"
                users = database.get_db()["users"]
                users.insert_one({
                    "username": username,
                    "password_salt": generate_password_hash(password),
                    "requests_created": [],
                    "requests_ongoing": [],
                })
            except AssertionError as e:
                flash(e.args[0])
            else:
                return redirect(url_for('login'))
        else:
            return render_template("signup.html")

    @app.route('/login', methods=("GET", "POST"))
    def login():
        return render_template("login.html")

    return app
