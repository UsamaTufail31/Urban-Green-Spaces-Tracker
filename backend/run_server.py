#!/usr/bin/env python3
"""
Startup script to run the FastAPI app with the city search endpoint
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("🌱 Starting Urban Green Spaces API Server...")
    print("📍 Server will be available at: http://127.0.0.1:8001")
    print("🔍 City search endpoint: http://127.0.0.1:8001/city/search?name=<city_name>")
    print("💬 Feedback endpoint: http://127.0.0.1:8001/feedback")
    print("📚 API documentation: http://127.0.0.1:8001/docs")
    print("🔄 Starting server...")
    
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8000)