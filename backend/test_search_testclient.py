#!/usr/bin/env python3
"""
Test the /city/search endpoint using FastAPI TestClient
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def test_city_search_endpoint():
    """Test the /city/search endpoint"""
    
    client = TestClient(app)
    
    print("Testing /city/search endpoint with TestClient...")
    print("=" * 50)
    
    # Test 1: Search for 'New' (should find "New York")
    print("\n1. Testing search for 'New'...")
    response = client.get("/city/search?name=New")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} cities:")
    for city in data:
        print(f"  - {city['name']}, {city['country']} (lat: {city['latitude']}, lon: {city['longitude']})")
    
    # Test 2: Search for 'London'
    print("\n2. Testing search for 'London'...")
    response = client.get("/city/search?name=London")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} cities:")
    for city in data:
        print(f"  - {city['name']}, {city['country']} (lat: {city['latitude']}, lon: {city['longitude']})")
    
    # Test 3: Search for 'Tokyo'
    print("\n3. Testing search for 'Tokyo'...")
    response = client.get("/city/search?name=Tokyo")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} cities:")
    for city in data:
        print(f"  - {city['name']}, {city['country']} (lat: {city['latitude']}, lon: {city['longitude']})")
    
    # Test 4: Case-insensitive search for 'york'
    print("\n4. Testing case-insensitive search for 'york'...")
    response = client.get("/city/search?name=york")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} cities:")
    for city in data:
        print(f"  - {city['name']}, {city['country']} (lat: {city['latitude']}, lon: {city['longitude']})")
    
    # Test 5: Search with empty name (should return error)
    print("\n5. Testing search with empty name...")
    response = client.get("/city/search?name=")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    # Test 6: Search for non-existent city
    print("\n6. Testing search for non-existent city...")
    response = client.get("/city/search?name=NonExistentCity123")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} cities")
    
    # Test 7: Search with limit parameter
    print("\n7. Testing search with limit=1...")
    response = client.get("/city/search?name=o&limit=1")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} cities (should be max 1):")
    for city in data:
        print(f"  - {city['name']}, {city['country']} (lat: {city['latitude']}, lon: {city['longitude']})")

if __name__ == "__main__":
    test_city_search_endpoint()