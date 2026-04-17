import os
import pdfplumber
import docx
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
import re
import math
from PIL import Image
import pytesseract
from ai.engine import ai_engine, ensure_nltk_resources

# NLTK resources are handled by ai_engine.ensure_nltk_resources()

class DocumentProcessor:
    @staticmethod
    def extract_text(file_path: str, content_type: str) -> str:
        text = ""
        try:
            if content_type == "application/pdf":
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                        else:
                            # Fallback to OCR if text extraction fails (scanned PDF)
                            img = page.to_image(resolution=300).original
                            text += pytesseract.image_to_string(img) + "\n"
                            
            elif content_type in ["image/jpeg", "image/png"]:
                text = pytesseract.image_to_string(Image.open(file_path))
                
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
                    
            elif content_type == "text/plain":
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                # Catch-all for unsupported types to prevent 'Pending' status
                return f"[Unsupported Format: {content_type}]"
                    
        except Exception as e:
            return f"[Extraction Error: {str(e)}]"
            
        return text.strip() if text else "[No text content found]"

    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        if not text or len(text) < 10:
            return []
        
        # Enhanced TF-IDF with better preprocessing
        stop_words = list(stopwords.words('english'))
        # Custom cleaning for enterprise text
        clean_text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        tfidf = TfidfVectorizer(stop_words=stop_words, max_features=top_n, ngram_range=(1, 2))
        
        try:
            tfidf.fit_transform([clean_text])
            feature_names = tfidf.get_feature_names_out()
            return feature_names.tolist()
        except Exception:
            # Fallback to Frequency analysis
            words = re.findall(r'\w+', clean_text)
            freq_dist = nltk.FreqDist(w for w in words if w not in stop_words and len(w) > 3)
            return [w for w, f in freq_dist.most_common(top_n)]

    @staticmethod
    async def generate_summary(text: str) -> str:
        if not text:
            return "No text content available for analysis."
            
        if text.startswith("[Unsupported Format"):
            return "This file format (Legacy Word .doc) is not supported. Please convert to .docx or PDF for AI analysis."

        if text.startswith("[Extraction Error"):
            return "The system encountered an error reading this file. It may be corrupted or password-protected."
        
        # Use the powerful transformer-based summarizer from the AI engine
        try:
            return await ai_engine.summarize_text(text)
        except Exception:
            # Fallback to extractive if AI engine is busy/failing
            sentences = re.split(r'(?<=[.!?]) +', text)
            return " ".join(sentences[:3])

doc_processor = DocumentProcessor()
