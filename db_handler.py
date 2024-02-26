from config import ATLAS_USERNAME, ATLAS_PASSWORD, ATLAS_DATABASE
from pymongo import MongoClient

class MongoDBHandler:
    def __init__(self, db_name, collection_name):
        uri = f"mongodb+srv://{ATLAS_USERNAME}:{ATLAS_PASSWORD}@{ATLAS_DATABASE}.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
    # A function to count the number of documents in a collection
    def count_documents(self):
        return self.collection.count_documents({})
    
    def count_deleted_documents(self):
        return self.collection.count_documents({"is_deleted": True})
    
    def last_documents(self, n=1):
        sort = [("_id", -1)]
        projection = {"_id": 0}
        return list(self.collection.find(projection=projection, sort=sort).limit(n))
    
    def find(self, projection={"_id": 0}, filter={}, sort=[("_id", -1)], limit=100):
        # find all documents that is_deleted field is False
        return list(self.collection.find(filter=filter, projection=projection, sort=sort).limit(limit))
    
    # A function to sample random documents from the collection, Filter is optional and is_deleted field is False by default
    def random_sample(self, filter={"is_deleted": False}, limit=100):
        return list(self.collection.aggregate([{"$match": filter}, {"$sample": {"size": limit}}]))