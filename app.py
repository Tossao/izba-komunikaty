import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'izba_przyjec_secret_123'
socketio = SocketIO(app, cors_allowed_origins="*")

# Domyślny stan ekranu
current_state = {
    "message": "PROSZĘ OCZEKIWAĆ NA WEZWANIE",
    "is_active": False
}

@app.route('/')
@app.route('/panel')
def panel():
    return render_template('panel.html')

@app.route('/tv')
def tv():
    return render_template('tv.html')

@socketio.on('send_message')
def handle_message(data):
    # data = {'text': 'ZAPRASZAM DO GABINETU NR 1', 'duration': 15}
    emit('update_tv', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)