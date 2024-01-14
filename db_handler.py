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
    
    def last_document(self, n=1):
        sort = [("_id", -1)]
        projection = {"_id": 0}
        return list(self.collection.find(projection=projection, sort=sort).limit(n))
    
    def find(self, projection={"_id": 0}, filter={}, sort=[("_id", -1)]):
        # find all documents that is_deleted field is False
        return list(self.collection.find(filter=filter, projection=projection, sort=sort))