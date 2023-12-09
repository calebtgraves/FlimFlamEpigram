from flask import request
from flask_socketio import SocketIO, emit
import os
import random

class EpigramGame:
    def __init__(self, socketio: SocketIO, players: list, host_sid):
        self.socketio = socketio
        self.host_sid = host_sid # Host sid (for emit(room=host_sid)
        
        self.players = players # List of player dicts
        #i.e. [..., {'name': player_name, 'vip': False, 'sid': session_id, 'score': 0, 'color':player_color}, ...]

        self.prompts = []  # List of all prompts
        self.prompt_answers = {1: {}, 2: {}, 3: {}} # prompts and answers
        # i.e. {'round x': {'prompt x': {'player 1': {'answer': answer, 'votes': [player objects]}}}
        self.crutches = [] # List of crutches (like safety quips)

        self.special_activities = [self.acro_lash, self.comic_lash, self.word_lash]  # Special activities
        
        ## Initializing Functions ##
        self.load_prompts()
        self.deliver_prompts(self.get_prompts(len(self.players)))

        ## Socket Listeners ##
        self.socketio.on_event('answer', self.receive_answers) # Get prompt answers
        self.socketio.on_event('special_answer', self.special_receive_answers) # Get player special answer
        self.socketio.on_event('answers_done', self.show_answers) # Show answers when host says time is up

        self.socketio.on_event('vote', self.receive_votes) # Get player votes
        self.socketio.on_event('special_vote', self.special_receive_votes) # Get player special votes
        self.socketio.on_event('votes_done', self.show_votes) # Show votes when host says time is up

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
        self.start(1)
        # self.play_round(2)
        # self.play_special_round(3)
        # self.show_winner()
        print('Done!')

    def start(self, round_num: int):
        # Logic for each round
        print(f"Round {round_num}")
        self.send_to_all('round', {'number': round_num})

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
        for i, prompt_list in enumerate(prompt_pairs):
            print(i+1, prompt_list)
        for i in range(len(self.players)): # Send prompts to each player
            prompts_for_player = prompt_pairs.pop()
            prompts_for_player = [prompts_for_player[:2], prompts_for_player[2:]]
            emit('new_prompts', prompts_for_player, room=self.players[i]['sid'])

    def receive_answers(self, data):
        if self.find_player('sid', request.sid):
            player = self.find_player('sid', request.sid) # Player giving answer
            prompts = data.prompts # List of two prompts
            answers = data.answers # List of two answers
            round_num = data.round_num # Round number
            player_name = player['name']

            for prompt, answer in zip(prompts, answers):
                if prompt not in self.prompt_answers[round_num]:
                    self.prompt_answers[round_num][prompt] = {} # Make prompt key if it doesn't exist

                self.prompt_answers[round_num][prompt][player_name] = {'answer': answer, 'votes': []}
            pass

    def receive_votes(self, data):
        if self.find_player('sid', request.sid):
            # Conduct voting for each prompt
            player_sending_vote = self.find_player('sid', request.sid) # This is the player who cast the vote
            vote = data.vote # Player name
            prompt = data.prompt # Prompt being voted on
            round_num = data.round_num # Round number
            player_voted_for = self.find_player('name', vote) # This is the player who got voted for
            player_voted_for_name = player_voted_for['name']
            
            self.prompt_answers[round_num][prompt][player_voted_for_name]['votes'].append(player_sending_vote) # Show who voted for what

            player_voted_for['score'] += 50
        pass

    def show_answers(self, data):
        # # Show player answers
        # for prompt in self.prompt_answers[round_num]:
        #     print(prompt)
        #     for player_name in prompt:
        #         print(player_name['answer'])
        #     print()
        # Emit round results to the host
        round_num = data.round_num
        emit('answers', self.prompt_answers[round_num], room=self.host_sid) # Give dictionary to host to display
        pass

    def show_votes(self, round_num):
        for prompt in self.prompt_answers[round_num].keys():
            print(prompt)
        pass

    def special_receive_answers(self, data):
        if self.find_player('sid', request.sid):
            player = self.find_player('sid', request.sid) # Player giving answer
            answer = data.answer # Single answer
            pass

    def special_receive_votes(self, data):
        if self.find_player('sid', request.sid):
            # Conduct voting for each prompt
            player_making_vote = self.find_player('sid', request.sid) # This is the player who cast the vote

            first_vote = data.vote1 # Player name (first vote)
            second_vote = data.vote2 # Player name (second vote)
            third_vote = data.vote3 # Player name (third vote)

            first_player_voted_for = self.find_player('name', first_vote) # This is the player who got voted for
            second_player_voted_for = self.find_player('name', second_vote) # This is the player who got voted for
            third_player_voted_for = self.find_player('name', third_vote) # This is the player who got voted for

            first_player_voted_for['score'] += 150 # Gold
            second_player_voted_for['score'] += 100 # Silver
            third_player_voted_for['score'] += 50 # Bronze
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

    def play_special_round(self, round_num: int): # Seems silly as round_num will always be 3, but this helps with self.prompt_answers
        # Logic for the special round
        print(f"--Round {round_num}: Special Round--")
        self.send_to_all('round', {'number': round_num})
        # Choose a special activity
        random.choice(self.special_activities)()

    def acro_lash(self):
        print('Acro-Lash!')
        acronym = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(4))
        self.send_to_all('acro_lash', {'acronym': acronym.upper()})
        pass

    def comic_lash(self):
        print('Comic-Lash!')
        # List all files in the given directory
        files = os.listdir('static/images/comic_lash')
        
        self.send_to_all('comic_lash', {'comic': random.choice(files)})
        pass

    def word_lash(self):
        print('Word-Lash!')
        # Get word
        with open('final_round/word_lash/word.txt', 'r') as words:
            word = random.choice(words.readlines())
        # Get prompt
        with open('final_round/word_lash/word_lash.txt', 'r') as word_lash:
            lash = random.choice(word_lash.readlines())

        self.send_to_all('word_lash', {'word': word, 'lash': lash})

    def send_to_all(self, event: str, data='', to_host=True):
        for player in self.players:
            emit(event, data, room=player['sid'])
        if to_host:
            emit(event, data, room=self.host_sid)

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