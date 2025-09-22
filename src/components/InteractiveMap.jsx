import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useFilters } from '../contexts/FilterContext';
import { getNearestParks } from '../services/api';
import MapFilterSidebar from './MapFilterSidebar';
import FilterButton from './FilterButton';

// Import icons from lucide-react as SVG strings
const createTreeIcon = () => {
  const svgString = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 22v-7" stroke="#16a34a" stroke-width="2" stroke-linecap="round"/>
      <path d="M17 8c0-5-5-5-5-5s-5 0-5 5c0 2 2 4 5 4s5-2 5-4z" fill="#22c55e" stroke="#16a34a" stroke-width="1.5"/>
      <path d="M16 12c0-3-4-3-4-3s-4 0-4 3c0 1.5 1.5 3 4 3s4-1.5 4-3z" fill="#22c55e" stroke="#16a34a" stroke-width="1.5"/>
    </svg>
  `;
  
  return new L.DivIcon({
    html: `<div style="
      background: white;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      border: 2px solid #22c55e;
    ">${svgString}</div>`,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
    className: 'custom-tree-marker'
  });
};

// Component to handle map view changes when city is selected
const MapViewController = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  
  return null;
};

// Component to handle adding markers to the map
const ParkMarkers = ({ parks, onParksFiltered }) => {
  const [filteredParks, setFilteredParks] = useState([]);
  const { applyFilters } = useFilters();
  
  useEffect(() => {
    if (parks && parks.length > 0) {
      // Apply filter context filters to parks from API
      const finalFilteredParks = applyFilters(parks);
      setFilteredParks(finalFilteredParks);
      
      // Notify parent component
      if (onParksFiltered) {
        onParksFiltered(finalFilteredParks);
      }
    } else {
      setFilteredParks([]);
      if (onParksFiltered) {
        onParksFiltered([]);
      }
    }
  }, [parks, applyFilters, onParksFiltered]);
  
  const treeIcon = createTreeIcon();
  
  return (
    <>
      {filteredParks.map((park, index) => (
        <Marker
          key={`park-${park.id || index}`}
          position={[park.latitude || park.coordinates?.[0], park.longitude || park.coordinates?.[1]]}
          icon={treeIcon}
        >
          <Popup>
            <div className="p-2 max-w-xs">
              <h3 className="font-semibold text-nature-green-700 text-lg mb-2">
                {park.name}
              </h3>
              {park.amenities && (
                <p className="text-gray-600 text-sm mb-2">
                  {park.amenities}
                </p>
              )}
              <div className="space-y-1 text-xs text-gray-500">
                {park.area_hectares && (
                  <p><strong>Area:</strong> {park.area_hectares} hectares</p>
                )}
                {park.distance_km && (
                  <p><strong>Distance:</strong> {park.distance_km.toFixed(2)} km away</p>
                )}
                {park.latitude && park.longitude && (
                  <p><strong>Location:</strong> {park.latitude.toFixed(4)}, {park.longitude.toFixed(4)}</p>
                )}
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

const InteractiveMap = ({ selectedCity, onMarkerHover, onParksUpdate }) => {
  const [parks, setParks] = useState([]);
  const [filteredParks, setFilteredParks] = useState([]);
  const [mapCenter, setMapCenter] = useState([40.7128, -74.0060]); // Default to NYC
  const [mapZoom, setMapZoom] = useState(10);
  const [isLoadingParks, setIsLoadingParks] = useState(false);
  const [parksError, setParksError] = useState(null);
  const mapRef = useRef(null);
  const { 
    filters, 
    setFilters, 
    isFilterSidebarOpen, 
    setIsFilterSidebarOpen,
    getActiveFilterCount 
  } = useFilters();

  // Fetch parks from API when a city is selected
  const fetchNearestParks = async (latitude, longitude) => {
    try {
      setIsLoadingParks(true);
      setParksError(null);
      
      const parksData = await getNearestParks(latitude, longitude, 10.0, 50); // 10km radius, max 50 parks
      
      // Transform API response to match expected format
      const transformedParks = parksData.map(park => ({
        id: park.id,
        name: park.name,
        latitude: park.latitude,
        longitude: park.longitude,
        coordinates: [park.latitude, park.longitude], // For backward compatibility
        amenities: park.amenities,
        area_hectares: park.area_hectares,
        distance_km: park.distance_km,
        type: 'Park', // Default type
        description: park.amenities || 'Urban park or green space'
      }));
      
      setParks(transformedParks);
    } catch (error) {
      console.error('Error fetching parks:', error);
      setParksError(error.message || 'Failed to load parks');
      setParks([]);
    } finally {
      setIsLoadingParks(false);
    }
  };

  useEffect(() => {
    if (selectedCity) {
      // Use coordinates from the city data if available (from API)
      if (selectedCity.latitude && selectedCity.longitude) {
        const coordinates = [selectedCity.latitude, selectedCity.longitude];
        setMapCenter(coordinates);
        setMapZoom(12);
        
        // Fetch parks near this city
        fetchNearestParks(selectedCity.latitude, selectedCity.longitude);
      }
    } else {
      // Clear parks when no city is selected
      setParks([]);
      setParksError(null);
    }
  }, [selectedCity]);

  // Handle filtered parks updates
  const handleParksFiltered = (filtered) => {
    setFilteredParks(filtered);
    if (onParksUpdate) {
      // Pass coordinates for the results list
      const userLocation = selectedCity ? [selectedCity.latitude, selectedCity.longitude] : null;
      onParksUpdate(filtered, userLocation);
    }
  };

  return (
    <div className="w-full h-screen relative flex">
      {/* Filter Sidebar */}
      <MapFilterSidebar
        isOpen={isFilterSidebarOpen}
        onClose={() => setIsFilterSidebarOpen(false)}
        filters={filters}
        onFiltersChange={setFilters}
      />
      
      {/* Map Container */}
      <div className="flex-1 relative">
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ height: '100%', width: '100%' }}
          className="z-0"
          ref={mapRef}
        >
          {/* Mapbox tile layer - using OpenStreetMap as default, replace with your Mapbox token */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            // For Mapbox, use this URL instead (requires API key):
            // url={`https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=YOUR_MAPBOX_TOKEN`}
          />
          
          {/* Map view controller */}
          <MapViewController center={mapCenter} zoom={mapZoom} />
          
          {/* Park markers */}
          <ParkMarkers 
            parks={parks} 
            onParksFiltered={handleParksFiltered}
          />
        </MapContainer>
        
        {/* Filter Button - Mobile */}
        <FilterButton className="absolute top-4 left-4 z-10 lg:hidden" />
        
        {/* Map overlay with city info */}
        {selectedCity && (
          <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-3 md:p-4 z-10 max-w-xs md:max-w-sm">
            <h3 className="font-semibold text-nature-green-700 text-base md:text-lg mb-2">
              📍 {selectedCity.name}
            </h3>
            <p className="text-gray-600 text-xs md:text-sm mb-2">
              {selectedCity.state && `${selectedCity.state}, `}{selectedCity.country}
            </p>
            <div className="flex items-center gap-2 text-xs md:text-sm text-nature-green-600">
              <span>🌳</span>
              {isLoadingParks ? (
                <span>Loading parks...</span>
              ) : parksError ? (
                <span className="text-red-500">Error loading parks</span>
              ) : (
                <span>Showing {parks.length} nearby parks</span>
              )}
            </div>
            {getActiveFilterCount() > 0 && (
              <div className="mt-2 text-xs text-nature-green-600 font-medium">
                {getActiveFilterCount()} filter{getActiveFilterCount() > 1 ? 's' : ''} active
              </div>
            )}
          </div>
        )}
        
        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-3 md:p-4 z-10">
          <h4 className="font-semibold text-gray-700 text-xs md:text-sm mb-2">Legend</h4>
          <div className="flex items-center gap-2 text-xs md:text-sm text-gray-600">
            <div className="w-5 h-5 md:w-6 md:h-6 bg-nature-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">🌳</span>
            </div>
            <span>Parks & Green Areas</span>
          </div>
          {getActiveFilterCount() > 0 && (
            <div className="mt-2 text-xs text-nature-green-600">
              Filtered results shown
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InteractiveMap;