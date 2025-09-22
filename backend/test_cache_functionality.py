"""
Test script to verify the caching functionality for coverage calculations.
"""

import requests
import time
import json
from datetime import datetime


def test_cache_functionality():
    """Test the caching functionality with real API calls."""
    
    API_BASE = "http://localhost:8002"
    
    print("=" * 70)
    print("TESTING COVERAGE CALCULATION CACHING")
    print("=" * 70)
    
    # Test 1: Check cache stats (should be empty initially)
    print("\n1. Checking initial cache stats...")
    try:
        response = requests.get(f"{API_BASE}/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Cache stats retrieved successfully!")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Valid entries: {stats['valid_entries']}")
            print(f"  Expired entries: {stats['expired_entries']}")
            print(f"  Type counts: {stats['type_counts']}")
        else:
            print(f"✗ Error getting cache stats: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error connecting to API: {e}")
        print("Make sure the FastAPI server is running on localhost:8000")
        return False
    
    # Test 2: Coverage comparison (first call - should calculate and cache)
    print("\n2. Testing coverage comparison caching...")
    city_name = "New York"  # You can change this to a city in your database
    
    print(f"   First call for {city_name} (should calculate and cache)...")
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/coverage/compare", params={"city_name": city_name})
        first_call_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ First call successful! Time: {first_call_time:.3f} seconds")
            print(f"  City: {result['city_name']}")
            print(f"  Coverage: {result['city_green_coverage_percentage']}%")
        elif response.status_code == 404:
            print(f"⚠ City '{city_name}' not found in database. This is expected if no data exists.")
            print("   Trying with a different endpoint...")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Wait a moment and make the same call again
    print(f"   Second call for {city_name} (should use cache)...")
    time.sleep(0.1)  # Small delay
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/coverage/compare", params={"city_name": city_name})
        second_call_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✓ Second call successful! Time: {second_call_time:.3f} seconds")
            if second_call_time < first_call_time:
                print(f"✓ Caching working! Second call was {first_call_time - second_call_time:.3f}s faster")
            else:
                print("⚠ Second call wasn't significantly faster - cache might not be working")
        elif response.status_code == 404:
            print(f"⚠ City '{city_name}' not found in database.")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Check cache stats again (should show entries now)
    print("\n3. Checking cache stats after API calls...")
    try:
        response = requests.get(f"{API_BASE}/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Cache stats retrieved successfully!")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Valid entries: {stats['valid_entries']}")
            print(f"  Expired entries: {stats['expired_entries']}")
            print(f"  Type counts: {stats['type_counts']}")
            
            if stats['total_entries'] > 0:
                print("✓ Cache is working! Entries were created.")
            else:
                print("⚠ No cache entries found. Cache might not be working as expected.")
        else:
            print(f"✗ Error getting cache stats: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Test cache cleanup
    print("\n4. Testing cache cleanup...")
    try:
        response = requests.post(f"{API_BASE}/cache/cleanup")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Cache cleanup successful!")
            print(f"  Message: {result['message']}")
        else:
            print(f"✗ Error during cache cleanup: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Test city stats caching (if we have cities in the database)
    print("\n5. Testing city stats caching...")
    try:
        # First get a list of cities
        response = requests.get(f"{API_BASE}/cities", params={"limit": 1})
        if response.status_code == 200:
            cities = response.json()
            if cities:
                city_id = cities[0]['id']
                city_name = cities[0]['name']
                
                print(f"   Testing with city: {city_name} (ID: {city_id})")
                
                # First call
                start_time = time.time()
                response = requests.get(f"{API_BASE}/cities/{city_id}/stats")
                first_call_time = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✓ First stats call successful! Time: {first_call_time:.3f} seconds")
                    
                    # Second call
                    time.sleep(0.1)
                    start_time = time.time()
                    response = requests.get(f"{API_BASE}/cities/{city_id}/stats")
                    second_call_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        print(f"✓ Second stats call successful! Time: {second_call_time:.3f} seconds")
                        if second_call_time < first_call_time:
                            print(f"✓ Stats caching working! Second call was {first_call_time - second_call_time:.3f}s faster")
                    else:
                        print(f"✗ Second stats call failed: {response.status_code}")
                else:
                    print(f"✗ First stats call failed: {response.status_code}")
            else:
                print("⚠ No cities found in database to test stats caching")
        else:
            print(f"✗ Error getting cities: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Final cache stats
    print("\n6. Final cache stats...")
    try:
        response = requests.get(f"{API_BASE}/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Final cache stats:")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Valid entries: {stats['valid_entries']}")
            print(f"  Type counts: {stats['type_counts']}")
        else:
            print(f"✗ Error getting final cache stats: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("CACHE TESTING COMPLETED")
    print("=" * 70)
    print("\nIf you see ✓ marks above, the caching system is working correctly!")
    print("Performance improvements should be visible in reduced response times for repeated queries.")
    print("\nTo test satellite imagery caching, you would need to upload shapefiles and raster data")
    print("to the /shapefile/calculate-green-coverage endpoint.")
    return True


if __name__ == "__main__":
    test_cache_functionality()