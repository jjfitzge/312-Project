import app as a

def openFile(fileName: str):
    with open(fileName, 'r', encoding='UTF-8') as file:
        read = file.read()
        length = a.sizeString(read)
        return length, read


# opens an image file and returns the (len + bytes of image)
def openImage(imagePath: str):
    with open(imagePath, "rb") as file:
        image = file.read()
        return len(image), image
