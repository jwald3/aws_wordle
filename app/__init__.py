from flask import Flask
import json
from .config import Config
from .wordle_repository import WordleRepository
from .wordle_service import WordleService
from .routes import create_routes
import boto3
from pathlib import Path


def create_app(config_class=Config):
    # Create a Flask application
    app = Flask(__name__)
    
    # Apply configuration settings from your config.py or environment
    app.config.from_object(config_class)

    # Initialize database connection or other services
    dynamodb = boto3.resource('dynamodb', region_name=app.config['DYNAMODB_REGION'])
    table = dynamodb.Table(app.config['DYNAMODB_TABLE'])

    print(app.config['DYNAMODB_REGION'])
    print(app.config['DYNAMODB_TABLE'])

    words_path = Path(__file__).parent.parent / 'resources' / 'words.json'

    with open(words_path) as f:
        word_list = json.load(f)
    
    wordle_repository = WordleRepository(table)
    
    app.extensions['dynamodb'] = dynamodb
    app.config['wordle_service'] = WordleService(wordle_repository, word_list)

    create_routes(app)

    return app