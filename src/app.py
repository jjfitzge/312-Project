from flask import Flask, render_template, request
import os
import html
from flask_socketio import SocketIO, emit, send
import json

#t_dir = os.path.abspath('./html')
app = Flask(__name__, template_folder='./html')
socketio = SocketIO(app)


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('index.html')


@app.route('/mainpage')
def return_news():
    return render_template('mainpage.html')


def check_str_for_safety(string):
    retstr = html.escape(string)
    return retstr


@socketio.on('connect')
def test_connect():
    emit('connected', "TestUsername")


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 8000
    socketio.run(app, HOST, PORT)
