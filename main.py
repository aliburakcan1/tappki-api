from fastapi import FastAPI, Header
from pydantic import BaseModel  
from typing import List, Annotated
from fastapi.middleware.cors import CORSMiddleware
import requests
from config import ATLAS_USERNAME, ATLAS_PASSWORD, ATLAS_DATABASE
from pymongo import MongoClient
import time
import random
from video_retriever import VideoRetriever
from loguru import logger


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


#videos = list(find_all())
retriever = VideoRetriever("reaction", "annotation")
link_retriever = VideoRetriever("reaction", "tweet", link_retriever=True)
suggestions = None

@app.get("/api/videos", response_model=VideoResponse)  
@logger.catch
def get_videos(query: str = None, page: int = 1, limit: int = 12, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | query: {query}, page: {page}, limit: {limit}")
    if not query:  
        query = "lütfunda"
    
    filtered_videos = retriever.search(query, X_Session_Id)#['hits']
    total_videos = len(filtered_videos)  
    start_index = (page - 1) * limit  
    end_index = start_index + limit  
  
    # Slice the filtered_videos list according to the current page and limit  
    paginated_videos = filtered_videos[start_index:end_index]  
  
    for item in paginated_videos:  
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']  
    
    logger.info(f"Session: {X_Session_Id} | total_videos: {total_videos} paginated_videos: {len(paginated_videos)}")

    # Return the paginated videos and the total number of videos  
    return {"videos": paginated_videos, "total": total_videos}  

@app.get("/api/get_download_link")
@logger.catch
def get_download_link(videoId: str, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked videoId to download: {videoId}")
    user_tweet_status = videoId
    download_link = link_retriever.retrieve_download_link(user_tweet_status, X_Session_Id)
    logger.info(f"Session: {X_Session_Id} | download_link: {download_link}")
    return download_link
    
@app.get("/api/get_random_reaction")
@logger.catch
def get_random_reaction(X_Session_Id: Annotated[str | None, Header()] = None):
    random_id = retriever.retrieve_random_one(X_Session_Id)
    logger.info(f"Session: {X_Session_Id} | random_id: {random_id}")
    return random_id

@app.get("/api/suggestions")
@logger.catch
def get_suggestions(X_Session_Id: Annotated[str | None, Header()] = None):
    global suggestions
    if suggestions is None:
        suggestions = retriever.retrieve_filters()
        suggestions = {k: list(v) for k, v in suggestions.items()}
        logger.info(f"Session: {X_Session_Id} | suggestions: {[(k, random.sample(v, 3)) for k, v in suggestions.items()]}")
    return suggestions

@app.post("/api/get_annotation")
@logger.catch
def get_annotation(tweetId: dict, X_Session_Id: Annotated[str | None, Header()] = None):
    logger.info(f"Session: {X_Session_Id} | Asked videoId for its annotation: {tweetId.get('tweet_id')}")
    user_tweet_status = tweetId.get('tweet_id')
    annotation = retriever.retrieve_annotation(user_tweet_status, X_Session_Id)
    logger.info(f"Session: {X_Session_Id} | annotation: {annotation}")
    return annotation