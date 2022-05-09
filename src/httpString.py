import file as f
import app as a

def createHttpString(httpResponse: str, length: int, contentType: str, body) -> bytes:
    if httpResponse == a.code301:
        s = "HTTP/1.1 %s\r\nContent-Length: %s\r\nLocation: %s\r\n\r\n" % (httpResponse, length, body)
    elif contentType == a.jpg or contentType == a.png:
        s = "HTTP/1.1 %s\r\nContent-Length: %s\r\nContent-Type: %s\r\nX-Content-Type-Options:nosniff\r\n\r\n" % (
            httpResponse, length, contentType)
        return s.encode(encoding='UTF-8') + body
    else:
        s = "HTTP/1.1 %s\r\nContent-Length: %s\r\nContent-Type: %s; charset=utf-8\r\nX-Content-Type-Options:nosniff\r\n\r\n%s" % (
            httpResponse, length, contentType, body)
    return s.encode(encoding='UTF-8')


def fileHttpString(code: str, fileName: str, fileType: str) -> bytes:
    fileContent = f.openFile(fileName)
    return createHttpString(code, fileContent[0], fileType, fileContent[1])


def imageHttpString(imagePath: str) -> bytes:
    image = f.openImage(imagePath)
    return createHttpString(a.code200, image[0], a.jpg, image[1])
