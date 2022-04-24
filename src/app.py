from flask import Flask, render_template, request
import os
from pymongo import MongoClient

#t_dir = os.path.abspath('./html')
app = Flask(__name__, template_folder='./html')



@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # if successful, mongodb_signedin flag set to one. 
        # if password = jsonData.get('pass').sha256() == mongodb.thatusername.hashpassword() 
        #   then allow them to login 
        return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == "POST":
        jsonData = request.form
        profileImg = request.files['profile']
        # username -> "user"
        # if username exists in the mongoDB break and ask them to make a new one.
        # if not continue with registration process, at line 43
        # password -> "pass"
        # password2 -> "pass2"
        print(jsonData)
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
        
        # hash that password, insert it into mongodb. 
        # 




@app.route('/mainpage')
def return_news():
    return render_template('mainpage.html')


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 5000
    app.run(HOST, PORT)
