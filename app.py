from flask import Flask, jsonify, request
import boto3
import uuid
import json
import random

app = Flask(__name__) 
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Wordle')

# route for creating a new game
@app.route('/wordle', methods=['POST'])
def create_game():
    letter_count = request.json['letter_count']
    hard_mode = request.json['hard_mode'] if 'hard_mode' in request.json else False
    
    wordle = WordleHelper.generate_wordle(letter_count, hard_mode)

    game_id = str(uuid.uuid4())

    table.put_item(Item={
        "game_id": game_id,
        'solution': wordle.solution,
        'guesses': wordle.guesses,
        'solved': wordle.solved,
        'surrendered': wordle.surrendered,
        'hard_mode': wordle.hard_mode
    })

    return jsonify({"game_id": game_id})

@app.route('/wordle/<game_id>', methods=['GET'])
def get_game(game_id):
    response = table.get_item(Key={'game_id': game_id})
    item = response['Item']

    # parse it into a DTO
    wordle = Wordle(item['solution'], item['guesses'], item['solved'], item['surrendered'], item['hard_mode'])

    return_json = wordle.return_format()

    return jsonify(return_json)
        
@app.route('/wordle/<game_id>/guess', methods=['POST'])
def make_guess(game_id):
    response = table.get_item(Key={'game_id': game_id})
    item = response['Item']

    # build item into Wordle object
    wordle = Wordle(item['solution'], item['guesses'], item['solved'], item['surrendered'], item['hard_mode'])

    try:
        WordleHelper.make_guess(wordle, request.json['guess'])

        table.update_item(
            Key={'game_id': game_id},
            UpdateExpression='SET guesses = :g, solved = :s',
            ExpressionAttributeValues={':g': wordle.guesses, ':s': wordle.solved},
            ReturnValues='UPDATED_NEW'
        )

        # return the updated item
        return jsonify(wordle.return_format())
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/wordle/<game_id>/surrender', methods=['POST'])
def surrender_game(game_id):
    response = table.get_item(Key={'game_id': game_id})
    item = response['Item']

    table.update_item(
        Key={'game_id': game_id},
        UpdateExpression='SET surrendered = :s1',
        ExpressionAttributeValues={':s1': True},
        ReturnValues='UPDATED_NEW'
    )

    #  return the updated item (with no obstructed solution)
    return jsonify(item)


class Wordle():
    def __init__(self, solution, guesses, solved, surrendered, hard_mode=False):
        self.solution: str = solution
        self.guesses: list[str] = guesses
        self.solved: bool = solved
        self.surrendered: bool = surrendered
        self.hard_mode: bool = hard_mode

    def return_format(self):
        return {
            "guesses": self.guesses,
            "guesses_formatted": self.get_formatted_guesses(),
            "letter_bank": self.get_formatted_alphabet(),
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
            "in_solution": True | False | None
        }
        If the letter is used and in the solution, it's marked as True. If it's used and not in the solution, it's marked as False. If it's not used, it's marked as None. Should avoid showing the user the solution."""
        alphabet = []
        for letter in "abcdefghijklmnopqrstuvwxyz":
            alphabet.append({"letter": letter, "used": letter in self.get_used_letters()})

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

# make a static class for the Wordle game logic
class WordleHelper:
    @staticmethod
    def generate_wordle(letter_count, hard_mode) -> Wordle:
        
        with open('words.json') as f:
            words = json.load(f)
        
        solution = random.choice(words)

        return Wordle(solution, [], False, False, hard_mode)
    
    @staticmethod
    def make_guess(wordle: Wordle, guess: str) -> Wordle:
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
        
        with open('words.json') as f:
            words = json.load(f)

        if guess not in words:
            raise Exception("Invalid guess")
        
        wordle.guesses.append(guess)

        if guess == wordle.solution:
            wordle.solved = True

        return wordle

if __name__ == '__main__':
    app.run(debug=True)