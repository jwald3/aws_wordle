from flask import Flask
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

    create_routes(app)
    create_user_routes(app)

    return app