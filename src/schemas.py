from pydantic import BaseModel , ConfigDict , Field
from datetime import datetime

class PostBase(BaseModel):
    title : str = Field(min_length = 1 , max_length = 100)
    content : str = Field(min_length = 10)
    author : str = Field(min_length = 5 , max_length = 45)

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id : int
    date_posted : str