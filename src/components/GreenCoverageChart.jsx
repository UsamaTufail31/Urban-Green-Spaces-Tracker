import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { getGreenCoverageTrend } from '../services/api';

const GreenCoverageChart = ({ selectedCity = null }) => {
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // WHO recommendation for urban green space coverage
  const WHO_RECOMMENDATION = 30; // 30% green coverage is WHO recommendation

  useEffect(() => {
    if (selectedCity && selectedCity.name) {
      fetchTrendData(selectedCity.name);
    }
  }, [selectedCity]);

  const fetchTrendData = async (cityName) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getGreenCoverageTrend(cityName);
      
      // Transform the data for Recharts
      const formattedData = data.map(item => ({
        year: item.year,
        coverage: parseFloat(item.coverage_percentage.toFixed(2)),
        green_area_km2: item.green_area_km2,
        total_area_km2: item.total_area_km2,
        data_source: item.data_source,
        measurement_method: item.measurement_method
      }));
      
      setTrendData(formattedData);
    } catch (err) {
      console.error('Error fetching trend data:', err);
      setError(err.message || 'Failed to fetch green coverage trend data');
      setTrendData([]);
    } finally {
      setLoading(false);
    }
  };

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg min-w-[200px]">
          <p className="font-semibold text-gray-800 mb-2">Year {label}</p>
          <div className="space-y-1">
            <p className="text-sm">
              <span className="text-gray-600">Green Coverage: </span>
              <span className="font-medium text-green-600">{data.coverage}%</span>
            </p>
            {data.green_area_km2 && (
              <p className="text-sm">
                <span className="text-gray-600">Green Area: </span>
                <span className="font-medium">{data.green_area_km2.toFixed(2)} km²</span>
              </p>
            )}
            {data.total_area_km2 && (
              <p className="text-sm">
                <span className="text-gray-600">Total Area: </span>
                <span className="font-medium">{data.total_area_km2.toFixed(2)} km²</span>
              </p>
            )}
            {data.data_source && (
              <p className="text-xs text-gray-500 mt-2 border-t pt-1">
                Source: {data.data_source}
              </p>
            )}
          </div>
          <div className="mt-2 pt-2 border-t">
            <span className={`text-xs px-2 py-1 rounded-full ${
              data.coverage >= WHO_RECOMMENDATION
                ? 'bg-green-100 text-green-800'
                : 'bg-orange-100 text-orange-800'
            }`}>
              {data.coverage >= WHO_RECOMMENDATION ? 'Meets WHO Standards' : 'Below WHO Standards'}
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  // Custom dot component
  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    const isAboveWHO = payload.coverage >= WHO_RECOMMENDATION;
    
    return (
      <circle
        cx={cx}
        cy={cy}
        r={4}
        fill={isAboveWHO ? '#10B981' : '#F59E0B'}
        stroke="#fff"
        strokeWidth={2}
        className="drop-shadow-sm"
      />
    );
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Green Coverage Trend
          </h3>
          <p className="text-sm text-gray-600">
            Historical green coverage data over time
          </p>
        </div>
        <div className="h-80 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
            <p className="text-gray-500 mt-2">Loading trend data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Green Coverage Trend
          </h3>
          <p className="text-sm text-gray-600">
            Historical green coverage data over time
          </p>
        </div>
        <div className="h-80 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 text-4xl mb-4">⚠️</div>
            <p className="text-gray-600 mb-2">Unable to load trend data</p>
            <p className="text-sm text-red-500">{error}</p>
            {selectedCity && (
              <button
                onClick={() => fetchTrendData(selectedCity.name)}
                className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Try Again
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!selectedCity) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Green Coverage Trend
          </h3>
          <p className="text-sm text-gray-600">
            Historical green coverage data over time
          </p>
        </div>
        <div className="h-80 flex items-center justify-center">
          <div className="text-center">
            <div className="text-gray-400 text-4xl mb-4">📈</div>
            <p className="text-gray-500">Select a city to view its green coverage trend</p>
          </div>
        </div>
      </div>
    );
  }

  if (trendData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Green Coverage Trend - {selectedCity.name}
          </h3>
          <p className="text-sm text-gray-600">
            Historical green coverage data over time
          </p>
        </div>
        <div className="h-80 flex items-center justify-center">
          <div className="text-center">
            <div className="text-gray-400 text-4xl mb-4">📊</div>
            <p className="text-gray-500">No historical data available for {selectedCity.name}</p>
            <p className="text-sm text-gray-400 mt-2">
              Historical coverage data may not be available for this city yet.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate trend direction
  const firstYear = trendData[0];
  const lastYear = trendData[trendData.length - 1];
  const coverageChange = lastYear.coverage - firstYear.coverage;
  const isPositiveTrend = coverageChange > 0;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-2">
          Green Coverage Trend - {selectedCity.name}
        </h3>
        <p className="text-sm text-gray-600">
          Historical green coverage data from {firstYear.year} to {lastYear.year}
        </p>
        
        {/* Trend Summary */}
        <div className="mt-3 flex items-center gap-4">
          <div className={`flex items-center gap-1 text-sm ${
            isPositiveTrend ? 'text-green-600' : 'text-red-600'
          }`}>
            <span>{isPositiveTrend ? '↗️' : '↘️'}</span>
            <span className="font-medium">
              {isPositiveTrend ? '+' : ''}{coverageChange.toFixed(1)}% 
            </span>
            <span className="text-gray-500">
              over {lastYear.year - firstYear.year} years
            </span>
          </div>
          <div className="text-sm text-gray-600">
            Current: <span className="font-medium">{lastYear.coverage}%</span>
          </div>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={trendData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 20,
            }}
          >
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="#f0f0f0"
              horizontal={true}
              vertical={false}
            />
            <XAxis
              dataKey="year"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#6B7280', fontSize: 12, fontWeight: 500 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#6B7280', fontSize: 12 }}
              label={{ 
                value: 'Green Coverage (%)', 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle', fill: '#6B7280', fontSize: '12px' }
              }}
              domain={[0, 'dataMax + 5']}
            />
            
            {/* WHO Recommendation Reference Line */}
            <ReferenceLine 
              y={WHO_RECOMMENDATION} 
              stroke="#DC2626" 
              strokeDasharray="5 5"
              label={{ value: "WHO Standard (30%)", position: "topRight", fill: "#DC2626", fontSize: 11 }}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <Line
              type="monotone"
              dataKey="coverage"
              stroke="#10B981"
              strokeWidth={3}
              dot={<CustomDot />}
              activeDot={{ 
                r: 6, 
                fill: '#10B981',
                stroke: '#fff',
                strokeWidth: 2
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-center space-x-6 text-sm">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-gray-600">Green Coverage</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-1 bg-red-600 rounded-full"></div>
          <span className="text-gray-600">WHO Standard</span>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Average</p>
            <p className="text-lg font-semibold text-gray-800">
              {(trendData.reduce((sum, item) => sum + item.coverage, 0) / trendData.length).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Highest</p>
            <p className="text-lg font-semibold text-green-600">
              {Math.max(...trendData.map(item => item.coverage)).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Lowest</p>
            <p className="text-lg font-semibold text-orange-600">
              {Math.min(...trendData.map(item => item.coverage)).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Data Points</p>
            <p className="text-lg font-semibold text-gray-800">
              {trendData.length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GreenCoverageChart;