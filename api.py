from flask import Flask, request, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv
from dataclasses import dataclass
from config import Config
import time
from flask_autodoc.autodoc import Autodoc
from flask_cors import CORS

"""flask Movie App REST API with JWT

Author: Reza Yogaswara - https://me.rezayogaswara.com
Base URL: http://movieapi.rezayogaswara.com
"""

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "*"}})

db = SQLAlchemy(app)

load_dotenv('./.flaskenv')
auto = Autodoc(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/')
def index():
    return redirect(url_for('documentation'))


@app.route('/auth/signin')
@auto.doc()
def signin():
    """User authentication (user signin)"""
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.now(
        ) + datetime.timedelta(minutes=240)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/auth/signout', methods=['GET'])
@auto.doc()
@token_required
def signout(current_user):
	current_user = None
	token = None

	return jsonify({'token': token})


# Default this
# @token_required
# def get_all_users(current_user):
# GET User list
@app.route('/user', methods=['GET'])
@auto.doc()
def get_all_users():
    """GET User list"""
    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['fullname'] = user.fullname
        user_data['created_at'] = user.created_at
        output.append(user_data)

    return jsonify({'users': output})


@app.route('/user/<public_id>', methods=['GET'])
@auto.doc()
@token_required
def get_one_user(current_user, public_id):
    """GET User by public_id"""
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['username'] = user.username
    user_data['password'] = user.password
    user_data['fullname'] = user.fullname
    user_data['created_at'] = user.created_at

    return jsonify(user_data)


@app.route('/auth/me', methods=['GET'])
@auto.doc()
@token_required
def get_me(current_user):
    """GET User by token"""
    
    if not current_user:
        return jsonify({'message': 'Invalid request!'})

    user_data = {}
    user_data['id'] = current_user.id
    user_data['public_id'] = current_user.public_id
    user_data['username'] = current_user.username
    user_data['password'] = current_user.password
    user_data['fullname'] = current_user.fullname
    user_data['created_at'] = current_user.created_at

    return jsonify(user_data)


@app.route('/auth/signup', methods=['POST'])
@auto.doc()
def signup():
    """User signup"""
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password,
                    fullname=data['fullname'], created_at=getCurrentDate(True))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@app.route('/user/<public_id>', methods=['PUT'])
@auto.doc()
@token_required
def update_user(current_user, public_id):
    """PUT update User by public_id"""
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user.password = hashed_password
    user.fullname = data['fullname']
    db.session.commit()

    return jsonify({'message': 'The user has been updated!'})


@app.route('/user/<public_id>', methods=['DELETE'])
@auto.doc()
@token_required
def delete_user(current_user, public_id):
    """DELETE User by public_id"""
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})


@app.route('/movie', methods=['GET'])
@auto.doc()
@token_required
def get_all_movies(current_user):
    """GET Movie list"""
    movies = Movie.query.filter_by(user_id=current_user.id).all()

    output = []

    for movie in movies:
        movie_data = {}
        movie_data['id'] = movie.id
        movie_data['user_id'] = movie.user_id
        movie_data['genre'] = movie.genre
        movie_data['title'] = movie.title
        movie_data['directors'] = movie.directors
        movie_data['actors'] = movie.actors
        movie_data['year'] = movie.year
        movie_data['billboard'] = movie.billboard
        movie_data['created_at'] = movie.created_at
        output.append(movie_data)

    return jsonify({'movies': output})


@app.route('/movie/<movie_id>', methods=['GET'])
@auto.doc()
@token_required
def get_one_movie(current_user, movie_id):
    """GET Movie by movie_id"""
    movie = Movie.query.filter_by(id=movie_id, user_id=current_user.id).first()

    if not movie:
        return jsonify({'message': 'No movie found!'})

    movie_data = {}
    movie_data['id'] = movie.id
    movie_data['user_id'] = movie.user_id
    movie_data['genre'] = movie.genre
    movie_data['title'] = movie.title
    movie_data['directors'] = movie.directors
    movie_data['actors'] = movie.actors
    movie_data['year'] = movie.year
    movie_data['billboard'] = movie.billboard
    movie_data['created_at'] = movie.created_at

    return jsonify(movie_data)


@app.route('/movie', methods=['POST'])
@auto.doc()
@token_required
def create_movie(current_user):
    """POST new Movie"""
    data = request.get_json()

    new_movie = Movie(user_id=current_user.id, genre=data['genre'], title=data['title'], directors=data['directors'],
                      actors=data['actors'], year=data['year'], billboard=data['billboard'], created_at=getCurrentDate(True))
    db.session.add(new_movie)
    db.session.commit()

    return jsonify({'message': "Movie created!"})


@app.route('/movie/<movie_id>', methods=['PUT'])
@auto.doc()
@token_required
def update_movie(current_user, movie_id):
    """PUT update Movie by movie_id"""
    movie = Movie.query.filter_by(id=movie_id, user_id=current_user.id).first()

    if not movie:
        return jsonify({'message': 'No movie found!'})

    data = request.get_json()
    movie.genre = data['genre']
    movie.title = data['title']
    movie.directors = data['directors']
    movie.actors = data['actors']
    movie.year = data['year']
    movie.billboard = data['billboard']
    db.session.commit()

    return jsonify({'message': 'Movie item has been completed!'})


@app.route('/movie/<movie_id>', methods=['DELETE'])
@auto.doc()
@token_required
def delete_movie(current_user, movie_id):
    """DELETE Movie by movie_id"""
    movie = Movie.query.filter_by(id=movie_id, user_id=current_user.id).first()

    if not movie:
        return jsonify({'message': 'No movie found!'})

    db.session.delete(movie)
    db.session.commit()

    return jsonify({'message': 'Movie item deleted!'})


def getCurrentDate(withTime=False):
    month = ['Januari',
             'Februari',
             'Maret',
             'April',
             'Mei',
             'Juni',
             'Juli',
             'Agustus',
             'September',
             'Oktober',
             'November',
             'Desember'
             ]

    if (withTime):
        return '%s-%s-%s %s:%s:%s' % (time.strftime('%Y'), time.strftime('%m'), time.strftime('%d'), time.strftime('%H'), time.strftime('%M'), time.strftime('%S'))
    return '%s-%s-%s' % (time.strftime('%d'), month[int(time.strftime('%m')) - 1].upper(), now.year)


@dataclass
class User(db.Model):
    __tablename__ = 'tb_users'

    id: int
    public_id: str
    username: str
    password: str
    fullname: str
    created_at: str

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    fullname = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.String(24), nullable=False)
    movie = db.relationship('Movie', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<User id: {self.id} - {self.username}>'


@dataclass
class Movie(db.Model):
    __tablename__ = 'tb_movies'

    id: int
    user_id: int
    genre: str
    title: str
    directors: str
    actors: str
    year: str
    billboard: str
    created_at: str

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'tb_users.id'), nullable=False)
    genre = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    directors = db.Column(db.String(256), nullable=False)
    actors = db.Column(db.String(256), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    billboard = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.String(24))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Movie id: {self.id} - {self.title} - {self.genre} - {self.year}>'


@app.route('/documentation')
def documentation():
    return auto.html(title='Movie App REST API Reference',
                     author='Reza Yogaswara')
    # return Response(str(auto.generate()), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
