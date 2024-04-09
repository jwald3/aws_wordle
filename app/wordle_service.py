from app.models import WordleHelper, Wordle
import uuid
from errors import UnauthorizedUserError

class WordleService:
    def __init__(self, wordle_repository, user_repository, word_list):
        self.wordle_repository = wordle_repository
        self.user_repository = user_repository
        self.word_list = word_list

    def generate_wordle(self, user_token, letter_count, hard_mode):
        # Assume we have a method in user_repository to get user_id by token
        user = self.user_repository.get_user_by_token(user_token)
        if not user:
            raise UnauthorizedUserError("Invalid or missing token.")
        
        game_id = str(uuid.uuid4())
        wordle = WordleHelper.generate_wordle(game_id, user_token, self.word_list, letter_count, hard_mode)

        wordle_dict = wordle.to_dict()

        self.wordle_repository.create_wordle(wordle_dict)
        return wordle

    def make_guess(self, game_id, user_token, guess):
        wordle_dict = self.wordle_repository.get_wordle(game_id, user_token)  # Pass user_token for retrieval
        wordle = Wordle.from_dict(wordle_dict)
        if wordle.user_token != user_token:
            raise UnauthorizedUserError("Unauthorized access")
        wordle = WordleHelper.make_guess(self.word_list, wordle, guess)
        self.wordle_repository.update_wordle(game_id, user_token, wordle.to_dict())  # Include user_token in update
        return wordle
    
    def surrender_game(self, user_token, game_id):
        wordle_dict = self.wordle_repository.get_wordle(game_id)
        wordle = Wordle.from_dict(wordle_dict)
        wordle = WordleHelper.surrender_game(wordle)
        if wordle.user_token != user_token:
            raise UnauthorizedUserError("Unauthorized access")
        self.wordle_repository.update_wordle(game_id, wordle.to_dict())
        return wordle
    
    def get_all_games_for_user(self, user_token):
        wordles = self.wordle_repository.get_all_wordles_for_user(user_token)
        return wordles
