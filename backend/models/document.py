from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    content_type: str

class DocumentCreate(DocumentBase):
    extracted_text: str
    keywords: List[str]
    summary: str

class DocumentInDB(DocumentCreate):
    id: Optional[str] = Field(None, alias="_id")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str # User ID

class DocumentResponse(DocumentInDB):
    id: str

    class Config:
        populate_by_name = True
