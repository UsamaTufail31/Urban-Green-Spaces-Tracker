import React, { useState, useRef, useEffect } from 'react';
import { Search, MapPin, X } from 'lucide-react';
import { searchCities, ApiError } from '../services/api';

const CitySearch = ({ onCitySelect, placeholder = "Search for a city..." }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  // Search cities using the backend API
  const searchCitiesFromAPI = async (searchQuery) => {
    try {
      setError(null);
      const cities = await searchCities(searchQuery, 8, true); // Enhanced search with real-time data
      return cities.map(city => ({
        id: city.id,
        name: city.name,
        country: city.country,
        state: city.state_province || '',
        latitude: city.latitude,
        longitude: city.longitude,
        population: city.population,
        area_km2: city.area_km2,
        description: city.description,
        realtime_data: city.realtime_data // Include real-time data
      }));
    } catch (err) {
      console.error('City search error:', err);
      setError(err instanceof ApiError ? err.message : 'Failed to search cities');
      return [];
    }
  };

  // Handle input change
  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    setError(null);
    
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (value.length >= 2) {
      setIsLoading(true);
      
      // Debounce API calls
      searchTimeoutRef.current = setTimeout(async () => {
        try {
          const cities = await searchCitiesFromAPI(value);
          setSuggestions(cities);
          setIsDropdownOpen(cities.length > 0);
          setSelectedIndex(-1);
        } catch (err) {
          setSuggestions([]);
          setIsDropdownOpen(false);
        } finally {
          setIsLoading(false);
        }
      }, 300);
    } else {
      setSuggestions([]);
      setIsDropdownOpen(false);
      setIsLoading(false);
    }
  };

  // Handle city selection
  const handleCitySelect = (city) => {
    const displayText = city.state 
      ? `${city.name}, ${city.state}, ${city.country}`
      : `${city.name}, ${city.country}`;
    
    setQuery(displayText);
    setIsDropdownOpen(false);
    setSuggestions([]);
    setSelectedIndex(-1);
    setError(null);
    
    if (onCitySelect) {
      onCitySelect(city);
    }
  };

  // Handle search button click
  const handleSearch = async () => {
    if (query.trim()) {
      // If there's a selected suggestion, use it
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        handleCitySelect(suggestions[selectedIndex]);
      } else {
        // Otherwise, search with the current query and use the first result
        try {
          setIsLoading(true);
          const cities = await searchCitiesFromAPI(query.trim());
          if (cities.length > 0) {
            handleCitySelect(cities[0]);
          } else {
            setError('No cities found for your search');
          }
        } catch (err) {
          setError('Failed to search cities');
        } finally {
          setIsLoading(false);
        }
      }
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!isDropdownOpen || suggestions.length === 0) {
      if (e.key === 'Enter') {
        handleSearch();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          handleCitySelect(suggestions[selectedIndex]);
        } else {
          handleSearch();
        }
        break;
      case 'Escape':
        setIsDropdownOpen(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
      default:
        break;
    }
  };

  // Clear input
  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setIsDropdownOpen(false);
    setSelectedIndex(-1);
    setError(null);
    
    // Clear any pending search
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    inputRef.current?.focus();
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        !inputRef.current?.contains(event.target)
      ) {
        setIsDropdownOpen(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      {/* Search Input Container */}
      <div className="relative">
        {/* Location Pin Icon */}
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
          <MapPin className="h-5 w-5 text-gray-400" />
        </div>

        {/* Input Field */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full pl-12 pr-24 py-4 text-lg border-2 border-gray-200 rounded-2xl 
                   focus:border-nature-green-400 focus:ring-4 focus:ring-nature-green-100 
                   transition-all duration-200 bg-white/50 backdrop-blur-sm
                   hover:border-gray-300 hover:shadow-md
                   placeholder:text-gray-400"
          autoComplete="off"
        />

        {/* Clear Button */}
        {query && (
          <button
            onClick={handleClear}
            className="absolute inset-y-0 right-16 flex items-center pr-2 text-gray-400 
                     hover:text-gray-600 transition-colors duration-200"
            type="button"
          >
            <X className="h-5 w-5" />
          </button>
        )}

        {/* Search Button */}
        <button
          onClick={handleSearch}
          disabled={!query.trim()}
          className="absolute inset-y-0 right-0 flex items-center pr-4 text-nature-green-500 
                   hover:text-nature-green-600 transition-colors duration-200
                   disabled:text-gray-300 disabled:cursor-not-allowed"
          type="button"
        >
          <Search className="h-6 w-6" />
        </button>

        {/* Loading Indicator */}
        {isLoading && (
          <div className="absolute inset-y-0 right-12 flex items-center pr-2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-nature-green-500 border-t-transparent"></div>
          </div>
        )}
      </div>

      {/* Dropdown Suggestions */}
      {isDropdownOpen && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-2xl 
                   border border-gray-200 overflow-hidden z-50 backdrop-blur-sm bg-white/95"
        >
          <div className="max-h-80 overflow-y-auto">
            {suggestions.map((city, index) => (
              <button
                key={city.id || `${city.name}-${city.state}-${city.country}`}
                onClick={() => handleCitySelect(city)}
                className={`w-full px-4 py-3 text-left hover:bg-nature-green-50 transition-colors duration-150
                          border-b border-gray-100 last:border-b-0 flex items-start gap-3
                          ${selectedIndex === index ? 'bg-nature-green-50 text-nature-green-700' : 'text-gray-700'}
                          ${index === 0 ? 'rounded-t-2xl' : ''} 
                          ${index === suggestions.length - 1 ? 'rounded-b-2xl' : ''}`}
                type="button"
              >
                <MapPin className="h-4 w-4 text-gray-400 flex-shrink-0 mt-1" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{city.name}</div>
                  <div className="text-sm text-gray-500 truncate">
                    {city.state ? `${city.state}, ${city.country}` : city.country}
                  </div>
                  {city.population && (
                    <div className="text-xs text-gray-400">
                      Population: {city.population.toLocaleString()}
                    </div>
                  )}
                  {/* Real-time weather data */}
                  {city.realtime_data?.weather && (
                    <div className="flex items-center gap-2 mt-1">
                      <div className="text-xs text-blue-600 font-medium">
                        {Math.round(city.realtime_data.weather.temperature)}°C
                      </div>
                      <div className="text-xs text-gray-500">
                        {city.realtime_data.weather.description}
                      </div>
                      {city.realtime_data.weather.icon && (
                        <img
                          src={`https://openweathermap.org/img/wn/${city.realtime_data.weather.icon}@2x.png`}
                          alt={city.realtime_data.weather.description}
                          className="w-6 h-6"
                        />
                      )}
                    </div>
                  )}
                  {/* Data freshness indicator */}
                  {city.realtime_data?.timestamp && (
                    <div className="text-xs text-green-500 mt-1">
                      ✓ Live data
                    </div>
                  )}
                  {city.realtime_data?.error && (
                    <div className="text-xs text-orange-500 mt-1">
                      ⚠ Limited data
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* No Results or Error Message */}
      {isDropdownOpen && suggestions.length === 0 && query.length >= 2 && !isLoading && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-2xl 
                   border border-gray-200 overflow-hidden z-50 backdrop-blur-sm bg-white/95"
        >
          <div className="px-4 py-6 text-center text-gray-500">
            <MapPin className="h-8 w-8 mx-auto mb-2 text-gray-300" />
            {error ? (
              <>
                <p className="text-red-500 font-medium">{error}</p>
                <p className="text-sm mt-1">Please try again or check your connection</p>
              </>
            ) : (
              <>
                <p>No cities found for "{query}"</p>
                <p className="text-sm mt-1">Try searching with a different name</p>
              </>
            )}
          </div>
        </div>
      )}

      {/* Error display above input */}
      {error && !isDropdownOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 text-sm text-red-500 bg-red-50 
                      px-3 py-2 rounded-lg border border-red-200">
          {error}
        </div>
      )}
    </div>
  );
};

export default CitySearch;