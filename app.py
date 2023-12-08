from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from logic import EpigramGame
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

## Constants ##
MAX_PLAYERS = 8
MIN_PLAYERS = 3
COLORS = [ #List of possible player colors as hex codes
    "#c93838",
    "#e5a22e",
    "#e3cb15",
    "#68c938",
    "#38c9c9",
    "#3874c9",
    "#9638c9",
    "#c9389e"
    ]

## Reference Dictionaries ##
connected_players = {} # keys are game id, values are player info
vips = {} # VIPs of each game id by session id (for emitting to VIPs)
game_hosts = {} # Game id as key, host's session id as value
colors_available = {} #Stores per game what player colors have not been assigned; keys are game ids, values are lists of colors.

active_codes = [] #List of active game codes. Used to let players know if they type in an invalid game code.

def get_letters(num_letters): # Yodahe's random letter function

    random_letters = [random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for letter in range(num_letters)]

    random_string = ''.join(random_letters)

    return random_string

@app.route('/host')
def host():
    return render_template('host.html')  # Host page

@app.route('/')
def client():
    return render_template('client.html')  # Client/player page

@socketio.on('game_id_request')
def serve_id():
    game_id = get_letters(4)
    while game_id in active_codes: #Make sure that there isn't a repeat code created.
        game_id = get_letters(4)
    active_codes.append(game_id)
    session_id = request.sid
    game_hosts[game_id] = session_id
    colors_available[game_id] = COLORS[::]
    random.shuffle(colors_available[game_id]) #Shuffle the colors list so that we can use .pop() to get a "random" color.
    emit('game_id', {'id': game_id})

@socketio.on('connect')
def handle_connect():
    print("A new player has connected.")
    # Here you can perform actions needed when a new player connects
    # For example, sending a welcome message
    emit('welcome_message', {'message': 'Welcome to the game!'})

@socketio.on('register_player')
def handle_player_registration(data):
    player_name = data['name']
    game_id = data['id'].upper()
    session_id = request.sid
    if game_id not in active_codes:
        emit('invalid_code',room=session_id)
        print(f'Game code "{game_id}" does not exist.')
        return
    if game_id in connected_players:
        if len(connected_players[game_id]) < MAX_PLAYERS:
            player_color = colors_available[game_id].pop() #Assign a color to a player whilst removing it from the list so no other players can have it.
            connected_players[game_id].append({'name': player_name, 'vip': False, 'sid': session_id, 'score': 0, 'votes': {'round1': [], 'round2': [], 'round3': []}, 'color':player_color})
            if len(connected_players[game_id]) == MIN_PLAYERS:
                emit('min_reached', room=vips[game_id])
            print(f"Player {player_name} has joined the game with ID {game_id}.")
            emit('new_player', {'name': player_name, 'vip': False,'color':player_color}, room=game_hosts[game_id]) # Send player name to host
            emit('color',player_color,room=session_id)
        else:
            print(f"Player {player_name} could not join: {MAX_PLAYERS} players are already connected.")
            emit('game_full',room=session_id)
    else:
        player_color = colors_available[game_id].pop() #Assign a color to a player whilst removing it from the list so no other players can have it.
        connected_players[game_id] = [{'name': player_name, 'vip': True, 'sid': session_id, 'score': 0, 'votes': {'round1': [], 'round2': [], 'round3': []}, 'color':player_color}]
        vips[game_id] = session_id
        print(f"Player {player_name} has joined the game with ID {game_id}.")
        emit('vip')
        emit('new_player', {'name': player_name, 'vip': True, 'color':player_color}, room=game_hosts[game_id]) # Send VIP player name to host
        emit('color',player_color,room=session_id)
        emit('vip',room=session_id)

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    for game in connected_players:
        for player in connected_players[game]:
            if player["sid"] == session_id:
                player_name = player["name"]
                print(f"Player {player_name} has disconnected.")
                # Make the player's color available
                print(player)
                colors_available[game].append(player['color'])
                random.shuffle(colors_available[game])
                # Remove player from the list
                connected_players[game].remove(player)
                if len(connected_players[game]) == 0:
                    del connected_players[game]
                    emit('last_player_disconnected',room=game_hosts[game])
                elif not connected_players[game][0]['vip']:
                    connected_players[game][0]['vip'] = True
                    vips[game] = connected_players[game][0]['sid']
                    emit('vip',room=connected_players[game][0]['sid'])
                    emit('new_vip',room=game_hosts[game])
                emit('player_disconnected',player_name,room=game_hosts[game])
                return

@socketio.on('start_game')
def start_game(game_id):
    game_id = game_id.upper()
    for player in connected_players[game_id]:
        emit('game_started',room=player["sid"])
    game = EpigramGame(socketio, connected_players[game_id], host_sid=game_hosts[game_id])
    game.run_game()

# Additional SocketIO events for game logic here...

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)