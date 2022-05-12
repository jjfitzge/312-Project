
from utility import database
import socketserver
import sys
from utility import paths
from utility import request
from utility import websocket
import json
from bson import json_util


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # Constant to hold the amount of bytes requested when reading from TCP connection
        default_length = 4000
        request.content_length[self] = default_length
        request.cur_length[self] = 0
        full_response = b''
        # Buffer data
        while request.cur_length[self] < request.content_length[self]:
            full_response += self.request.recv(default_length)
            sys.stdout.flush()
            sys.stdout.flush()
            if request.cur_length[self] == 0:
                request.parse_content_length(full_response, self)
            request.cur_length[self] += default_length
            sys.stdout.flush()
            sys.stdout.flush()
        # Commenting out Databse
        # database.init_db()
        sys.stdout.flush()
        sys.stdout.flush()

        request_dict = request.new_parse(full_response)
        # Start routing requests after response if fully parsed
        response_back: bytes = paths.route_path(full_response, self)
        if request_dict["path"] == "/websocket":
            # Send handshake
            self.request.sendall(response_back)
            # Send connected users initial user frame
            test_username = "Hello World"
            id = len(paths.online_users)
            send_frame = websocket.generate_frame(
                websocket.gen_user_payload('addOnlineUser', 'user'+str(id) + "F", '/static/images/walruslogo.png', 'red'), paths.websocket_connections[self])
            paths.online_users[self] = {
                "username": "user"+str(id), "img_src": '/static/images/walruslogo.png', "color": "red"}
            for user in paths.websocket_connections.keys():
                user.request.sendall(send_frame)
            while True:
                websocket.ws_payload_length[self] = default_length
                websocket.ws_payload_cur_length[self] = 0
                full_ws_data = b''
                # Buffer WS Frame
                while websocket.ws_payload_cur_length[self] < websocket.ws_payload_length[self]:
                    full_ws_data += self.request.recv(default_length)
                    if websocket.ws_payload_cur_length[self] == 0:
                        websocket.parse_payload_length(full_ws_data, self)
                        # Parse the payload to see if we have read payload_len bytes
                        temp_dict = websocket.parse_frame(full_ws_data)
                        # If opcode == 8, break out loop so WS connection can close and DS's update
                        if temp_dict["opcode"] == 8:
                            break
                        # If Payload lenght bytes already read, exit loop
                        if websocket.ws_payload_length[self] <= len(temp_dict["data"]):
                            print(
                                "Breaking out of loop, already have payload_length amount of data")
                            break
                    else:
                        websocket.ws_payload_cur_length[self] += default_length
                    sys.stdout.flush()
                sys.stdout.flush()
                frame_dict = websocket.parse_frame(full_ws_data)
                # print(type(frame_dict["data"]))
                sys.stdout.flush()
                username = paths.websocket_connections[self]
                if frame_dict["opcode"] == 8:
                    # remove self from data structures
                    send_frame = websocket.generate_frame(
                        websocket.gen_user_payload('removeOnlineUser', 'user'+str(len(paths.online_users))), paths.websocket_connections[self])
                    for user in paths.websocket_connections.keys():
                        user.request.sendall(send_frame)
                    paths.user_connections.pop(username)
                    paths.websocket_connections.pop(self)
                    paths.online_users.pop(self)
                    break
                sys.stdout.flush()
                is_webRTC = websocket.check_msg(json.loads(frame_dict["data"]))
                if is_webRTC:
                    # Send just the payload to the other client
                    send_frame = websocket.generate_webrtc_frame(
                        frame_dict["data"])
                    for user in paths.websocket_connections.keys():
                        if user != self:
                            user.request.sendall(send_frame)
                elif json.loads(frame_dict["data"])['messageType'] == 'directMsg':
                    print("This is a direct message")
                    # Get the username of who the message is for
                    toUser = json.loads(frame_dict["data"])['toUser']
                    send_frame = websocket.generate_frame(
                        frame_dict["data"], paths.websocket_connections[self])
                    paths.user_connections[toUser].request.sendall(send_frame)

                else:
                    send_frame = websocket.generate_frame(
                        frame_dict["data"], paths.websocket_connections[self])
                    if (send_frame == None):
                        print("The frame is empty")
                        continue
                    sys.stdout.flush()
                    msg = json.loads(frame_dict["data"])
                    msg = msg['comment']
                    sys.stdout.flush()
                    sys.stdout.flush()
                    #database.insert_chat(username, msg)
                    # Send message to every WS connection currently connected
                    for user in paths.websocket_connections.keys():
                        sys.stdout.flush()
                        user.request.sendall(send_frame)
        else:
            sys.stdout.flush()
            sys.stdout.flush()
            self.request.sendall(response_back)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
