import React from 'react';
import { Filter } from 'lucide-react';
import { useFilters } from '../contexts/FilterContext';

const FilterButton = ({ className = '' }) => {
  const { toggleFilterSidebar, getActiveFilterCount } = useFilters();
  const activeCount = getActiveFilterCount();

  return (
    <button
      onClick={toggleFilterSidebar}
      className={`
        relative bg-white/90 backdrop-blur-sm border border-white/20 rounded-full p-3 shadow-lg 
        hover:bg-white hover:shadow-xl transition-all duration-200 group
        ${className}
      `}
      aria-label="Open map filters"
    >
      <Filter className="w-5 h-5 text-nature-green-600 group-hover:text-nature-green-700 transition-colors duration-150" />
      
      {/* Active filter count badge */}
      {activeCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-nature-green-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
          {activeCount}
        </span>
      )}
    </button>
  );
};

export default FilterButton;