from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from logic import QuiplashGame

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/host')
def host():
    return render_template('host.html')  # Host page

@app.route('/client')
def client():
    return render_template('client.html')  # Client/player page

@socketio.on('connect')
def handle_connect():
    print("A new player has connected.")
    # Here you can perform actions needed when a new player connects
    # For example, sending a welcome message
    emit('welcome_message', {'message': 'Welcome to the game!'})

connected_players = {}

@socketio.on('register_player')
def handle_player_registration(data):
    player_name = data['name']
    session_id = request.sid
    print(f"Player {player_name} has joined the game with session ID {session_id}.")
    connected_players[session_id] = []

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    if session_id in connected_players:
        player_name = connected_players[session_id]
        print(f"Player {player_name} has disconnected.")
        # Remove player from the list
        del connected_players[session_id]

# Additional SocketIO events for game logic here...

if __name__ == '__main__':
    socketio.run(app)