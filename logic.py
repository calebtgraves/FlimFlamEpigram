from flask import request
from flask_socketio import SocketIO, emit
import os
import random

class EpigramGame:
    def __init__(self, socketio: SocketIO, players: list, host_sid):
        self.socketio = socketio
        self.host_sid = host_sid # Host sid (for emit(room=host_sid)

        self.round_num = 0
        self.answers_received = 0
        self.votes_received = 0
        
        self.players = players # List of player dicts
        #i.e. [..., {'name': player_name, 'vip': False, 'sid': session_id, 'score': 0, 'color':player_color}, ...]

        self.prompts = []  # List of all prompts
        self.prompt_answers = {1: {}, 2: {}, 3: {}} # prompts and answers
        # i.e. {'round x': {'prompt x': {'player 1': {'answer': answer, 'votes': [player objects], 'crutch': bool}}}
        self.crutches = [] # List of crutches (like safety quips)

        self.special_activities = [self.acro_lash, self.comic_lash, self.word_lash]  # Special activities
        
        ## Initializing Functions ##
        self.load_prompts()
        self.deliver_prompts(self.get_prompts(len(self.players)))

        ## Socket Listeners ##
        # Receive answers from client.html
        self.socketio.on_event('answer', self.receive_answers) # Get prompt answers
        self.socketio.on_event('special_answer', self.special_receive_answers) # Get player special answer
        
        # Receive votes from client.html
        self.socketio.on_event('vote', self.receive_votes) # Get player votes
        self.socketio.on_event('special_vote', self.special_receive_votes) # Get player special votes

        # Receive requests from host.html
        self.socketio.on_event('client_input_done', self.send_results_dict) # Send updated dictionary of prompts, answers, votes to host.html
        self.socketio.on_event('votes_needed', self.send_clients_challenge)

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
        self.send_to_all('all_players', self.players)
        self.play_round() # Start the Python-Javascript back-and-forth
        # self.play_round(2)
        # self.play_special_round(3)
        # self.show_winner()

    def play_round(self):
        # Increment round number
        self.round_num += 1
        # Clear answer/vote count trackers
        self.answers_received = 0
        self.votes_received = 0
        # Send round event
        print(f"Round {self.round_num}")
        self.send_to_all('round', {'number': self.round_num})

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

    def build_dictionary(self, prompts: list, player):
        #prompts looks like this: [['prompt1','prompt2'],['prompt3','prompt4']]
        for i, prompt_pair in enumerate(prompts):
            if not prompt_pair[0] in self.prompt_answers[i+1]:
                self.prompt_answers[i+1][prompt_pair[0]] = {}
            if not prompt_pair[1] in self.prompt_answers[i+1]:
                self.prompt_answers[i+1][prompt_pair[1]] = {}
            self.prompt_answers[i+1][prompt_pair[0]][player] = {'answer': '[NO ANSWER]', 'crutch': False, 'votes': []}
            self.prompt_answers[i+1][prompt_pair[1]][player] = {'answer': '[NO ANSWER]', 'crutch': False, 'votes': []}
    
    def get_crutches(self): # This function will be used to generate the crutches that each player will be able to use throughout the game.
        myCrutches = set() # Use a set so that each player will not have any duplicates.
        while len(myCrutches) < 5: # The number of prompts that each player will answer using a while loop to make sure we will have 5 no matter what.
            myCrutches.add(random.choice(self.crutches))
        return list(myCrutches)

    def deliver_prompts(self, prompt_pairs: list):
        player_names = [player['name'] for player in self.players]
        for name, prompt_list in zip(player_names, prompt_pairs):
            print(name, prompt_list)
        print(self.players)
        for i in range(len(self.players)): # Send prompts to each player
            prompts_for_player = prompt_pairs.pop()
            prompts_for_player = [prompts_for_player[:2], prompts_for_player[2:]]
            self.build_dictionary(prompts_for_player,self.players[i]['name'])
            emit('new_prompts', {'myPrompts':prompts_for_player,'myCrutches':self.get_crutches()}, room=self.players[i]['sid'])

    def receive_answers(self, data):
        if self.find_player('sid', request.sid):
            self.answers_received += 1
            player = self.find_player('sid', request.sid) # Player giving answer
            print(data)
            prompts = data['prompts'] # List of two prompts
            answers = data['answers'] # List of two dictionaries: {'response': string, 'crutch': bool}
            player_name = player['name']

            for prompt, answer in zip(prompts, answers):
                self.prompt_answers[self.round_num][prompt][player_name] = {'answer': answer['response'], 'crutch':answer['crutch'], 'votes': []}

            emit('player_answer', {'name': player_name}, room=self.host_sid)
            print(f'{self.answers_received}/{len(self.players)} players have submitted answers...')

            if self.answers_received == len(self.players):
                emit('players_done', room=self.host_sid)
                print(f'All {len(self.players)} players have submitted their answers.')

    def send_clients_challenge(self, data):
        if self.host_sid == request.sid:
            prompt_to_match = data['prompt'] # prompt_to_match is a string

            players_involved_answers = {}

            for prompt_key in self.prompt_answers[self.round_num]:
                if prompt_key == prompt_to_match:
                    prompt_data = self.prompt_answers[self.round_num][prompt_key]
                    for player_name in prompt_data:
                        answer = prompt_data[player_name]['answer']
                        players_involved_answers[player_name] = answer

            for player in self.players:
                if player['name'] not in players_involved_answers.keys():
                    # responses is a dictionary -> {player_name1: answer, player_name2: answer}
                    emit('challenge', {'prompt': prompt_to_match, 'responses': players_involved_answers}, room=player['sid']) 
                    print(f'{player["name"]} is voting...')
                else:
                    emit('challenge_wait', room=player['sid'])
                    print(f'{player["name"]} is waiting...')

    def receive_votes(self, data):
        # TODO: Quiplash awards points based on the percent of players who chose an answer.
        # Quiplash also awards bonus points for a Quiplash and keeps track of which answers
        # were Quiplashes. We're planning to add this functionality in the future.
        if self.find_player('sid', request.sid):
            self.votes_received += 1
            # Conduct voting for each prompt
            player_sending_vote = self.find_player('sid', request.sid) # This is the player who cast the vote
            submitter_name = player_sending_vote['name']
            vote = data['name'] # Player name
            response = data['text']
            print(f'{player_sending_vote["name"]} voted for {vote}')
            print(f'{self.votes_received}/{len(self.players) - 2} players have submitted votes...')

            prompt = data['prompt'] # Prompt being voted on
            player_voted_for = self.find_player('name', vote) # This is the player who got voted for
            winner_name = player_voted_for['name']
            
            self.prompt_answers[self.round_num][prompt][winner_name]['votes'].append(player_sending_vote) # Show who voted for what
            if not self.prompt_answers[self.round_num][prompt][winner_name]['crutch']:
                player_voted_for['score'] += 50
            else:
                player_voted_for['score'] += 25

            # Send updated dictionary to host
            emit('votes', {'winner': winner_name, 'submitter': submitter_name, 'response': response}, room=self.host_sid)

            if self.votes_received == (len(self.players) - 2):
                emit('players_done', room=self.host_sid)
                print(f'All {len(self.players)} players have submitted their votes.')
        pass

    def send_results_dict(self):
        if self.host_sid == request.sid: # If it is our host sending, then accept
            # Have host show player answers
            emit('answers', self.prompt_answers[self.round_num], room=self.host_sid) # Give dictionary to host to display
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

    def play_special_round(self): # Seems silly as round_num will always be 3, but this helps with self.prompt_answers
        # Logic for the special round
        print(f"--Round {self.round_num}: Special Round--")
        self.send_to_all('round', {'number': self.round_num})
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