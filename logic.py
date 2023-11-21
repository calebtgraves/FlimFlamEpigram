import random
import time

class QuiplashGame:
    def __init__(self):
        self.players = []  # List of player names
        self.scores = {}   # Dictionary to keep track of scores
        self.prompts = []  # List of prompts
        self.safety_epigrams = [ # List of safety epigrams (like safety quips)
            'A beetle with an attitude', 
            'Your mom', 
            'Loaded banana',
            'Your friend Kevin',
            'Flim-Flam Epigram']
        self.special_activities = ["Activity 1", "Activity 2", "..."]  # Special activities

    def run_game(self):
        self.setup_lobby()
        self.show_instructions()
        for round_num in range(1, 3):
            self.play_round(round_num)
        self.play_special_round()
        self.show_winner()

    def load_prompts(self):
        with open('prompts/prompts.txt', 'r') as prompts:
            for prompt in prompts:
                self.prompts.append(prompt)

    def setup_lobby(self):
        print("Waiting for players to join...")

        while len(self.players) < 3 or not self.check_all_in_pressed():
            new_player = self.check_for_new_player()
            if new_player:
                self.players.append(new_player)
                print(f"{new_player} has joined the game.")

        print("All players are in. Starting the game...")

    def check_for_new_player(self):
        # Needs to return None if there is no new player or the player
        # name if one joins.
        pass

    def check_all_in_pressed(self):
        # In need of a frontend solution here that can tell when 'All In'
        # gets pressed.
        pass

    def show_instructions(self):
        # Display game instructions
        print("Welcome to the game! Here are the instructions...")

    def play_round(self, round_num):
        # Logic for each round
        print(f"Round {round_num}")
        self.collect_answers()
        self.voting_phase()
        self.show_results()
        self.update_leaderboard()

    def collect_answers(self):
        # Collect answers from players for prompts
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