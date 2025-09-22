import React, { useState, useEffect } from 'react';
import { getGreenCoverageComparisonWithWHO, ApiError } from '../services/api';

const DashboardCards = ({ selectedCity, greenCoverageData = null }) => {
  const [coverageData, setCoverageData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch coverage comparison data when selectedCity changes
  useEffect(() => {
    if (selectedCity?.name) {
      fetchCoverageData(selectedCity.name);
    } else {
      setCoverageData(null);
      setError(null);
    }
  }, [selectedCity]);

  const fetchCoverageData = async (cityName) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getGreenCoverageComparisonWithWHO(cityName);
      setCoverageData(data);
    } catch (err) {
      console.error('Error fetching coverage data:', err);
      setError(err instanceof ApiError ? err.message : 'Failed to fetch coverage data');
    } finally {
      setLoading(false);
    }
  };

  // Use real data from API or fallback to mock data
  const cityGreenCoverage = coverageData?.city_green_coverage_percentage ?? greenCoverageData?.percentage ?? 25;
  const whoStandard = coverageData?.who_recommendation_percentage ?? 30;
  const difference = cityGreenCoverage - whoStandard;
  const cityName = coverageData?.city_name || selectedCity?.name || 'This city';
  const dataYear = coverageData?.year;
  
  const comparison = coverageData?.comparison_result || 
    (cityGreenCoverage >= whoStandard 
      ? `${cityName} meets WHO standards!` 
      : `${cityName} has less than WHO standard`);

  const comparisonColor = difference >= 0 ? 'text-green-600' : 'text-amber-600';

  // Enhanced SVG Icons
  const TreeIcon = () => (
    <svg 
      className="w-8 h-8 text-green-500" 
      fill="currentColor" 
      viewBox="0 0 24 24"
    >
      <path d="M12 2L13.09 8.26L19 7L14.74 13L21 14.09L14.74 15.74L17 21L11.26 15.74L10 21L7.74 15.74L2 17L7.26 15.74L3 14.09L9.26 13L5 7L10.91 8.26L12 2Z"/>
      <rect x="11" y="15" width="2" height="6" rx="1"/>
    </svg>
  );

  const WHOIcon = () => (
    <svg 
      className="w-8 h-8 text-blue-500" 
      fill="currentColor" 
      viewBox="0 0 24 24"
    >
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
    </svg>
  );

  const ComparisonIcon = ({ difference }) => {
    if (loading) {
      return (
        <svg className="w-8 h-8 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
      );
    }
    
    if (difference >= 10) {
      return (
        <svg className="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      );
    } else if (difference >= 0) {
      return (
        <svg className="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
      );
    } else if (difference >= -5) {
      return (
        <svg className="w-8 h-8 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
      );
    } else {
      return (
        <svg className="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      );
    }
  };

  const StatusBadge = ({ difference }) => {
    if (difference >= 10) {
      return <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded-full">★ Excellent</span>;
    } else if (difference >= 0) {
      return <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded-full">✓ Good</span>;
    } else if (difference >= -5) {
      return <span className="px-2 py-1 text-xs font-semibold bg-amber-100 text-amber-800 rounded-full">⚠ Needs Improvement</span>;
    } else {
      return <span className="px-2 py-1 text-xs font-semibold bg-red-100 text-red-800 rounded-full">⚠ Critical</span>;
    }
  };

  const cards = [
    {
      title: 'City Green Coverage',
      value: loading ? 'Loading...' : `${cityGreenCoverage.toFixed(1)}%`,
      icon: <TreeIcon />,
      description: selectedCity?.name ? 
        (dataYear ? `${selectedCity.name} (${dataYear} data)` : `in ${selectedCity.name}`) : 
        'Select a city to see data',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-700',
      badge: null
    },
    {
      title: 'WHO Recommendation',
      value: `${whoStandard}%`,
      icon: <WHOIcon />,
      description: 'Minimum for healthy urban areas',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-700',
      badge: null
    },
    {
      title: 'Status Comparison',
      value: loading ? 'Calculating...' : 
        (error ? 'Error' : 
          (Math.abs(difference) < 0.1 ? 'Meets Standard' : 
            (difference > 0 ? `+${difference.toFixed(1)}%` : `${difference.toFixed(1)}%`))),
      icon: <ComparisonIcon difference={difference} />,
      description: loading ? 'Please wait...' : 
        (error ? error : 
          (Math.abs(difference) < 0.1 ? 'Right on target' : 
            `${Math.abs(difference).toFixed(1)}% ${difference >= 0 ? 'above' : 'below'} WHO standard`)),
      bgColor: loading ? 'bg-gray-50' : 
        (error ? 'bg-red-50' : 
          (difference >= 0 ? 'bg-green-50' : 
            (difference >= -5 ? 'bg-amber-50' : 'bg-red-50'))),
      borderColor: loading ? 'border-gray-200' : 
        (error ? 'border-red-200' : 
          (difference >= 0 ? 'border-green-200' : 
            (difference >= -5 ? 'border-amber-200' : 'border-red-200'))),
      textColor: loading ? 'text-gray-700' : 
        (error ? 'text-red-700' : 
          (difference >= 0 ? 'text-green-700' : 
            (difference >= -5 ? 'text-amber-700' : 'text-red-700'))),
      badge: loading || error ? null : <StatusBadge difference={difference} />
    }
  ];

  return (
    <div className="w-full bg-white/95 backdrop-blur-sm border-t border-gray-200 p-4 md:p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-6">
          <h3 className="text-xl md:text-2xl font-bold text-gray-800 mb-2">
            🌿 Green Space Analytics
          </h3>
          <p className="text-gray-600 text-sm md:text-base">
            Urban green coverage compared to WHO recommendations
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
          {cards.map((card, index) => (
            <div
              key={index}
              className={`${card.bgColor} ${card.borderColor} border-2 rounded-2xl p-6 transition-all duration-300 hover:shadow-lg hover:scale-105 cursor-pointer relative`}
            >
              {card.badge && (
                <div className="absolute top-4 right-4">
                  {card.badge}
                </div>
              )}
              
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {card.icon}
                  <h4 className={`font-semibold text-lg ${card.textColor}`}>
                    {card.title}
                  </h4>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className={`text-2xl md:text-3xl font-bold ${card.textColor}`}>
                  {card.value}
                </div>
                <p className="text-gray-600 text-sm">
                  {card.description}
                </p>
              </div>

              {/* Progress bar for percentage values */}
              {card.title !== 'Status Comparison' && !loading && !error && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        card.title.includes('Green Coverage') ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{
                        width: `${Math.min(100, card.title.includes('Green Coverage') ? cityGreenCoverage : whoStandard)}%`
                      }}
                    ></div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1 text-right">
                    {card.title.includes('Green Coverage') ? cityGreenCoverage.toFixed(1) : whoStandard}% of urban area
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Additional insights */}
        {selectedCity && (
          <div className="mt-6 space-y-4">
            {/* Detailed comparison result from API */}
            {coverageData?.comparison_result && !loading && (
              <div className="p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-xl border border-blue-200">
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    <ComparisonIcon difference={difference} />
                  </div>
                  <div>
                    <h5 className="font-semibold text-gray-800 mb-2">WHO Standards Analysis</h5>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      {coverageData.comparison_result}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* General insights */}
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">💡</span>
                <h5 className="font-semibold text-gray-800">Quick Insights</h5>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span>Parks and recreational areas contribute to mental well-being</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  <span>Green spaces help reduce urban heat island effects</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                  <span>Trees improve air quality by filtering pollutants</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                  <span>Urban forests support biodiversity and wildlife</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardCards;