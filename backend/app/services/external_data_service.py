"""
External Data Service for fetching real-time city information from various APIs
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.config import settings
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class ExternalDataService:
    """Service for fetching real-time data from external APIs"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API endpoints and configurations
        self.apis = {
            'weather': {
                'base_url': 'http://api.openweathermap.org/data/2.5',
                'key_required': True,
                'timeout': 5
            },
            'geocoding': {
                'base_url': 'http://api.openweathermap.org/geo/1.0',
                'key_required': True,
                'timeout': 5
            },
            'countries': {
                'base_url': 'https://restcountries.com/v3.1',
                'key_required': False,
                'timeout': 10
            },
            'news': {
                'base_url': 'https://newsapi.org/v2',
                'key_required': True,
                'timeout': 10
            }
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Urban-Project/1.0'}
            )
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch_weather_data(self, latitude: float, longitude: float, city_name: str) -> Optional[Dict[str, Any]]:
        """Fetch current weather data for a city"""
        cache_key = f"weather:{latitude}:{longitude}"
        
        # Check cache first (cache for 10 minutes)
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Weather data for {city_name} retrieved from cache")
            return json.loads(cached_data)
        
        # API key check
        weather_api_key = getattr(settings, 'openweather_api_key', None)
        if not weather_api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return None
        
        try:
            session = await self.get_session()
            url = f"{self.apis['weather']['base_url']}/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': weather_api_key,
                'units': 'metric'
            }
            
            async with session.get(url, params=params, timeout=self.apis['weather']['timeout']) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process and structure the weather data
                    weather_info = {
                        'temperature': data.get('main', {}).get('temp'),
                        'feels_like': data.get('main', {}).get('feels_like'),
                        'humidity': data.get('main', {}).get('humidity'),
                        'pressure': data.get('main', {}).get('pressure'),
                        'description': data.get('weather', [{}])[0].get('description', '').title(),
                        'icon': data.get('weather', [{}])[0].get('icon'),
                        'wind_speed': data.get('wind', {}).get('speed'),
                        'wind_direction': data.get('wind', {}).get('deg'),
                        'visibility': data.get('visibility'),
                        'timestamp': datetime.utcnow().isoformat(),
                        'source': 'OpenWeatherMap'
                    }
                    
                    # Cache for 10 minutes
                    await self.cache_service.set(cache_key, json.dumps(weather_info), ttl=600)
                    logger.info(f"Weather data for {city_name} fetched successfully")
                    return weather_info
                else:
                    logger.warning(f"Weather API returned status {response.status} for {city_name}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Weather API timeout for {city_name}")
            return None
        except Exception as e:
            logger.error(f"Error fetching weather data for {city_name}: {str(e)}")
            return None
    
    async def fetch_country_data(self, country_name: str) -> Optional[Dict[str, Any]]:
        """Fetch country information"""
        cache_key = f"country:{country_name.lower()}"
        
        # Check cache first (cache for 1 hour)
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Country data for {country_name} retrieved from cache")
            return json.loads(cached_data)
        
        try:
            session = await self.get_session()
            url = f"{self.apis['countries']['base_url']}/name/{country_name}"
            params = {'fields': 'name,capital,population,region,subregion,languages,currencies,timezones,flag'}
            
            async with session.get(url, params=params, timeout=self.apis['countries']['timeout']) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        country = data[0]  # Take the first match
                        
                        country_info = {
                            'name': country.get('name', {}).get('common'),
                            'official_name': country.get('name', {}).get('official'),
                            'capital': country.get('capital', [None])[0] if country.get('capital') else None,
                            'population': country.get('population'),
                            'region': country.get('region'),
                            'subregion': country.get('subregion'),
                            'languages': list(country.get('languages', {}).values()) if country.get('languages') else [],
                            'currencies': [curr.get('name') for curr in country.get('currencies', {}).values()] if country.get('currencies') else [],
                            'timezones': country.get('timezones', []),
                            'flag_url': country.get('flags', {}).get('png'),
                            'timestamp': datetime.utcnow().isoformat(),
                            'source': 'REST Countries'
                        }
                        
                        # Cache for 1 hour
                        await self.cache_service.set(cache_key, json.dumps(country_info), ttl=3600)
                        logger.info(f"Country data for {country_name} fetched successfully")
                        return country_info
                else:
                    logger.warning(f"Countries API returned status {response.status} for {country_name}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Countries API timeout for {country_name}")
            return None
        except Exception as e:
            logger.error(f"Error fetching country data for {country_name}: {str(e)}")
            return None
    
    async def fetch_city_news(self, city_name: str, country_name: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch recent news about the city"""
        cache_key = f"news:{city_name.lower()}:{country_name.lower()}"
        
        # Check cache first (cache for 30 minutes)
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            logger.info(f"News data for {city_name} retrieved from cache")
            return json.loads(cached_data)
        
        # API key check
        news_api_key = getattr(settings, 'news_api_key', None)
        if not news_api_key:
            logger.warning("NewsAPI key not configured")
            return None
        
        try:
            session = await self.get_session()
            url = f"{self.apis['news']['base_url']}/everything"
            
            # Search for city news
            query = f'"{city_name}" AND ("{country_name}" OR city OR urban)'
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'pageSize': 5,
                'language': 'en',
                'apiKey': news_api_key
            }
            
            async with session.get(url, params=params, timeout=self.apis['news']['timeout']) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    news_items = []
                    for article in articles[:3]:  # Limit to 3 most recent
                        news_items.append({
                            'title': article.get('title'),
                            'description': article.get('description'),
                            'url': article.get('url'),
                            'published_at': article.get('publishedAt'),
                            'source': article.get('source', {}).get('name'),
                            'image_url': article.get('urlToImage')
                        })
                    
                    # Cache for 30 minutes
                    await self.cache_service.set(cache_key, json.dumps(news_items), ttl=1800)
                    logger.info(f"News data for {city_name} fetched successfully ({len(news_items)} articles)")
                    return news_items
                else:
                    logger.warning(f"News API returned status {response.status} for {city_name}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"News API timeout for {city_name}")
            return None
        except Exception as e:
            logger.error(f"Error fetching news data for {city_name}: {str(e)}")
            return None
    
    async def get_enhanced_city_data(self, city_name: str, country_name: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch comprehensive real-time data for a city from multiple sources
        """
        logger.info(f"Fetching enhanced data for {city_name}, {country_name}")
        
        # Create tasks for concurrent API calls
        tasks = [
            self.fetch_weather_data(latitude, longitude, city_name),
            self.fetch_country_data(country_name),
            self.fetch_city_news(city_name, country_name)
        ]
        
        try:
            # Execute all API calls concurrently
            weather_data, country_data, news_data = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            if isinstance(weather_data, Exception):
                logger.error(f"Weather data fetch failed: {weather_data}")
                weather_data = None
            
            if isinstance(country_data, Exception):
                logger.error(f"Country data fetch failed: {country_data}")
                country_data = None
            
            if isinstance(news_data, Exception):
                logger.error(f"News data fetch failed: {news_data}")
                news_data = None
            
            # Compile enhanced data
            enhanced_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'weather': weather_data,
                'country_info': country_data,
                'recent_news': news_data,
                'data_sources': {
                    'weather': 'OpenWeatherMap' if weather_data else None,
                    'country': 'REST Countries' if country_data else None,
                    'news': 'NewsAPI' if news_data else None
                }
            }
            
            logger.info(f"Enhanced data compilation completed for {city_name}")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error in enhanced data fetching for {city_name}: {str(e)}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': f"Failed to fetch enhanced data: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of external APIs"""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'apis': {}
        }
        
        # Check each API endpoint
        for api_name, config in self.apis.items():
            try:
                session = await self.get_session()
                
                # Use a simple endpoint for health check
                if api_name == 'weather':
                    # Skip if no API key
                    if not getattr(settings, 'openweather_api_key', None):
                        health_status['apis'][api_name] = {'status': 'disabled', 'reason': 'No API key'}
                        continue
                    
                    url = f"{config['base_url']}/weather?q=London&appid={settings.openweather_api_key}"
                elif api_name == 'geocoding':
                    if not getattr(settings, 'openweather_api_key', None):
                        health_status['apis'][api_name] = {'status': 'disabled', 'reason': 'No API key'}
                        continue
                    url = f"{config['base_url']}/direct?q=London&appid={settings.openweather_api_key}"
                elif api_name == 'countries':
                    url = f"{config['base_url']}/name/united-kingdom"
                elif api_name == 'news':
                    if not getattr(settings, 'news_api_key', None):
                        health_status['apis'][api_name] = {'status': 'disabled', 'reason': 'No API key'}
                        continue
                    url = f"{config['base_url']}/top-headlines?country=us&apiKey={settings.news_api_key}"
                
                async with session.get(url, timeout=config['timeout']) as response:
                    if response.status == 200:
                        health_status['apis'][api_name] = {'status': 'healthy', 'response_time': response.headers.get('X-Response-Time')}
                    else:
                        health_status['apis'][api_name] = {'status': 'error', 'status_code': response.status}
                        
            except asyncio.TimeoutError:
                health_status['apis'][api_name] = {'status': 'timeout'}
            except Exception as e:
                health_status['apis'][api_name] = {'status': 'error', 'error': str(e)}
        
        return health_status


# Global instance
_external_data_service: Optional[ExternalDataService] = None


def get_external_data_service(cache_service: CacheService) -> ExternalDataService:
    """Get or create external data service instance"""
    global _external_data_service
    if _external_data_service is None:
        _external_data_service = ExternalDataService(cache_service)
    return _external_data_service


async def cleanup_external_data_service():
    """Cleanup external data service resources"""
    global _external_data_service
    if _external_data_service:
        await _external_data_service.close_session()
        _external_data_service = None