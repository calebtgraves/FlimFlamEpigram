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
        self.deliver_prompts(self.get_prompts(len(self.players)))

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
        emit("instructions", room=self.host_sid)

    def play_round(self, round_num):
        # Logic for each round
        print(f"Round {round_num}")
        self.show_results(round_num)
        self.update_leaderboard()

    def get_prompts(self, numPlayers: int):
        playerPrompts = [[] for i in range(numPlayers)]
        selectedPrompts = set() # All of the prompts to be used during this game. It's a set so that there will be no duplicates.
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
            prompts_for_player = [prompts_for_player[:2], prompts_for_player[2:]]
            emit('new_prompts', prompts_for_player, room=self.players[i]['sid'])

    def receive_answers(self, data):
        if self.find_player('sid', request.sid):
            player = self.find_player('sid', request.sid) # Player giving answer
            prompts = data.prompts # List of two prompts
            answers = data.answers # List of two answers
            pass

    def receive_votes(self, data):
        if self.find_player('sid', request.sid):
            # Conduct voting for each prompt
            player_making_vote = self.find_player('sid', request.sid) # This is the player who cast the vote
            vote = data.vote # Can be player name
            player_voted_for = self.find_player('name', vote) # This is the player who got voted for
            player_voted_for['score'] += 50
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
        random.choice(self.special_activities)()

    def acro_lash(self):
        print('Acro-Lash!')
        self.send_to_all('acro_lash', {'acronym': 'ATSI'})
        pass

    def comic_lash(self):
        print('Comic-Lash!')
        self.send_to_all('comic_lash', {'comic': 'comic_location'})
        pass

    def word_lash(self):
        print('Word-Lash!')
        # Get prompt
        with open('final_round/word_lash/word_lash.txt', 'r') as word_lash:
            pass
        # Get word
        with open('final_round/word_lash/word.txt', 'r') as word:
            pass

        emit('word_lash', {'prompt': 'prompt_with_word'})
        pass

    def send_to_all(self, event: str, data, to_host=True):
        for player in self.players:
            emit(event, data, room=player['sid'])
        if to_host:
            emit(emit(event, data, room=self.host_id))

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