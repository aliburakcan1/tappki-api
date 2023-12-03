import meilisearch
from config import MEILISEARCH_MASTER_KEY, MEILISEARCH_HOSTNAME
from loguru import logger

class MSearch:
    def __init__(self, annotations):
        self.msearch_client = meilisearch.Client(MEILISEARCH_HOSTNAME, MEILISEARCH_MASTER_KEY)
        #msearch_indexes = self.msearch_client.get_raw_indexes()
        try:
            self.msearch_client.get_index("reaction_index")
            self.msearch_client.delete_index("reaction_index")
        except:
            logger.info("Index is not found.")
        finally:
            self.msearch_client.create_index("reaction_index")
        self.msearch_index = self.msearch_client.index("reaction_index")
        #index_stats = self.msearch_index.get_stats()
        #self.number_of_documents = -1
        #for i in index_stats:
        #    if i[0] == "number_of_documents":
        #        self.number_of_documents = i[1]
        #        break
        #if number_of_documents != len(annotations):
        self.msearch_index.add_documents(annotations)
    
    def add_documents(self, documents):
        logger.info(f"INDEX_UPDATE | Number of documents in index: {self.number_of_documents}")
        self.msearch_index.add_documents(documents)
        #index_stats = self.msearch_index.get_stats()
        #for i in index_stats:
        #    if i[0] == "number_of_documents":
        #        self.number_of_documents = i[1]
        #        break
        logger.info(f"INDEX_UPDATE | New documents are added. Number of documents in index: {self.number_of_documents}")

    @logger.catch
    def search(self, query, X_Session_Id):
        logger.info(f"Session: {X_Session_Id} | query is being searched: {query}")
        documents = self.msearch_index.search(query, {"limit": 100})
        #logger.info(f"documents are retrieved: {documents}")
        return documents['hits']