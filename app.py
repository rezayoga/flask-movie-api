from distutils.log import debug
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"


if __name__ == '__main__':
    app.run(debug=True)