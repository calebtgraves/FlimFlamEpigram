from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from logic import QuiplashGame
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

## Constants ##
MAX_PLAYERS = 8
MIN_PLAYERS = 3
COLORS = ["#c93838","#c99438","#c9b838","#68c938","#38c9c9","#3874c9","#9638c9","#c9389e"] #List of possible player colors as hex codes

## Reference Dictionaries ##
connected_players = {} # keys are game id, values are player info
vips = {} # VIPs of each game id by session id (for emitting to VIPs)
game_hosts = {} # Game id as key, host's session id as value
colors_available = {} #Stores per game what player colors have not been assigned; keys are game ids, values are lists of colors.

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
    player_color = colors_available[game_id].pop() #Assign a color to a player whilst removing it from the list so no other players can have it.
    if game_id in connected_players:
        if len(connected_players[game_id]) < MAX_PLAYERS:
            connected_players[game_id].append({'name': player_name, 'vip': False, 'sid': session_id})
            if len(connected_players[game_id]) == MIN_PLAYERS:
                emit('min_reached', room=vips[game_id])
            print(f"Player {player_name} has joined the game with ID {game_id}.")
        else:
            print(f"Player {player_name} could not join: {MAX_PLAYERS} players are already connected.")
        emit('new_player', {'name': player_name, 'vip': False,'color':player_color}, room=game_hosts[game_id]) # Send player name to host
        emit('color',player_color,room=session_id)
    else:
        connected_players[game_id] = [{'name': player_name, 'vip': True, 'sid': session_id, 'color':player_color}]
        vips[game_id] = session_id
        emit('vip')
        emit('new_player', {'name': player_name, 'vip': True, 'color':player_color}, room=game_hosts[game_id]) # Send VIP player name to host
        emit('color',player_color,room=session_id)

@socketio.on('disconnect')
def handle_disconnect(data):
    session_id = data.sid
    if session_id in connected_players:
        player_name = connected_players[session_id]
        print(f"Player {player_name} has disconnected.")
        # Remove player from the list
        del connected_players[session_id]

@socketio.on('start_game')
def start_game(game_id):
    game_id = game_id.upper()
    game = QuiplashGame(connected_players[game_id], host_sid=game_hosts[game_id])
    game.run_game()

# Additional SocketIO events for game logic here...

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)