from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import shutil
from database.mongodb import get_database
from services.document_processor import doc_processor
from models.document import DocumentCreate, DocumentResponse
from utils.auth import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from bson import ObjectId

router = APIRouter()
security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(auth.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete documents")
    
    try:
        result = await db.documents.delete_one({"_id": ObjectId(doc_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...), 
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload documents")

    # Temporary save for processing
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process document
        text = doc_processor.extract_text(temp_path, file.content_type)
        keywords = doc_processor.extract_keywords(text)
        summary = await doc_processor.generate_summary(text)
        
        doc_data = {
            "filename": file.filename,
            "content_type": file.content_type,
            "extracted_text": text,
            "keywords": keywords,
            "summary": summary,
            "uploaded_by": current_user["sub"]
        }
        
        result = await db.documents.insert_one(doc_data)
        created_doc = await db.documents.find_one({"_id": result.inserted_id})
        created_doc["id"] = str(created_doc["_id"])
        
        return created_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(db = Depends(get_database), current_user = Depends(get_current_user)):
    cursor = db.documents.find()
    docs = []
    async for document in cursor:
        document["id"] = str(document["_id"])
        docs.append(document)
    return docs
