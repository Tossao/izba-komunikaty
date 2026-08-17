import os
from functools import wraps
from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'izba_przyjec_secret_123')
socketio = SocketIO(app, cors_allowed_origins="*")

PANEL_USERNAME = os.environ.get('PANEL_USER', 'admin')
PANEL_PASSWORD = os.environ.get('PANEL_PASS', 'szpital123')

# Zmienna przechowująca aktualnego lekarza
current_doctor = ""

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
    emit('update_tv', data, broadcast=True)

@socketio.on('connect')
def handle_connect():
    # Przy połączeniu wysyłamy aktualnego lekarza do nowego klienta (TV lub Panel)
    emit('update_doctor', {'doctor': current_doctor})

@socketio.on('change_doctor')
def handle_change_doctor(data):
    global current_doctor
    current_doctor = data.get('doctor', '')
    # Rozsyłamy nową wartość do wszystkich połączeń
    emit('update_doctor', {'doctor': current_doctor}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
