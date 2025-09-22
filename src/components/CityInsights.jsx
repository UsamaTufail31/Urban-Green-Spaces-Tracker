import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine
} from 'recharts';
import { TrendingUp, Leaf, Calendar, Info, Cloud, Thermometer, Wind, Eye, Newspaper, Flag } from 'lucide-react';

const CityInsights = ({ cityName = "Your City", realTimeData = null }) => {
  const [animationComplete, setAnimationComplete] = useState(false);
  
  // Mock historical data - in a real app this would come from an API
  const historicalData = [
    { year: '2015', coverage: 8.2, population: 2.1 },
    { year: '2016', coverage: 8.8, population: 2.15 },
    { year: '2017', coverage: 9.1, population: 2.2 },
    { year: '2018', coverage: 10.3, population: 2.25 },
    { year: '2019', coverage: 11.2, population: 2.3 },
    { year: '2020', coverage: 12.1, population: 2.32 },
    { year: '2021', coverage: 13.5, population: 2.35 },
    { year: '2022', coverage: 14.2, population: 2.4 },
    { year: '2023', coverage: 15.1, population: 2.45 },
    { year: '2024', coverage: 16.3, population: 2.5 },
    { year: '2025', coverage: 17.2, population: 2.52 }
  ];

  const WHO_RECOMMENDATION = 15;
  const currentCoverage = historicalData[historicalData.length - 1].coverage;
  const growthRate = ((currentCoverage - historicalData[0].coverage) / historicalData[0].coverage * 100).toFixed(1);

  useEffect(() => {
    const timer = setTimeout(() => setAnimationComplete(true), 1500);
    return () => clearTimeout(timer);
  }, []);

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-xl shadow-lg">
          <p className="font-semibold text-gray-800 mb-2">{label}</p>
          <div className="space-y-1">
            <p className="text-sm flex items-center">
              <Leaf className="w-3 h-3 text-green-500 mr-2" />
              <span className="text-gray-600">Green Coverage: </span>
              <span className="font-medium text-green-600 ml-1">
                {payload[0].value}%
              </span>
            </p>
            <p className="text-sm">
              <span className="text-gray-600">Population: </span>
              <span className="font-medium text-gray-700">
                {data.population}M
              </span>
            </p>
            {data.coverage >= WHO_RECOMMENDATION && (
              <p className="text-xs text-green-500 mt-1 flex items-center">
                <span className="w-1 h-1 bg-green-500 rounded-full mr-1"></span>
                Meets WHO standards ✓
              </p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    const isAboveWHO = payload.coverage >= WHO_RECOMMENDATION;
    
    return (
      <circle
        cx={cx}
        cy={cy}
        r={4}
        fill={isAboveWHO ? "#10B981" : "#F59E0B"}
        stroke="white"
        strokeWidth={2}
        className="filter drop-shadow-sm"
      />
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto pt-20">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6">
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            {cityName} Green Coverage Insights
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Explore the historical development of urban green spaces in your city. 
            Track progress towards sustainable urban development goals and understand 
            the environmental impact of green coverage growth over time.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <Leaf className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-sm font-medium text-green-600 bg-green-50 px-3 py-1 rounded-full">
                Current
              </span>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-1">
              {currentCoverage}%
            </h3>
            <p className="text-gray-600 text-sm">Green Coverage (2025)</p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                Growth
              </span>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-1">
              +{growthRate}%
            </h3>
            <p className="text-gray-600 text-sm">Total Growth (2015-2025)</p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <Calendar className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-sm font-medium text-purple-600 bg-purple-50 px-3 py-1 rounded-full">
                Timeline
              </span>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-1">
              2021
            </h3>
            <p className="text-gray-600 text-sm">WHO Standard Achieved</p>
          </div>
        </div>

        {/* Main Chart Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 mb-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Historical Green Coverage Trends
              </h2>
              <p className="text-gray-600">
                Track the evolution of urban green spaces from 2015 to 2025
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">Green Coverage</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 border-2 border-dashed border-gray-400 rounded-full"></div>
                <span className="text-sm text-gray-600">WHO Target (15%)</span>
              </div>
            </div>
          </div>

          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={historicalData}
                margin={{
                  top: 20,
                  right: 30,
                  left: 20,
                  bottom: 20,
                }}
              >
                <defs>
                  <linearGradient id="coverageGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#f0f0f0"
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
                  domain={[0, 20]}
                />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine 
                  y={WHO_RECOMMENDATION} 
                  stroke="#6B7280" 
                  strokeDasharray="5 5"
                  label={{ value: "WHO Recommendation", position: "topRight" }}
                />
                <Area
                  type="monotone"
                  dataKey="coverage"
                  stroke="#10B981"
                  strokeWidth={3}
                  fill="url(#coverageGradient)"
                  dot={<CustomDot />}
                  activeDot={{ r: 6, fill: "#10B981", strokeWidth: 2, stroke: "#fff" }}
                  animationDuration={2000}
                  animationEasing="ease-in-out"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Insights Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Info className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Key Achievement
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Your city successfully exceeded WHO recommendations in 2021, 
                  demonstrating commitment to sustainable urban development and 
                  improved quality of life for residents.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Growth Pattern
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Consistent upward trend with accelerated growth since 2018, 
                  indicating effective urban planning policies and increased 
                  investment in green infrastructure projects.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Data Section */}
        {realTimeData && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <Cloud className="w-4 h-4 text-blue-600" />
              </div>
              Live City Data
              <span className="ml-3 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                Updated Now
              </span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              
              {/* Weather Information */}
              {realTimeData.weather && (
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-lg p-6 border border-blue-100">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Thermometer className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">Current Weather</h3>
                        <p className="text-sm text-gray-500">Live conditions</p>
                      </div>
                    </div>
                    {realTimeData.weather.icon && (
                      <img
                        src={`https://openweathermap.org/img/wn/${realTimeData.weather.icon}@2x.png`}
                        alt={realTimeData.weather.description}
                        className="w-12 h-12"
                      />
                    )}
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-2xl font-bold text-gray-800">
                        {Math.round(realTimeData.weather.temperature)}°C
                      </span>
                      <span className="text-sm text-gray-600">
                        Feels like {Math.round(realTimeData.weather.feels_like)}°C
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-700 capitalize">
                      {realTimeData.weather.description}
                    </p>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center space-x-1">
                        <Wind className="w-3 h-3 text-gray-500" />
                        <span>{realTimeData.weather.wind_speed} m/s</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Eye className="w-3 h-3 text-gray-500" />
                        <span>{(realTimeData.weather.visibility / 1000).toFixed(1)} km</span>
                      </div>
                      <div className="text-gray-600">
                        Humidity: {realTimeData.weather.humidity}%
                      </div>
                      <div className="text-gray-600">
                        Pressure: {realTimeData.weather.pressure} hPa
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Country Information */}
              {realTimeData.country_info && (
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-lg p-6 border border-green-100">
                  <div className="flex items-start space-x-3 mb-4">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <Flag className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-800">Country Info</h3>
                      <p className="text-sm text-gray-500">Regional data</p>
                    </div>
                    {realTimeData.country_info.flag_url && (
                      <img
                        src={realTimeData.country_info.flag_url}
                        alt={`${realTimeData.country_info.name} flag`}
                        className="w-8 h-6 rounded border border-gray-200"
                      />
                    )}
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Capital:</span>
                      <span className="ml-2 text-gray-600">{realTimeData.country_info.capital}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Region:</span>
                      <span className="ml-2 text-gray-600">{realTimeData.country_info.region}</span>
                    </div>
                    {realTimeData.country_info.population && (
                      <div>
                        <span className="font-medium text-gray-700">Population:</span>
                        <span className="ml-2 text-gray-600">
                          {realTimeData.country_info.population.toLocaleString()}
                        </span>
                      </div>
                    )}
                    {realTimeData.country_info.languages && realTimeData.country_info.languages.length > 0 && (
                      <div>
                        <span className="font-medium text-gray-700">Languages:</span>
                        <span className="ml-2 text-gray-600">
                          {realTimeData.country_info.languages.slice(0, 2).join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Recent News */}
              {realTimeData.recent_news && realTimeData.recent_news.length > 0 && (
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl shadow-lg p-6 border border-purple-100">
                  <div className="flex items-start space-x-3 mb-4">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Newspaper className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">Recent News</h3>
                      <p className="text-sm text-gray-500">Latest updates</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {realTimeData.recent_news.slice(0, 2).map((article, index) => (
                      <div key={index} className="border-l-2 border-purple-200 pl-3">
                        <h4 className="text-sm font-medium text-gray-800 line-clamp-2 leading-tight">
                          {article.title}
                        </h4>
                        <p className="text-xs text-gray-600 mt-1">
                          {article.source} • {new Date(article.published_at).toLocaleDateString()}
                        </p>
                        {article.url && (
                          <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-purple-600 hover:text-purple-800 mt-1 inline-block"
                          >
                            Read more →
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Data Sources */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-2">Data Sources:</p>
              <div className="flex flex-wrap gap-2">
                {realTimeData.data_sources?.weather && (
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    Weather: {realTimeData.data_sources.weather}
                  </span>
                )}
                {realTimeData.data_sources?.country && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                    Country: {realTimeData.data_sources.country}
                  </span>
                )}
                {realTimeData.data_sources?.news && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                    News: {realTimeData.data_sources.news}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CityInsights;