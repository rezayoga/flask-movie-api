from distutils.log import debug
#from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, redirect, url_for
#from flask_sqlalchemy import SQLAlchemy

#from config import Config

#load_dotenv('./.flaskenv')

app = Flask(__name__)
#app.config.from_object(Config)

#db = SQLAlchemy(app)


@app.route('/')
def index():
    return "Hello Musa!"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
