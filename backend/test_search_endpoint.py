#!/usr/bin/env python3
"""
Test script for the new /city/search endpoint
"""

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy.orm import Session

# Create test client
client = TestClient(app)

def test_city_search_endpoint():
    """Test the /city/search endpoint"""
    
    print("Testing /city/search endpoint...")
    
    # Test 1: Valid search with existing city (assuming there are cities in the database)
    print("\n1. Testing valid search...")
    response = client.get("/city/search?name=New")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Search with empty name (should return error)
    print("\n2. Testing search with empty name...")
    response = client.get("/city/search?name=")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Search with non-existent city
    print("\n3. Testing search with non-existent city...")
    response = client.get("/city/search?name=NonExistentCity123")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Search with limit parameter
    print("\n4. Testing search with limit parameter...")
    response = client.get("/city/search?name=a&limit=3")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_city_search_endpoint()