import React, { useState } from 'react';
import CitySearch from './CitySearch';
import InteractiveMap from './InteractiveMap';
import DashboardCards from './DashboardCards';
import ParksResultsList from './ParksResultsList';
import { FilterProvider } from '../contexts/FilterContext';

const MapExplorer = () => {
  const [selectedCity, setSelectedCity] = useState(null);
  const [isSearchCollapsed, setIsSearchCollapsed] = useState(false);
  const [filteredParks, setFilteredParks] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [isLoadingParks, setIsLoadingParks] = useState(false);

  const handleCitySelect = (city) => {
    setSelectedCity(city);
    setIsLoadingParks(true);
    // Clear previous parks while loading new ones
    setFilteredParks([]);
    
    // Collapse search on mobile after selection
    if (window.innerWidth < 768) {
      setIsSearchCollapsed(true);
    }
  };

  const handleParksUpdate = (parks, location) => {
    setFilteredParks(parks);
    setUserLocation(location);
    setIsLoadingParks(false);
  };

  return (
    <FilterProvider>
      <div className="relative w-full min-h-screen bg-gray-100 flex flex-col">
        {/* Search overlay */}
        <div className={`absolute top-4 left-1/2 transform -translate-x-1/2 z-20 w-full max-w-2xl px-4 transition-all duration-300 ${
          isSearchCollapsed ? 'translate-y-[-100%] opacity-0 pointer-events-none' : ''
        }`}>
          <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/30 p-4 md:p-6">
            <div className="text-center mb-4">
              <h2 className="text-xl md:text-2xl font-bold text-gray-800 mb-2">
                🌍 Explore Urban Green Spaces
              </h2>
              <p className="text-gray-600 text-xs md:text-sm">
                Search for a city to discover parks, gardens, and green areas
              </p>
            </div>
            <CitySearch 
              onCitySelect={handleCitySelect}
              placeholder="Search for a city to explore green spaces..."
            />
            
            {/* Collapse button for mobile */}
            {selectedCity && (
              <button
                onClick={() => setIsSearchCollapsed(true)}
                className="md:hidden w-full mt-3 px-4 py-2 bg-nature-green-500 text-white rounded-xl text-sm font-medium hover:bg-nature-green-600 transition-colors"
              >
                Show Map
              </button>
            )}
          </div>
        </div>

        {/* Expand search button for mobile */}
        {isSearchCollapsed && (
          <button
            onClick={() => setIsSearchCollapsed(false)}
            className="md:hidden absolute top-4 left-4 z-20 bg-white/90 backdrop-blur-sm rounded-full p-3 shadow-lg border border-white/20 hover:bg-white transition-colors"
          >
            <span className="text-lg">🔍</span>
          </button>
        )}

        {/* Map container */}
        <div className="flex-1 relative">
          <InteractiveMap 
            selectedCity={selectedCity} 
            onParksUpdate={handleParksUpdate}
          />
          
          {/* Instructions overlay */}
          {!selectedCity && !isSearchCollapsed && (
            <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-20 w-full max-w-lg px-4">
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-4 text-center">
                <div className="flex items-center justify-center gap-2 text-nature-green-600 mb-2">
                  <span className="text-xl md:text-2xl">🔍</span>
                  <span className="font-medium text-sm md:text-base">Getting Started</span>
                </div>
                <p className="text-gray-600 text-xs md:text-sm">
                  Search for a city above to see parks and green areas on the map. 
                  Click on the green markers to learn more about each location.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Parks Results Section */}
        <ParksResultsList 
          parks={filteredParks}
          userLocation={userLocation}
          isLoading={isLoadingParks}
          selectedCity={selectedCity}
        />

        {/* Dashboard Cards Section */}
        <DashboardCards selectedCity={selectedCity} />
      </div>
    </FilterProvider>
  );
};

export default MapExplorer;