import re

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


# Import flask_cors
from flask_cors import CORS

app = Flask(__name__)

# Initialize CORS with default options (all origins allowed)
CORS(app)

# Configurations
app.config.from_object('config.Config')

# Extensions
from extensions import db, jwt

db.init_app(app)
jwt.init_app(app)

# Models
from models import User, Tweet

@app.before_first_request
def create_tables():
    """
    Create database tables before the first request.
    """
    db.create_all()

def is_valid_email(email):
    """
    Check if the email follows a valid pattern.
    """
    if not email:
        return False
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request Body:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    
    Returns:
    {
        "message": "User created successfully"
    }
    """
    data = request.get_json()
    if not data or not all(key in data for key in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing data. Required fields: username, email, password'}), 400

    username = data['username']
    email = data['email']
    password = data['password']

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Log in an existing user and generate access token.
    
    Request Body:
    {
        "email": "string",
        "password": "string"
    }
    
    Returns:
    {
        "access_token": "string"
    }
    """
    data = request.get_json()
    if not data or not all(key in data for key in ('email', 'password')):
        return jsonify({'message': 'Missing data. Required fields: email, password'}), 400

    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/tweets', methods=['POST'])
@jwt_required()
def post_tweet():
    """
    Post a new tweet for the logged-in user.
    
    Request Body:
    {
        "content": "string"
    }
    
    Returns:
    {
        "message": "Tweet posted successfully"
    }
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'message': 'Missing data. Required field: content'}), 400

    content = data['content']

    new_tweet = Tweet(content=content, user_id=user_id)
    db.session.add(new_tweet)
    db.session.commit()

    return jsonify({'message': 'Tweet posted successfully'}), 201

@app.route('/tweets', methods=['GET'])
def get_tweets():
    """
    Get all tweets.
    
    Returns:
    [
        {
            "id": 1,
            "content": "string",
            "date_posted": "YYYY-MM-DD HH:MM:SS",
            "username": "string"
        },
        ...
    ]
    """
    tweets = Tweet.query.all()
    usernames = {user.id: user.username for user in User.query.all()}
    for tweet in tweets:
        tweet.username = usernames[tweet.user_id]
    tweets_list = [{'id': tweet.id, 'content': tweet.content, 'date_posted': tweet.date_posted, 'username': tweet.username} for tweet in tweets]
    return jsonify(tweets_list), 200

if __name__ == '__main__':
    app.run(debug=True)
