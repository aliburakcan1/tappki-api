from fastapi import FastAPI, Header
from pydantic import BaseModel  
from typing import List, Annotated
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import random
from mongo_db_retriever import MongoDbRetriever
from m_search import MSearch
from loguru import logger
from config import ATLAS_USERNAME, ATLAS_PASSWORD, ATLAS_DATABASE
from pymongo import MongoClient


logger.add("logs/tepki.log", format = "{time} | {level} | {message}" , rotation="1 day", backtrace=True, diagnose=True)


app = FastAPI()  

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Video(BaseModel):
    tweet_id: str
    title: str
    content: str
    people: List[str]
    tags: List[str]
    program: str
    music: str
    animal: str
    sport: str
    url: str

class VideoResponse(BaseModel):  
    videos: List[Video]  
    total: int

class VideoQuery(BaseModel):
    query: str
    page: int
    limit: int

class SuggestionResponse(BaseModel):
    people: List[str]
    tags: List[str]
    program: List[str]
    music: List[str]
    animal: List[str]
    sport: List[str]
    reaction: List[str]

@logger.catch
def get_tweet_html(tweet_id):
    url = "https://twitter.com/i/status/" + tweet_id
    try:
        api = "https://publish.twitter.com/oembed?url={}".format(url)
        print(api)
        response = requests.get(api)
        html = response.json()['html']
    except:
        print("Tweet not found. Trying again.", url)
        html = f"<blockquote class='missing'>This tweet {url} is no longer available.</blockquote>"
    return html

@logger.catch
def mongo_db_init(db_name, collection_name):
    uri = f"mongodb+srv://{ATLAS_USERNAME}:{ATLAS_PASSWORD}@{ATLAS_DATABASE}.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    sort = [("_id", -1)]
    projection = {"_id": 0}
    docs = collection.find(projection=projection, sort=sort)
    return list(docs)


#videos = list(find_all())
reaction_annotation = mongo_db_init("reaction", "annotation")
reaction_tweet = mongo_db_init("reaction", "tweet")
m_search = MSearch(reaction_annotation)

@app.post("/api/videos", response_model=VideoResponse)
@logger.catch
def get_videos(params: VideoQuery, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | query: {params.query}, page: {params.page}, limit: {params.limit}")
    if not params.query:  
        params.query = "lütfunda"
    
    filtered_videos = m_search.search(params.query, X_Session_Id)#['hits']
    total_videos = len(filtered_videos)  
    start_index = (params.page - 1) * params.limit  
    end_index = start_index + params.limit  
  
    # Slice the filtered_videos list according to the current page and limit  
    paginated_videos = filtered_videos[start_index:end_index]  
  
    for item in paginated_videos:  
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']  
    
    logger.info(f"Session: {X_Session_Id} | total_videos: {total_videos} paginated_videos: {len(paginated_videos)}")

    # Return the paginated videos and the total number of videos  
    return {"videos": paginated_videos, "total": total_videos}

@app.post("/api/get_download_link")
@logger.catch
def get_download_link(params: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked videoId to download: {params.get('video_id')}")
    user_tweet_status = params.get('video_id')
    download_links = [i["download_link"] for i in reaction_tweet if i["id"] == user_tweet_status]
    download_link = download_links[0] if len(download_links) > 0 else None
    logger.info(f"Session: {X_Session_Id} | download_link: {download_link}")
    return download_link
    
@app.get("/api/get_random_reaction")
@logger.catch
def get_random_reaction(X_Session_Id: Annotated[str | None, Header()] = None):
    random_id = random.choice(reaction_tweet)["id"]
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
        for doc in reaction_annotation:
            for k, v in doc.items():
                if k in ret_dict.keys():
                    if isinstance(v, list):
                        ret_dict[k].update(set([i.strip() for i in v if (i.strip() != "") and (i != "-")]))
                    else:
                        if (v.strip() != "") and (v != "-"):
                            ret_dict[k].add(v.strip())
        suggestions = {k: list(v) for k, v in ret_dict.items()}
        suggestions["reaction"] = []
    logger.info(f"Session: {X_Session_Id} | suggestions: {[(k, random.sample(v, 2)) if len(v)>2 else (k, v) for k, v in suggestions.items()]}")
    return suggestions

@app.post("/api/get_annotation")
@logger.catch
def get_annotation(tweetId: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked videoId for its annotation: {tweetId.get('tweet_id')}")
    user_tweet_status = tweetId.get('tweet_id')
    annotations = [i for i in reaction_annotation if i["tweet_id"] == user_tweet_status]
    annotation = annotations[0] if len(annotations) > 0 else None
    logger.info(f"Session: {X_Session_Id} | annotation: {annotation}")
    return annotation

@app.post("/api/get_popular_videos")
@logger.catch
def get_popular_videos(rangeFilter: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked {rangeFilter.get('range_filter')} popular videos")
    range_filter = rangeFilter.get('range_filter')
    now = time.time() - 60*24*60*60
    if range_filter == "weekly":
        start_date = now- 7*24*60*60
        end_date = now
    elif range_filter == "monthly":
        start_date = now - 30*24*60*60
        end_date = now
    elif range_filter == "daily":
        start_date = now - 24*60*60
        end_date = now
    
    popular_videos = sorted(reaction_tweet, key=lambda i: i['views'] if isinstance(i["views"], int) else 0, reverse=True)
    popular_video_statuses = [i["id"] for i in popular_videos if (i['timestamp'] >= start_date) and (i['timestamp'] <= end_date)][:200]
    popular_videos_annotation = [i for i in reaction_annotation if i["tweet_id"] in popular_video_statuses][:9]

    for item in popular_videos_annotation:  
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']  
    #logger.info(f"Session: {X_Session_Id} | popular_videos_annotation: {popular_videos_annotation}")
    return {"videos": popular_videos_annotation} 