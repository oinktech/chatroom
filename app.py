from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_socketio import SocketIO, emit, join_room
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 用户存储
users = {}
messages = defaultdict(list)

class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

@login_manager.user_loader
def load_user(username):
    return users.get(username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('此用户名已被注册，请选择其他用户名。', 'error')
        else:
            users[username] = User(username, password)
            flash('注册成功，请登录。', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误，请重试。', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功登出！', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/chat/<chat_mode>', methods=['GET', 'POST'])
@login_required
def chat(chat_mode):
    if request.method == 'POST':
        message = request.form['message']
        if message:
            messages[chat_mode].append((current_user.username, message))
            socketio.emit('new_message', {'user': current_user.username, 'message': message}, room=chat_mode)
    return render_template('chat.html', chat_mode=chat_mode, messages=messages[chat_mode])

@socketio.on('join')
def on_join(chat_mode):
    join_room(chat_mode)

@socketio.on('send_message')
def handle_message(data):
    messages[data['chat_mode']].append((current_user.username, data['message']))
    emit('new_message', {'user': current_user.username, 'message': data['message']}, room=data['chat_mode'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000, debug=True)
