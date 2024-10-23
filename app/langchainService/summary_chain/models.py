from typing import List, Dict
from langchain.pydantic_v1 import BaseModel, Field

class Topics(BaseModel):
    topic_summaries: List[Dict[str, str]] = Field(description="List of dictionaries with two fields topics and their summaries")
   