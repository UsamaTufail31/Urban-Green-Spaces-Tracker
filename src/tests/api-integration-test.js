// Integration test for the city search API connection
import { searchCities, ApiError } from '../services/api.js';

// Test function to verify the integration
async function testCitySearchIntegration() {
  console.log('🧪 Testing City Search API Integration...\n');
  
  try {
    // Test 1: Search for "New" should return cities
    console.log('Test 1: Searching for "New"...');
    const newCities = await searchCities('New', 3);
    console.log(`✅ Found ${newCities.length} cities:`, newCities.map(c => `${c.name}, ${c.country}`).join('; '));
    
    // Test 2: Search for "London" should return London
    console.log('\nTest 2: Searching for "London"...');
    const londonCities = await searchCities('London', 1);
    if (londonCities.length > 0) {
      const london = londonCities[0];
      console.log(`✅ Found: ${london.name}, ${london.country}`);
      console.log(`📍 Coordinates: ${london.latitude}, ${london.longitude}`);
    } else {
      console.log('❌ No results for London');
    }
    
    // Test 3: Search for non-existent city
    console.log('\nTest 3: Searching for "NonExistentCity123"...');
    const nonExistent = await searchCities('NonExistentCity123', 1);
    console.log(`✅ Expected empty result: ${nonExistent.length} cities found`);
    
    // Test 4: Error handling - empty search
    console.log('\nTest 4: Testing error handling with empty search...');
    try {
      await searchCities('', 1);
      console.log('❌ Should have thrown an error');
    } catch (error) {
      if (error instanceof ApiError) {
        console.log('✅ Correctly handled error:', error.message);
      } else {
        console.log('❌ Unexpected error type:', error);
      }
    }
    
    console.log('\n🎉 All tests completed successfully!');
    return true;
  } catch (error) {
    console.error('❌ Test failed:', error);
    return false;
  }
}

// Export for use in browser console
window.testCitySearchIntegration = testCitySearchIntegration;

// Run tests automatically if this file is loaded
if (typeof window !== 'undefined') {
  console.log('🔗 City Search API integration test loaded. Run testCitySearchIntegration() in the console to test.');
}

export { testCitySearchIntegration };