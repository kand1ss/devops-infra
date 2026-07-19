from pydantic import BaseModel, HttpUrl

class CreateLink(BaseModel):
    original_url: HttpUrl

class CreateLinkOut(BaseModel):
    original_url: HttpUrl
    shorted_url: HttpUrl
