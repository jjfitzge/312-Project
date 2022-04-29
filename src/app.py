from ast import parse
import socketserver
from typing import List
import httpString as hP

# variables for type of requests
code101 = "101 Switching Protocols"
code200 = "200 OK"
code201 = "201 Created"
code204 = "204 No Content"
code301 = "301 Moved Permanently"
code304 = "304 Not Modified"
code403 = "403 Forbidden"
code404 = "404 Not Found"
code500 = "500 Internal Server Error"

# variables for MIME types
plain = "text/plain"
html = "text/html"
css = "text/css"
js = "text/javascript"
png = "image/png"
jpg = "image/jpeg"
ico = "image/x-icon"
mp4 = "video/mp4"
MiMEjson = "application/json"
multiPart = "multipart/form-data"

class MyTcpHandler(socketserver.BaseRequestHandler):

    def handle(self):

        received_data = self.request.recv(1024)
        request: List[str] = requestParse(received_data.decode())
        print("------Request Begins")
        print(request)
        if isGET(request):
            if getPath(request) == "/":
                self.request.sendall(hP.fileHttpString(code200,"src/html/index.html",html))
            elif getPath(request) == "/static/styles/index.css":
                self.request.sendall(hP.fileHttpString(code200, "src/static/styles/index.css", css))
            elif getPath(request) == "/static/images/hero.jpg":
                self.request.sendall(hP.imageHttpString("src/static/images/hero.jpg"))
            elif getPath(request) == "/register":
                self.request.sendall(hP.fileHttpString(code200, "src/html/register.html", html))
            elif getPath(request) == "/static/images/favicon.ico":
                self.request.sendall(hP.imageHttpString("src/static/images/favicon.ico"))
            elif getPath(request) =="/static/images/walrusicon.png":
                self.request.sendall(hP.imageHttpString("src/static/images/walrusicon.png"))
            elif getPath(request) == "/static/images/walruslogo.png":
                self.request.sendall(hP.imageHttpString("src/static/images/walruslogo.png"))
        elif isPost(request): 
            if getPath(request) == "/register":
                # username = userInfo["user"]
                # password = userInfo["pass"]
                # password2 = userInfo["pass2"]
                userInfo: List[str] = parseUserInfo(request)
                print(userInfo)
                if userInfo["user"] != "" and userInfo["pass"] != "" and userInfo["pass2"] != "":
                    if userInfo["pass"] == userInfo["pass2"]:
                        self.request.sendall(hP.fileHttpString(code200, "src/html/chatpage.html", html))
                else:
                    self.request.sendall(hP.fileHttpString(code200, "src/html/register.html", html))

            
def requestParse(decoded_string: str) -> List[str]:
    string = decoded_string.split("\r\n")
    return string

def isGET(requestList: List[str]) -> bool:
    request = requestList[0]
    if request[0:3] == "GET":
        return True
    else:
        return False

# function to determine its a POST request
def isPost(requestList: List[str]) -> bool:
    request = requestList[0]
    if request[0:4] == "POST":
        return True
    else:
        return False

def getPath(requestList: List[str]) -> str:
    request: str = requestList[0]
    path = request.split(" ")
    if len(path) > 1:
        return path[1]
    return path[0]

def sizeString(string: str) -> int:
    fileSize = bytes(string, 'utf-8')
    return len(fileSize)

def parseUserInfo(request):
    information: str = request[-1]
    # 'user=hi&pass=thisIsMyPass&pass2=+++++hi'
    idxUser = information.find("user=") 
    idxPass = information.find("pass=") 
    idxPass2 = information.find("pass2=")
    user = information[idxUser + len("user="):idxPass].replace("&","")
    password = information[idxPass+ len("pass="): idxPass2].replace("&","")
    password2 = information[idxPass2 + len("pass2="):].replace("&","")
    return {"user" : user, "pass": password , "pass2": password2}

if __name__ == '__main__':
    host, port = "0.0.0.0", 5000

    with socketserver.ThreadingTCPServer((host, port), MyTcpHandler) as server:
        server.serve_forever()
