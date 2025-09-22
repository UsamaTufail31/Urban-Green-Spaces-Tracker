import React, { useState, useEffect } from 'react';
import ParkCard from './ParkCard';
import { MapPin, Search } from 'lucide-react';

const ParksResultsList = ({ parks = [], userLocation, isLoading = false, selectedCity }) => {
  const [visibleCards, setVisibleCards] = useState([]);
  const [sortedParks, setSortedParks] = useState([]);

  // Calculate distance between two coordinates (Haversine formula)
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  // Sort parks by distance and calculate distances
  useEffect(() => {
    if (parks.length > 0 && userLocation) {
      const parksWithDistance = parks.map(park => {
        // Handle both API format (latitude/longitude) and mock format (coordinates array)
        const parkLat = park.latitude || park.coordinates?.[0];
        const parkLon = park.longitude || park.coordinates?.[1];
        
        let distance = 0;
        if (parkLat && parkLon) {
          // Use distance from API if available, otherwise calculate
          distance = park.distance_km || calculateDistance(
            userLocation[0], 
            userLocation[1], 
            parkLat, 
            parkLon
          );
        }
        
        return {
          ...park,
          distance: distance
        };
      });

      // Sort by distance and take the nearest 8 parks
      const sorted = parksWithDistance
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 8);
      
      setSortedParks(sorted);
    } else {
      setSortedParks(parks.slice(0, 8)); // Just take first 8 if no user location
    }
  }, [parks, userLocation]);

  // Animate cards in with staggered delays
  useEffect(() => {
    if (sortedParks.length > 0 && !isLoading) {
      setVisibleCards([]);
      
      sortedParks.forEach((_, index) => {
        setTimeout(() => {
          setVisibleCards(prev => [...prev, index]);
        }, index * 150); // 150ms delay between each card
      });
    }
  }, [sortedParks, isLoading]);

  if (isLoading) {
    return (
      <div className="bg-white border-t border-gray-200 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-2 mb-4">
            <Search className="w-5 h-5 text-nature-green-600 animate-spin" />
            <h2 className="text-lg font-semibold text-gray-900">
              Finding nearest parks...
            </h2>
          </div>
          
          {/* Loading skeleton */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[...Array(8)].map((_, index) => (
              <div 
                key={index}
                className="bg-gray-100 rounded-xl h-32 animate-pulse"
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (sortedParks.length === 0) {
    return (
      <div className="bg-white border-t border-gray-200 p-6">
        <div className="max-w-6xl mx-auto text-center py-8">
          <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No parks found nearby
          </h3>
          <p className="text-gray-500">
            {selectedCity 
              ? `Try selecting a different city or adjusting your filters` 
              : `Select a city to find parks and green spaces`
            }
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-t border-gray-200 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-nature-green-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Nearest Parks
            </h2>
            <span className="bg-nature-green-100 text-nature-green-700 text-sm px-2 py-1 rounded-full font-medium">
              {sortedParks.length}
            </span>
          </div>
          
          {selectedCity && (
            <div className="text-sm text-gray-500">
              Near {selectedCity.name}
            </div>
          )}
        </div>

        {/* Parks Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {sortedParks.map((park, index) => (
            <ParkCard
              key={`${park.name}-${index}`}
              park={park}
              distance={park.distance}
              isVisible={visibleCards.includes(index)}
            />
          ))}
        </div>

        {/* View More Button (placeholder for future pagination) */}
        {parks.length > 8 && (
          <div className="text-center mt-6">
            <button className="bg-nature-green-50 hover:bg-nature-green-100 text-nature-green-700 px-6 py-2 rounded-lg font-medium transition-colors duration-200">
              View More Parks
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ParksResultsList;