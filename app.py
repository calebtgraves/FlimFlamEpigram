from flask import Flask, render_template
from flask_socketio import SocketIO
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
    # Handle new connection
    pass

# Additional SocketIO events for game logic here...

if __name__ == '__main__':
    socketio.run(app)