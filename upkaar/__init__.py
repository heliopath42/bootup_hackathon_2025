from flask import Flask, render_template, send_file
import os
from . import database

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db, close = database.get_database("upkaar")

    @app.route('/')
    def hello():
        return render_template("index.html")

    @app.route('/favicon.ico')
    def favicon():
        return send_file("static/favicon.ico")

    @app.route('/db')
    def db_():
        data = db["users"].find()
        return render_template("db.html", data = data)
        

    return app
