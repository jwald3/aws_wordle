from flask import Flask
import json
from .config import Config
from .wordle_repository import WordleRepository
from .wordle_service import WordleService
from .routes import create_routes
import boto3
from pathlib import Path
from flask_cors import CORS

def create_app(config_class=Config):
    # Create a Flask application
    app = Flask(__name__)

    # Enable CORS
    CORS(app, resources={r'/*': {'origins': ['http://localhost:5173', 'http://localhost:5000']}})
    
    # Apply configuration settings from your config.py or environment
    app.config.from_object(config_class)

    # Initialize database connection or other services
    dynamodb = boto3.resource('dynamodb', region_name=app.config['DYNAMODB_REGION'])
    table = dynamodb.Table(app.config['DYNAMODB_TABLE'])

    words_path = Path(__file__).parent.parent / 'resources' / 'words.txt'

    # Load the word list
    with open(words_path, 'r') as f:
        word_list = f.read().splitlines()

    wordle_repository = WordleRepository(table)
    
    app.extensions['dynamodb'] = dynamodb
    app.config['wordle_service'] = WordleService(wordle_repository, word_list)

    create_routes(app)

    return app