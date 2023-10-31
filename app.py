from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

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

if __name__ == "__main__":
    socketio.run(app, debug=True)

@socketio.on('submit_answer')
def handle_submit_answer(data):
    player_answers[data['username']] = data['answer']

@socketio.on('request_next_question')
def handle_next_question():
    if questions:
        question = questions.pop(0)
        socketio.emit('show_question', {'question': question})

@socketio.on('new_question')
def handle_new_question(data):
    socketio.emit('show_question', data)

# # FOR USE IN JAVASCRIPT
# // Emit new question
# socket.emit('new_question', { question: 'The worst pizza topping ever invented' });

# // Listen for new question
# socket.on('show_question', function(data) {
#   document.getElementById('question').innerHTML = data.question;
# });