
from utility import database
import socketserver
import sys
from utility import paths
from utility import request
from utility import websocket
from utility import response
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
            userInfo = database.getUserbyUser(
                paths.websocket_connections[self])
            send_frame = websocket.generate_frame(
                websocket.gen_user_payload('addOnlineUser', paths.websocket_connections[self], userInfo["imagePath"], 'red'), paths.websocket_connections[self])
            print("Sending the frame", send_frame)
            print(userInfo["imagePath"])
            for user in paths.websocket_connections.keys():
                user.request.sendall(send_frame)
            paths.online_users[self] = {
                "username": paths.websocket_connections[self], "img_src": userInfo["imagePath"], "color": "red"}
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
                    print("---Closing The connection--")
                    print("Sending a notification message to the users",
                          paths.websocket_connections)
                    print("username collection", paths.websocket_connections)
                    print("Online users", paths.online_users)
                    print("Open Dm's", paths.open_dms)
                    print("------------------------------")
                    send_frame = websocket.generate_frame(
                        websocket.gen_user_payload('removeOnlineUser', paths.websocket_connections[self]), paths.websocket_connections[self])
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
                    toUser = json.loads(frame_dict["data"]).get('toUser')
                    """ for user in paths.websocket_connections.keys():
                        if user != self:
                            user.request.sendall(send_frame) """
                    print("This is a webRTC connection")
                    print(toUser)
                    if toUser:
                        print(paths.webRtc)
                        paths.webRtc[self] = toUser
                        # get the other users handle
                        otherUser = paths.user_connections[toUser]
                        paths.webRtc[otherUser] = paths.websocket_connections[self]
                        paths.user_connections[toUser].request.sendall(
                            send_frame)
                    else:
                        print(paths.webRtc)
                        toUser = paths.webRtc[self]
                        paths.user_connections[toUser].request.sendall(
                            send_frame)
                elif json.loads(frame_dict["data"])['messageType'] == 'initDM':
                    print("This is a direct message")
                    # Get the username of who the message is for
                    toUser = json.loads(frame_dict["data"])['toUser']
                    # Handle dm
                    websocket.handle_dm(
                        paths.websocket_connections[self], toUser)
                    print("Init DM", paths.websocket_connections)
                    print("To the User", toUser)
                    print("username collection", paths.websocket_connections)
                    print("Online users", paths.online_users)
                    print("Open Dm's", paths.open_dms)
                    """ send_frame = websocket.generate_frame(
                        frame_dict["data"], paths.websocket_connections[self])
                    paths.user_connections[toUser].request.sendall(send_frame) """
                    """ response_code = '301 Moved Permanently'
                    body = b''
                    content_type = 'text/plain; charset=utf-8\r\nLocation: /dm'
                    # Remove from DS
                    paths.user_connections.pop(username)
                    paths.websocket_connections.pop(self)
                    # paths.online_users.pop(self)
                    self.request.sendall(response.get_response(
                        body, response_code, content_type)) """
                elif json.loads(frame_dict["data"])['messageType'] == 'directMessage':
                    print("user is sending a direct message")
                    toUser = json.loads(frame_dict["data"])['toUser']
                    send_frame = websocket.generate_dm_frame(
                        frame_dict["data"], paths.websocket_connections[self], toUser)
                    # Send the message
                    print("Sending a direct message to the users",
                          paths.websocket_connections)
                    print("To the User", toUser)
                    print("username collection", paths.websocket_connections)
                    print("Online users", paths.online_users)
                    print("Open Dm's", paths.open_dms)
                    paths.user_connections[toUser].request.sendall(send_frame)
                    self.request.sendall(send_frame)
                    # Send the notications frame
                    comment = json.loads(frame_dict["data"])['comment']

                    print("This is the frame being sent for notifications", websocket.gen_user_payload(
                        'recievedNotif', paths.websocket_connections[self], color='red', msg=comment))
                    send_frame = websocket.generate_frame(
                        websocket.gen_user_payload('receivedNotif', paths.websocket_connections[self], color='red', msg=comment), paths.websocket_connections[self])
                    print("Sending a notification message to the users",
                          paths.websocket_connections)
                    print("To the User", toUser)
                    print("username collection", paths.websocket_connections)
                    print("Online users", paths.online_users)
                    print("Open Dm's", paths.open_dms)
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
                    """ if not msg.get("username"):
                        break """
                    sys.stdout.flush()
                    sys.stdout.flush()
                    #database.insert_chat(username, msg)
                    # Send message to every WS connection currently connected
                    print("Sending a chat message to the users",
                          paths.websocket_connections)
                    print("username collection", paths.websocket_connections)
                    print("Online users", paths.online_users)
                    print("Open Dm's", paths.open_dms)
                    for user in paths.websocket_connections.keys():
                        sys.stdout.flush()
                        if paths.websocket_connections[user] != '':
                            user.request.sendall(send_frame)

        else:
            sys.stdout.flush()
            sys.stdout.flush()
            self.request.sendall(response_back)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
