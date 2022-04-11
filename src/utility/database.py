from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["cse312_project"]
# Collections
user_collection = db["user"]


# Sample functions for DB

def create_entry(collection, email, username, password):
    # In the full app password can't be stored directly
    data = {"email": email, "username": username, "password": password}
    collection.insert_one(data)


def list_entry(collection):
    entry_list = collection.find(
        {}, {"_id": 1, "email": 1, "username": 1, "password": 1})
    retlist = []
    for entry in entry_list:
        retlist.append(entry)
    return retlist
