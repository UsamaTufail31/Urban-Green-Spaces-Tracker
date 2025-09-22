# Real-Time City Data Integration

This guide explains how to set up and use the enhanced city search feature that provides real-time data from multiple external APIs.

## 🌟 Features

The enhanced city search now provides:

- **Current Weather Data**: Live temperature, humidity, wind speed, weather conditions
- **Country Information**: Capital, population, region, languages, currencies
- **Recent News**: Latest news articles related to the searched city
- **Live Data Indicators**: Visual indicators showing data freshness and availability

## 🔧 Setup

### 1. Install Dependencies

The required dependencies are already listed in `requirements.txt`. Make sure you have installed them:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Sign up for free API keys and add them to your `.env` file:

#### OpenWeatherMap API (Weather Data)
1. Visit [OpenWeatherMap API](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add to `.env`: `OPENWEATHER_API_KEY=your_api_key_here`

#### NewsAPI (Recent News)
1. Visit [NewsAPI](https://newsapi.org/)
2. Sign up for a free account
3. Get your API key from the dashboard  
4. Add to `.env`: `NEWS_API_KEY=your_api_key_here`

**Note**: The REST Countries API doesn't require an API key and provides country information.

### 3. Environment Configuration

Your `.env` file should include:

```bash
# External API Keys
OPENWEATHER_API_KEY=your_openweather_api_key_here
NEWS_API_KEY=your_news_api_key_here

# External Data Settings
ENABLE_EXTERNAL_DATA=true
EXTERNAL_API_TIMEOUT=10
EXTERNAL_API_CACHE_TTL=600
```

## 🚀 Usage

### Backend API

#### Enhanced City Search
```http
GET /city/search/enhanced?name=London&limit=5&include_realtime=true
```

#### API Health Check
```http
GET /health/external-apis
```

### Frontend Components

The city search now automatically shows real-time data:

- **Weather icons and temperature** in search suggestions
- **Live data indicators** showing data freshness
- **Enhanced city insights** with comprehensive real-time information

### Example Response

```json
{
  "id": 1,
  "name": "London",
  "country": "United Kingdom",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "population": 8982000,
  "realtime_data": {
    "weather": {
      "temperature": 15.5,
      "description": "Partly Cloudy",
      "humidity": 72,
      "wind_speed": 3.2,
      "icon": "02d"
    },
    "country_info": {
      "name": "United Kingdom",
      "capital": "London",
      "population": 67215293,
      "region": "Europe"
    },
    "recent_news": [
      {
        "title": "Latest developments in London...",
        "source": "BBC News",
        "published_at": "2025-09-21T10:00:00Z",
        "url": "https://..."
      }
    ],
    "data_sources": {
      "weather": "OpenWeatherMap",
      "country": "REST Countries",
      "news": "NewsAPI"
    }
  }
}
```

## 🔍 Testing

Run the test script to verify your setup:

```bash
cd backend
python test_enhanced_search.py
```

This will:
- Check API key configuration
- Test external API connectivity
- Verify data fetching functionality

## ⚡ Performance

### Caching
- Weather data: cached for 10 minutes
- Country data: cached for 1 hour  
- News data: cached for 30 minutes

### Error Handling
- Graceful fallback when APIs are unavailable
- Individual API failures don't break the search
- Clear error indicators in the UI

### Rate Limiting
- Respectful API usage with timeout limits
- Automatic retry mechanisms for transient failures

## 🎨 UI Features

### Search Suggestions
- Live weather data shown directly in dropdown
- Temperature and weather conditions
- Data freshness indicators

### City Insights Page
- Comprehensive real-time dashboard
- Weather information with icons
- Country details with flag
- Recent news articles
- Data source attribution

## 🛠️ Troubleshooting

### API Keys Not Working
1. Verify keys are correctly added to `.env`
2. Check if keys are active (some require email verification)
3. Ensure no extra spaces in the `.env` file

### No Real-Time Data Showing
1. Check `ENABLE_EXTERNAL_DATA=true` in `.env`
2. Verify API health with `/health/external-apis`
3. Check browser console for errors

### Performance Issues
1. Check cache settings in `.env`
2. Monitor API response times
3. Consider adjusting timeout values

## 📊 Monitoring

The system provides several monitoring endpoints:

- `/health` - Basic API health
- `/health/external-apis` - External API status
- Detailed error logging in backend logs

## 🔮 Future Enhancements

Potential additions:
- Air quality data integration
- Traffic information
- Economic indicators
- Social media sentiment
- More weather details (forecasts, alerts)

## 📝 Development

### Adding New Data Sources

1. Add API configuration to `external_data_service.py`
2. Implement fetch method for the new data type
3. Update the `get_enhanced_city_data` method
4. Add UI components to display the new data
5. Update tests and documentation

### API Rate Limits

Current free tier limits:
- OpenWeatherMap: 1,000 calls/day
- NewsAPI: 1,000 requests/day
- REST Countries: No limit

For production use, consider upgrading to paid tiers for higher limits.