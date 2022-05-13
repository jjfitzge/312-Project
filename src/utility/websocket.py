import hashlib
import base64
from sys import byteorder
import json
from bson import json_util
from utility import paths

# Dictionary to store the payload for a WS connection
ws_payload_length = {}
# Dictionary to store the current length retrieved from the incoming frame
ws_payload_cur_length = {}

# Generate accept header for WS handshake


def generate_accept(key):
    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    concat_str = key + guid
    sha_1 = hashlib.sha1(concat_str.encode()).digest()
    retval = base64.standard_b64encode(sha_1)
    return retval

# Function for parsing a given WS frame


def parse_frame(frame):
    frame_dict = {}
    if (len(frame) == 0):
        print("Frame has no length frame: ", frame)
        return None
    opcode = int(frame[0] & 15)
    length = frame[1] & 127
    mask_key = ''
    payload_i = 2
    data = b''
    if length == 126:
        # read next 16 bits
        print("Getting the length for payload length 126")
        padded_bits = prepend_bits(
            bin(frame[3])[2:], 8 - len(bin(frame[3])[2:]))
        length = int(bin(frame[2]) + padded_bits[2:], 2)
        payload_i = 4
    if length == 127:
        # read next 64 bits
        print("Payload Length is equal to 127")
        padded_bits = []
        padded_bits.append(prepend_bits(
            bin(frame[3])[2:], 8 - len(bin(frame[3])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[4])[2:], 8 - len(bin(frame[4])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[5])[2:], 8 - len(bin(frame[5])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[6])[2:], 8 - len(bin(frame[6])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[7])[2:], 8 - len(bin(frame[7])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[8])[2:], 8 - len(bin(frame[8])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[9])[2:], 8 - len(bin(frame[9])[2:])))

        length = int(bin(frame[2]) + padded_bits[0][2:] +
                     padded_bits[1][2:] + padded_bits[2][2:] + padded_bits[3][2:] + padded_bits[4][2:] + padded_bits[5][2:] + padded_bits[6][2:], 2)
        payload_i = 10
    length = int(length)
    if opcode == 8:
        frame_dict["opcode"] = 8
        return frame_dict
    elif opcode == 1:
        # mask key is next 4 bytes (32 bits)
        mask_key = frame[payload_i:payload_i+5]
        data = get_payload(mask_key, length, frame[payload_i+4:]).decode()
    else:
        print("binary")
    frame_dict["opcode"] = opcode
    frame_dict["length"] = length
    frame_dict["data"] = data
    return frame_dict

# Function that parses the payload using the mask_key and length


def get_payload(key, length, payload):
    cur_length = length
    payload_data = b''
    while cur_length > 0:
        if (cur_length >= 4):
            four_bytes = payload[0:4]
            cur_length -= 4
            payload_data += bytes(x ^ y for x, y in zip(key, four_bytes))
            if cur_length == 0:
                break
            payload = payload[4:]
        else:
            given_bytes = payload[0:cur_length]
            payload_data += bytes(x ^ y for x,
                                  y in zip(key[0:cur_length+1], given_bytes))
            cur_length -= cur_length
    return payload_data

# opcode = 129: TEXT
# opcode = 136: CLOSE CONNECTION

# Function that creates the frame to be returned to other users from a WS connection


def generate_frame(payload, username, opcode=129):
    # sanitize payload
    new_payload = parse_frame_message(json.loads(payload), username)
    frame = bytearray()
    frame.extend(bytes([opcode]))
    frame.extend(generate_payload_length(new_payload))
    frame.extend(new_payload)
    return bytes(frame)


# Function that generates the correct payload length header in the frame

def generate_payload_length(payload):
    length = len(payload)
    if length >= 126 and length < 65536:
        padded_header = add_padding(bin(length), 16)
        return padded_header
    elif length >= 65536:
        padded_header = add_padding(bin(length), 64)
        return padded_header
    else:
        padding = add_padding(bin(length), 0)
        padding = int(padding, 2)
        retval = bytes([padding])
        return retval

# Function that handles the different amount of bytes depending on payload_len and add's the correct padding


def add_padding(payload_length, bytes_needed):
    # add zero mask
    if bytes_needed == 0:
        app_len = 8 % (len(payload_length)-2)
        orig_pLength = payload_length[2:]
        return prepend_bits(orig_pLength, app_len)
    elif bytes_needed == 16:
        # 7 bits of payload length need to be equal to 126 + 0 bit mask
        payload_header = bytearray()
        payload_header.append(126)
        # add the actual payload length
        app_len = 16 - (len(payload_length)-2)
        orig_pLength = payload_length[2:]
        new_pLength = prepend_bits(orig_pLength, app_len)
        payload_header.extend(bytes([int(new_pLength[2:10], 2)]))
        payload_header.extend(bytes([int(new_pLength[10:], 2)]))
        print("Generated Payload Header", payload_header)
        return bytes(payload_header)

    else:
        print(64)
        # 7 bits of payload length need to be equal to 127 + 0 bit mask
        payload_header = bytearray()
        payload_header.append(127)
        # add the actual payload length
        app_len = 64 - (len(payload_length)-2)
        orig_pLength = payload_length[2:]
        new_pLength = prepend_bits(orig_pLength, app_len)
        payload_header.extend(bytes([int(new_pLength[2:10], 2)]))
        payload_header.extend(bytes([int(new_pLength[10:18], 2)]))
        payload_header.extend(bytes([int(new_pLength[18:26], 2)]))
        payload_header.extend(bytes([int(new_pLength[26:34], 2)]))
        payload_header.extend(bytes([int(new_pLength[34:42], 2)]))
        payload_header.extend(bytes([int(new_pLength[42:50], 2)]))
        payload_header.extend(bytes([int(new_pLength[50:58], 2)]))
        payload_header.extend(bytes([int(new_pLength[58:66], 2)]))
        print("Generated Payload Header", payload_header)
        return bytes(payload_header)


# Function that prepend's bits of a binary string to get the correct amount of bits for a byte

def prepend_bits(string, bits):
    prepend_str = '0b'
    for i in range(bits):
        prepend_str += '0'
    return prepend_str + string

# Function that parses a frame's message if it is not a WebRTC connection


def parse_frame_message(message, username, toUser=None):
    if message["messageType"] == 'chatMessage' or message["messageType"] == 'directMessage':
        # sanitize message
        message["comment"] = message["comment"].replace('&', '&amp;')
        message["comment"] = message["comment"].replace('<', '&lt;')
        message["comment"] = message["comment"].replace('>', '&gt;')
        # add username
        message["username"] = username
        # Eventually need to get color of the database for this user
        message["color"] = 'black'
        if message["messageType"] == 'directMessage':
            # Add username and comment to DS for both users
            # Get dict for username
            curUser = paths.open_dms[username]['openDMs']
            for dms in curUser:
                if dms['otherUsersName'] == toUser:
                    dms['messages'].append(
                        {'username': username, 'comment': message["comment"]})
            otherUser = paths.open_dms[toUser]['openDMs']
            for dms in otherUser:
                if dms['otherUsersName'] == username:
                    dms['messages'].append(
                        {'username': username, 'comment': message["comment"]})
            # Add username and message to both User objects

        return json_util.dumps(message).encode()
    elif message["messageType"] == 'addOnlineUser':
        return json_util.dumps(message).encode()
    elif message["messageType"] == 'removeOnlineUser':
        return json_util.dumps(message).encode()


# -----For Testing Purposes---
# Function to parse the generated frame for WS response

def parse_gen_frame(frame):
    print("Given the frame: ", frame)
    print("got frame length: ", len(frame))
    frame_dict = {}
    if (len(frame) == 0):
        print("Frame has no length frame: ", frame)
        #frame_dict["opcode"] = 8
        return None
        # return frame_dict
    opcode = int(frame[0] & 15)
    length = frame[1] & 127
    print(frame[1])
    print("opcode=", opcode)
    print("payloadlen=", length)
    mask_key = ''
    payload_i = 2
    data = b''
    if length == 126:
        # read next 16 bits
        print("Getting the length for payload length 126")
        #length = frame[2:4]
        # print(frame[2])
        # print(frame[3])
        padded_bits = prepend_bits(
            bin(frame[3])[2:], 8 - len(bin(frame[3])[2:]))
        length = int(bin(frame[2]) + padded_bits[2:], 2)
        # print(length)
        #length = 340
        payload_i = 4
    if length == 127:
        # read next 64 bits
        print("Payload Length is equal to 127")
        padded_bits = []
        padded_bits.append(prepend_bits(
            bin(frame[3])[2:], 8 - len(bin(frame[3])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[4])[2:], 8 - len(bin(frame[4])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[5])[2:], 8 - len(bin(frame[5])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[6])[2:], 8 - len(bin(frame[6])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[7])[2:], 8 - len(bin(frame[7])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[8])[2:], 8 - len(bin(frame[8])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[9])[2:], 8 - len(bin(frame[9])[2:])))

        length = int(bin(frame[2]) + padded_bits[0][2:] +
                     padded_bits[1][2:] + padded_bits[2][2:] + padded_bits[3][2:] + padded_bits[4][2:] + padded_bits[5][2:] + padded_bits[6][2:], 2)
        payload_i = 10
    print(opcode)
    length = int(length)
    print(length)
    if opcode == 8:
        print("opcode is 8")
        frame_dict["opcode"] = 8
        return frame_dict
    elif opcode == 1:
        print("text")
        # mask key is next 4 bytes (32 bits)
        #mask_key = frame[payload_i:payload_i+5]
        #print("key :", mask_key)
        data = (frame[payload_i:]).decode()
        print("retrieved data", data)
    else:
        print("binary")

    frame_dict["opcode"] = opcode
    frame_dict["length"] = length
    frame_dict["data"] = data
    print(frame_dict)
    return frame_dict

# Function to initially parse the header of the frame to read the payload length


def parse_payload_length(frame, handler):

    if (len(frame) == 0):
        print("Frame has no length frame: ", frame)
        return None
    length = frame[1] & 127
    if length == 126:
        # read next 16 bits
        print("Getting the length for payload length 126")
        padded_bits = prepend_bits(
            bin(frame[3])[2:], 8 - len(bin(frame[3])[2:]))
        length = int(bin(frame[2]) + padded_bits[2:], 2)
        print(length)
    if length == 127:
        # read next 64 bits
        print("Getting the length for payload length 127")

        padded_bits = []
        padded_bits.append(prepend_bits(
            bin(frame[3])[2:], 8 - len(bin(frame[3])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[4])[2:], 8 - len(bin(frame[4])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[5])[2:], 8 - len(bin(frame[5])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[6])[2:], 8 - len(bin(frame[6])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[7])[2:], 8 - len(bin(frame[7])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[8])[2:], 8 - len(bin(frame[8])[2:])))
        padded_bits.append(prepend_bits(
            bin(frame[9])[2:], 8 - len(bin(frame[9])[2:])))

        length = int(bin(frame[2]) + padded_bits[0][2:] +
                     padded_bits[1][2:] + padded_bits[2][2:] + padded_bits[3][2:] + padded_bits[4][2:] + padded_bits[5][2:] + padded_bits[6][2:], 2)
    ws_payload_length[handler] = length

# Function that returns BOOL based on if the message type is WebRTC or not


def check_msg(message):
    print(message)
    return message["messageType"][:6] == 'webRTC'

# Function that generates the return frame for a webRTC connection


def generate_webrtc_frame(payload, opcode=129):
    new_payload = payload.encode()
    frame = bytearray()
    frame.extend(bytes([opcode]))
    frame.extend(generate_payload_length(new_payload))
    frame.extend(new_payload)
    return bytes(frame)
# Function to generate the user information sent over WS


def gen_user_payload(messageType: str, username: str, src=None, color=None):
    # Get user info from database (img_src, color)
    if messageType == 'addOnlineUser':
        return json.dumps({'messageType': messageType, 'username': username, "img_src": src, 'color': color})
    if messageType == 'recieveNotif':
        return json.dumps({'messageType': messageType, 'username': username, 'color': color})
    else:
        return json.dumps({'messageType': messageType, 'username': username})


def handle_dm(fromUser, toUser):
    # If database does not have record for fromUser or toUser
    # Initialize
    paths.toUserDict[fromUser] = toUser
    if fromUser not in paths.open_dms:
        retdict = {"currentUser": fromUser, 'openDMs': [
            {'otherUsersName': toUser, 'messages': []}]}
        retdict_reverse = {"currentUser": toUser, 'openDMs': [
            {'otherUsersName': fromUser, 'messages': []}]}
        paths.open_dms[fromUser] = retdict
        paths.open_dms[toUser] = retdict_reverse
    else:
        openDms = paths.open_dms[fromUser]['openDMs']
        if any(toUser in d for d in openDms) == False:
            # Add Touser to openDm's for fromUser
            openDms.append({'otherUsersName': toUser, 'messages': []})
            # Add fromUser to openDM's for toUser
            paths.open_dms[toUser]['openDMs'].append(
                {'otherUsersName': fromUser, 'messages': []})

    # If the record already exists do nothing
    # messages are in form {'username': username, 'comment': comment}


def generate_dm_frame(payload, username, toUser, opcode=129):
    # sanitize payload
    new_payload = parse_frame_message(json.loads(payload), username, toUser)
    frame = bytearray()
    frame.extend(bytes([opcode]))
    frame.extend(generate_payload_length(new_payload))
    frame.extend(new_payload)
    return bytes(frame)
