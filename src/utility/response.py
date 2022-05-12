import random
import string

xsrf_token = {}


def get_response(body: bytes, response_code: str = '200 OK', content_type: str = 'text/plain; charset=utf-8'):
    response = b'HTTP/1.1 ' + response_code.encode()
    response += b'\r\nContent-Length: ' + str(len(body)).encode()
    response += b'\r\nContent-Type: ' + content_type.encode()
    response += b'\r\n\r\n'
    response += body
    return response


def get_token(username):
    length = 22
    token = ''.join(random.sample(string.ascii_letters, length))
    xsrf_token[username] = token
    return token


def get_handshake(body: bytes, response_code: str = '200 OK', content_type: bytes = b'text/plain; charset=utf-8'):
    response = b'HTTP/1.1 ' + response_code.encode()
    response += b'\r\n' + content_type
    response += b'\r\n\r\n'
    return response
