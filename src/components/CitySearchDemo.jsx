import React from 'react';
import CitySearch from './CitySearch';

const CitySearchDemo = () => {
  const handleCitySelect = (city) => {
    console.log('Demo: Selected city:', city);
    alert(`Selected: ${city.name}${city.state ? `, ${city.state}` : ''}${city.country ? `, ${city.country}` : ''}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-nature-green-50 via-sky-blue-50 to-nature-green-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            City Search Component Demo
          </h1>
          <p className="text-lg text-gray-600">
            Try searching for cities with autocomplete suggestions
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-white/20">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Search for a City
            </h2>
            <p className="text-gray-600 mb-6">
              Start typing to see autocomplete suggestions. Use arrow keys to navigate and Enter to select.
            </p>
          </div>

          <CitySearch 
            onCitySelect={handleCitySelect}
            placeholder="Start typing a city name..."
          />

          <div className="mt-8 p-4 bg-gray-50 rounded-xl">
            <h3 className="font-semibold text-gray-700 mb-2">Features:</h3>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              <li>Real-time autocomplete with city suggestions</li>
              <li>Keyboard navigation (Arrow keys, Enter, Escape)</li>
              <li>Click to select or search manually</li>
              <li>Location pin icon inside input field</li>
              <li>Clear button when text is entered</li>
              <li>Loading indicator during search</li>
              <li>Responsive design with hover effects</li>
              <li>Rounded borders and modern styling</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CitySearchDemo;