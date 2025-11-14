import time
from typing import Dict, Optional
from fastapi import HTTPException, Request
from datetime import datetime, timedelta


class RateLimiter:
    def __init__(self, calls: int = 10, period: int = 60):
        """
        Rate limiter implementation
        :param calls: Number of calls allowed
        :param period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.requests: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier"""
        current_time = datetime.now()
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < timedelta(seconds=self.period)
            ]
        else:
            self.requests[identifier] = []

        # Check if under limit
        if len(self.requests[identifier]) < self.calls:
            self.requests[identifier].append(current_time)
            return True
        
        return False

    def get_reset_time(self, identifier: str) -> Optional[datetime]:
        """Get when rate limit resets for identifier"""
        if identifier not in self.requests or not self.requests[identifier]:
            return None
        
        oldest_request = min(self.requests[identifier])
        return oldest_request + timedelta(seconds=self.period)


# Global rate limiter instance
rate_limiter = RateLimiter(calls=5, period=60)  # 5 calls per minute


async def check_rate_limit(request: Request, user_id: str = None):
    """Rate limiting middleware"""
    # Use user ID if authenticated, otherwise use IP
    identifier = user_id if user_id else request.client.host
    
    if not rate_limiter.is_allowed(identifier):
        reset_time = rate_limiter.get_reset_time(identifier)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {rate_limiter.calls} per {rate_limiter.period} seconds",
                "reset_time": reset_time.isoformat() if reset_time else None
            }
        )
    
    return True