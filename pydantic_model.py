from pydantic import BaseModel  
from typing import List

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

class LastAddedQuery(BaseModel):
    page: int
    limit: int