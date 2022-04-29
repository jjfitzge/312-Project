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
multiPart = "multipart/form-data"-
IMAGECOUNT = 0


def serve_image(request_msg):
    remainder = ""
    for i in range(7, len(request_msg)):
        remainder += request_msg[i:i + 1]
        open_msg = "./image/{}".format(remainder)
    with open(open_msg, "rb") as f:
        text = f.read()
        size = len(text)
        contentlen = str(size)
    response = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: "
    nextpart = "\r\nContent-Type: image/jpeg; charset=utf-8\r\n\r\n"
    retval = (response+contentlen+nextpart).encode()+text
    return retval

#http://localhost:5000/static/styles/hero.jpg
#http: // localhost: 8000 / image / elephant.jpg

def check_str_and_img_for_safety(string):
    return string

def Bstring_Len_To_Num(b_string):

    store = str(b_string)
    a = store.replace("b", "")
    final = a.replace("'", "")
    res = int(final)
    return res


class MyTcpHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global IMAGECOUNT

        received_data = self.request.recv(1024)
        #handles image upload
        if received_data == b'POST /image-upload':
            byte_copy_of_received_data = received_data
        else:
            request: List[str] = requestParse(received_data.decode())
            raw_request_str_decoded = received_data.decode()

#/Users/jiawe/PycharmProjects/imgs/312-Project/src/html/index.html

        #print(request)
        #if getPath(request) == "/":
        #    self.request.sendall(hP.fileHttpString(code200, "src/html/index.html", html))
        #elif getPath(request) == "/static/styles/index.css":
        #    self.request.sendall(hP.fileHttpString(code200, "src/static/styles/index.css", css))
        #elif getPath(request) == "/static/images/hero.jpg":
        #    self.request.sendall(hP.imageHttpString("src/static/images/hero.jpg"))




       # if isGET(request):
       #     print(request)
        #    if getPath(request) == "/":
       #         self.request.sendall(hP.fileHttpString(code200,"./html/index.html",html))
       #     elif getPath(request) == "./index.css":
       #         self.request.sendall(hP.fileHttpString(code200, "./static/styles/index.css", css))
       #     elif getPath(request) == "./static/images/hero.jpg":
       #        self.request.sendall(hP.imageHttpString("./static/images/hero.jpg"))


        #print(request)
        if getPath(request) == "/":
                 self.request.sendall(hP.fileHttpString(code200,"./html/index.html",html))
        elif getPath(request) == "/static/styles/index.css":
                 self.request.sendall(hP.fileHttpString(code200, "./static/styles/index.css", css))
        elif getPath(request) == "/static/styles/hero.jpg":
                 self.request.sendall(hP.imageHttpString("./static/images/hero.jpg"))
        if getPath(request) == "/htmltest":
                 self.request.sendall(hP.fileHttpString (code200, "./html/htmltest.html", html))

        if received_data[0:18] == b'POST /image-upload':
            start_index_content_len = received_data.find(b'Content-Length:')
            content_len = b''
            for i in range(start_index_content_len + 15, len(received_data)):
                if received_data[i:i + 2] != b'\r\n':
                    content_len += received_data[i:i + 1]
                else:
                    break
            content_len = content_len.replace(b' ', b'')
            int_content_len = Bstring_Len_To_Num(content_len)
            counter = 0
            build_whole_msg = b''
            build_whole_msg += byte_copy_of_received_data
            while counter <= int_content_len:
                received_data = self.request.recv(1024)
                build_whole_msg += received_data
                counter += 1024
            print("byte msg is this", build_whole_msg)
            # at this point, you've built the whole big message, the comment comes after the second webkit
            cpy_whole_msg = build_whole_msg
            web_kit_msg = b''
            # webkitmsg of the form WebKitAaEnd
            first = cpy_whole_msg.find(b'----')
            for i in range(first + 4, len(cpy_whole_msg)):
                if cpy_whole_msg[i:i + 2] != b'\r\n':
                    web_kit_msg += cpy_whole_msg[i:i + 1]
                else:
                    break
            # get the user comment
            dash_web_kit_msg = b'------' + web_kit_msg
            idx_first_comment = cpy_whole_msg.find(b'comment')
            temp_usr_comment = b''
            for i in range(idx_first_comment + 7, len(cpy_whole_msg)):
                if cpy_whole_msg[i:i + len(dash_web_kit_msg)] != dash_web_kit_msg:
                    temp_usr_comment += cpy_whole_msg[i:i + 1]
                else:
                    break
            clean = str(temp_usr_comment)
            clean1 = clean.replace("b'", "")
            clean2 = clean1.replace(r'\r\n', "")
            clean3 = clean2.replace('"', "")
            clean4 = clean3.replace("'", "")
            secured = check_str_and_img_for_safety(clean4)
            #secured is the message that the user sent, if they did send any.
            # handle printing the image now.
            dash_web_kit_msg_final = dash_web_kit_msg + b'--'
            a = cpy_whole_msg.split(b'Content-Type')
            unfiltered_image = a[2]
            store = unfiltered_image
            synth = 0
            if (len(store) > 2):  # yes, there is a picture being sent here
                IMAGECOUNT += 1
            else:
                synth = 1
            num = len(dash_web_kit_msg_final) + 4
            second_num = len(store) - num
            img = store[16: second_num]
            #img is the image byte data for the image, if they did send any.
            jpg = '.jpg'
            string = './image/{}{}'.format(IMAGECOUNT, jpg)
            string_without_dot = string[1:len(string)]  # /image/1.jpg
            f = open(string, 'wb')
            f.write(img)
            f.close
            full_string = '<img src="{}"/>'.format(string_without_dot)


#http://localhost:5000/static/styles/hero.jpg


        #http: // localhost: 8000 / image / elephant.jpg


        #for handling serving an image that is now saved in directory.
        if raw_request_str_decoded[0:3] == 'GET':
            request_msg = ''
            for i in range(4, len(raw_request_str_decoded), 1):
                endcond = raw_request_str_decoded[i + 1:i + 10]
                request_msg += raw_request_str_decoded[i:i + 1]
                if endcond == " HTTP/1.1":  # endcond is 9 chars long so you want to end it on
                    break
            if request_msg[0:7] == "/image/":
                self.request.sendall(serve_image(request_msg))






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
