import re

requests = []
# Dictionary to hold the current length of the request
cur_length = {}
# Dictionary to hold the parsed content length
content_length = {}


def print_request(dict):
    print("------------------REQUEST--------------------------")
    for item in dict:
        print("Key : {} , Value : {}".format(item, dict[item]))
    # print("###################HEADERS##########################")
    for item in dict["header"]:
        print("Key : {} , Value : {}".format(item, dict["header"][item]))
    print("---------------------------------------------------")


def parse_header(header_line):
    header = ""
    info = ""
    header_found = False
    for char in header_line:
        if char == ":":
            header_found = True
        elif char != " " and header_found == True:
            info += char
        else:
            if char != " ":
                header += char
    return [header, info]


def parse_request_line(request_line):
    request_dict = {}
    request_dict["header"] = {}
    space: int = 0
    request_type = ""
    path = ""
    img_path = False
    user_path = False
    for char in request_line:
        if char == " ":
            space += 1
            continue
        if space == 0:
            request_type += char
        elif space < 2:
            path += char
        else:
            break
        if path == "/static/images":
            request_dict["path"] = path
            path = ""
            img_path = True
        if path == "/users/":
            request_dict["path"] = path
            path = ""
            user_path = True
    if img_path:
        request_dict["img_path"] = path
        request_dict["request_type"] = request_type
    elif user_path:
        request_dict["user_path"] = path
        request_dict["request_type"] = request_type
    else:
        request_dict["request_type"] = request_type
        request_dict["path"] = path
    return request_dict

# Old Method for parsing


def parse(data):
    new_parse(data)
    data: str = data.decode().split("\r\n")
    print(data)
    request_dict = {}
    request_dict["header"] = {}
    header_dict = request_dict["header"]
    request_line: str = data[0]
    space: int = 0
    request_type = ""
    path = ""
    img_path = False
    user_path = False
    for char in request_line:
        if char == " ":
            space += 1
            continue
        if space == 0:
            request_type += char
        elif space < 2:
            path += char
        else:
            break
        if path == "/image":
            request_dict["path"] = path
            path = ""
            img_path = True
        if path == "/users/":
            request_dict["path"] = path
            path = ""
            user_path = True
    if img_path:
        request_dict["img_path"] = path
        request_dict["request_type"] = request_type
    elif user_path:
        request_dict["user_path"] = path
        request_dict["request_type"] = request_type
    else:
        request_dict["request_type"] = request_type
        request_dict["path"] = path
    is_body = False
    for line in data[1:]:
        if is_body:
            #print(f"body: {line}\ntype: {type(line)}")
            request_dict["body"] = line
            break
        if line == "":
            is_body = True
        else:
            header_list = parse_header(line)
            header_dict[header_list[0]] = header_list[1]
    requests.append(request_dict)
    # print_request(request_dict)
    return request_dict


def parse_multipart_heading(line):
    # TODO if needed: split up the content dispositon line to get each value
    content = line.split(';')
    for value in content:
        if (value.find('name=')) != -1:
            return value[value.find('name=')+len('name='):].replace('"', '')

    return line


def parse_multipart_header(headers):
    header_dict = {}
    for heading in headers:
        if heading != '':
            retlist = parse_header(heading)
            if retlist[0] == 'Content-Disposition':
                header_dict["name"] = parse_multipart_heading(retlist[1])
            header_dict[retlist[0]] = retlist[1]
        else:
            continue
    return header_dict


def parse_multipart(boundary, body):
    # find boundry, then parse the header using newline
    # print(boundary)
    # Dictionary to store all multipart lines key: is # entry -> value: Dict{headers -> , body -> }
    multipart_dic = {}
    boundary_ln = body[body.find(bytes(boundary, 'utf-8')):]
    # print(boundary_ln)
    i = 0
    while len(boundary_ln) != 0:
        # increment boundary_ln by boundary_ln bytes
        multipart_dic[i] = {}
        boundary_ln = boundary_ln[len((bytes(boundary, 'utf-8'))):]
        # print(boundary_ln)
        headers: str = boundary_ln[:boundary_ln.find(b'\r\n\r\n')]
        # print("-------------headers:", headers)
        headers = headers.decode().split("\r\n")
        if len(headers) == 0 or headers[0] == '--\r':
            break
        # print("-------------headers:", headers)
        multipart_dic[i]["heading"] = parse_multipart_header(headers)
        multipart_body = boundary_ln[boundary_ln.find(
            b'\r\n\r\n')+len(b'\r\n\r\n'):boundary_ln.find(b'\r\n--')]
        if multipart_dic[i]["heading"].get("Content-Type"):
            multipart_dic[i]["type"] = multipart_dic[i]["heading"].get(
                "Content-Type")
        else:
            multipart_body = multipart_body.decode()
            # Security: replace HTML elements in case of injection
            multipart_body = multipart_body.replace('&', '&amp;')
            multipart_body = multipart_body.replace('<', '&lt;')
            multipart_body = multipart_body.replace('>', '&gt;')
            # if multipart_dic[i]["heading"]["name"] == "comment":
            #multipart_dic[i]["type"] = "comment"
            # else:
            #multipart_dic[i]["type"] = "token"
        # print("---------------------body: ", multipart_body)
        multipart_dic[i]["body"] = multipart_body
        boundary_ln = boundary_ln[boundary_ln.find(bytes(boundary, 'utf-8')):]
        # print(boundary_ln)
        i += 1
    return multipart_dic


def parse_content_length(data, handler):
    headers: str = data[:data.find(b'\r\n\r\n')]
    headers = headers.decode().split("\r\n")
    header_dict = {}
    for heading in headers:
        parsed = parse_header(heading)
        header_dict[parsed[0]] = parsed[1]
    global content_length
    # print("===================Content-Len: ",
    # header_dict.get("Content-Length", content_length[handler]))
    content_length[handler] = int(header_dict.get(
        "Content-Length", content_length[handler]))


def new_parse(data):
    # print("----------------------parse------------------------")
    headers: str = data[:data.find(b'\r\n\r\n')]
    headers = headers.decode().split("\r\n")
    req_dict = parse_request_line(headers[0])
    header_dict = req_dict["header"]
    for heading in headers:
        parsed = parse_header(heading)
        header_dict[parsed[0]] = parsed[1]
    body: bytes = data[data.find(b'\r\n\r\n'):]
    if header_dict.get("Content-Type"):
        if re.search("multipart/form-data", header_dict["Content-Type"]):
            boundary = header_dict["Content-Type"][header_dict["Content-Type"].find(
                "boundary=")+len("boundary="):]
            #print("boundry: ", boundary)
            req_dict["multi-part"] = parse_multipart(boundary, body)

    # print(req_dict["request_type"])
    # print("body: ", body)
    req_dict["body"] = body
    print_request(req_dict)
    return req_dict
    # print("======================================================")
