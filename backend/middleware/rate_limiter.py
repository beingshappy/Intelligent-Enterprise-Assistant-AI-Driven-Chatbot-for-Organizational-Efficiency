import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

class SimpleRateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.limit = requests_per_minute
        self.history = {}

    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        
        if client_ip not in self.history:
            self.history[client_ip] = []
        
        # Keep only timestamps within the last minute
        self.history[client_ip] = [t for t in self.history[client_ip] if now - t < 60]
        
        if len(self.history[client_ip]) >= self.limit:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please wait a minute before sending more messages."
            )
        
        self.history[client_ip].append(now)

rate_limiter = SimpleRateLimiter(requests_per_minute=10)
