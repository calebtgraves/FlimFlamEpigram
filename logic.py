from flask import request
from flask_socketio import SocketIO, emit
import random

class EpigramGame:
    def __init__(self, socketio: SocketIO, players: list, host_sid):
        self.socketio = socketio
        # List of player dicts: 
            #[{'name': player_name, 'vip': False, 'sid': session_id, 
            #'score': 0, 'votes': {'round1': [], 'round2': [], 'round3': []},
            #'color':player_color}]
        self.players = players
        self.host_sid = host_sid # Host sid (for emit(room=host_sid)
        self.scores = {}   # Dictionary to keep track of scores
        self.prompts = []  # List of all prompts
        self.prompt_answers = {'round 1': {}, 'round 2': {}, 'round 3': {}} # prompts and answers (i.e. {'round x': {'prompt x': {'player 1': {'answer': answer, 'votes': [votes_by_name]}}})
        self.special_activities = [self.acro_lash, self.comic_lash, self.word_lash]  # Special activities
        self.crutches = [] # List of crutches (like safety quips)

        self.load_prompts()
        self.socketio.on_event('answer', self.receive_answers) # Get prompt answers
        self.socketio.on_event('vote', self.receive_votes) # Get player votes

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

    def run_game(self):
        self.show_instructions()
        for round_num in range(1, 3):
            self.play_round(round_num)
        self.play_special_round()
        self.show_winner()    

    def show_instructions(self):
        # Display game instructions
        wait_time = 15
        emit("instructions", {'wait': wait_time}, room=self.host_sid)

    def play_round(self, round_num):
        # Logic for each round
        print(f"Round {round_num}")
        self.get_prompts(len(self.players))
        prompts = self.make_prompt_pairs()
        self.deliver_prompts(prompts)
        self.show_results(round_num)
        self.update_leaderboard()

    def get_prompts(self, numPlayers:int):
        playerPrompts = [[] for i in range(numPlayers)]
        selectedPrompts = set() # All of the prompts to be used during this game. It's a set so that there will be no duplicates.

        for i in range(2): # For the first and second rounds. The third round will only have one prompt.
            while len(selectedPrompts) < numPlayers: # Should have as many prompts as players (each prompt goes to 2 players)
                selectedPrompts.add(random.choice(self.prompts))
        selectedPrompts = list(selectedPrompts)
        
        # Assign prompts for each player
        for i in range(numPlayers):
            # Current player's unique prompt
            playerPrompts[i].append(selectedPrompts[i])
            
            # Previous player's prompt, will wrap around for the first player (-1 index points to end)
            previous_player_prompt = selectedPrompts[i - 1]
            playerPrompts[i].append(previous_player_prompt)

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

    def receive_answers(self, data):
        player = self.find_player('sid', request.sid)
        prompt = data.prompt
        answer = data.answer
        pass

    def receive_votes(self, data):
        self.process_votes(self)
        pass        

    def process_votes(self, data):
        # Conduct voting for each prompt
        player = self.find_player('sid', request.sid)
        vote = data.vote # Can be player name
        player_voted = self.find_player('name', vote)
        player_voted['score'] += 50
        pass

    def show_results(self, round_num):
        # Show results of voting
        for prompt in self.prompt_answers[f'round {round_num}']:
            print(prompt['prompt'])
        pass

    def update_leaderboard(self):
        # Update and display the leaderboard
        # Sorting the list of dictionaries by 'score' in descending order
        sorted_players = sorted(self.players, key=lambda x: x['score'], reverse=True)

        # Extracting just the names in sorted order
        sorted_names = [player['name'] for player in sorted_players]

        emit('leaderboard', {'leaderboard_list': sorted_names}, room=self.host_sid)

        print('Scores:')
        for i, name in enumerate(sorted_names):
            print(f'    {i}. {name}')
        pass

    def play_special_round(self):
        # Logic for the special round
        print("--Special Round--")
        # Choose a special activity
        activity = random.choice(self.special_activities)
        activity()

    def acro_lash(self):
        print('Acro-Lash!')
        emit('special_round')
        pass

    def comic_lash(self):
        print('Comic-Lash!')
        emit('special_round')
        pass

    def word_lash(self):
        print('Word-Lash!')
        emit('special_round')
        pass

    def show_winner(self):
        # Determine and show the game winner
        pass

    def find_player(self, category:str, match_value):
        for player in self.players:
            if player[category] == match_value:
                return player
        return None  # Return None if no player with the given sid is found

if __name__ == "__main__":
    # To start the game
    game = EpigramGame()
    game.run_game()