import random
from ..errors import GameOverError, GuessAlreadyMadeError, HardModeViolationError, InvalidGuessError

class Wordle():
    def __init__(self, game_id, user_id, solution, guesses, solved, surrendered, hard_mode=False):
        self.game_id = game_id
        self.user_id = user_id
        self.solution = solution
        self.guesses = guesses
        self.solved = solved
        self.surrendered = surrendered
        self.hard_mode = hard_mode

    def __repr__(self):
        return f"Wordle(game_id={self.game_id}, user_id={self.user_id}, solution={self.solution}, guesses={self.guesses}, solved={self.solved}, surrendered={self.surrendered}, hard_mode={self.hard_mode})"
    
    def __str__(self):
        return f"Wordle(game_id={self.game_id}, user_id={self.user_id}, solution={self.solution}, guesses={self.guesses}, solved={self.solved}, surrendered={self.surrendered}, hard_mode={self.hard_mode})"

    def to_dict(self):
        return {
            "solution": self.solution,
            "guesses": self.guesses,
            "solved": self.solved,
            "surrendered": self.surrendered,
            "hard_mode": self.hard_mode
        }
    
    @staticmethod
    def from_dict(wordle_dict):
        return Wordle(wordle_dict['game_id'], wordle_dict['user_id'], wordle_dict['solution'], wordle_dict['guesses'], wordle_dict['solved'], wordle_dict['surrendered'], wordle_dict['hard_mode'])

    def return_format(self):
        return {
            # if the game is over, the solution should be returned
            "solution": self.solution if self.is_game_over() else None,
            "guesses": self.guesses,
            "guesses_formatted": self.get_formatted_guesses(),
            "letter_bank": self.get_formatted_alphabet(),
            "letter_count": len(self.solution),
            "guesses_remaining": self.get_guesses_remaining(),
            "solved": self.solved,
            "surrendered": self.surrendered,
            "game_over": self.is_game_over()
        }

    def is_game_over(self):
        return self.solved or self.surrendered or (len(self.solution) + 1 - len(self.guesses) == 0)

    def get_guesses_remaining(self):
        if self.is_game_over():
            return 0
        return len(self.solution) + 1 - len(self.guesses)

    def get_formatted_guesses(self):
        formatted_guesses = []
        for guess in self.guesses:
            formatted_guess = []
            solution_letters = list(self.solution)  # Create a mutable list of solution letters
            
            # First pass: Mark correct positions
            for i, letter in enumerate(guess):
                if letter == solution_letters[i]:
                    formatted_guess.append({"letter": letter, "in_solution": True, "correct_position": True})
                    solution_letters[i] = None  # Remove from consideration for 'present' marking
                else:
                    formatted_guess.append({"letter": letter, "in_solution": False, "correct_position": False})

            # Second pass: Mark present but in wrong position, avoiding double-counting
            for i, entry in enumerate(formatted_guess):
                letter = guess[i]
                if not entry['correct_position'] and letter in solution_letters:
                    formatted_guess[i]["in_solution"] = True
                    formatted_guess[i]["correct_position"] = False  # Redundant but clarifies logic
                    solution_letters[solution_letters.index(letter)] = None  # Mark as used
            
            formatted_guesses.append(formatted_guess)
        return formatted_guesses


    def get_formatted_alphabet(self):
        """Return the alphabet as a list of objects with the following format:
        {
            "letter": "a",
            "used": True | False,
            "in_solution": True | False | None,
            "in_position": True | False | None
        }
        If the letter is used and in the solution, it's marked as True. If it's used and not in the solution, it's marked as False. If it's not used, it's marked as None. Any letters ."""
        alphabet = []
        for letter in "abcdefghijklmnopqrstuvwxyz":
            alphabet.append({"letter": letter, "used": letter in self.get_used_letters(), "in_position": letter in self.get_correct_positions()})

        for letter in alphabet:
            if letter["used"]:
                if letter["letter"] in self.solution:
                    letter["in_solution"] = True
                else:
                    letter["in_solution"] = False
            else:
                letter["in_solution"] = None

        return alphabet

    def get_used_letters(self):
        return sorted(list(set(''.join(self.guesses))))
    
    # create a method to see what letters are in the solution and in the right position in any of the guesses
    def get_correct_positions(self):
        # correct positions will be a set of letters that are in the solution and in the correct position in any of the guesses
        correct_positions = set()

        for guess in self.guesses:
            for i, letter in enumerate(guess):
                if letter == self.solution[i]:
                    correct_positions.add(letter)

        return sorted(list(correct_positions))
    

class WordleHelper:
    @staticmethod
    def generate_wordle(game_id, user_id, words, letter_count, hard_mode):
        # make a random choice from the list of words where the length of the word is equal to the letter_count
        solution = random.choice([word for word in words if len(word) == letter_count])

        return Wordle(game_id, user_id, solution, [], False, False, hard_mode)
    
    @staticmethod
    def surrender_game(wordle):
        if wordle.is_game_over():
            raise GameOverError("Game is over")
        
        wordle.surrendered = True
        return wordle

    @staticmethod
    def make_guess(words, wordle, guess):
        guess = guess.lower()

        if wordle.is_game_over():
            raise GameOverError("Game is over")
        
        if guess in wordle.guesses:
            raise GuessAlreadyMadeError("Guess already made")
        
        if len(guess) != len(wordle.solution):
            raise InvalidGuessError("Invalid guess")
        
        if wordle.hard_mode and len(wordle.guesses) > 0:
            last_guess = wordle.get_formatted_guesses()[-1]
            for i, letter in enumerate(guess):
                if last_guess[i]['correct_position'] and letter != last_guess[i]['letter']:
                    raise HardModeViolationError("Hard mode violation")

        if guess not in words:
            raise InvalidGuessError("Invalid guess")
        
        wordle.guesses.append(guess)
        if guess == wordle.solution:
            wordle.solved = True

        return wordle
