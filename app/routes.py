from flask import jsonify, request
from .models import Wordle, WordleHelper
from .wordle_repository import WordleRepository
from .wordle_service import WordleService

def create_routes(app):
    @app.route('/wordle', methods=['POST'])
    def create_game():
        letter_count = request.json['letter_count']
        hard_mode = request.json.get('hard_mode', False)
        wordle = app.config['wordle_service'].generate_wordle(letter_count, hard_mode)
        return jsonify({"game_id": wordle.game_id})

    @app.route('/wordle/<game_id>', methods=['GET'])
    def get_game(game_id):
        wordle: dict = app.config['wordle_service'].wordle_repository.get_wordle(game_id)
        wordle_obj = Wordle.from_dict(wordle)
        return jsonify(wordle_obj.return_format())

    @app.route('/wordle/<game_id>/guess', methods=['POST'])
    def make_guess(game_id):
        guess = request.json['guess']
        try:
            wordle = app.config['wordle_service'].make_guess(game_id, guess)
            return jsonify(wordle.return_format())
        except Exception as e:
            print(e)
            # return a 400 status code if the guess is invalid
            return jsonify({"message": "Invalid guess"}), 400

    @app.route('/wordle/<game_id>/surrender', methods=['POST'])
    def surrender_game(game_id):
        wordle = app.config['wordle_service'].surrender_game(game_id)
        return jsonify(wordle.return_format())

    return app
