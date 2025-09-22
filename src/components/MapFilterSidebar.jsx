import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Filter, X } from 'lucide-react';

const MapFilterSidebar = ({ isOpen, onClose, filters, onFiltersChange }) => {
  const [expandedSections, setExpandedSections] = useState({
    parkSize: true,
    walkingDistance: false,
    amenities: false
  });

  // Filter options
  const filterOptions = {
    parkSize: [
      { id: 'small', label: 'Small Parks', description: 'Under 50 acres' },
      { id: 'medium', label: 'Medium Parks', description: '50-200 acres' },
      { id: 'large', label: 'Large Parks', description: 'Over 200 acres' }
    ],
    walkingDistance: [
      { id: '1km', label: '1 km radius', description: 'Within walking distance' },
      { id: '3km', label: '3 km radius', description: 'Short bike ride' },
      { id: '5km', label: '5 km radius', description: 'Extended area' }
    ],
    amenities: [
      { id: 'playground', label: 'Playground', description: 'Child-friendly areas' },
      { id: 'jogging-track', label: 'Jogging Track', description: 'Dedicated running paths' },
      { id: 'lake', label: 'Lake/Water Feature', description: 'Scenic water views' },
      { id: 'sports-facilities', label: 'Sports Facilities', description: 'Courts and fields' },
      { id: 'picnic-areas', label: 'Picnic Areas', description: 'Family gathering spots' },
      { id: 'dog-park', label: 'Dog Park', description: 'Pet-friendly zones' }
    ]
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleFilterChange = (category, filterId, checked) => {
    const newFilters = { ...filters };
    if (!newFilters[category]) {
      newFilters[category] = [];
    }
    
    if (checked) {
      if (!newFilters[category].includes(filterId)) {
        newFilters[category] = [...newFilters[category], filterId];
      }
    } else {
      newFilters[category] = newFilters[category].filter(id => id !== filterId);
    }
    
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      parkSize: [],
      walkingDistance: [],
      amenities: []
    });
  };

  const getActiveFilterCount = () => {
    return Object.values(filters).reduce((count, filterArray) => {
      return count + (filterArray ? filterArray.length : 0);
    }, 0);
  };

  const AccordionSection = ({ title, category, icon, children }) => {
    const isExpanded = expandedSections[category];
    const activeCount = filters[category] ? filters[category].length : 0;
    
    return (
      <div className="border-b border-gray-100 last:border-b-0">
        <button
          onClick={() => toggleSection(category)}
          className="w-full px-4 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors duration-200"
        >
          <div className="flex items-center gap-3">
            <span className="text-nature-green-600 text-lg">{icon}</span>
            <div>
              <h3 className="font-semibold text-gray-800 text-sm md:text-base">
                {title}
              </h3>
              {activeCount > 0 && (
                <span className="text-xs text-nature-green-600 font-medium">
                  {activeCount} selected
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {activeCount > 0 && (
              <span className="bg-nature-green-100 text-nature-green-700 text-xs font-medium px-2 py-1 rounded-full">
                {activeCount}
              </span>
            )}
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </button>
        
        <div className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <div className="px-4 pb-4 space-y-3">
            {children}
          </div>
        </div>
      </div>
    );
  };

  const CheckboxItem = ({ option, category, isChecked }) => (
    <label className="flex items-start gap-3 cursor-pointer group hover:bg-gray-50 p-2 rounded-lg transition-colors duration-150">
      <div className="relative mt-0.5">
        <input
          type="checkbox"
          checked={isChecked}
          onChange={(e) => handleFilterChange(category, option.id, e.target.checked)}
          className="w-4 h-4 text-nature-green-600 bg-gray-100 border-gray-300 rounded focus:ring-nature-green-500 focus:ring-2 transition-colors duration-150"
        />
        {isChecked && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        )}
      </div>
      <div className="flex-1">
        <span className="text-sm font-medium text-gray-700 group-hover:text-nature-green-700 transition-colors duration-150">
          {option.label}
        </span>
        <p className="text-xs text-gray-500 mt-0.5">
          {option.description}
        </p>
      </div>
    </label>
  );

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed top-0 right-0 h-full w-full max-w-sm bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out
        lg:relative lg:w-80 lg:shadow-lg lg:z-10
        ${isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-nature-green-600" />
            <h2 className="text-lg font-bold text-gray-800">Map Filters</h2>
          </div>
          <div className="flex items-center gap-2">
            {getActiveFilterCount() > 0 && (
              <button
                onClick={clearAllFilters}
                className="text-xs text-gray-500 hover:text-nature-green-600 font-medium transition-colors duration-150"
              >
                Clear All
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors duration-150 lg:hidden"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Active filters summary */}
        {getActiveFilterCount() > 0 && (
          <div className="p-4 bg-nature-green-50 border-b border-nature-green-100">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-nature-green-800">
                Active Filters ({getActiveFilterCount()})
              </span>
            </div>
            <div className="flex flex-wrap gap-1">
              {Object.entries(filters).map(([category, selectedFilters]) => 
                selectedFilters?.map(filterId => {
                  const option = filterOptions[category]?.find(opt => opt.id === filterId);
                  return option ? (
                    <span
                      key={`${category}-${filterId}`}
                      className="inline-flex items-center gap-1 bg-nature-green-200 text-nature-green-800 text-xs font-medium px-2 py-1 rounded-full"
                    >
                      {option.label}
                      <button
                        onClick={() => handleFilterChange(category, filterId, false)}
                        className="hover:bg-nature-green-300 rounded-full p-0.5 transition-colors duration-150"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ) : null;
                })
              )}
            </div>
          </div>
        )}

        {/* Filter sections */}
        <div className="flex-1 overflow-y-auto">
          {/* Park Size */}
          <AccordionSection 
            title="Park Size" 
            category="parkSize" 
            icon="📏"
          >
            {filterOptions.parkSize.map(option => (
              <CheckboxItem
                key={option.id}
                option={option}
                category="parkSize"
                isChecked={filters.parkSize?.includes(option.id) || false}
              />
            ))}
          </AccordionSection>

          {/* Walking Distance */}
          <AccordionSection 
            title="Walking Distance" 
            category="walkingDistance" 
            icon="🚶"
          >
            {filterOptions.walkingDistance.map(option => (
              <CheckboxItem
                key={option.id}
                option={option}
                category="walkingDistance"
                isChecked={filters.walkingDistance?.includes(option.id) || false}
              />
            ))}
          </AccordionSection>

          {/* Amenities */}
          <AccordionSection 
            title="Amenities" 
            category="amenities" 
            icon="🎯"
          >
            {filterOptions.amenities.map(option => (
              <CheckboxItem
                key={option.id}
                option={option}
                category="amenities"
                isChecked={filters.amenities?.includes(option.id) || false}
              />
            ))}
          </AccordionSection>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-500 text-center">
            Filters help you find the perfect green space for your needs
          </p>
        </div>
      </div>
    </>
  );
};

export default MapFilterSidebar;