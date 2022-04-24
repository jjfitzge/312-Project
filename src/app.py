from flask import Flask, render_template, request
import os

#t_dir = os.path.abspath('./html')
app = Flask(__name__, template_folder='./html')



@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('index.html')


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
            pass
        else:
            return render_template('register.html')
        # if not then, take them back to the page to try and register again
        # try divs that are hidden




@app.route('/mainpage')
def return_news():
    return render_template('mainpage.html')


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 5000
    app.run(HOST, PORT)
