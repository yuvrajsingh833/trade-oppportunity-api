from fastapi import FastAPI, Depends, HTTPException, Request, status, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel

from .models import *
from .auth import (
    authenticate_user, create_access_token, get_current_active_user,
    create_demo_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from .rate_limiter import check_rate_limit
from .data_collector import DataCollector
from .ai_analyzer import AIAnalyzer

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Trade Opportunities API",
    description="AI-powered market analysis API for Indian sectors",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions = {}
analysis_cache = {}

# Initialize services
ai_analyzer = AIAnalyzer()

# Basic auth for demo purposes
security = HTTPBasic()


# Pydantic model to accept JSON login payloads
class LoginRequest(BaseModel):
    username: str
    password: str


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    # Create demo users
    create_demo_user("demo", "demo123", "demo@tradeapi.com", "Demo User")
    create_demo_user("trader", "trader123", "trader@tradeapi.com", "Professional Trader")
    print("Trade Opportunities API is starting up...")
    print("Demo users created:")
    print("   - Username: demo, Password: demo123")
    print("   - Username: trader, Password: trader123")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Trade Opportunities API",
        "version": "1.0.0",
        "description": "AI-powered market analysis for Indian sectors",
        "docs": "/docs",
        "endpoints": {
            "login": "/login",
            "token": "/token",
            "register": "/register",
            "analyze": "/analyze/{sector}",
            "health": "/health"
        },
        "demo_credentials": {
            "username": "demo",
            "password": "demo123"
        }
    }


@app.post("/login", response_model=Token)
@app.post("/token", response_model=Token)
async def login_for_access_token(
    body: Optional[LoginRequest] = Body(None),
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
):
    """
    Authenticate and return an access token.

    Accepts either:
      - JSON body: {"username": "...", "password": "..."} (Content-Type: application/json)
      - HTTP Basic auth (Authorization header)

    Prefers JSON body if provided; otherwise falls back to Basic auth.
    """
    # Determine username/password from JSON body or HTTP Basic
    if body is not None and body.username and body.password:
        username = body.username
        password = body.password
    elif credentials is not None:
        username = credentials.username
        password = credentials.password
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register_user(user: UserCreate):
    """Register a new user (demo purposes)"""
    try:
        success = create_demo_user(
            user.username,
            user.password,
            user.email,
            user.full_name
        )
        if success:
            return {"message": "User created successfully", "username": user.username}
        else:
            raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_analyzer": "operational",
            "data_collector": "operational",
            "rate_limiter": "operational"
        }
    }


@app.get("/analyze/{sector}")
async def analyze_sector(
    sector: str,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Main endpoint: Analyze trade opportunities for a given sector
    """
    # Input validation
    if not sector or len(sector.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Sector name must be at least 2 characters long"
        )

    if len(sector) > 50:
        raise HTTPException(
            status_code=400,
            detail="Sector name too long (max 50 characters)"
        )

    # Clean sector input
    sector = sector.strip().lower()

    # Rate limiting check
    await check_rate_limit(request, current_user.username)

    # Generate unique request ID
    request_id = str(uuid.uuid4())

    # Check cache first (5 minutes cache)
    cache_key = f"{sector}_{current_user.username}"
    current_time = datetime.now()

    if cache_key in analysis_cache:
        cached_data = analysis_cache[cache_key]
        if current_time - cached_data['timestamp'] < timedelta(minutes=5):
            cached_data['request_id'] = request_id
            cached_data['from_cache'] = True
            return cached_data

    try:
        # Collect market data
        async with DataCollector() as collector:
            sector_data = await collector.collect_sector_data(sector)

        # Generate AI analysis
        analysis_text = await ai_analyzer.analyze_sector(sector_data)

        # Prepare response
        response_data = {
            "sector": sector.title(),
            "analysis": analysis_text,
            "timestamp": current_time,
            "sources_used": sector_data.get('data_sources', []),
            "request_id": request_id,
            "data_points_analyzed": sector_data.get('total_data_points', 0),
            "from_cache": False,
            "user": current_user.username
        }

        # Cache the result
        analysis_cache[cache_key] = response_data.copy()

        # Update session tracking
        if current_user.username not in sessions:
            sessions[current_user.username] = {
                "requests": [],
                "total_requests": 0
            }

        sessions[current_user.username]["requests"].append({
            "sector": sector,
            "timestamp": current_time,
            "request_id": request_id
        })
        sessions[current_user.username]["total_requests"] += 1

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": str(e),
                "request_id": request_id
            }
        )


@app.get("/user/stats")
async def get_user_stats(current_user: User = Depends(get_current_active_user)):
    """Get user statistics and request history"""
    user_data = sessions.get(current_user.username, {
        "requests": [],
        "total_requests": 0
    })

    return {
        "username": current_user.username,
        "total_requests": user_data["total_requests"],
        "recent_requests": user_data["requests"][-10:],  # Last 10 requests
        "available_sectors": [
            "pharmaceuticals",
            "technology",
            "agriculture",
            "banking",
            "automotive",
            "energy",
            "telecommunications",
            "retail",
            "real-estate",
            "textiles"
        ]
    }


@app.get("/sectors")
async def list_available_sectors():
    """List all available sectors for analysis"""
    return {
        "available_sectors": [
            {
                "name": "pharmaceuticals",
                "description": "Pharmaceutical and healthcare sector analysis"
            },
            {
                "name": "technology",
                "description": "IT and software technology sector analysis"
            },
            {
                "name": "agriculture",
                "description": "Agriculture and food processing sector analysis"
            },
            {
                "name": "banking",
                "description": "Banking and financial services sector analysis"
            },
            {
                "name": "automotive",
                "description": "Automotive and transportation sector analysis"
            },
            {
                "name": "energy",
                "description": "Energy and renewable resources sector analysis"
            },
            {
                "name": "telecommunications",
                "description": "Telecom and communication sector analysis"
            },
            {
                "name": "retail",
                "description": "Retail and consumer goods sector analysis"
            },
            {
                "name": "real-estate",
                "description": "Real estate and construction sector analysis"
            },
            {
                "name": "textiles",
                "description": "Textiles and apparel sector analysis"
            }
        ],
        "usage": "Use GET /analyze/{sector} to get detailed analysis"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
