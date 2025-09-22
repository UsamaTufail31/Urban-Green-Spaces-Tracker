"""
Test script for the enhanced city search with real-time data
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.external_data_service import ExternalDataService
from app.config import settings

async def test_external_data_service():
    """Test the external data service functionality"""
    print("🌍 Testing External Data Service")
    print("=" * 50)
    
    # Create a simple in-memory cache service for testing
    class MockCacheService:
        def __init__(self):
            self.cache = {}
        
        async def get(self, key):
            return self.cache.get(key)
        
        async def set(self, key, value, ttl=None):
            self.cache[key] = value
    
    # Initialize services
    cache_service = MockCacheService()
    external_service = ExternalDataService(cache_service)
    
    try:
        # Test health check
        print("\n1. Testing API Health Check...")
        health_status = await external_service.health_check()
        print(f"Health Status: {health_status}")
        
        # Test weather data (using coordinates for London)
        print("\n2. Testing Weather Data...")
        weather_data = await external_service.fetch_weather_data(51.5074, -0.1278, "London")
        if weather_data:
            print(f"Weather in London: {weather_data['temperature']}°C, {weather_data['description']}")
            print(f"Humidity: {weather_data['humidity']}%, Wind: {weather_data['wind_speed']} m/s")
        else:
            print("Weather data not available (API key may be missing)")
        
        # Test country data
        print("\n3. Testing Country Data...")
        country_data = await external_service.fetch_country_data("United Kingdom")
        if country_data:
            print(f"Country: {country_data['name']}")
            print(f"Capital: {country_data['capital']}")
            print(f"Population: {country_data.get('population', 'N/A')}")
            print(f"Region: {country_data['region']}")
        else:
            print("Country data not available")
        
        # Test enhanced city data
        print("\n4. Testing Enhanced City Data...")
        enhanced_data = await external_service.get_enhanced_city_data(
            "London", "United Kingdom", 51.5074, -0.1278
        )
        
        print(f"Enhanced Data Keys: {list(enhanced_data.keys())}")
        if enhanced_data.get('weather'):
            print(f"✓ Weather data available")
        if enhanced_data.get('country_info'):
            print(f"✓ Country info available")
        if enhanced_data.get('recent_news'):
            print(f"✓ News data available ({len(enhanced_data['recent_news'])} articles)")
        
        print(f"\nData Sources: {enhanced_data.get('data_sources', {})}")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    finally:
        # Cleanup
        await external_service.close_session()
        print("\n✅ Test completed!")

def check_api_configuration():
    """Check if API keys are configured"""
    print("🔧 API Configuration Check")
    print("=" * 30)
    
    openweather_key = getattr(settings, 'openweather_api_key', None)
    news_key = getattr(settings, 'news_api_key', None)
    
    if openweather_key:
        print("✅ OpenWeatherMap API key configured")
    else:
        print("⚠️  OpenWeatherMap API key not configured")
        print("   Sign up at: https://openweathermap.org/api")
        print("   Add OPENWEATHER_API_KEY to your .env file")
    
    if news_key:
        print("✅ NewsAPI key configured")
    else:
        print("⚠️  NewsAPI key not configured")
        print("   Sign up at: https://newsapi.org/")
        print("   Add NEWS_API_KEY to your .env file")
    
    if not openweather_key and not news_key:
        print("\n📝 To get API keys:")
        print("1. Copy backend/.env.example to backend/.env")
        print("2. Sign up for free API keys:")
        print("   - OpenWeatherMap: https://openweathermap.org/api")
        print("   - NewsAPI: https://newsapi.org/")
        print("3. Add your keys to the .env file")
        print("4. Run this test again")
    
    print()

if __name__ == "__main__":
    print("🚀 Urban Project - Enhanced City Search Test")
    print("=" * 60)
    
    check_api_configuration()
    
    # Run the async test
    asyncio.run(test_external_data_service())