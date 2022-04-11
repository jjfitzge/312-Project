from flask import Flask, render_template, request
import os

#t_dir = os.path.abspath('./html')
app = Flask(__name__, template_folder='./html')


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('index.html')


@app.route('/mainpage')
def return_news():
    return render_template('mainpage.html')


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 8000
    app.run(HOST, PORT)
