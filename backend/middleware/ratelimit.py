from fastapi import Request, HTTPException
import time
from typing import Dict, Tuple

class RateLimiter:
    """Simple Enterprise Rate Limiter (Memory-based for Demo)."""
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.client_history: Dict[str, list] = {}

    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        current_time = time.time()
        
        # Initialize client if not seen
        if client_ip not in self.client_history:
            self.client_history[client_ip] = []
            
        # Clean up old requests
        self.client_history[client_ip] = [
            t for t in self.client_history[client_ip] 
            if t > current_time - 60
        ]
        
        # Check limit
        if len(self.client_history[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429, 
                detail="Too many requests. Enterprise AI safety policy: Please wait 60 seconds."
            )
            
        # Log this request
        self.client_history[client_ip].append(current_time)
        return True

limit_chat = RateLimiter(requests_per_minute=20)
limit_auth = RateLimiter(requests_per_minute=5)
