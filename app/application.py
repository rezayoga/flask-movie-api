
from forms import TaskForm
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from config import Config

load_dotenv('./.flaskenv')

db = SQLAlchemy()

def create_app(app_name="Flask Vue"):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from . import routes
    with app.app_context():
        db.create_all()

        return app
