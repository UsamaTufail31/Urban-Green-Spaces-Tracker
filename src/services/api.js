// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// API error handling
class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Generic API request function
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: 'An error occurred' };
      }
      
      throw new ApiError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }
    
    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Network errors or other issues
    throw new ApiError(
      `Network error: ${error.message}`,
      0,
      { error: error.message }
    );
  }
}

// City search API (enhanced version with real-time data)
export async function searchCities(name, limit = 10, includeRealtime = true) {
  if (!name || name.trim().length < 1) {
    throw new ApiError('City name is required', 400, { detail: 'City name parameter is required' });
  }
  
  const params = new URLSearchParams({
    name: name.trim(),
    limit: limit.toString(),
    include_realtime: includeRealtime.toString()
  });
  
  return await apiRequest(`/city/search/enhanced?${params}`);
}

// City search API (original version without real-time data)
export async function searchCitiesBasic(name, limit = 10) {
  if (!name || name.trim().length < 1) {
    throw new ApiError('City name is required', 400, { detail: 'City name parameter is required' });
  }
  
  const params = new URLSearchParams({
    name: name.trim(),
    limit: limit.toString()
  });
  
  return await apiRequest(`/city/search?${params}`);
}

// Get all cities
export async function getAllCities() {
  return await apiRequest('/cities');
}

// Get city by ID
export async function getCityById(cityId) {
  return await apiRequest(`/cities/${cityId}`);
}

// Get nearest parks
export async function getNearestParks(latitude, longitude, radiusKm = 5.0, limit = 20) {
  const params = new URLSearchParams({
    latitude: latitude.toString(),
    longitude: longitude.toString(),
    radius_km: radiusKm.toString(),
    limit: limit.toString()
  });
  
  return await apiRequest(`/parks/nearest?${params}`);
}

// Get green coverage comparison
export async function getGreenCoverageComparison(cityId) {
  return await apiRequest(`/green-coverage/comparison/${cityId}`);
}

// Get green coverage comparison with WHO standards
export async function getGreenCoverageComparisonWithWHO(cityName) {
  if (!cityName || cityName.trim().length < 1) {
    throw new ApiError('City name is required', 400, { detail: 'City name parameter is required' });
  }
  
  const params = new URLSearchParams({
    city_name: cityName.trim()
  });
  
  return await apiRequest(`/coverage/compare?${params}`);
}

// Get green coverage trend data for a city
export async function getGreenCoverageTrend(cityName, startYear = null, endYear = null) {
  if (!cityName || cityName.trim().length < 1) {
    throw new ApiError('City name is required', 400, { detail: 'City name parameter is required' });
  }
  
  const params = new URLSearchParams({
    city_name: cityName.trim()
  });
  
  if (startYear) {
    params.append('start_year', startYear.toString());
  }
  
  if (endYear) {
    params.append('end_year', endYear.toString());
  }
  
  return await apiRequest(`/coverage/trend?${params}`);
}

// Feedback API
export async function submitFeedback(feedbackData) {
  return await apiRequest('/feedback', {
    method: 'POST',
    body: JSON.stringify(feedbackData)
  });
}

// Export API error class for error handling in components
export { ApiError };

// Health check function
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    return response.ok;
  } catch {
    return false;
  }
}

// External APIs health check
export async function externalApisHealthCheck() {
  try {
    return await apiRequest('/health/external-apis');
  } catch (error) {
    console.warn('External APIs health check failed:', error);
    return { status: 'error', message: 'Health check failed', apis: {} };
  }
}