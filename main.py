from fastapi import FastAPI  
from pydantic import BaseModel  
from typing import List
from fastapi.middleware.cors import CORSMiddleware

  
app = FastAPI()  

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
  
class Video(BaseModel):  
    id: str  
    title: str  
    description: str  
    thumbnail_url: str  
  
videos = [  
    {  
        "id": "1",  
        "title": "Video 1",  
        "description": "This is a sample video 1.",  
        "thumbnail_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",  
    },  
    {  
        "id": "2",  
        "title": "Video 2",  
        "description": "This is a sample video 2.",  
        "thumbnail_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",  
    },  
    {  
        "id": "3",  
        "title": "Video 3",  
        "description": "This is a sample video 3.",  
        "thumbnail_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",  
    },
    {  
        "id": "4",  
        "title": "Video 1",  
        "description": "This is a sample video 1.",  
        "thumbnail_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",  
    },  
    {  
        "id": "5",  
        "title": "Video 2",  
        "description": "This is a sample video 2.",  
        "thumbnail_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",  
    },  
    {  
        "id": "6",  
        "title": "Video 3",  
        "description": "This is a sample video 3.",  
        "thumbnail_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",  
    },
]  
  
@app.get("/api/videos", response_model=List[Video])  
def get_videos(query: str = None):
    print("q: ", query)
    if query:  
        filtered_videos = [video for video in videos if query.lower() in video["title"].lower()]  
        return filtered_videos  
    return videos  

