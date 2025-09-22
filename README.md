# Urban Green Tracker Application
- 🗺️ **Interactive Maps**: Powered by Leaflet and React-Leaflet for exploring green spaces
- 📊 **Data Visualization**: Real-time charts and statistics using Recharts
- 🔍 **Smart City Search**: Intelligent search with autocomplete and real-time data integration
- 🌤️ **Live Weather Data**: Current weather conditions, temperature, and forecasts
- 📰 **Recent News**: Latest city-related news and updates
- 🏴 **Country Information**: Real-time country data including population and demographics
- 📍 **Location Services**: Find nearest parks and green spaces within customizable radius
- � **Green Coverage Analysis**: Compare cities against WHO recommendations (30% green coverage)
- � **Historical Trends**: Visualize green coverage changes over time
- 🌓 **Dark/Light Theme**: Responsive design with theme switching
- 📱 **Mobile Responsive**: Optimized for all device sizespaces Tracker

A comprehensive full-stack web application for discovering, analyzing, and managing urban green spaces, parks, and environmental data. This platform combines satellite imagery processing, real-time data visualization, and interactive mapping to promote sustainable urban development.

## 🌟 Key Features

### Frontend Application
- 🗺️ **Interactive Maps**: Powered by Leaflet and React-Leaflet for exploring green spaces
- 📊 **Data Visualization**: Real-time charts and statistics using Recharts
- 🔍 **Smart City Search**: Intelligent search with autocomplete and suggestions
- 📍 **Location Services**: Find nearest parks and green spaces within customizable radius
- � **Green Coverage Analysis**: Compare cities against WHO recommendations (30% green coverage)
- � **Historical Trends**: Visualize green coverage changes over time
- 🌓 **Dark/Light Theme**: Responsive design with theme switching
- 📱 **Mobile Responsive**: Optimized for all device sizes

### Backend API
- 🛰️ **Satellite Imagery Processing**: Automated green coverage analysis using NDVI
- 🌍 **External API Integration**: Real-time data from weather, news, and country APIs
- ⏰ **Background Tasks**: Weekly automated updates with APScheduler
- 🔐 **JWT Authentication**: Secure admin panel with role-based access
- 💾 **Intelligent Caching**: Multi-layer caching for database and external API data
- 🗃️ **PostgreSQL Integration**: Robust data management with SQLAlchemy ORM
- 📋 **Comprehensive API**: RESTful endpoints for all data operations
- 🌐 **CORS Support**: Seamless frontend-backend integration
- 📝 **Feedback System**: User feedback collection and management

## 🛠️ Technology Stack

### Frontend
- **React 19** - Modern UI framework with hooks and context
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first styling framework
- **Leaflet** - Interactive mapping library
- **React-Leaflet** - React bindings for Leaflet
- **Recharts** - Responsive chart library
- **Lucide React** - Beautiful icon library

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL** - Production-ready relational database
- **Geopandas** - Geospatial data processing
- **Rasterio** - Satellite imagery processing
- **APScheduler** - Background task scheduling
- **JWT** - JSON Web Token authentication
- **Uvicorn** - ASGI server for production
## Web Pages
[📄 Open Report (PDF)](Green Track project.pdf.pdf)

## 🚀 Getting Started

### Prerequisites

#### Frontend
- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager

#### Backend
- **Python** (version 3.8 or higher)
- **PostgreSQL** (version 12 or higher)
- **pip** package manager

### Installation & Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd urban-project
```

#### 2. Frontend Setup
```bash
# Install frontend dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

#### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials and configuration

# Optional: Set up real-time data APIs (see REALTIME_DATA_SETUP.md for details)
# Add API keys for weather data, news, and enhanced city search features

# Initialize database
python app/init_db.py

# Start the API server
python run_server.py
```

The backend API will be available at `http://localhost:8000`

#### 4. Database Setup
1. Create a PostgreSQL database
2. Update the database URL in your `.env` file
3. Run database migrations and seed initial data:
```bash
python migrate_database.py
python app/seed_data.py
```

### Building for Production

#### Frontend
```bash
npm run build
```
Built files will be in the `dist` directory.

#### Backend
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📁 Project Structure

```
urban-project/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx         # Main landing page
│   │   │   ├── CitySearch.jsx          # City search functionality
│   │   │   ├── InteractiveMap.jsx      # Leaflet map component
│   │   │   ├── MapExplorer.jsx         # Advanced map interface
│   │   │   ├── GreenCoverageChart.jsx  # Data visualization
│   │   │   ├── CityInsights.jsx        # City analytics dashboard
│   │   │   ├── ParksResultsList.jsx    # Parks search results
│   │   │   ├── Navbar.jsx              # Navigation component
│   │   │   └── Footer.jsx              # Footer component
│   │   ├── contexts/
│   │   │   ├── FilterContext.jsx       # Map filtering state
│   │   │   └── ThemeContext.jsx        # Dark/light theme
│   │   ├── services/
│   │   │   └── api.js                  # API client functions
│   │   ├── App.jsx                     # Main application component
│   │   └── main.jsx                    # React entry point
│   ├── public/                         # Static assets
│   ├── package.json                    # Frontend dependencies
│   ├── vite.config.js                  # Vite configuration
│   └── tailwind.config.js              # Tailwind CSS config
├── backend/
│   ├── app/
│   │   ├── models/                     # Database models
│   │   │   ├── city.py                 # City data model
│   │   │   ├── park.py                 # Park data model
│   │   │   ├── green_coverage.py       # Coverage data model
│   │   │   ├── user.py                 # User authentication
│   │   │   ├── feedback.py             # User feedback model
│   │   │   └── cache.py                # Caching system
│   │   ├── routers/                    # API route handlers
│   │   │   ├── auth.py                 # Authentication routes
│   │   │   └── shapefile.py            # Geospatial data routes
│   │   ├── services/                   # Business logic services
│   │   │   ├── auth_service.py         # Authentication logic
│   │   │   ├── cache_service.py        # Caching operations
│   │   │   └── background_tasks.py     # Automated updates
│   │   ├── main.py                     # FastAPI application
│   │   ├── database.py                 # Database configuration
│   │   ├── schemas.py                  # Pydantic data models
│   │   └── config.py                   # Application settings
│   ├── requirements.txt                # Python dependencies
│   ├── run_server.py                   # Development server
│   └── migrate_database.py             # Database migrations
└── README.md                           # Project documentation
```

## 🔌 API Documentation

### Core Endpoints

#### Cities
- `GET /cities` - List all cities with pagination
- `GET /city/search?name={query}` - Search cities by name
- `GET /cities/{city_id}` - Get specific city details
- `POST /cities` - Create new city (admin only)
- `PUT /cities/{city_id}` - Update city (admin only)
- `DELETE /cities/{city_id}` - Delete city (admin only)

#### Parks
- `GET /parks` - List all parks with optional city filtering
- `GET /parks/nearest` - Find nearest parks within radius
- `GET /parks/{park_id}` - Get specific park details
- `POST /parks` - Create new park (admin only)
- `PUT /parks/{park_id}` - Update park (admin only)
- `DELETE /parks/{park_id}` - Delete park (admin only)

#### Green Coverage
- `GET /green-coverage` - List green coverage data
- `GET /coverage/compare?city_name={name}` - Compare with WHO standards
- `GET /coverage/trend?city_name={name}` - Historical trend data
- `POST /green-coverage` - Create coverage data (admin only)

#### Background Tasks
- `GET /background-tasks/status` - Check automation status
- `POST /background-tasks/trigger-update` - Manual update (admin only)
- `POST /background-tasks/start` - Start scheduler (admin only)
- `POST /background-tasks/stop` - Stop scheduler (admin only)

#### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/register` - Create new user (admin only)
- `GET /auth/me` - Get current user info

### Interactive API Documentation
Visit `http://localhost:8000/docs` for the complete Swagger UI documentation with interactive testing capabilities.

## 📊 Features in Detail

### Satellite Imagery Processing
- **NDVI Analysis**: Normalized Difference Vegetation Index calculations
- **Automated Updates**: Weekly processing of new satellite data
- **Historical Tracking**: Multi-year coverage trend analysis
- **Data Sources**: Integration with multiple satellite imagery providers

### Intelligent Caching System
- **Performance Optimization**: Smart caching of expensive calculations
- **Automatic Expiration**: Time-based cache invalidation
- **Selective Clearing**: City-specific cache management
- **Statistics Tracking**: Cache hit/miss ratio monitoring

### Authentication & Security
- **JWT Tokens**: Secure user session management
- **Role-Based Access**: Admin/user permission levels
- **Password Hashing**: Bcrypt encryption for user passwords
- **API Rate Limiting**: Protection against abuse

### Real-Time Data Processing
- **Background Tasks**: Automated data collection and processing
- **Scheduler Management**: APScheduler for recurring tasks
- **Error Handling**: Robust error recovery and logging
- **Manual Triggers**: Admin-controlled update processes

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/urban_project

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Background Tasks
ENABLE_BACKGROUND_TASKS=true
UPDATE_SCHEDULE_CRON="0 2 * * 1"  # Weekly at 2 AM on Mondays

# Logging
LOG_LEVEL=INFO
LOG_FILE=urban_api.log

# Cache Configuration
CACHE_EXPIRY_HOURS=24
```

### Frontend Configuration

The frontend automatically connects to the backend API. Update `src/services/api.js` if needed:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run specific test files
pytest test_auth_system.py
pytest test_feedback_endpoint.py
pytest test_nearest_parks.py
```

### Frontend Testing
```bash
# Run frontend tests
npm test

# Run integration tests
npm run test:integration
```

## 🚀 Deployment

### Production Deployment

#### Backend (FastAPI)
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --host 0.0.0.0 --port 8000
```

#### Frontend (React)
```bash
# Build for production
npm run build

# Serve with any static file server
npx serve -s dist
```

### Docker Deployment

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: urban_project
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/urban_project
    depends_on:
      - db
    ports:
      - "8000:8000"

  frontend:
    build: ./
    ports:
      - "80:80"

volumes:
  postgres_data:
```

## 🤝 Contributing

We welcome contributions to the Urban Green Spaces Tracker! Here's how you can help:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Test your changes**
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend tests
   npm test
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Submit a pull request**

### Code Style Guidelines

#### Frontend (React/JavaScript)
- Use ES6+ syntax and React hooks
- Follow ESLint configuration
- Use Tailwind CSS for styling
- Write descriptive component names

#### Backend (Python)
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Write comprehensive docstrings
- Follow FastAPI best practices

### Areas for Contribution

- 🐛 **Bug fixes** - Help us squash bugs
- 🚀 **New features** - Add exciting new functionality
- 📚 **Documentation** - Improve or translate documentation
- 🧪 **Testing** - Increase test coverage
- 🎨 **UI/UX** - Enhance user experience
- 🌍 **Internationalization** - Add multi-language support

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Urban Green Spaces Tracker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🏆 Acknowledgments

- **Icons**: Beautiful icons provided by [Lucide React](https://lucide.dev/)
- **Maps**: Interactive mapping powered by [Leaflet](https://leafletjs.com/)
- **Satellite Data**: Geospatial analysis using [Geopandas](https://geopandas.org/) and [Rasterio](https://rasterio.readthedocs.io/)
- **Charts**: Data visualization with [Recharts](https://recharts.org/)
- **Design**: Inspiration from modern eco-friendly design trends
- **Community**: Built following React, FastAPI, and accessibility best practices
- **WHO Standards**: Green coverage recommendations based on World Health Organization guidelines

## 📞 Support

### Getting Help

- 📖 **Documentation**: Check this README and inline code comments
- 🐛 **Issues**: Report bugs or request features via [GitHub Issues](../../issues)
- 💬 **Discussions**: Join community discussions in [GitHub Discussions](../../discussions)
- 📧 **Contact**: Reach out to the maintainers for specific questions

### Reporting Issues

When reporting issues, please include:
- Operating system and version
- Node.js and Python versions
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs

### Feature Requests

We love hearing about new ideas! When suggesting features:
- Describe the problem you're trying to solve
- Explain how the feature would work
- Consider the impact on existing functionality
- Provide examples or mockups if helpful

---

**Happy coding! 🌱 Let's make cities greener together!**
