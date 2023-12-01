from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import time

class QuiplashGame:
    def __init__(self, players: list, host_sid):
        self.players = players  # List of player names
        self.host_sid = host_sid # Host sid (for emit(room=host_sid)
        self.scores = {}   # Dictionary to keep track of scores
        self.prompts = []  # List of prompts
        self.special_activities = ['acro_lash', 'comic_lash', 'word_lash']  # Special activities
        self.safety_epigrams = [ # List of safety epigrams (like safety quips)
            'A beetle with an attitude', 
            'Your mom', 
            'Loaded Banana',
            'Your friend Kevin',
            'Flim-Flam Epigram']

    def run_game(self):
        self.show_instructions()
        for round_num in range(1, 3):
            self.play_round(round_num)
        self.play_special_round()
        self.show_winner()

    def load_prompts(self, shuffle=True):
        with open('prompts/prompts.txt', 'r') as prompts:
            for prompt in prompts:
                self.prompts.append(prompt)
        if shuffle:
            random.shuffle(self.prompts)

        while len(self.players) < 3:
            new_player = self.check_for_new_player()
            if new_player:
                self.players.append(new_player)
                print(f"{new_player} has joined the game.")
            time.sleep(1) # Short rest before checking again

        while not self.all_in:
            self.check_all_in_pressed()
            time.sleep(1)

        print("All players are in. Starting the game...")

    def check_for_new_player(self):
        # Needs to return None if there is no new player or the player
        # name if one joins.
        # Will likely be an issue of Flask implementation
        test = True
        if test:
            return 'Player Name'
        else:
            return None

    def check_all_in_pressed(self):
        # TODO: Get Caleb's help for Javascript frontend
            # In need of a frontend solution here that can tell when 'All In'
            # gets pressed. When it gets pressed, I'd like to change self.all_in
            # to be True using logic like that below.
        javascript_button_pressed = True
        if javascript_button_pressed:
            self.all_in = True
        else:
            pass

    def show_instructions(self):
        # Display game instructions
        emit("instructions", room=self.host_sid)
        # TODO: This could be a good place for Yodahe to adapt player
        # instructions using the documentation. This is a near-the-end step.

    def play_round(self, round_num):
        # Logic for each round
        print(f"Round {round_num}")
        prompts = self.make_prompt_pairs()
        self.deliver_prompts(prompts)
        self.collect_answers()
        self.voting_phase()
        self.show_results()
        self.update_leaderboard()

    def make_prompt_pairs(self, shuffle=True):
        prompts = [] # Local prompt list
        players = len(self.players)
        # Get unique prompts (1 per player) and add to local list
        for i in range(players):
            unique_prompt = self.prompts.pop(i) # Get and then remove prompt from list of prompts
            prompts.append(unique_prompt)

        prompt_pairs = [] # List of tuple prompt pairs
        index = -1 # Start index at -1 to access end of list and go forward
        for _ in range(players):
            prompt_pair = (prompts[index], prompts[(index+1)])
            prompt_pairs.append(prompt_pair)
            index += 1 # Increment index at end

        if shuffle:
            random.shuffle(prompt_pairs)

        return prompt_pairs
            

    def deliver_prompts(self, prompt_pairs: tuple):
        prompt_pairs = prompt_pairs # Deliver 2 prompts per player
        for i in range(len(self.players)): # TODO: Finish this part and receiving part in javascript
            emit('new_prompt', {'prompt': self.player_dict[i]['name']}, room=self.player_dict[i]['sid'])
            emit('new_prompt', {'prompt': self.player_dict[i]['name']}, room=self.player_dict[i]['sid'])

    def collect_answers(self):
        # TODO: Need frontend solution to collect answers from players for prompts
        pass

    def voting_phase(self):
        # Conduct voting for each prompt
        pass

    def show_results(self):
        # Show results of voting
        pass

    def update_leaderboard(self):
        # Update and display the leaderboard
        pass

    def play_special_round(self):
        # Logic for the special round
        print("Special Round")
        # Choose a special activity
        activity = random.choice(self.special_activities)
        print(f"Special Activity: {activity}")
        # Rest of the logic

    def show_winner(self):
        # Determine and show the game winner
        pass

if __name__ == "__main__":
    # To start the game
    game = QuiplashGame()
    game.run_game()