#!/usr/bin/env python3
"""
Demo script to test the feedback endpoint functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from time import sleep

def test_feedback_endpoint():
    """Test the feedback endpoint with various scenarios."""
    
    print("🚀 Testing Feedback Endpoint")
    print("=" * 50)
    
    # Base URL for the API
    base_url = "http://127.0.0.1:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Feedback",
            "data": {
                "name": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "message": "I absolutely love this urban green spaces application! The park finder feature is incredibly useful for my daily walks."
            },
            "expected_status": 201
        },
        {
            "name": "Another Valid Feedback",
            "data": {
                "name": "Bob Smith",
                "email": "bob.smith@example.com", 
                "message": "The green coverage comparison feature helped me understand how my city compares to WHO recommendations. Very informative!"
            },
            "expected_status": 201
        },
        {
            "name": "Invalid Email",
            "data": {
                "name": "Charlie Brown",
                "email": "invalid-email",
                "message": "This should fail due to invalid email format."
            },
            "expected_status": 422
        },
        {
            "name": "Message Too Short",
            "data": {
                "name": "David Wilson",
                "email": "david@example.com",
                "message": "Short"
            },
            "expected_status": 422
        },
        {
            "name": "Missing Name",
            "data": {
                "email": "eve@example.com",
                "message": "This feedback is missing a name field."
            },
            "expected_status": 422
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{base_url}/feedback",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {test_case['expected_status']}")
            
            if response.status_code == test_case["expected_status"]:
                print("✅ Test PASSED")
                
                if response.status_code == 201:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                else:
                    print(f"Error Details: {response.json()}")
            else:
                print("❌ Test FAILED")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the server is running on http://127.0.0.1:8000")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Feedback Endpoint Testing Complete!")


if __name__ == "__main__":
    test_feedback_endpoint()