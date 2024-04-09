from flask import Flask, jsonify, request
import jwt
from .config import Config
from .repositories.wordle_repository import WordleRepository
from .repositories.user_repository import UserRepository
from .services.wordle_service import WordleService
from .services.user_service import UserService
from .routes.wordle_routes import create_routes
from .routes.user_routes import create_user_routes
import boto3
from pathlib import Path
from flask_cors import CORS
from functools import wraps
from .utils.middleware import validate_and_decode_jwt

def create_app(config_class=Config):
    # Create a Flask application
    app = Flask(__name__)

    # Enable CORS
    CORS(app, resources={r'/*': {'origins': ['*']}})
    
    # Apply configuration settings from your config.py or environment
    app.config.from_object(config_class)


    # Initialize database connection or other services
    dynamodb = boto3.resource('dynamodb', region_name=app.config['DYNAMODB_REGION'])
    wordle_table = dynamodb.Table(app.config['DYNAMODB_WORDLE_TABLE'])
    user_table = dynamodb.Table(app.config['DYNAMODB_USER_TABLE'])

    words_path = Path(__file__).parent.parent / 'resources' / 'words.txt'

    # Load the word list
    with open(words_path, 'r') as f:
        word_list = f.read().splitlines()

    wordle_repository = WordleRepository(wordle_table)
    user_repository = UserRepository(user_table)
    
    app.extensions['dynamodb'] = dynamodb
    app.config['wordle_service'] = WordleService(wordle_repository, word_list)
    app.config['user_service'] = UserService(user_repository)

    # JWT validation middleware
    @app.before_request
    def before_request_func():
        # Exclude the login and registration routes from requiring JWT
        if request.endpoint not in ['login_user', 'register_user']:
            token = request.headers.get('Authorization', None)
            if token:
                token = token.replace('Bearer ', '', 1)
                user_id = validate_and_decode_jwt(token, app.config['SECRET_KEY'])
                if user_id:
                    request.user_id = user_id
                else:
                    return jsonify({"message": "Invalid or expired token"}), 401
            else:
                return jsonify({"message": "Missing authentication token"}), 401


    create_routes(app)
    create_user_routes(app)

    return app