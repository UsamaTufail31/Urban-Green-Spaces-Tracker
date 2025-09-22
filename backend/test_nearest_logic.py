#!/usr/bin/env python3
"""
Direct test of the nearest parks logic without requiring a running server
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Park
from app.main import calculate_distance

def test_nearest_parks_logic():
    """Test the nearest parks calculation logic directly"""
    print("Testing nearest parks logic...")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    # Test coordinates (Central Park area)
    user_lat = 40.7829
    user_lon = -73.9654
    radius_km = 5.0
    
    print(f"User location: ({user_lat}, {user_lon})")
    print(f"Search radius: {radius_km} km")
    print()
    
    # Get all parks with coordinates
    parks = db.query(Park).filter(
        Park.latitude.isnot(None),
        Park.longitude.isnot(None)
    ).all()
    
    print(f"Found {len(parks)} parks with coordinates in database")
    print()
    
    # Calculate distances and filter within radius
    parks_with_distance = []
    for park in parks:
        distance = calculate_distance(user_lat, user_lon, park.latitude, park.longitude)
        
        print(f"{park.name}: {distance:.2f} km")
        
        if distance <= radius_km:
            parks_with_distance.append({
                "id": park.id,
                "name": park.name,
                "area_hectares": park.area_hectares,
                "amenities": park.facilities,
                "distance_km": round(distance, 2),
                "latitude": park.latitude,
                "longitude": park.longitude
            })
    
    # Sort by distance
    parks_with_distance.sort(key=lambda x: x["distance_km"])
    
    print()
    print(f"Parks within {radius_km} km radius:")
    print("-" * 30)
    
    if parks_with_distance:
        for i, park in enumerate(parks_with_distance, 1):
            print(f"{i}. {park['name']}")
            print(f"   Distance: {park['distance_km']} km")
            print(f"   Area: {park.get('area_hectares', 'N/A')} hectares")
            print(f"   Amenities: {park.get('amenities') or 'None listed'}")
            print(f"   Coordinates: ({park['latitude']}, {park['longitude']})")
            print()
    else:
        print("No parks found within the specified radius")
    
    db.close()
    return parks_with_distance

def test_distance_calculation():
    """Test the Haversine distance calculation"""
    print("\nTesting distance calculation...")
    print("=" * 50)
    
    # Test known distances
    test_cases = [
        {
            "name": "Central Park to Prospect Park (NYC)",
            "lat1": 40.7829, "lon1": -73.9654,  # Central Park
            "lat2": 40.6602, "lon2": -73.969,   # Prospect Park
            "expected_approx": 13.5  # Approximate distance in km
        },
        {
            "name": "Same location",
            "lat1": 40.7829, "lon1": -73.9654,
            "lat2": 40.7829, "lon2": -73.9654,
            "expected_approx": 0.0
        }
    ]
    
    for test in test_cases:
        distance = calculate_distance(test["lat1"], test["lon1"], test["lat2"], test["lon2"])
        print(f"{test['name']}")
        print(f"  Calculated: {distance:.2f} km")
        print(f"  Expected: ~{test['expected_approx']} km")
        print(f"  Difference: {abs(distance - test['expected_approx']):.2f} km")
        print()

if __name__ == "__main__":
    test_distance_calculation()
    results = test_nearest_parks_logic()
    
    print("\nTest completed successfully!")
    print(f"Found {len(results)} parks within radius")