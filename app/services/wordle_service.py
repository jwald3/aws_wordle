from ..models.wordle_models import WordleHelper, Wordle
import uuid

class WordleService:
    def __init__(self, wordle_repository, word_list):
        self.wordle_repository = wordle_repository
        self.word_list = word_list

    def generate_wordle(self, user_id, letter_count, hard_mode):
        game_id = str(uuid.uuid4())
        wordle = WordleHelper.generate_wordle(game_id, user_id, self.word_list, letter_count, hard_mode)

        wordle_dict = {
            "game_id": game_id,
            "user_id": wordle.user_id,
            'solution': wordle.solution,
            'guesses': wordle.guesses,
            'solved': wordle.solved,
            'surrendered': wordle.surrendered,
            'hard_mode': wordle.hard_mode
        }

        self.wordle_repository.create_wordle(wordle_dict)
        return wordle

    def make_guess(self, game_id, user_id, guess):
        wordle_dict = self.wordle_repository.get_wordle(game_id, user_id)
        wordle = Wordle.from_dict(wordle_dict)

        print(wordle)

        if not wordle:
            return None

        wordle = WordleHelper.make_guess(self.word_list, wordle, guess)

        print(wordle)
        print(wordle.to_dict())

        self.wordle_repository.update_wordle(game_id, wordle.to_dict())
        return wordle
    
    def surrender_game(self, game_id, user_id):
        wordle_dict = self.wordle_repository.get_wordle(game_id, user_id)
        wordle = Wordle.from_dict(wordle_dict)
        wordle = WordleHelper.surrender_game(wordle)
        self.wordle_repository.update_wordle(game_id, wordle.to_dict())
        return wordle
    
    def get_wordle(self, game_id, user_id):
        wordle_dict = self.wordle_repository.get_wordle(game_id, user_id)

        if not wordle_dict:
            return None

        wordle = Wordle.from_dict(wordle_dict)
        return wordle
    
    def get_user_wordles(self, user_id):
        wordles = self.wordle_repository.get_all_wordles(user_id)
        return wordles
