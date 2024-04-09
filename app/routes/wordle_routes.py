from flask import jsonify, request
from ..models.wordle_models import Wordle, WordleHelper
from ..repositories.wordle_repository import WordleRepository
from ..services.wordle_service import WordleService
# import the errors from resources/errors.py
from ..errors import GameOverError, GuessAlreadyMadeError, HardModeViolationError, InvalidGuessError
from ..utils.middleware import jwt_required

def create_routes(app):
    @app.route('/wordle', methods=['POST'])
    @jwt_required
    def create_game():
        user_id = getattr(request, 'user_id', None)
        letter_count = request.json['letter_count']
        hard_mode = request.json.get('hard_mode', False)
        wordle = app.config['wordle_service'].generate_wordle(user_id, letter_count, hard_mode)
        return jsonify({"game_id": wordle.game_id})

    @app.route('/wordle/<game_id>', methods=['GET'])
    @jwt_required
    def get_game(game_id):
        user_id = getattr(request, "user_id", None)
        wordle: dict = app.config['wordle_service'].wordle_repository.get_wordle(game_id, user_id)
        wordle_obj = Wordle.from_dict(wordle)
        return jsonify(wordle_obj.return_format())

    @app.route('/wordle/<game_id>/guess', methods=['POST'])
    @jwt_required
    def make_guess(game_id):
        user_id = getattr(request, "user_id", None)
        guess = request.json['guess']
        try:
            wordle = app.config['wordle_service'].make_guess(game_id, user_id, guess)
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
    @jwt_required
    def surrender_game(game_id):
        user_id = getattr(request, "user_id", None)
        wordle = app.config['wordle_service'].surrender_game(game_id, user_id)
        return jsonify(wordle.return_format())
    
    @app.route('/wordle', methods=['GET'])
    @jwt_required
    def get_user_wordles():
        user_id = getattr(request, "user_id", None)
        wordles = app.config['wordle_service'].get_user_wordles(user_id)
        return jsonify([Wordle.from_dict(wordle).return_format() for wordle in wordles])


    return app
