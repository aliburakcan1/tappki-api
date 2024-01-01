from fastapi import FastAPI, Header
from typing import Annotated
from pydantic_model import Video, VideoResponse, VideoQuery, SuggestionResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import random
from m_search import MSearch
from loguru import logger
from db_handler import MongoDBHandler
from apscheduler.schedulers.background import BackgroundScheduler

logger.add("logs/tepki.log", format = "{time} | {level} | {message}" , rotation="1 day", backtrace=True, diagnose=True)
app = FastAPI()  
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
scheduler = BackgroundScheduler()
tweets = MongoDBHandler("reaction", "tweet").find(filter={"is_deleted": False})
reaction_annotation = MongoDBHandler("reaction", "annotation")
annotations = reaction_annotation.find()
annotations = [i for i in annotations if i["tweet_id"] in [j["id"] for j in tweets]]

m_search = MSearch(annotations)
annotation_count = len(annotations)
logger.info(f"INITIAL | Number of documents: {annotation_count}")

def add_docs_to_index():
    global annotation_count
    new_annotation_count = reaction_annotation.count_documents()
    logger.info(f"Number of documents: {new_annotation_count}")
    if new_annotation_count > annotation_count:
        new_docs = reaction_annotation.last_document(n = new_annotation_count - annotation_count)
        m_search.add_documents(new_docs)
        annotation_count = new_annotation_count
        logger.info(f"INDEX_UPDATE | New documents are added. Number of documents: {new_annotation_count}")
    else:
        logger.info(f"INDEX_UPDATE | No new documents are added. Number of documents: {new_annotation_count}")

def update_variables():
    global tweets
    global annotations
    tweets = MongoDBHandler("reaction", "tweet").find(filter={"is_deleted": False})
    logger.info(f"UPDATE_VARIABLES | Tweets are updated. Number of tweets: {len(tweets)}")
    annotations = reaction_annotation.find()
    annotations = [i for i in annotations if i["tweet_id"] in [j["id"] for j in tweets]]
    logger.info(f"UPDATE_VARIABLES | Annotations are updated. Number of annotations: {len(annotations)}")

scheduler.add_job(add_docs_to_index, 'interval', minutes=30)
scheduler.add_job(update_variables, 'cron', hour=5)
scheduler.start()

videos_per_page = 5

@app.post("/api/videos", response_model=VideoResponse)
@logger.catch
def get_videos(params: VideoQuery, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | query: {params.query}, page: {params.page}, videos_per_page: {videos_per_page}")
    if not params.query:  
        params.query = "lütfunda"
    
    filtered_videos = m_search.search(params.query, X_Session_Id)#['hits']
    total_videos = len(filtered_videos)  
    start_index = (params.page - 1) * videos_per_page
    end_index = start_index + videos_per_page
  
    # Slice the filtered_videos list according to the current page and limit  
    paginated_videos = filtered_videos[start_index:end_index]  
  
    for item in paginated_videos:  
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']  
    
    logger.info(f"Session: {X_Session_Id} | total_videos: {total_videos} paginated_videos: {len(paginated_videos)}")

    # Return the paginated videos and the total number of videos  
    return {"videos": paginated_videos, "total": total_videos, "videos_per_page": videos_per_page}

@app.post("/api/one_reaction")
@logger.catch
def get_reaction_video(params: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | id for one reaction: {params.get('video_id')}")
    user_tweet_status = params.get('video_id')
    details = [i for i in annotations if i["tweet_id"] == user_tweet_status]
    detail = details[0] if len(details) > 0 else None
    logger.info(f"Session: {X_Session_Id} | detail: {detail}")
    return detail

@app.post("/api/get_download_link")
@logger.catch
def get_download_link(params: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked videoId to download: {params.get('video_id')}")
    user_tweet_status = params.get('video_id')
    download_links = [i["download_link"] for i in tweets if i["id"] == user_tweet_status]
    download_link = download_links[0] if len(download_links) > 0 else None
    logger.info(f"Session: {X_Session_Id} | download_link: {download_link}")
    return download_link
    
@app.get("/api/get_random_reaction")
@logger.catch
def get_random_reaction(X_Session_Id: Annotated[str | None, Header()] = None):
    random_id = random.choice(tweets)["id"]
    logger.info(f"Session: {X_Session_Id} | random_id: {random_id}")
    return random_id


suggestions = None

@app.post("/api/suggestions", response_model=SuggestionResponse)
@logger.catch
def get_suggestions(X_Session_Id: Annotated[str | None, Header()] = None):
    global suggestions
    if suggestions is None:
        ret_dict = {
            "people": set(),
            "tags": set(),
            "program": set(),
            "music": set(),
            "animal": set(),
            "sport": set()
        }
        for doc in annotations:
            for k, v in doc.items():
                if k in ret_dict.keys():
                    if isinstance(v, list):
                        ret_dict[k].update(set([i.strip() for i in v if (i.strip() != "") and (i != "-") and (i != "Yok")]))
                    else:
                        if (v.strip() != "") and (v.strip() != "-") and (v.strip() != "Yok"):
                            ret_dict[k].add(v.strip())
        suggestions = {k: list(v) for k, v in ret_dict.items()}
        suggestions["reaction"] = []
    ret_val = {k: random.sample(v, 2) if len(v)>2 else v for k, v in suggestions.items()}
    logger.info(f"Session: {X_Session_Id} | suggestions: {ret_val}")
    return ret_val

##@app.post("/api/get_annotation")
##@logger.catch
##def get_annotation(tweetId: dict, X_Session_Id: Annotated[str | None, Header()] = None):
##    logger.info(f"Session: {X_Session_Id} | Asked videoId for its annotation: {tweetId.get('tweet_id')}")
##    user_tweet_status = tweetId.get('tweet_id')
##    annotation_l = [i for i in annotations if i["tweet_id"] == user_tweet_status]
##    annotation = annotation_l[0] if len(annotation_l) > 0 else None
##    logger.info(f"Session: {X_Session_Id} | annotation: {annotation}")
##    return annotation

@app.post("/api/get_video_details")
@logger.catch
def get_video_details(tweetId: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked videoId for its details: {tweetId.get('tweet_id')}")
    user_tweet_status = tweetId.get('tweet_id')
    annotation_l = [i for i in annotations if i["tweet_id"] == user_tweet_status]
    annotation = annotation_l[0] if len(annotation_l) > 0 else None
    ret_val = {k:v if v not in ("Yok", "-", "", []) else None for k, v in annotation.items() if (k == "program") or (k == "music") or (k == "animal") or (k == "people")}
    logger.info(f"Session: {X_Session_Id} | video details: {ret_val}")
    return ret_val

@app.post("/api/get_popular_videos")
@logger.catch
def get_popular_videos(rangeFilter: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked {rangeFilter.get('range_filter')} popular videos")
    range_filter = rangeFilter.get('range_filter')
    now = time.time() - 60*60*24*60
    if range_filter == "weekly":
        start_date = now- 7*24*60*60
        end_date = now
    elif range_filter == "monthly":
        start_date = now - 30*24*60*60
        end_date = now
    elif range_filter == "daily":
        start_date = now - 24*60*60
        end_date = now
    
    popular_videos = sorted(tweets, key=lambda i: i['views'] if isinstance(i["views"], int) else 0, reverse=True)
    popular_video_statuses = [i["id"] for i in popular_videos if (i['timestamp'] >= start_date) and (i['timestamp'] <= end_date)][:400]
    popular_videos_annotation = [i for i in annotations if i["tweet_id"] in popular_video_statuses][:videos_per_page]
    for item in popular_videos_annotation:  
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']  
    #logger.info(f"Session: {X_Session_Id} | popular_videos_annotation: {popular_videos_annotation}")
    return {"videos": popular_videos_annotation} 