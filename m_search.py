import meilisearch
from config import MEILISEARCH_MASTER_KEY, MEILISEARCH_HOSTNAME
from loguru import logger

class MSearch:
    def __init__(self, annotations):
        self.msearch_client = meilisearch.Client(MEILISEARCH_HOSTNAME, MEILISEARCH_MASTER_KEY)
        msearch_indexes = self.msearch_client.get_raw_indexes()
        if "reaction_index" not in msearch_indexes:
            self.msearch_client.create_index("reaction_index")
            self.msearch_index = self.msearch_client.index("reaction_index")
            self.msearch_index.add_documents(annotations)
        else:
            self.msearch_index = self.msearch_client.index("reaction_index")


    @logger.catch
    def search(self, query, X_Session_Id):
        logger.info(f"Session: {X_Session_Id} | query is being searched: {query}")
        documents = self.msearch_index.search(query, {"limit": 100})
        #logger.info(f"documents are retrieved: {documents}")
        return documents['hits']