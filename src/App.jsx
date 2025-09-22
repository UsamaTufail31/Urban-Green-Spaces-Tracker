import React, { useState } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import CitySearchDemo from './components/CitySearchDemo';
import MapExplorer from './components/MapExplorer';
import GreenCoverageChart from './components/GreenCoverageChart';
import CityInsights from './components/CityInsights';
import CitySearch from './components/CitySearch';
import Footer from './components/Footer';
import About from './components/About';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [globalSelectedCity, setGlobalSelectedCity] = useState(null);

  const handleCitySelection = (city) => {
    setGlobalSelectedCity(city);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-300">
      {/* Main Navbar */}
      <Navbar />
      
      {/* Navigation */}
      <div className="fixed top-20 left-4 z-40">
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 dark:border-gray-700/20 p-2">
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage('landing')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                currentPage === 'landing'
                  ? 'bg-nature-green-500 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Landing Page
            </button>
            <button
              onClick={() => setCurrentPage('demo')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                currentPage === 'demo'
                  ? 'bg-nature-green-500 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Search Demo
            </button>
            <button
              onClick={() => setCurrentPage('map')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                currentPage === 'map'
                  ? 'bg-nature-green-500 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Map Explorer
            </button>
            <button
              onClick={() => setCurrentPage('stats')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                currentPage === 'stats'
                  ? 'bg-nature-green-500 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Statistics
            </button>
            <button
              onClick={() => setCurrentPage('insights')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                currentPage === 'insights'
                  ? 'bg-nature-green-500 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              City Insights
            </button>
            <button
              onClick={() => setCurrentPage('about')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                currentPage === 'about'
                  ? 'bg-nature-green-500 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              About
            </button>
          </div>
        </div>
      </div>

      {/* Page Content - Added padding top for navbar */}
      <div className="pt-16">
        {currentPage === 'landing' ? (
          <LandingPage />
        ) : currentPage === 'demo' ? (
          <CitySearchDemo />
        ) : currentPage === 'map' ? (
          <MapExplorer />
        ) : currentPage === 'stats' ? (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800 p-8">
            <div className="max-w-6xl mx-auto pt-20">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">
                  Green Coverage Statistics
                </h1>
                <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                  Analyze urban green space coverage and compare with WHO recommendations for sustainable city development.
                </p>
              </div>
              
              {/* City Selection for Statistics */}
              <div className="mb-8 max-w-md mx-auto">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select a city to view its green coverage trend:
                </label>
                <CitySearch
                  onCitySelect={handleCitySelection}
                  placeholder="Search for a city..."
                />
                {globalSelectedCity && (
                  <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    Selected: <span className="font-medium">{globalSelectedCity.name}, {globalSelectedCity.country}</span>
                  </div>
                )}
              </div>
              
              <GreenCoverageChart 
                selectedCity={globalSelectedCity}
              />
            </div>
          </div>
        ) : currentPage === 'insights' ? (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800 p-8">
            <div className="max-w-6xl mx-auto pt-20">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">
                  City Insights & Live Data
                </h1>
                <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                  Explore comprehensive city insights with real-time weather, news, and country data.
                </p>
              </div>
              
              {/* City Selection for Insights */}
              <div className="mb-8 max-w-md mx-auto">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select a city to view insights:
                </label>
                <CitySearch
                  onCitySelect={handleCitySelection}
                  placeholder="Search for a city with live data..."
                />
                {globalSelectedCity && (
                  <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    Selected: <span className="font-medium">{globalSelectedCity.name}, {globalSelectedCity.country}</span>
                  </div>
                )}
              </div>
              
              <CityInsights 
                cityName={globalSelectedCity ? `${globalSelectedCity.name}, ${globalSelectedCity.country}` : "Your City"}
                realTimeData={globalSelectedCity?.realtime_data}
              />
            </div>
          </div>
        ) : currentPage === 'about' ? (
          <About />
        ) : (
          <MapExplorer />
        )}
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
