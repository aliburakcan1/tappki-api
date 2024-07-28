import meilisearch
from config import MEILISEARCH_MASTER_KEY, MEILISEARCH_HOSTNAME
from loguru import logger
import datetime

class MSearch:
    def __init__(self, index_name):
        self.index_name = index_name
        self.msearch_client = meilisearch.Client(MEILISEARCH_HOSTNAME, MEILISEARCH_MASTER_KEY)
        #msearch_indexes = self.msearch_client.get_raw_indexes()
        #try:
        #    self.msearch_client.get_index("reaction_index")
        #    self.msearch_client.delete_index("reaction_index")
        #except:
        #    logger.info("Index is not found.")
        #finally:
        #    self.msearch_client.create_index("reaction_index")
        self.msearch_index = self.msearch_client.index(index_name)
        logger.info(f"Index is found: {index_name}")
        #index_stats = self.msearch_index.get_stats()
        #self.number_of_documents = -1
        #for i in index_stats:
        #    if i[0] == "number_of_documents":
        #        self.number_of_documents = i[1]
        #        break
        #if number_of_documents != len(annotations):
        #self.msearch_index.add_documents(annotations)
    
    def add_documents(self, documents):
        #logger.info(f"INDEX_UPDATE | Number of documents in index: {self.number_of_documents}")
        for doc in documents:
            self.msearch_index.add_documents([doc])
        #index_stats = self.msearch_index.get_stats()
        #for i in index_stats:
        #    if i[0] == "number_of_documents":
        #        self.number_of_documents = i[1]
        #        break
        #logger.info(f"INDEX_UPDATE | New documents are added. Number of documents in index: {self.number_of_documents}")
    
    def update_index(self, reaction_annotation):
        results = self.msearch_index.get_documents({
            "fields": ["tweet_id"],
            "limit": 1000000000
        })
        #results = results.results
        ids = [i.tweet_id for i in results.results]
        annotations = reaction_annotation.find(
            filter={"tweet_id": {"$nin": ids}},
            projection={"_id": 0},
            limit=1000000000
        )
        if len(annotations) > 0:
            self.add_documents(annotations)

    @logger.catch
    def search(self, query, X_Session_Id):
        logger.info(f"Session: {X_Session_Id} | query is being searched: {query}")
        documents = self.msearch_index.search(query, {"limit": 100})
        #logger.info(f"documents are retrieved: {documents}")
        return documents['hits']