from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from logic import QuiplashGame
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

MAX_PLAYERS = 8
MIN_PLAYERS = 3

game_id = None

## Reference Dictionaries ##
connected_players = {} # keys are game id, values are player info
vips = {} # VIPs of each game id by session id (for emitting to VIPs)
game_hosts = {} # Game id as key, host's session id as value

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
    global game_id
    game_id = get_letters(4)
    session_id = request.sid
    game_hosts[game_id] = session_id
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
    game_id = data['id']
    session_id = request.sid
    if game_id in connected_players:
        if len(connected_players[game_id]) < MAX_PLAYERS:
            connected_players[game_id].append({'name': player_name, 'vip': False, 'sid': session_id})
            if len(connected_players[game_id]) == MIN_PLAYERS:
                emit('min_reached', room=vips[game_id])
            print(f"Player {player_name} has joined the game with ID {game_id}.")
        else:
            print(f"Player {player_name} could not join: {MAX_PLAYERS} players are already connected.")
        emit('new_player', {'name': player_name, 'vip': False}, room=game_hosts[game_id]) # Send player name to host
    else:
        connected_players[game_id] = [{'name': player_name, 'vip': True, 'sid': session_id}]
        vips[game_id] = session_id
        emit('vip')
        emit('new_player', {'name': player_name, 'vip': True}, room=game_hosts[game_id]) # Send VIP player name to host

@socketio.on('disconnect')
def handle_disconnect(data):
    session_id = data.sid
    if session_id in connected_players:
        player_name = connected_players[session_id]
        print(f"Player {player_name} has disconnected.")
        # Remove player from the list
        del connected_players[session_id]

@socketio.on('start_game')
def start_game():
    game = QuiplashGame(connected_players[game_id], host_sid=game_hosts[game_id])
    game.run_game()

# Additional SocketIO events for game logic here...

if __name__ == '__main__':
    socketio.run(app)