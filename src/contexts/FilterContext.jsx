import React, { createContext, useContext, useState, useEffect } from 'react';

const FilterContext = createContext();

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};

export const FilterProvider = ({ children }) => {
  const [filters, setFilters] = useState({
    parkSize: [],
    walkingDistance: [],
    amenities: []
  });

  const [isFilterSidebarOpen, setIsFilterSidebarOpen] = useState(false);

  // Filter parks based on current filter selections
  const filterParks = (parks) => {
    if (!parks) return [];

    return parks.filter(park => {
      // Park size filtering
      if (filters.parkSize.length > 0) {
        const parkArea = parseInt(park.area?.replace(/[^\d]/g, '') || '0');
        const sizeMatch = filters.parkSize.some(size => {
          switch (size) {
            case 'small':
              return parkArea < 50;
            case 'medium':
              return parkArea >= 50 && parkArea <= 200;
            case 'large':
              return parkArea > 200;
            default:
              return false;
          }
        });
        if (!sizeMatch) return false;
      }

      // Amenities filtering
      if (filters.amenities.length > 0) {
        const parkFeatures = park.features?.map(f => f.toLowerCase()) || [];
        const amenityMatch = filters.amenities.some(amenity => {
          switch (amenity) {
            case 'playground':
              return parkFeatures.some(f => f.includes('playground') || f.includes('children'));
            case 'jogging-track':
              return parkFeatures.some(f => f.includes('trail') || f.includes('path') || f.includes('track') || f.includes('jogging'));
            case 'lake':
              return parkFeatures.some(f => f.includes('lake') || f.includes('water') || f.includes('pond') || f.includes('river'));
            case 'sports-facilities':
              return parkFeatures.some(f => f.includes('sport') || f.includes('court') || f.includes('field') || f.includes('gym'));
            case 'picnic-areas':
              return parkFeatures.some(f => f.includes('picnic') || f.includes('dining') || f.includes('table'));
            case 'dog-park':
              return parkFeatures.some(f => f.includes('dog') || f.includes('pet'));
            default:
              return false;
          }
        });
        if (!amenityMatch) return false;
      }

      return true;
    });
  };

  // Calculate distance between two coordinates (simplified)
  const calculateDistance = (coord1, coord2) => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (coord2[0] - coord1[0]) * Math.PI / 180;
    const dLon = (coord2[1] - coord1[1]) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(coord1[0] * Math.PI / 180) * Math.cos(coord2[0] * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  // Filter parks by distance from selected city
  const filterParksByDistance = (parks, cityCoordinates) => {
    if (!cityCoordinates || filters.walkingDistance.length === 0) return parks;

    const maxDistances = filters.walkingDistance.map(distance => {
      switch (distance) {
        case '1km': return 1;
        case '3km': return 3;
        case '5km': return 5;
        default: return Infinity;
      }
    });

    const maxDistance = Math.max(...maxDistances);

    return parks.filter(park => {
      if (!park.coordinates) return false;
      const distance = calculateDistance(cityCoordinates, park.coordinates);
      return distance <= maxDistance;
    });
  };

  // Apply all filters
  const applyFilters = (parks, cityCoordinates) => {
    let filteredParks = filterParks(parks);
    if (cityCoordinates) {
      filteredParks = filterParksByDistance(filteredParks, cityCoordinates);
    }
    return filteredParks;
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      parkSize: [],
      walkingDistance: [],
      amenities: []
    });
  };

  // Get active filter count
  const getActiveFilterCount = () => {
    return Object.values(filters).reduce((count, filterArray) => {
      return count + (filterArray ? filterArray.length : 0);
    }, 0);
  };

  // Check if any filters are active
  const hasActiveFilters = () => {
    return getActiveFilterCount() > 0;
  };

  // Toggle filter sidebar
  const toggleFilterSidebar = () => {
    setIsFilterSidebarOpen(!isFilterSidebarOpen);
  };

  const value = {
    filters,
    setFilters,
    filterParks,
    filterParksByDistance,
    applyFilters,
    resetFilters,
    getActiveFilterCount,
    hasActiveFilters,
    isFilterSidebarOpen,
    setIsFilterSidebarOpen,
    toggleFilterSidebar
  };

  return (
    <FilterContext.Provider value={value}>
      {children}
    </FilterContext.Provider>
  );
};

export default FilterContext;