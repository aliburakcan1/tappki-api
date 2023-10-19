from dotenv import load_dotenv
import os
from loguru import logger

logger.info(f"DEPLOY_ENV: {os.environ.get('DEPLOY_ENV')}")
logger.info(f"APP_ENV: {os.environ.get('APP_ENV')}")
if os.environ.get("DEPLOY_ENV") == 'digitalocean':
    pass
else:
    if os.environ.get("APP_ENV") == 'prod':
        load_dotenv('.env.prod')
    else:
        load_dotenv('.env.dev')


ATLAS_USERNAME = os.environ.get("ATLAS_USERNAME")
ATLAS_PASSWORD = os.environ.get("ATLAS_PASSWORD")
ATLAS_DATABASE = os.environ.get("ATLAS_DATABASE")
MEILISEARCH_MASTER_KEY = os.environ.get("MEILISEARCH_MASTER_KEY")
MEILISEARCH_HOSTNAME = os.environ.get("MEILISEARCH_HOSTNAME")