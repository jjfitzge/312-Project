
from pymongo import MongoClient
from . import authentication


mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
user_collection = db["user"]
user_msg_collection = db["msg"]
id_collection = db["id"]
img_count_collection = db["img_count"]
users = db["users"]
users_tokens = db["authToken"]


def init_db():
    id_collection.insert_one({"latest_id": 0})
    img_count_collection.insert_one({"latest_id": 0})


def create_entry(collection, email, username):
    id = update_id(id_collection)
    data = {"id": id, "email": email, "username": username}
    collection.insert_one(data)
    return collection.find({"id": id}, {"_id": 0, "id": 1, "email": 1, "username": 1})


def list_entry(collection):
    return collection.find({}, {"_id": 0, "id": 1, "email": 1, "username": 1})


def get_id(collection):
    id = collection.find_one()
    return int(id["latest_id"])


def update_id(collection):
    id = get_id(collection)
    query = {"latest_id": id}
    retval = {"$set": {"latest_id": id+1}}
    collection.update_one(query, retval)
    return id+1


def retrieve(collection, id):
    print("running retrieve")
    ret_dict = {}
    ret_dict["exists"] = False
    if record_exists(collection, id):
        ret_dict["exists"] = True
        print("record exists")
        return collection.find({"id": id}, {"_id": 0, "id": 1, "email": 1, "username": 1})
    else:
        return False


def update(collection, id, email, username):
    ret_dict = {}
    ret_dict["exists"] = False
    if record_exists(collection, id):
        ret_dict["exists"] = True
        retval = {"$set": {"email": email, "username": username}}
        collection.update_one({"id": id}, retval)
        return collection.find({"id": id}, {"_id": 0, "id": 1, "email": 1, "username": 1})
    else:
        return False


def delete(collection, id):
    if record_exists(collection, id):
        collection.delete_one({"id": id})
        return True
    else:
        return False


def record_exists(collection, id):
    # Return bool depending on if record exists or not
    # https://docs.mongodb.com/manual/reference/method/db.collection.countDocuments/
    return collection.count_documents({"id": id}) > 0


def create_msg(comment, img):
    update_id(img_count_collection)
    data = {"comment": comment, "img": img}
    user_msg_collection.insert_one(data)


def list_msg():
    data = user_msg_collection.find({}, {"_id": 0, "comment": 1, "img": 1})
    retval = []
    for entry in data:
        # print(entry)
        retval.append(entry)
    return retval


def list_img():
    data = user_msg_collection.find({}, {"_id": 0, "comment": 1, "img": 1})
    retval = []
    for entry in data:
        # print(entry)
        file = entry['img']
        file_path = './image/' + str(file)
        retval.append(file_path)
    return retval


def create_user(username, password):
    salt_dict = authentication.get_saltedhash(password)

    data = {"username": username,
            "salt": salt_dict["salt"], "saltedhash": salt_dict["saltedhash"]}
    users.insert_one(data)


def check_user(username, password):
    # Match username and salted hash password

    # Get record for username and password
    query = {"username": username}

    doc = users.find(query)

    for x in doc:
        salt = x["salt"]
        checksalt = authentication.check_salt(password, salt)

        if x["saltedhash"] == checksalt:
            return True
    return False


def create_authToken(username, token):
    hashed_token = authentication.get_saltedhash(token)
    data = {"username": username,
            "authToken": hashed_token["saltedhash"], "salt": hashed_token["salt"]}
    users_tokens.insert_one(data)


def check_token(username, token):
    # Match username and salted hash password
    # Get record for username and password
    query = {"username": username}
    print(query)

    doc = users_tokens.find(query)

    for x in doc:
        print(x)
        salt = x["salt"]
        checksalt = authentication.check_salt(token, salt)
        if x["authToken"] == checksalt:
            print("User is Authenticated")
            return True
    return False
