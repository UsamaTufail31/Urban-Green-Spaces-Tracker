#!/usr/bin/env python3
"""
Simple test for the new /city/search endpoint
"""

import requests
import json

def test_search_endpoint():
    """Test the /city/search endpoint using requests"""
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Search for 'New'",
            "url": f"{base_url}/city/search?name=New",
            "expected_status": 200
        },
        {
            "name": "Search for 'London'", 
            "url": f"{base_url}/city/search?name=London",
            "expected_status": 200
        },
        {
            "name": "Search for 'Tokyo'",
            "url": f"{base_url}/city/search?name=Tokyo", 
            "expected_status": 200
        },
        {
            "name": "Search for 'York' (partial match)",
            "url": f"{base_url}/city/search?name=York",
            "expected_status": 200
        },
        {
            "name": "Search with empty name",
            "url": f"{base_url}/city/search?name=",
            "expected_status": 400
        },
        {
            "name": "Search for non-existent city",
            "url": f"{base_url}/city/search?name=NonExistentCity123",
            "expected_status": 200  # Should return empty list
        }
    ]
    
    print("Testing /city/search endpoint...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"URL: {test_case['url']}")
        
        try:
            response = requests.get(test_case['url'], timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == test_case['expected_status']:
                print("✅ Status code matches expected")
            else:
                print(f"❌ Expected {test_case['expected_status']}, got {response.status_code}")
            
            # Print response
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"Results count: {len(data)}")
                    for city in data:
                        print(f"  - {city.get('name', 'N/A')}, {city.get('country', 'N/A')} "
                              f"(lat: {city.get('latitude', 'N/A')}, lon: {city.get('longitude', 'N/A')})")
                else:
                    print(f"Response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response text: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_search_endpoint()