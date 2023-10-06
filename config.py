from dotenv import load_dotenv
import os

print(os.environ.get("APP_ENV"))
if os.environ.get("APP_ENV") == 'prod':
    load_dotenv('.env.prod')
else:
    print("dev")
    load_dotenv('.env.dev')


ATLAS_USERNAME = os.environ.get("ATLAS_USERNAME")
ATLAS_PASSWORD = os.environ.get("ATLAS_PASSWORD")
ATLAS_DATABASE = os.environ.get("ATLAS_DATABASE")
MEILISEARCH_MASTER_KEY = os.environ.get("MEILISEARCH_MASTER_KEY")