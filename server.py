from flask import Flask, request, session, redirect, url_for, render_template
import user_account_system
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
app.secret_key = 'replace_this_with_a_random_string'

user_system = user_account_system.UserAccountSystem('database.db')

# Function to run when the app starts up
@app.before_first_request
def on_startup():
    print('Server is online. Sending message to all clients.')
    # Here you can add code to send a message to all clients. For example:
    
    socketio = SocketIO(app)
    socketio.emit('server_online', {'data': 'Server is online!'}, broadcast=True)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html',user=session['username'],logtype="signout",dash="dash")
    else:
        return render_template('index.html',user="anonymous user",logtype="signup")
    
@app.route('/server_status')
def server_status():
    if 'username' in session:
        return {'status': 'online'}
    else:
        return {'status': 'offline'}


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(len(username)>=8)
        print(len(password)>=8)
        if user_system.register_user(username, password) and len(username)>=4 and len(password)>=8:
            return redirect(url_for('login'))
        else:
            return render_template('signup.html',message="Error. Check your inputs. password must be more than 8 characters")
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_system.authenticate_user(username, password) and len(username)>=4 and len(password)>=8:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html',message='Invalid username or password!')
    else:
        return render_template('login.html')

@app.route('/signout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html',user=session['username'],logtype="signout",dash="dash",password="*********")
    else:
        return render_template('dashboard.html',user="anonymous user",logtype="signup")


@app.route('/update-username', methods=['POST'])
def update_username():
    if 'username' in session:
        new_username = request.json['username']
        user_system.update_username(session['username'], new_username)
        session['username'] = new_username
        return 'OK'
    else:
        return 'Unauthorized', 401
    
@app.route('/update-password', methods=['POST'])
def update_password():
    if 'username' in session:
        new_password = request.json['password']
        user_system.update_password(session['username'], new_password)
        return 'OK'
    else:
        return 'Unauthorized', 401


if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)