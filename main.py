from fastapi import FastAPI  
from pydantic import BaseModel  
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import requests
from env_vars import ATLAS_USERNAME, ATLAS_PASSWORD, ATLAS_DATABASE
from pymongo import MongoClient

  
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
    content: str
    url: str


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
    collection = db.annotation
    return collection

def find_all():
    collection = get_collection()
    return collection.find({}, {"_id": 0, "tweet_id":1, "content": 1})

def find_one(id):
    collection = get_collection()
    return collection.find_one({"_id": id})

def find_top_n(n):
    collection = get_collection()
    return collection.find({}, {"_id": 0, "tweet_id":1, "content": 1}).limit(n)

@app.get("/api/annotations", response_model=List[Video])
def get_annotations():
    ret_val = list(find_top_n(50))
    for item in ret_val:
        #item['html'] = get_tweet_html(item['tweet_id'])
        item['url'] = "https://twitter.com/i/status/" + item['tweet_id']
    return ret_val

@app.get("/api/videos", response_model=List[Video])  
def get_videos(query: str = None):
    if query:
        videos = list(find_all())
        filtered_videos = [video for video in videos if query.lower() in video["content"].lower()]
        for item in filtered_videos:
            item['url'] = "https://twitter.com/i/status/" + item['tweet_id']  
        return filtered_videos[:10]
    return videos  

