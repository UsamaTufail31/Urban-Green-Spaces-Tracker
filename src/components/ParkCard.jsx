import React from 'react';
import { Trees, MapPin, Maximize2 } from 'lucide-react';

const ParkCard = ({ park, distance, isVisible = true }) => {
  const formatDistance = (distanceInKm) => {
    if (distanceInKm < 1) {
      return `${Math.round(distanceInKm * 1000)}m`;
    }
    return `${distanceInKm.toFixed(1)}km`;
  };

  return (
    <div 
      className={`
        bg-white rounded-xl shadow-lg border border-gray-100 p-4 
        hover:shadow-xl hover:border-nature-green-200 
        transition-all duration-300 ease-out
        transform ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}
        hover:scale-105 cursor-pointer
      `}
    >
      {/* Header with icon and name */}
      <div className="flex items-start gap-3 mb-3">
        <div className="bg-nature-green-100 p-2 rounded-lg flex-shrink-0">
          <Trees className="w-5 h-5 text-nature-green-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight truncate">
            {park.name}
          </h3>
          <p className="text-gray-500 text-xs mt-1 truncate">
            {park.amenities || park.type || 'Park'}
          </p>
        </div>
      </div>

      {/* Stats row */}
      <div className="flex items-center justify-between text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <MapPin className="w-3 h-3 text-nature-green-500" />
          <span className="font-medium">{formatDistance(distance)}</span>
        </div>
        
        <div className="flex items-center gap-1">
          <Maximize2 className="w-3 h-3 text-nature-green-500" />
          <span className="font-medium">
            {park.area_hectares 
              ? `${park.area_hectares} ha` 
              : park.area || 'N/A'
            }
          </span>
        </div>
      </div>

      {/* Rating if available */}
      {park.rating && (
        <div className="flex items-center gap-1 mt-2 pt-2 border-t border-gray-100">
          <span className="text-yellow-400 text-sm">⭐</span>
          <span className="text-xs font-medium text-gray-700">{park.rating}/5</span>
        </div>
      )}

      {/* Quick feature tags */}
      {park.features && park.features.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-100">
          <div className="flex flex-wrap gap-1">
            {park.features.slice(0, 2).map((feature, index) => (
              <span 
                key={index}
                className="inline-block bg-nature-green-50 text-nature-green-700 text-xs px-2 py-1 rounded-full"
              >
                {feature}
              </span>
            ))}
            {park.features.length > 2 && (
              <span className="text-xs text-gray-400 px-1 py-1">
                +{park.features.length - 2} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ParkCard;