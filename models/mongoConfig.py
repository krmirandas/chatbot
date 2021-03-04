import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

database = client["chatbot"]
