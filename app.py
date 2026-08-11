import os
from functools import wraps
from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'izba_przyjec_secret_123')
socketio = SocketIO(app, cors_allowed_origins="*")

# Domyślny login i hasło do panelu (można też zmienić w zmiennych środowiskowych na Renderze)
PANEL_USERNAME = os.environ.get('PANEL_USER', 'admin')
PANEL_PASSWORD = os.environ.get('PANEL_PASS', 'szpital123')

def check_auth(username, password):
    return username == PANEL_USERNAME and password == PANEL_PASSWORD

def authenticate():
    return Response(
        'Wymagana autoryzacja do dostępu do panelu.', 401,
        {'WWW-Authenticate': 'Basic realm="Dostep tylko dla personelu"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
        return decorated

# Domyślny stan ekranu
current_state = {
    "message": "PROSZĘ OCZEKIWAĆ NA WEZWANIE",
    "is_active": False
}

@app.route('/')
@app.route('/panel')
@requires_auth
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
