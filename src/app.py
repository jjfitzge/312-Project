from flask import Flask, render_template, request, make_response
from flask_socketio import SocketIO, emit, send
import random


#t_dir = os.path.abspath('./html')
app = Flask(__name__, template_folder='./html')
socketio = SocketIO(app)


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('index.html')


@app.route('/mainpage')
def return_news():
    userID = request.cookies.get("ID")
    return render_template('mainpage.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == "POST":
        jsonData = request.form
        # username -> "user"
        # password -> "pass"
        # password2 -> "pass2"
        print(jsonData)
        user = jsonData
        username = jsonData.get('user')
        password = jsonData.get('pass')
        pass2 = jsonData.get('pass2')
        print(username, password, pass2)
        # if the passwords are equal then let them create the account and sign in
        if password == pass2:
            # Log in and save info to Database
            response = make_response(render_template('mainpage.html'))
            # Randomly generate ID until database implemented
            userID = "User" + str(random.randint(0, 1000))
            response.set_cookie("ID", userID)
            return response
        else:
            return render_template('register.html')
        # if not then, take them back to the page to try and register again
        # try divs that are hidden


@socketio.on('connect')
def test_connect():
    emit('connected', "TestUsername")


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 8000
    socketio.run(app, HOST, PORT)
