from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import time

class EpigramGame:
    def __init__(self, players: list, host_sid):
        self.players = players  # List of player objects, including names, sids for emits, etc.
        self.host_sid = host_sid # Host sid (for emit(room=host_sid)
        self.scores = {}   # Dictionary to keep track of scores
        self.prompts = []  # List of all prompts
        self.special_activities = ['acro_lash', 'comic_lash', 'word_lash']  # Special activities
        self.crutches = [ # List of crutches (like safety quips)
            'A beetle with an attitude', 
            'Your mom', 
            'Loaded Banana',
            'Your friend Kevin',
            'Flim-Flam Epigram',
            "Clown shoes",
            "Moonwalking fish",
            "Tofu sword fights",
            "Banana peel surfing",
            "Giraffe ballet",
            "Wombat rodeo",
            "Disco chickens",
            "Ninja librarians",
            "Jellybean juggling",
            "Marshmallow dodgeball",
            "Sock puppetry",
            "Penguin tap-dance",
            "Llama opera",
            "Pajama parade",
            "Synchronized sneezing",
            "Bagpipe karaoke",
            "Bubblegum sculpting",
            "Pirate pancake",
            "Robot poetry",
            "Pickle juggling",
            "Boomerang Frisbee",
            "Snail racing",
            "Zombie gardening",
            "Elephant limbo",
            "Cupcake cannon",
            "Laser tag marshmallows",
            "Alien salsa",
            "Lawn mower ballet",
            "Cactus pillow",
            "T-Rex yoga",
            "Unicorn rodeo",
            "Squirrel karate",
            "Disco ninja",
            "Fish fashion",
            "Hula hoop marathon",
            "Taco Tuesday",
            "Penguin wrestling",
            "Jedi gardening",
            "Juggling cacti",
            "Ninja disco",
            "Llama rodeo",
            "Robot tap-dance",
            "Pancake Olympics",
            "Kangaroo karaoke",
            "Pirate pogo",
            "Giraffe surfing",
            "Wombat opera",
            "Moonwalking llamas",
            "Jellybean ballet",
            "Tofu juggling",
            "Banana hammocks",
            "Disco sloths",
            "Robot rodeo",
            "Cupcake fencing",
            "Zombie fashion",
            "Pickle limbo",
            "Elephant disco",
            "Alien rodeo",
            "Lawn mower opera",
            "Synchronized llamas",
            "Boomerang gardening",
            "Snail ballet",
            "Laser tag pillow",
            "Unicorn pancake",
            "Marshmallow yoga",
            "Cactus karaoke",
            "Fish cannon",
            "Hula hoop ninja",
            "Taco sculpture",
            "Penguin Frisbee",
            "Jedi fashion",
            "Squirrel rodeo",
            "Disco gardening",
            "T-Rex marathon",
            "Giraffe limbo",
            "Pirate yoga",
            "Wombat disco",
            "Jellybean wrestling",
            "Moonwalking cacti",
            "Elephant tap-dance",
            "Cupcake opera",
            "Zombie karaoke",
            "Robot fencing",
            "Alien ballet",
            "Lawn mower surfing",
            "Pickle fashion",
            "Banana pillow",
            "Unicorn cannon",
            "Juggling pancakes",
            "Marshmallow rodeo",
            "Disco ninja turtles",
            "Synchronized llamas",
            "Boomerang opera",
            "Snail yoga",
            "Laser tag disco",
            "Elephant fencing",
            "Cactus karaoke",
            "Alien limbo",
            "Lawn mower fashion",
            "Hula hoop pogo",
            "T-Rex rodeo",
            "Giraffe karaoke",
            "Pirate disco",
            "Wombat ninja",
            "Jellybean fashion",
            "Moonwalking pancakes",
            "Unicorn yoga",
            "Marshmallow fencing",
            "Pickle opera",
            "Banana rodeo",
            "Synchronized turtles",
            "Disco cacti",
            "Robot yoga",
            "Jedi limbo",
            "Fish disco",
            "Hula hoop opera",
            "Elephant pogo",
            "Zombie fencing",
            "Cupcake karaoke",
            "Alien tap-dance",
            "Laser tag pancake",
            "Lawn mower ballet",
            "Boomerang ninja",
            "Snail rodeo",
            "T-Rex opera",
            "Giraffe disco",
            "Pancake fencing",
            "Pirate yoga",
            "Banana ninja",
            "Wombat limbo",
            "Synchronized disco",
            "Jellybean tap-dance",
            "Unicorn fencing",
            "Marshmallow ninja",
            "Pickle yoga",
            "Elephant rodeo",
            "Disco opera",
            "Robot fencing",
            "Jedi disco",
            "Alien ballet",
            "Fish karaoke",
            "Hula hoop pancake",
            "Cupcake tap-dance",
            "Laser tag ninja",
            "Lawn mower yoga",
            "Snail disco",
            "T-Rex fencing",
            "Giraffe pogo"
            ]
        self.load_prompts()
        self.deliver_prompts(self.get_prompts(len(self.players)))

    def run_game(self):
        self.show_instructions()
        for round_num in range(1, 3):
            self.play_round(round_num)
        self.play_special_round()
        self.show_winner()

    def load_prompts(self, shuffle=True):
        with open('prompts/prompts.txt', 'r') as prompts:
            for prompt in prompts:
                self.prompts.append(prompt.strip())
        if shuffle:
            random.shuffle(self.prompts)

    def show_instructions(self):
        # Display game instructions
        emit("instructions", room=self.host_sid)
        # TODO: This could be a good place for Yodahe to adapt player
        # instructions using the documentation. This is a near-the-end step.

    def play_round(self, round_num):
        # Logic for each round
        print(f"Round {round_num}")
        self.collect_answers()
        self.voting_phase()
        self.show_results()
        self.update_leaderboard()

    def get_prompts(self,numPlayers:int):
        playerPrompts = [[] for i in range(numPlayers)]
        selectedPrompts = set() # All of the prompts to be used during this game. It's a set so that there will be no duplicates.
        for i in range(2): # For the first and second rounds. The third round will only have one prompt.
            while len(selectedPrompts) < numPlayers*2:
                selectedPrompts.add(random.choice(self.prompts))
        selectedPrompts = list(selectedPrompts)
        gamePrompts = [selectedPrompts[:len(selectedPrompts)//2],selectedPrompts[len(selectedPrompts)//2:]]
        for round in gamePrompts:
            for i in range(numPlayers):
                playerPrompts[i].append(round[i])
                playerPrompts[i].append(round[i-1])
        random.shuffle(playerPrompts)
        return playerPrompts

    def deliver_prompts(self, prompt_pairs: list):
        print(prompt_pairs)
        for i in range(len(self.players)): # Send prompts to each player
            prompts_for_player = prompt_pairs.pop()
            prompts_for_player = [prompts_for_player[:2],prompts_for_player[2:]]
            emit('new_prompts',prompts_for_player,room=self.players[i]['sid'])

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
    game = EpigramGame()
    game.run_game()