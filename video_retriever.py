from config import MEILISEARCH_MASTER_KEY
import os
#import meilisearch
import subprocess
import time
from pymongo import MongoClient
from config import ATLAS_USERNAME, ATLAS_PASSWORD, ATLAS_DATABASE
import socket
from loguru import logger

class VideoRetriever:

    @logger.catch
    def __init__(self, mongo_db, mongo_db_collection) -> None:
        #subprocess.Popen(["./meilisearch", f"--master-key={MEILISEARCH_MASTER_KEY}"])
        #time.sleep(1)
        #self.msearch_client = meilisearch.Client('http://localhost:7700', MEILISEARCH_MASTER_KEY)
        #print(self.msearch_client.version())
        self.mongo_uri = f"mongodb+srv://{ATLAS_USERNAME}:{ATLAS_PASSWORD}@{ATLAS_DATABASE}.mongodb.net/?retryWrites=true&w=majority"
        self.mongo_client = MongoClient(self.mongo_uri)
        self.mongo_db = self.mongo_client[mongo_db]
        self.mongo_db_collection = self.mongo_db[mongo_db_collection]
        #self.mongo_db_query = {"title": {"$ne": ""}}
        #self.mongo_db_sort = [("_id", -1)]
        #self.mongo_db_project = {"_id": 0}
        #self.mongo_db_documents = self.mongo_db_collection.find(self.mongo_db_query, sort=self.mongo_db_sort, projection=self.mongo_db_project)
        #self.msearch_documents = list(self.mongo_db_documents)
        #self.index.add_documents(documents=documents)
        #self.msearch_client.delete_index("videos")
        #self.msearch_index = self.msearch_client.index('videos')
        #self.msearch_index.add_documents(self.msearch_documents)
        #print(self.msearch_client.get_task(0))
    
    @logger.catch
    def search(self, query):
        logger.info(f"query is being searched: {query}")
        documents = self.mongo_db_collection.aggregate([
                {
                        "$search": {
                            "index": "tappki_index",
                            "text": {
                                "query": query,
                                "path": {
                                "wildcard": "*"
                                }
                            }
                            }
                    }, {
                        '$limit': 100
                    }, {
                        "$match": {
                            "$expr": {
                                "$not": {
                                    "$eq": [
                                        "$title", ""
                                    ]
                                }
                            }
                        }
                    }, {
                        '$sort': {
                            '_id': -1
                        }
                    }
                ])
        #logger.info(f"documents are retrieved: {documents}")
        return list(documents)

    @logger.catch
    def retrieve_download_link(self, tweet_id):
        logger.info(f"tweet_id is being asked to download: {tweet_id}")
        # Find the tweet_id's that match the tweet_id
        query = {"tweet_id": tweet_id}
        projection = {"_id": 0, "download_link": 1}
        documents = self.mongo_db_collection.find(query, projection)
        return list(documents)[0]['download_link']
