import random

class Wordle():
    def __init__(self, game_id, solution, guesses, solved, surrendered, hard_mode=False):
        self.game_id: str = game_id
        self.solution: str = solution
        self.guesses: list[str] = guesses
        self.solved: bool = solved
        self.surrendered: bool = surrendered
        self.hard_mode: bool = hard_mode

    def __repr__(self):
        return f"Wordle(game_id={self.game_id}, solution={self.solution}, guesses={self.guesses}, solved={self.solved}, surrendered={self.surrendered}, hard_mode={self.hard_mode})"
    
    def __str__(self):
        return f"Wordle(game_id={self.game_id}, solution={self.solution}, guesses={self.guesses}, solved={self.solved}, surrendered={self.surrendered}, hard_mode={self.hard_mode})"

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
        return Wordle(wordle_dict['game_id'], wordle_dict['solution'], wordle_dict['guesses'], wordle_dict['solved'], wordle_dict['surrendered'], wordle_dict['hard_mode'])

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
        """Return the guesses as a list of objects with the following format:
        {
            "letter": "a",
            "in_solution": True | False,
            "correct_position": True | False
        }
        The guesses enable frontend to display the guesses in the same order with formatted cells for each letter.
        """
        formatted_guesses = []
        for idx, guess in enumerate(self.guesses):
            # guesses are single letters, so each letter needs to be tested against the solution
            formatted_guess = []
            for i, letter in enumerate(self.guesses[idx]):
                # if the letter is in the word, there's a chance it's in the correct position
                if letter in self.solution:
                    #  if the letter is in the same position as the solution, it's correct
                    if letter == self.solution[i]:
                        formatted_guess.append({"letter": letter, "in_solution": True, "correct_position": True})
                    else:
                        formatted_guess.append({"letter": letter, "in_solution": True, "correct_position": False})
                else:
                    formatted_guess.append({"letter": letter, "in_solution": False, "correct_position": False})
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
    def generate_wordle(game_id, words, letter_count, hard_mode) -> Wordle:
        # make a random choice from the list of words where the length of the word is equal to the letter_count
        solution = random.choice([word for word in words if len(word) == letter_count])

        return Wordle(game_id, solution, [], False, False, hard_mode)
    
    @staticmethod
    def surrender_game(wordle: Wordle) -> Wordle:
        if wordle.is_game_over():
            raise Exception("Game is over")
        
        wordle.surrendered = True
        return wordle

    @staticmethod
    def make_guess(words: list[str], wordle: Wordle, guess: str) -> Wordle:
        guess = guess.lower()

        if wordle.is_game_over():
            raise Exception("Game is over")
        
        if guess in wordle.guesses:
            raise Exception("Guess already made")
        
        # optional to hard_mode — if letters were guessed in the correct order, they need to be included in all future guesses
        if wordle.hard_mode and len(wordle.guesses) > 0:
            # only the last guess is relevant
            last_guess: str = wordle.get_formatted_guesses()[-1]
            # loop over each letter in the guess along with the last_guess array. 
            for i, letter in enumerate(guess):
                # if the letter is in the solution, it must be in the same position as the last guess
                if last_guess[i]['correct_position']:
                    if letter != last_guess[i]['letter']:
                        raise Exception("Hard mode violation")

        if guess not in words:
            raise Exception("Invalid guess")
        
        wordle.guesses.append(guess)

        if guess == wordle.solution:
            wordle.solved = True

        return wordle
