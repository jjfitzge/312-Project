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
mp4 = "video/mp4"
MiMEjson = "application/json"
multiPart = "multipart/form-data"

class MyTcpHandler(socketserver.BaseRequestHandler):

    def handle(self):

        received_data = self.request.recv(1024)
        request: List[str] = requestParse(received_data.decode())

        if isGET(request):
            print(request)
            if getPath(request) == "/":
                self.request.sendall(hP.fileHttpString(code200,"src/html/index.html",html))
            elif getPath(request) == "/static/styles/index.css":
                self.request.sendall(hP.fileHttpString(code200, "src/static/styles/index.css", css))
            elif getPath(request) == "/static/images/hero.jpg":
                self.request.sendall(hP.imageHttpString("src/static/images/hero.jpg"))
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
       

if __name__ == '__main__':
    host, port = "0.0.0.0", 5000

    with socketserver.ThreadingTCPServer((host, port), MyTcpHandler) as server:
        server.serve_forever()
