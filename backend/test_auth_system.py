"""
Test script for the authentication system.
This script tests the main authentication endpoints.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://127.0.0.1:8001"

def test_authentication():
    """Test the authentication system."""
    print("🔐 Testing Urban Green Spaces API Authentication System")
    print("=" * 60)
    
    # Test 1: Check root endpoint without authentication
    print("\n1. Testing root endpoint (no auth)...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is running: {data['message']}")
            if 'authentication' in data:
                print(f"   Authentication endpoints available")
        else:
            print(f"❌ Failed to reach API")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Try to login with default admin credentials
    print("\n2. Testing admin login...")
    login_data = {
        "username": "admin",
        "password": "AdminPass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print(f"✅ Login successful!")
            print(f"   Token type: {data['token_type']}")
            print(f"   Expires in: {data['expires_in']} seconds")
            
            # Test 3: Get user info with token
            print("\n3. Testing authenticated user info...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ User info retrieved:")
                print(f"   Username: {user_data['username']}")
                print(f"   Email: {user_data['email']}")
                print(f"   Role: {user_data['role']}")
                print(f"   Full name: {user_data['full_name']}")
            else:
                print(f"❌ Failed to get user info: {response.status_code}")
            
            # Test 4: Try to access admin endpoint
            print("\n4. Testing admin endpoint access...")
            response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
            
            if response.status_code == 200:
                users_data = response.json()
                print(f"✅ Admin access successful!")
                print(f"   Total users: {len(users_data)}")
                for user in users_data:
                    print(f"   - {user['username']} ({user['role']})")
            else:
                print(f"❌ Failed to access admin endpoint: {response.status_code}")
            
            # Test 5: Try to create a city (admin protected)
            print("\n5. Testing protected city creation endpoint...")
            city_data = {
                "name": "Test City",
                "country": "Test Country",
                "population": 100000,
                "latitude": 40.7128,
                "longitude": -74.0060
            }
            
            response = requests.post(f"{BASE_URL}/cities", json=city_data, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                created_city = response.json()
                print(f"✅ City created successfully!")
                print(f"   City ID: {created_city['id']}")
                print(f"   City Name: {created_city['name']}")
                
                # Clean up - delete the test city
                print("\n6. Cleaning up test city...")
                response = requests.delete(f"{BASE_URL}/cities/{created_city['id']}", headers=headers)
                if response.status_code == 200:
                    print(f"✅ Test city deleted successfully")
                else:
                    print(f"⚠️ Failed to delete test city: {response.status_code}")
            else:
                print(f"❌ Failed to create city: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test 6: Test token verification
            print("\n7. Testing token verification...")
            response = requests.post(f"{BASE_URL}/auth/verify-token", headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"✅ Token verification successful!")
                print(f"   Valid: {token_data['valid']}")
                print(f"   Username: {token_data['username']}")
                print(f"   Role: {token_data['role']}")
            else:
                print(f"❌ Token verification failed: {response.status_code}")
            
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
    
    # Test 7: Try accessing protected endpoint without token
    print("\n8. Testing access without authentication...")
    try:
        response = requests.post(f"{BASE_URL}/cities", json={"name": "Test"})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"✅ Properly rejected unauthenticated request")
        else:
            print(f"❌ Should have rejected unauthenticated request")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Authentication system test completed!")
    print("\nDefault admin credentials:")
    print("  Username: admin")
    print("  Email: admin@urbanproject.com")
    print("  Password: AdminPass123!")
    print("\n⚠️  IMPORTANT: Change the default admin password in production!")


if __name__ == "__main__":
    test_authentication()