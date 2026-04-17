import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime
import logging
import gc

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import nltk
from nltk.tokenize import sent_tokenize

import nltk
from nltk.tokenize import sent_tokenize
import zipfile

# Production logging
logger = logging.getLogger(__name__)

# Resilient NLTK resource loading
def ensure_nltk_resources():
    resources = ['tokenizers/punkt', 'corpora/stopwords']
    for res in resources:
        try:
            nltk.data.find(res)
        except (LookupError, zipfile.BadZipFile):
            logger.info(f"Downloading/Fixing NLTK resource: {res}")
            name = res.split('/')[-1]
            nltk.download(name, quiet=True)

ensure_nltk_resources()

class ChatAIEngine:
    def __init__(self):
        self.embed_model = None
        self.tokenizer = None
        self.gen_model = None
        self.generator = None
        self.summarizer = None
        self.embedding_cache = {} # Context-aware cache for documents
        self.last_indexed_count = 0
        
        # Bad language blacklist
        self.blacklist = ["abuse", "stupid", "idiot", "nonsense", "kill", "porn"] 
        
        # Model IDs
        self.embed_model_name = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
        self.gen_model_id = "google/flan-t5-small"
        self.sum_model_id = "sshleifer/distilbart-cnn-12-6"

    def _load_models(self):
        """Lazy load models with error resilience for hardware constraints."""
        try:
            if self.embed_model is None:
                logger.info(f"Loading embedding model: {self.embed_model_name}")
                self.embed_model = SentenceTransformer(self.embed_model_name)
                gc.collect()

            if self.generator is None:
                logger.info(f"Loading generative model: {self.gen_model_id}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.gen_model_id)
                self.gen_model = AutoModelForSeq2SeqLM.from_pretrained(self.gen_model_id)
                self.generator = pipeline(
                    "text-generation", 
                    model=self.gen_model, 
                    tokenizer=self.tokenizer,
                    device=-1 # CPU
                )
                gc.collect()
                
            if self.summarizer is None:
                logger.info("Loading summarizer model...")
                self.summarizer = pipeline("summarization", model=self.sum_model_id, device=-1)
                gc.collect()
        except Exception as e:
            logger.error(f"AI Model load warning: {e}")
            # Do not raise - allow system to run in Lightweight Mode
            self.embed_model = None
            self.generator = None

    def detect_intent(self, query: str) -> str:
        """Heuristic intent detection for enterprise routing."""
        query_low = query.lower().strip()
        if any(w in query_low for w in ["hi", "hello", "hey", "greetings"]):
            return "GREETING"
        elif any(w in query_low for w in ["how to", "policy", "limit", "procedure", "what is the", "tell me about"]):
            return "INTERNAL_DOC_QUERY"
        elif any(w in query_low for w in ["summarize", "summary", "shorten"]):
            return "SUMMARIZE"
        return "GENERAL_CHAT"

    def filter_bad_language(self, text: str) -> Tuple[bool, str]:
        words = text.lower().split()
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word in self.blacklist:
                logger.warning(f"Bad language violation detected: {clean_word}")
                return True, "I apologize, but I cannot process messages containing offensive language. Please keep our conversation professional."
        return False, text

    async def get_relevant_context(self, query: str, db) -> str:
        self._load_models()
        
        if db is None:
            return ""

        documents = []
        try:
            cursor = db.documents.find({}, {"extracted_text": 1, "filename": 1})
            async for doc in cursor:
                documents.append(doc)
        except Exception as e:
            logger.error(f"Failed to fetch documents from DB: {e}")
            return ""
            
        if not documents:
            return ""

        # Advanced Overlapping Chunking Strategy
        all_chunks = []
        chunk_size = 512
        overlap = 100
        
        for doc in documents:
            text = doc["extracted_text"]
            # Character based overlap for robustness
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i + chunk_size]
                if len(chunk) > 50: # Ignore tiny fragments
                    all_chunks.append({"text": chunk.strip(), "source": doc["filename"]})

        if not all_chunks:
            return ""

        # Retrieval Phase
        try:
            if self.embed_model:
                # Semantic Search (High Quality with Caching)
                chunk_texts = [c["text"] for c in all_chunks]
                
                # Check if cache is valid (simple doc count check for demo)
                if len(documents) != self.last_indexed_count or not self.embedding_cache:
                    logger.info(" [.] AI: Re-indexing Knowledge Base into Neural Cache...")
                    self.embedding_cache = self.embed_model.encode(chunk_texts, convert_to_tensor=True)
                    self.last_indexed_count = len(documents)
                
                query_embedding = self.embed_model.encode(query, convert_to_tensor=True)
                chunk_embeddings = self.embedding_cache # Use cached embeddings
                
                hits = util.semantic_search(query_embedding, chunk_embeddings, top_k=3)[0]
                
                context = ""
                for hit in hits:
                    if hit['score'] > 0.35:
                        matched_chunk = all_chunks[hit['corpus_id']]
                        context += f"[Ref: {matched_chunk['source']}] {matched_chunk['text']} "
                return context.strip()
            else:
                # Keyword Fallback (High Reliability)
                logger.warning("Embedding model not ready, using keyword-weighted retrieval.")
                query_words = set(re.findall(r'\w+', query.lower()))
                scored_chunks = []
                for chunk in all_chunks:
                    chunk_words = set(re.findall(r'\w+', chunk['text'].lower()))
                    score = len(query_words.intersection(chunk_words))
                    if score > 0:
                        scored_chunks.append((score, chunk))
                
                scored_chunks.sort(key=lambda x: x[0], reverse=True)
                context = ""
                for _, chunk in scored_chunks[:2]: # Top 2 keyword matches
                    context += f"[Ref: {chunk['source']}] {chunk['text']} "
                return context.strip()
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return ""

    async def summarize_text(self, text: str) -> str:
        self._load_models()
        if len(text) < 100:
            return text
            
        try:
            # Check if transformer model is ready
            if not self.summarizer:
                logger.warning(" [!] Summarization model not loaded. Using Extractive Fallback.")
                # Fast Extractive Fallback: Take first 3 sentences for demo professionalism
                sentences = text.split('.')[:3]
                fallback_summary = ". ".join(sentences).strip() + "."
                return fallback_summary if len(fallback_summary) > 20 else text[:150] + "..."

            # Transformer Summarization (High Quality)
            # Handle long docs by taking safe window for the summarizer
            input_text = text[:1500] 
            summary = self.summarizer(input_text, max_length=130, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            logger.error(f"Summarization crash: {e}")
            # Absolute Fail-Safe fallback
            return text[:200] + "... [Preview Mode]"

    async def generate_response(self, query: str, context: str, history: List[Dict]) -> str:
        self._load_models()

        # Build Session Memory Context
        history_context = ""
        if history:
            for msg in history[-3:]: # Last 3 messages for context
                history_context += f"{'User' if msg['is_user'] else 'Assistant'}: {msg['content']}\n"

        # Construct Agentic Prompt
        intent = self.detect_intent(query)
        
        if intent == "GREETING":
            prompt = f"User: {query}\nAssistant: Hello! I am your Enterprise AI Assistant. How can I help you today?"
        elif intent == "INTERNAL_DOC_QUERY" and context:
            prompt = f"Instruction: Use the context below to answer professionally.\nContext: {context}\nUser: {query}\nResponse:"
        else:
            prompt = f"Instruction: Respond as a professional assistant.\nUser: {query}\nResponse:"

        try:
            if not self.generator:
                logger.warning("Generative AI not ready, using direct synthesis.")
                if context:
                    # Professional synthesis of retrieved context
                    synthesis = f"Based on the internal company records I've accessed:\n\n{context[:400]}..."
                    return synthesis
                return "The Enterprise Assistant is ready. How can I help you with your company documents and policies today?"

            # Optimized for Demo Speed: num_beams=1 for instant response
            outputs = self.generator(prompt, max_length=120, num_beams=1, do_sample=False)
            response = outputs[0]['generated_text']
            
            if not response:
                return "I'm sorry, I couldn't formulate a clear answer based on the documents. Please rephrase."
                
            return response
        except Exception as e:
            logger.error(f"Inference crash: {e}")
            return "The AI engine encountered a resource error. Please try again in 30 seconds."

ai_engine = ChatAIEngine()
