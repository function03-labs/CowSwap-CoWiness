from pymongo import MongoClient


def connect(uri, db_name, collection_name):
    # Create a new client and connect to the server
    client = MongoClient(uri)
    # Access the desired database and collection
    db = client[db_name]
    collection = db[collection_name]
    return collection
