from flask_socketio import emit
import random
import time

class EpigramGame:
    def __init__(self, players: list, host_sid):
        self.players = players  # List of player objects, including names, sids for emits, etc.
        self.host_sid = host_sid # Host sid (for emit(room=host_sid)
        self.scores = {}   # Dictionary to keep track of scores
        self.prompts = []  # List of all prompts
        self.special_activities = ['acro_lash', 'comic_lash', 'word_lash']  # Special activities
        self.crutches = [] # List of crutches (like safety quips)
        self.load_prompts()

    def run_game(self):
        self.show_instructions()
        for round_num in range(1, 3):
            self.play_round(round_num)
        self.play_special_round()
        self.show_winner()

    def load_prompts(self, shuffle=True):
        # Load prompts
        with open('prompts/prompts.txt', 'r') as prompts:
            for prompt in prompts:
                self.prompts.append(prompt.strip())
        if shuffle:
            random.shuffle(self.prompts)

        # Load crutches
        with open('prompts/crutches.txt', 'r') as crutches:
            for crutch in crutches:
                self.crutches.append(crutch.strip())

    def show_instructions(self):
        # Display game instructions
        wait_time = 15
        print(f'Waiting {wait_time} seconds for players to read instructions...')
        emit("instructions", room=self.host_sid)
        time.sleep(wait_time) # Wait for a bit so players can read the instructions

    def play_round(self, round_num):
        # Logic for each round
        print(f"Round {round_num}")
        self.get_prompts(len(self.players))
        prompts = self.make_prompt_pairs()
        self.deliver_prompts(prompts)
        self.collect_answers()
        self.voting_phase()
        self.show_results()
        self.update_leaderboard()

    def get_prompts(self, numPlayers:int):
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
        print(playerPrompts)
        return playerPrompts
                

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
            emit('new_prompt', {'prompt': self.players[i]['name']}, room=self.players[i]['sid'])
            emit('new_prompt', {'prompt': self.players[i]['name']}, room=self.players[i]['sid'])

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