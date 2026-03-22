import os
from pymongo import MongoClient
from config import Config   

MONGO_URI = Config.MONGO_URI

client = MongoClient(MONGO_URI)

db = client["Fake_News_Detection_Webai"]

users = db["users"]
history = db["history"]

users.create_index("email", unique=True)
history.create_index("user")
history.create_index("time")