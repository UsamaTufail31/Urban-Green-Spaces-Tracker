#!/usr/bin/env python3
"""
Test script for the /parks/nearest endpoint
"""
import requests
import json

def test_nearest_parks_endpoint():
    """Test the nearest parks endpoint with sample coordinates"""
    base_url = "http://127.0.0.1:8001"
    endpoint = "/parks/nearest"
    
    # Test coordinates (example: somewhere in New York City)
    test_cases = [
        {
            "name": "NYC Central Park area",
            "params": {
                "latitude": 40.7829,
                "longitude": -73.9654,
                "radius_km": 5.0,
                "limit": 10
            }
        },
        {
            "name": "London Hyde Park area", 
            "params": {
                "latitude": 51.5074,
                "longitude": -0.1278,
                "radius_km": 3.0,
                "limit": 5
            }
        }
    ]
    
    print("Testing /parks/nearest endpoint...")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print(f"Parameters: {test_case['params']}")
        
        try:
            response = requests.get(
                f"{base_url}{endpoint}",
                params=test_case['params'],
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} parks")
                
                if data:
                    print("Sample results:")
                    for i, park in enumerate(data[:3], 1):  # Show first 3 results
                        print(f"  {i}. {park['name']}")
                        print(f"     Distance: {park['distance_km']} km")
                        print(f"     Area: {park.get('area_hectares', 'N/A')} hectares")
                        print(f"     Amenities: {park.get('amenities') or 'None listed'}")
                        print()
                else:
                    print("  No parks found in the specified radius")
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        print("-" * 30)

def test_endpoint_validation():
    """Test endpoint parameter validation"""
    base_url = "http://127.0.0.1:8001"
    endpoint = "/parks/nearest"
    
    print("\nTesting parameter validation...")
    print("=" * 50)
    
    # Test cases for validation
    validation_tests = [
        {
            "name": "Missing latitude",
            "params": {"longitude": -73.9654, "radius_km": 5.0}
        },
        {
            "name": "Invalid latitude (too high)",
            "params": {"latitude": 91.0, "longitude": -73.9654, "radius_km": 5.0}
        },
        {
            "name": "Invalid longitude (too low)",
            "params": {"latitude": 40.7829, "longitude": -181.0, "radius_km": 5.0}
        },
        {
            "name": "Invalid radius (too high)",
            "params": {"latitude": 40.7829, "longitude": -73.9654, "radius_km": 100.0}
        }
    ]
    
    for test in validation_tests:
        print(f"\nValidation Test: {test['name']}")
        try:
            response = requests.get(
                f"{base_url}{endpoint}",
                params=test['params'],
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code != 200:
                print(f"Error Response: {response.text}")
            else:
                print("Unexpected success - validation may not be working")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    # First test normal functionality
    test_nearest_parks_endpoint()
    
    # Then test validation
    test_endpoint_validation()
    
    print("\nTesting complete!")