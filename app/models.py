from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class MarketData(BaseModel):
    sector: str
    timestamp: datetime
    data_points: List[str]
    sources: List[str]


class AnalysisRequest(BaseModel):
    sector: str = Field(..., min_length=2, max_length=50, description="Market sector to analyze")


class AnalysisResponse(BaseModel):
    sector: str
    analysis: str
    timestamp: datetime
    sources_used: List[str]
    request_id: str