from email import header
from importlib.resources import path
import json

from flask import redirect
from . import response, database, request, template, authentication, cookies, websocket
from bson import json_util
import random


storage = []
storage_tokens = []
users = {}
users_tokens = {}
chat_history = {}
user_connections = {}
websocket_connections = {}
users_ws = {}

# b'\r\n\r\nusername=hello&password=there'


def getUserInfo(body: bytes):
    body = body.decode().strip()
    idxUser = body.find("username=") + len("username=")
    idxPass = body.find("password=")
    username = body[idxUser: idxPass - len("&")]
    password = body[idxPass + len("password="):]
    return [username, password]
# Keep collection of currently logged in users


online_users = {}
online_users_id = {}

# DS for DM's
# Username -> user's open DM object
open_dms = {}
toUserDict = {}


def route_path(data, handler):
    request_dict = request.new_parse(data)
    path, img_src, type, body, user_id, headers = request_dict["path"], request_dict.get(
        "img_path"), request_dict["request_type"], request_dict.get("body"), request_dict.get("user_path"), request_dict.get("header")
    if path == "/":
        # return get_html(headers)
        if type == "GET":
            print('---------------requestDict----------')
            print(request_dict)
            print('++++++++++++++++++++++++++++++++++++')
            cookie = headers.get("Cookie", "")
            if cookie != "":
                print(cookie)
                auth_token = cookie.split("=")[1]
                print("Auth-Token", auth_token)
                # if auth-token in database send the chatpage
                userInfo = database.getUser(auth_token)
                if userInfo != "":
                    return get_html_file("/src/html/chatpage.html", headers)
            return get_html_file("/src/html/index.html", headers)
        if type == "POST":
            print("body---Body-------", body)
            userInfo = getUserInfo(body)
            print(userInfo)
            username = userInfo[0]
            password = userInfo[1]
            print(storage)
            if {"username": username, "password": password} in storage:
                # if database.check_user(username, password):
                auth_token = authentication.gen_authToken()
                # database.create_authToken(username, auth_token)
                # add username cookie
                user_cookie = cookies.set_cookie("Username=%s" % username)
                # the above add the token to db with key "authToken"
                cookie = cookies.set_cookie(
                    "Auth-Token=%s" % auth_token, options='; HttpOnly')
                hashedToken = authentication.get_saltedhash(auth_token)[
                    "saltedhash"]
                storage_tokens.append({"authToken": hashedToken})
                contentType = "text/html; charset=utf-8\r\nX-Content-Type-Options:nosniff" + \
                    cookie + user_cookie
                body = get_body("./src/html/chatpage.html")
                return response.get_response(body, "200 OK", contentType)
                # return get_html_file("/src/html/chatpage.html", cookie)
                # send the http request of the chatpage, and set auth-token cookie
            else:
                return get_html_file("/src/html/index.html", headers)
    elif path == "/static/styles/index.css":
        return get_css(path)
    elif path == "src/html/register.html":
        return get_html_file(path, headers)
    elif path == "/static/styles/chatpage.css":
        return get_css(path)
    elif path == "/static/scripts/sidebar.js":
        return get_js(path)
    elif path == "/static/styles/sidebar.css":
        return get_css(path)
    elif path == "/static/scripts/sidebar.js":
        return get_js(path)
    elif path == "/src/html/chatpage.html":
        return get_html_file(path, headers)
    elif path == "/register":
        if type == "GET":
            return get_html_file("/src/html/register.html", headers)
        elif type == "POST":
            d = request_dict["multi-part"].values()
            print("HEADINGGGGGGGGG", d) 
            user = ""
            password = ""
            password2 = ""
            imagePath = ""
            for dic in d:
                if dic['heading']['name'] == "user":
                    user = dic['body']
                if dic['heading']['name'] == "pass":
                    password = dic['body']
                if dic['heading']['name'] == "pass2":
                    password2 = dic['body']
                if dic['heading']['name'] == "upload":
                    imagePath = user_upload(request_dict["multi-part"])
                userInfo = {"user": user, "pass": password, "pass2": password2, "imagePath" : imagePath}
                print( "UserInfo__________",userInfo)
                if userInfo["user"] != "" and userInfo["pass"] != "" and userInfo["pass2"] != "":
                    if userInfo["pass"] == userInfo["pass2"]:
                        response_code = '301 Moved Permanently'
                    body = b''
                    content_type = 'text/plain; charset=utf-8\r\nLocation: /'
                    storage.append({"username": user, "password": password})
                    print("storage in register", storage)
                    # database.create_user(userInfo['user'], userInfo["pass"])
                    return response.get_response(body, response_code, content_type)
            response_code = '301 Moved Permanently'
            body = b''
            content_type = 'text/plain; charset=utf-8\r\nLocation: /register'
            return response.get_response(body, response_code, content_type)

            pass
            # return register(d)
    elif path == "/chat":
        return get_html_file("/src/html/chatpage.html", headers)
    elif path == "/static/scripts/chat.js":
        return get_js(path)
    elif path == "/style.css":
        return get_css()
    elif path == "/functions.js":
        return get_js()
    elif path == "/static/images/favicon.ico":
        return get_icon()
    elif path == "/hello":
        return hello()
    elif path == "/hi":
        return hi()
    elif path == "/static/images":
        # Security: Sanitize path
        img_src = img_src.replace('/', '')
        # print(img_src)
        if img_src == "-upload":
            return user_upload(request_dict["multi-part"])
        else:
            return get_img('/'+img_src, img_src[len(img_src)-3:])
    elif path == "/image-upload":
        return user_upload(request_dict["multi-part"])
    elif path == "/online-users":
        return get_online_users()
    elif path == "/dm":
        print("Trying to get dm page")
        return get_html_file("/src/html/dm.html", headers)
    elif path == "/redirectdm":
        return redirect_dm()
    elif path == "/open-dms":
        return get_dm_history(headers)
    elif path == "/dm-to":
        return get_toUser(headers)
    elif path == "/static/scripts/dm.js":
        return get_js(path)
    elif path == "/static/styles/dm.css":
        return get_css(path)
    elif path == "/users":
        if type == "GET":
            return retrieve_all()
        elif type == "POST":
            return create(body)
        else:
            return four_o_four()
    elif path == "/users/":
        if type == "GET":
            return retrieve(user_id)
        elif type == "PUT":
            return update(user_id, body)
        elif type == "DELETE":
            return delete(user_id)
        else:
            return four_o_four()
    elif path == "/signup":
        return signup(request_dict["multi-part"])
    elif path == "/login":
        return login(request_dict["multi-part"])
    elif path == "/userchat":
        return chat(request_dict["multi-part"], headers)
    elif path == "/websocket":
        return websocket_upgrade(request_dict["header"]["Sec-WebSocket-Key"], handler, headers)
    else:
        return four_o_four()


def get_body(filename):
    valid_files = ['./src/static/images/favicon.ico', './src/static/images/hero.jpg', './src/static/images/walrusicon.png', './src/static/images/walruslogo.png', './src/static/scripts/chat.js', './src/static/scripts/sidebar.js', './src/static/styles/chatpage.css', './src/static/styles/index.css',
                   './src/static/styles/sidebar.css', './src/static/svgs/arrow-right-from-bracket.svg', '/src./static/svgs/gear.svg', './src/static/svgs/inbox.svg', './src/static/svgs/message.svg', './src/static/svgs/paper-plane.svg', './src/static/svgs/square-caret.svg', './src/static/svgs/video.svg', './src/html/chatpage.html', './src/html/index.html', './src/html/loginpage.html', './src/html/mainpage.html', './src/html/register.html', './src/html/dm.html', './src/static/scripts/dm.js', './src/static/styles/dm.css']
    # Comment out Database
    # valid_files += database.list_img()
    # print(filename)
    # print(valid_files)
    if filename in valid_files:
        # print("the file is valid")
        with open(filename, 'rb') as data:
            return data.read()
    else:
        # print("the file is invalid")
        return False


def hello():
    body = b'Welcome!'
    return response.get_response(body)


def hi():
    response_code = '301 Moved Permanently'
    body = b''
    content_type = 'text/plain; charset=utf-8\r\nLocation: /hello'
    return response.get_response(body, response_code, content_type)


def four_o_four():
    response_code = '404 Not Found'
    body = b'Content was not found'
    return response.get_response(body, response_code)


def four_hundred():
    response_code = '400 Bad Request'
    body = b'Bad Request'
    return response.get_response(body, response_code)


def get_html_file(path, headers):
    body: bytes = get_body('.'+path)
    content_type = 'text/html; charset=utf-8\r\nX-Content-Type-Options: nosniff'
    return response.get_response(body, content_type=content_type)


def get_html(headers):
    # data = [{"comment": "hello", "img": "kitten.jpg"}, {"comment": "hi",
    # "img": "kitten.jpg"}, {"comment": "hey", "img": "kitten.jpg"}]
    #data = database.list_msg()

    # Check Headers dictionary for cookies
    cookies = headers.get('Cookie', '')
    # print("Cookies: ", cookies)
    visits = 1
    auth = False
    username = ''
    if cookies.find("visits=") != -1:
        visits = int(cookies[cookies.find("visits=")+len("visits=")]) + 1
        if cookies.find("auth-token=") != -1:
            authToken = cookies[cookies.find(
                "auth-token=")+len("auth-token="):]
            authToken = authToken[:authToken.find(';')]
            username = cookies[cookies.find("username=")+len("username="):]
            if username.find(';') != -1:
                username = username[:username.find(';')]
            # print(username)
            #username = username[:username.find(';')]
            # print(username)
            print("username: ", username)
            print("AuthToken: ", authToken)
            # Check for valid auth token
            print("-------------------444444444------------------------")
            #auth = database.check_token(username, authToken)

            print("Auth value: ", auth)
            print("------------------444444444444----------------------")
            # --- For Local Testing only ---
            if username in users_tokens.keys():
                print(users_tokens)
                if users_tokens[username]["saltedhash"] == authentication.check_salt(authToken, users_tokens[username]["salt"]):
                    auth = True
                    print("authenticated")
    # Get chat messages from database
    if len(chat_history) > 0:
        print("====Serving Chat History====")
        body: bytes = bytes(template.render_template(
            './chatindex.html', chat_history, None, visits), 'utf-8')
        if auth:
            user_token = response.get_token(username)
            body: bytes = bytes(template.render_template(
                './chatlogin.html', chat_history, user_token, visits, username), 'utf-8')
        content_type = 'text/html; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nSet-Cookie: visits='
        content_type += str(visits) + '; Max-Age=3600'
        #print("Content Type", content_type)
        #print(response.get_response(body, content_type=content_type))
        return response.get_response(body, content_type=content_type)
    else:
        body: bytes = bytes(template.render_template(
            './index.html', None, None, visits), 'utf-8')
        if auth:
            user_token = response.get_token(username)
            body: bytes = bytes(template.render_template(
                './login.html', None, user_token, visits, username), 'utf-8')
        content_type = 'text/html; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nSet-Cookie: visits='
        content_type += str(visits) + '; Max-Age=3600'
        #print("Content Type", content_type)
        #print(response.get_response(body, content_type=content_type))
        return response.get_response(body, content_type=content_type)


def get_css(path):
    body: bytes = get_body('./src'+path)
    content_type = 'text/css; charset=utf-8\r\nX-Content-Type-Options: nosniff'
    return response.get_response(body, content_type=content_type)


def get_js(path):
    body: bytes = get_body('./src'+path)
    content_type = 'text/javascript; charset=utf-8\r\nX-Content-Type-Options: nosniff'
    return response.get_response(body, content_type=content_type)


def get_icon():
    body: bytes = get_body('./src/static/images/favicon.ico')
    content_type = '"image/x-icon"; charset=utf-8\r\nX-Content-Type-Options: nosniff'
    return response.get_response(body, content_type=content_type)


def get_img(img_path, type):
    body: bytes = get_body('./src/static/images'+img_path)
    if body == False:
        return four_hundred()
    else:
        if type == 'jpg':
            type = 'jpeg'
        content_type = 'image/' + type + '; charset=utf-8\r\nX-Content-Type-Options: nosniff'
        return response.get_response(body, content_type=content_type)


def retrieve_all():
    retval = database.list_entry(database.user_collection)
    return response.get_response(json_util.dumps(retval).encode())


def create(entry):
    dict = json.loads(entry)
    retval = database.create_entry(
        database.user_collection, dict["email"], dict["username"])
    return response.get_response(json_util.dumps(retval).encode(), '201 Created')


def retrieve(given_id):
    dict = database.retrieve(database.user_collection, int(given_id))
    if dict != False:
        return response.get_response(json_util.dumps(dict).encode(), '200 OK')
    else:
        return four_o_four()


def update(id, entry):
    dict = json.loads(entry)
    ret_dict = database.update(database.user_collection, int(
        id), dict["email"], dict["username"])
    if ret_dict != False:
        return response.get_response(json_util.dumps(ret_dict).encode(), '200 OK')
    else:
        return four_o_four()


def delete(id):
    retval = database.delete(database.user_collection, int(id))
    body = b''
    response_code = '204 No Content'
    if retval:
        return response.get_response(body, response_code)
    else:
        return four_o_four()


def user_upload(formdata):
    comment = ""
    """ img_path = 'picture' + \
        str(database.get_id(database.img_count_collection)+1)+'.jpg' """
    img_path = 'picture' + str(random.randint(0, 1000))
    valid_token = False
    for data in formdata.values():
        if len(data) != 0:
            data_heading = data["heading"]
            if len(data_heading) == 0:
                continue
            if data_heading["name"] == "comment":
                comment = data["body"]
            elif data_heading["name"] == "upload":
                with open('./src/static/profiles/'+img_path+'.jpg', 'wb') as f:
                    f.write(data["body"])
    #database.create_msg(comment, img_path)
    # response_code = '301 Moved Permanently'
    # body = b''
    # content_type = 'text/plain; charset=utf-8\r\nLocation: /'
    # return response.get_response(body, response_code, content_type)
    return './src/static/profiles/'+img_path+'.jpg'
    """ else:
        response_code = '403 Forbidden'
        body = b'request was rejected'
        return response.get_response(body, response_code) """


def signup(formdata):
    # valid_token = False
    username = ''
    password = ''
    for data in formdata.values():
        if len(data) != 0:
            data_heading = data["heading"]
            if len(data_heading) == 0:
                continue
            if data_heading['name'] == "username":
                username = data["body"]
            elif data_heading['name'] == "password":
                password = data["body"]

    #database.create_msg(comment, img_path)
    # Store username in database
    database.create_user(username, password)
    # --- For Local Testing Only ---
    #salt_dict = authentication.get_saltedhash(password)
    #salted_pass = salt_dict["saltedhash"]
    #print("username: ", username)
    #print("password: ", salted_pass)
    #global users
    #users[username] = salt_dict

    response_code = '301 Moved Permanently'
    body = b''
    content_type = 'text/plain; charset=utf-8\r\nLocation: /'
    return response.get_response(body, response_code, content_type)


def login(formdata):
    valid_token = False
    username = ''
    password = ''
    for data in formdata.values():
        if len(data) != 0:
            data_heading = data["heading"]
            if len(data_heading) == 0:
                continue
            if data_heading['name'] == "username":
                username = data["body"]
            elif data_heading['name'] == "password":
                password = data["body"]
    # Store username in database
    auth = database.check_user(username, password)
    #auth = False

    #print("users dictionary: ", users)
    #print("got salted_pass: ", salted_pass)
    # --- For Local Testing Only ---
    """ if username in users.keys():
        print("username: ", username)
        print("password: ", users[username])
        salted_pass = authentication.check_salt(
            password, users[username]["salt"])
        if users[username]["saltedhash"] == salted_pass:
            print("Authenticated")
            auth = True """

    if auth:
        # Generate Authentication Token
        token = authentication.gen_authToken()
        # Store hashed token in database
        database.create_authToken(username, token)
        # ---This is for local testing---
        """ salted_token = authentication.get_saltedhash(token)
        users_tokens[username] = salted_token
        print("Users w/ Tokens", users_tokens) """
        # -----------------------------------
        # Add original token as a cookie
        cookie = cookies.set_cookie(
            "auth-token="+token, options='; HttpOnly')
        username_cookie = cookies.set_cookie(
            "username="+username, options='; HttpOnly')
        # print(cookie)
        # print(username_cookie)
        response_code = '301 Moved Permanently'
        body = b''
        content_type = 'text/plain; charset=utf-8\r\nLocation: /'
        content_type += cookie
        content_type += username_cookie
        # print(content_type)
        return response.get_response(body, response_code, content_type)
    else:
        response_code = '403 Forbidden'
        body = b'request was rejected'
        return response.get_response(body, response_code)


def chat(formdata, headers):
    cookies = headers.get('Cookie')
    print("=======Cookies: ", cookies)
    auth = False
    username = ''
    valid_token = False
    comment = ''

    if cookies.find("visits=") != -1:
        if cookies.find("auth-token=") != -1:
            authToken = cookies[cookies.find(
                "auth-token=")+len("auth-token="):]
            authToken = authToken[:authToken.find(';')]
            username = cookies[cookies.find("username=")+len("username="):]
            print(username)
            #username = username[:username.find(';')]
            # print(username)
            print("username: ", username)
            print("AuthToken: ", authToken)
            # Check for valid auth token
            auth = database.check_token(username, authToken)
            # --- For Local Testing only ---
            """ if username in users_tokens.keys():
                print(users_tokens)
                if users_tokens[username]["saltedhash"] == authentication.check_salt(authToken, users_tokens[username]["salt"]):
                    auth = True
                    print("authenticated") """
    for data in formdata.values():
        # print(data)
        if len(data) != 0:
            data_heading = data["heading"]
            # print(data_heading)
            if len(data_heading) == 0:
                continue
            if data_heading['name'] == "comment":
                comment = data["body"]
            if data_heading["name"] == "xsrf_token":
                # check the token with our stored to see if match
                if data["body"] == response.xsrf_token[username]:
                    valid_token = True

    if auth and valid_token:
        # Add chat message to record
        chat_history[username] = comment
        print("Chat History", chat_history)
        response_code = '301 Moved Permanently'
        body = b''
        content_type = 'text/plain; charset=utf-8\r\nLocation: /'
        return response.get_response(body, response_code, content_type)
    else:
        response_code = '403 Forbidden'
        body = b'request was rejected'
        return response.get_response(body, response_code)


def websocket_upgrade(headers, handler, request_header):
    print("sending websocket upgrade request")
    # print(headers)
    accept = websocket.generate_accept(headers)
    # print("accept", accept)
    response_code = '101 Switching Protocols'
    content_type = b'Connection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept: ' + accept
    body = b''
    # print("getting response")
    gen_response = response.get_handshake(body, response_code, content_type)
    print(gen_response)
    """ lobal count
    count += 1 """
    # print(count)
    cookies = request_header.get('Cookie', '')
    username = cookies[cookies.find("Username=")+len("Username="):]
    if username.find(';') != -1:
        username = username[:username.find(';')]
    print("Got the Username:", username)
    #username = "User" + str(random.randint(0, 1000))
    # Check if username is already in the dS and remove it
    if user_connections.get(username):
        print("found duplicates")
        user_connections.pop(username)
        key = {
            x for x in websocket_connections if websocket_connections[x] == username}
        websocket_connections.pop(key[0])

    user_connections[username] = handler
    #users[username] = handler
    websocket_connections[handler] = username
    # Retrieve users info
    print("==USER CONNECTIONS==")
    print(user_connections)
    print("-------------------------")
    print("==Websocket Connections==")
    print(websocket_connections)
    print("------------------------------")
    return gen_response
    #global websocket_connections
    #websocket_connections.append({'Socket': handler, 'Username': username})


def retrieve_messages():
    retval = database.list_chat()
    print("retrieved messages", retval)
    print(response.get_response(json_util.dumps(retval).encode(),
          content_type='application/json; charset=utf-8'))
    return response.get_response(json_util.dumps(retval).encode(), content_type='application/json; charset=utf-8')


def register(information):
    user = ""
    password = ""
    password2 = ""
    print(information)
    if len(information.values()) > 1:
        for dic in information.values():
            print("dcitionary",dic)
            # if dic['heading']['name'] == "user":
            #     user = dic['body']
            # if dic['heading']['name'] == "pass":
            #     password = dic['body']
            # if dic['heading']['name'] == "pass2":
            #     password2 = dic['body']
        userInfo = {"user": user, "pass": password, "pass2": password2}
        print( "UserInfo__________",userInfo)
        if userInfo["user"] != "" and userInfo["pass"] != "" and userInfo["pass2"] != "":
            if userInfo["pass"] == userInfo["pass2"]:
                response_code = '301 Moved Permanently'
            body = b''
            content_type = 'text/plain; charset=utf-8\r\nLocation: /'
            storage.append({"username": user, "password": password})
            print("storage in register", storage)
            # database.create_user(userInfo['user'], userInfo["pass"])
            return response.get_response(body, response_code, content_type)
    response_code = '301 Moved Permanently'
    body = b''
    content_type = 'text/plain; charset=utf-8\r\nLocation: /register'
    return response.get_response(body, response_code, content_type)


def get_online_users():
    retval = list(online_users.values())
    print(retval)
    print(type(retval))
    print(json_util.dumps(retval).encode())
    return response.get_response(json_util.dumps(retval).encode(), '200 OK')


def redirect_dm():
    response_code = '301 Moved Permanently'
    body = b''
    content_type = 'text/plain; charset=utf-8\r\nLocation: /dm'
    return response.get_response(body, response_code, content_type)


def get_dm_history(request_header):
    # from DS get the specfied user's collection
    print(websocket_connections)
    cookies = request_header.get('Cookie', '')
    username = cookies[cookies.find("Username=")+len("Username="):]
    if username.find(';') != -1:
        username = username[:username.find(';')]
    print("Got the Username:", username)
    print("username", username)
    print(open_dms)
    return response.get_response(json_util.dumps(open_dms[username]).encode(), '200 OK')


def get_toUser(request_header):
    cookies = request_header.get('Cookie', '')
    username = cookies[cookies.find("Username=")+len("Username="):]
    if username.find(';') != -1:
        username = username[:username.find(';')]
    return response.get_response(json_util.dumps(toUserDict[username]).encode(), '200 OK')
