import React, { useState, useEffect } from 'react';
import { Search, MapPin, Leaf, Trees, Flower, Globe } from 'lucide-react';
import CitySearch from './CitySearch';

const FloatingLeaf = ({ delay, size, left, animationDuration }) => (
  <div
    className={`leaf animate-float`}
    style={{
      left: `${left}%`,
      width: `${size}px`,
      height: `${size}px`,
      animationDelay: `${delay}s`,
      animationDuration: `${animationDuration}s`,
    }}
  />
);

const LandingPage = () => {
  const [selectedCity, setSelectedCity] = useState(null);
  const [isLocationLoading, setIsLocationLoading] = useState(false);

  const handleCitySelect = (city) => {
    setSelectedCity(city);
    console.log('Selected city:', city);
    // Here you would implement the actual search functionality
  };

  const handleUseMyLocation = () => {
    setIsLocationLoading(true);
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('Location:', position.coords);
          setIsLocationLoading(false);
          // Here you would implement reverse geocoding to get city name
          setSelectedCity({ 
            name: 'Current Location', 
            country: '', 
            state: '',
            coords: position.coords 
          });
        },
        (error) => {
          console.error('Error getting location:', error);
          setIsLocationLoading(false);
          alert('Unable to get your location. Please enter your city manually.');
        }
      );
    } else {
      setIsLocationLoading(false);
      alert('Geolocation is not supported by this browser.');
    }
  };

  // Generate floating leaves
  const leaves = Array.from({ length: 8 }, (_, i) => ({
    id: i,
    delay: Math.random() * 6,
    size: 15 + Math.random() * 25,
    left: Math.random() * 100,
    animationDuration: 6 + Math.random() * 4,
  }));

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-nature-green-50 via-sky-blue-50 to-nature-green-100">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {leaves.map((leaf) => (
          <FloatingLeaf
            key={leaf.id}
            delay={leaf.delay}
            size={leaf.size}
            left={leaf.left}
            animationDuration={leaf.animationDuration}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12 max-w-4xl">
          {/* Icon Header */}
          <div className="flex justify-center items-center gap-4 mb-6">
            <div className="p-3 bg-nature-green-100 rounded-full shadow-lg">
              <Trees className="w-8 h-8 text-nature-green-600" />
            </div>
            <div className="p-3 bg-sky-blue-100 rounded-full shadow-lg">
              <Globe className="w-8 h-8 text-sky-blue-600" />
            </div>
            <div className="p-3 bg-nature-green-100 rounded-full shadow-lg">
              <Flower className="w-8 h-8 text-nature-green-600" />
            </div>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-800 mb-6 leading-tight">
            <span className="bg-gradient-to-r from-nature-green-600 to-sky-blue-600 bg-clip-text text-transparent">
              Green Space
            </span>
            <br />
            <span className="text-gray-700">Tracker</span>
          </h1>

          {/* Description */}
          <p className="text-xl md:text-2xl text-gray-600 mb-12 leading-relaxed max-w-3xl mx-auto">
            Discover parks, gardens, and green spaces in your city. Find your perfect spot to connect with nature, 
            relax, and enjoy the outdoors right in your neighborhood.
          </p>
        </div>

        {/* Search Card */}
        <div className="w-full max-w-2xl mx-auto">
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 md:p-12 border border-white/20">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 bg-nature-green-100 text-nature-green-700 px-4 py-2 rounded-full text-sm font-medium mb-4">
                <Leaf className="w-4 h-4" />
                Start Your Green Journey
              </div>
              <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">
                Find Green Spaces Near You
              </h2>
              <p className="text-gray-600">
                Enter your city name or use your current location to discover beautiful green spaces nearby.
              </p>
            </div>

            {/* Search Form */}
            <div className="space-y-6">
              {/* City Search Component */}
              <CitySearch 
                onCitySelect={handleCitySelect}
                placeholder="Enter your city name..."
              />

              {/* Use My Location Button */}
              <div className="flex justify-center">
                <button
                  type="button"
                  onClick={handleUseMyLocation}
                  disabled={isLocationLoading}
                  className="bg-gradient-to-r from-sky-blue-500 to-sky-blue-600 text-white py-4 px-8 rounded-2xl font-semibold text-lg hover:from-sky-blue-600 hover:to-sky-blue-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  <span className="flex items-center justify-center gap-2">
                    <MapPin className={`w-5 h-5 ${isLocationLoading ? 'animate-pulse' : ''}`} />
                    {isLocationLoading ? 'Getting Location...' : 'Use My Location'}
                  </span>
                </button>
              </div>

              {/* Selected City Display */}
              {selectedCity && (
                <div className="mt-4 p-4 bg-nature-green-50 rounded-xl border border-nature-green-200">
                  <div className="flex items-center gap-2 text-nature-green-700">
                    <MapPin className="w-4 h-4" />
                    <span className="font-medium">Selected:</span>
                    <span>
                      {selectedCity.name}
                      {selectedCity.state && `, ${selectedCity.state}`}
                      {selectedCity.country && `, ${selectedCity.country}`}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Feature Icons */}
            <div className="mt-8 pt-8 border-t border-gray-200">
              <div className="flex justify-center items-center gap-8 text-sm text-gray-500">
                <div className="flex items-center gap-2">
                  <Trees className="w-5 h-5 text-nature-green-500" />
                  <span>Parks</span>
                </div>
                <div className="flex items-center gap-2">
                  <Flower className="w-5 h-5 text-nature-green-500" />
                  <span>Gardens</span>
                </div>
                <div className="flex items-center gap-2">
                  <Leaf className="w-5 h-5 text-nature-green-500" />
                  <span>Nature Trails</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Text */}
        <div className="mt-12 text-center">
          <p className="text-gray-500 text-sm">
            Join thousands of nature lovers discovering green spaces in their cities
          </p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;