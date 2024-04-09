from flask import jsonify, request
from ..models.wordle_models import Wordle, WordleHelper
from ..repositories.wordle_repository import WordleRepository
from ..services.wordle_service import WordleService
# import the errors from resources/errors.py
from ..errors import GameOverError, GuessAlreadyMadeError, HardModeViolationError, InvalidGuessError

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
        except GameOverError:
            return jsonify({"message": "Game is over"}), 400
        except GuessAlreadyMadeError:
            return jsonify({"message": "Guess already made"}), 400
        except HardModeViolationError:
            return jsonify({"message": "Hard mode violation"}), 400
        except InvalidGuessError:
            return jsonify({"message": "Invalid guess"}), 400
        except Exception as e:  # Catch-all for any other unexpected errors
            print(e)
            return jsonify({"message": "An unexpected error occurred"}), 500


    @app.route('/wordle/<game_id>/surrender', methods=['POST'])
    def surrender_game(game_id):
        wordle = app.config['wordle_service'].surrender_game(game_id)
        return jsonify(wordle.return_format())

    return app
