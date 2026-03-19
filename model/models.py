from pydantic import BaseModel, Field,RootModel
from typing import Optional, List, Dict, Any, Union


class Metadata(BaseModel):
    summary: List[str] = Field(default_factory=list, description="Summary of the document")
    title: Optional[str] = None
    author: Optional[str] = None
    date_created: Optional[str] = None
    last_modified_date: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[Union[int, str]] = None
    sentiment_tone: Optional[str] = None


class ChangeFormat(BaseModel):
    Page:str
    changes:str

class SummaryResponse(RootModel[List[ChangeFormat]]):
   pass