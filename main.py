from fastapi import FastAPI  
from pydantic import BaseModel  
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import requests
from config import ATLAS_USERNAME, ATLAS_PASSWORD, ATLAS_DATABASE
from pymongo import MongoClient
import time
import random

  
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


def get_db():
    uri = f"mongodb+srv://{ATLAS_USERNAME}:{ATLAS_PASSWORD}@{ATLAS_DATABASE}.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client.tepki
    return db

def get_collection():
    db = get_db()
    collection = db.video
    return collection

def find_all():
    collection = get_collection()
    return collection.find({}, {"_id": 0})

def find_one(id):
    collection = get_collection()
    return collection.find_one({"_id": id})

def find_top_n(n):
    collection = get_collection()
    return collection.find({}, {"_id":-1, "_id": 0}).limit(n)



@app.get("/api/annotations", response_model=List[Video])
def get_annotations():
    ret_val = list(find_top_n(50))
    for item in ret_val:
        #item['html'] = get_tweet_html(item['tweet_id'])
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']
    return ret_val


videos = list(find_all())

@app.get("/api/videos", response_model=VideoResponse)  
def get_videos(query: str = None, page: int = 1, limit: int = 12):  
    if query:  
        filtered_videos = [video for video in videos if query.lower() in video["content"].lower()]  
    else:  
        filtered_videos = random.sample(videos, 12)
  
    total_videos = len(filtered_videos)  
    start_index = (page - 1) * limit  
    end_index = start_index + limit  
  
    # Slice the filtered_videos list according to the current page and limit  
    paginated_videos = filtered_videos[start_index:end_index]  
  
    for item in paginated_videos:  
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']  
  
    # Return the paginated videos and the total number of videos  
    return {"videos": paginated_videos, "total": total_videos}  


