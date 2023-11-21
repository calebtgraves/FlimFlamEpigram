from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'some_secret'

rooms = {}

player_answers = {}
questions = ["The worst pizza topping ever invented", "A rejected Olympic sport; Synchronized _____."]

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/host')
def host():
    return render_template('host.html')

@app.route('/player')
def player():
    return render_template('player.html')

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    rooms[room] = rooms.get(room, [])
    rooms[room].append(data['name'])

@socketio.on('submit_answer')
def handle_submit_answer(data):
    player_answers[data['username']] = data['answer']

@socketio.on('request_next_question')
def handle_next_question():
    if questions:
        question = questions.pop(0)
        socketio.emit('show_question', {'question': question})

if __name__ == "__main__":
    socketio.run(app, debug=True)

# # FOR USE IN JAVASCRIPT
## HOST.js
# var socket = io.connect('http://' + document.domain + ':' + location.port);
# var room = "your_generated_room_id"; // Should come from your Flask backend
# socket.emit('join', {room: room, name: 'host'});

# PLAYER.js
# var socket = io.connect('http://' + document.domain + ':' + location.port);
# var room = "your_generated_room_id"; // Should come from user input
# function joinGame() {
#     var name = document.getElementById("playerName").value;
#     socket.emit('join', {room: room, name: name});
# }