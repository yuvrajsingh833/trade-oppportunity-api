#!/usr/bin/env python3
"""
Trade Opportunities API - Main Runner Script

This script starts the FastAPI server with proper configuration.
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the FastAPI application"""
    print("🚀 Starting Trade Opportunities API...")
    print("📊 API Documentation will be available at:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n👤 Demo Credentials:")
    print("   - Username: demo, Password: demo123")
    print("   - Username: trader, Password: trader123")
    print("\n🔗 Main Endpoint: GET /analyze/{sector}")
    print("📖 Available sectors: pharmaceuticals, technology, agriculture, banking, etc.")
    print("\n" + "="*60)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()