from config import MEILISEARCH_MASTER_KEY
import os
import meilisearch
import subprocess
import time
from pymongo import MongoClient
from config import ATLAS_USERNAME, ATLAS_PASSWORD, ATLAS_DATABASE, MEILISEARCH_MASTER_KEY, MEILISEARCH_HOSTNAME
import random
from loguru import logger

class VideoRetriever:

    @logger.catch
    def __init__(self, mongo_db, mongo_db_collection) -> None:
        #subprocess.Popen(["./meilisearch", f"--master-key={MEILISEARCH_MASTER_KEY}"])
        #time.sleep(1)
        self.msearch_client = meilisearch.Client(MEILISEARCH_HOSTNAME, MEILISEARCH_MASTER_KEY)
        #print(self.msearch_client.version())
        self.mongo_uri = f"mongodb+srv://{ATLAS_USERNAME}:{ATLAS_PASSWORD}@{ATLAS_DATABASE}.mongodb.net/?retryWrites=true&w=majority"
        self.mongo_client = MongoClient(self.mongo_uri)
        self.mongo_db = self.mongo_client[mongo_db]
        self.mongo_db_collection = self.mongo_db[mongo_db_collection]
        self.mongo_db_query = {"title": {"$ne": ""}}
        self.mongo_db_sort = [("_id", -1)]
        self.mongo_db_project = {"_id": 0}
        self.mongo_db_documents = self.mongo_db_collection.find(self.mongo_db_query, sort=self.mongo_db_sort, projection=self.mongo_db_project)
        self.msearch_documents = list(self.mongo_db_documents)
        #self.index.add_documents(documents=self.msearch_documents)
        self.msearch_client.delete_index("annotation_index")
        self.msearch_index = self.msearch_client.index('annotation_index')
        self.msearch_index.add_documents(self.msearch_documents)
        #print(self.msearch_client.get_task(0))
    
    @logger.catch
    def search(self, query, X_Session_Id):
        logger.info(f"Session: {X_Session_Id} | query is being searched: {query}")
        documents = self.msearch_index.search(query, {"limit": 100})
        #logger.info(f"documents are retrieved: {documents}")
        return documents['hits']
    
    @logger.catch
    def search_mongodb(self, query, X_Session_Id):
        logger.info(f"Session: {X_Session_Id} | query is being searched: {query}")
        documents = self.mongo_db_collection.aggregate([
                {
                        "$search": {
                            "index": "reaction_index",
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
    def retrieve_download_link(self, tweet_id, X_Session_Id):
        logger.info(f"Session: {X_Session_Id} | tweet_id is being asked to download: {tweet_id}")
        # Find the tweet_id's that match the tweet_id
        query = {"tweet_id": tweet_id}
        projection = {"_id": 0, "download_link": 1}
        documents = self.mongo_db_collection.find(query, projection)
        return list(documents)[0]['download_link']
    
    @logger.catch
    def retrieve_random_one(self, X_Session_Id):
        logger.info(f"Session: {X_Session_Id} | random video is being retrieved")
        # Find the tweet_id's that match the tweet_id
        #query = {"title": {"$ne": ""}}
        #projection = {"_id": 0, "tweet_id": 1, "download_link": 1}
        #documents = self.mongo_db_collection.find(query, projection)
        #return random.choice([i["tweet_id"] for i in list(documents)])
        document = self.mongo_db_collection.aggregate([
            {
            "$sample": {
            "size": 1
            }
        },
        {
                        "$match": {
                            "$expr": {
                                "$not": {
                                    "$eq": [
                                        "$title", ""
                                    ]
                                }
                            }
                        }
                    },
        ])
        return list(document)[0]['tweet_id']