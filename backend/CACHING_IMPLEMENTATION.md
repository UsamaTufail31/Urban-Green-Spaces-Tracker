# Coverage Calculation Caching Implementation

## Overview

This implementation adds intelligent caching for coverage calculations to improve performance for repeated queries. The caching system uses a SQLite cache table with automatic expiration to ensure data freshness while providing significant performance improvements.

## Features Implemented

### 1. Cache Table Model (`app/models/cache.py`)
- **Table**: `coverage_cache`
- **Fields**:
  - `id`: Primary key
  - `city_id`: Reference to city (nullable for shapefile-based calculations)
  - `city_name`: City name for easy querying
  - `cache_key`: SHA-256 hash of calculation parameters
  - `cached_data`: JSON-serialized calculation results
  - `created_at`: Cache entry creation timestamp
  - `expires_at`: Cache entry expiration timestamp
  - `calculation_type`: Type of calculation (`satellite`, `stats`, `stored`)

- **Indexes**: Optimized for fast lookups by cache key, city name, and expiration time

### 2. Cache Service (`app/services/cache_service.py`)
- **Intelligent Key Generation**: Creates unique cache keys based on calculation parameters
- **Automatic Expiration**: Different expiration times for different calculation types:
  - Satellite calculations: 72 hours (expensive operations)
  - Stats calculations: 12 hours (moderate cost)
  - Default: 24 hours
- **Cache-or-Calculate Pattern**: Seamlessly integrates with existing calculation functions
- **Cleanup Management**: Automatic removal of expired entries

### 3. Integration Points

#### Shapefile Router (`app/routers/shapefile.py`)
- **Endpoint**: `POST /shapefile/calculate-green-coverage`
- **Caching Strategy**: Cache results based on:
  - City name
  - NDVI threshold
  - Band indices
  - Year
  - File hashes (shapefile and raster)

#### Main API Endpoints (`app/main.py`)
- **Endpoint**: `GET /cities/{city_id}/stats`
- **Caching Strategy**: Cache comprehensive city statistics

- **Endpoint**: `GET /coverage/compare`
- **Caching Strategy**: Cache WHO comparison results

### 4. Cache Management Endpoints

#### Cache Statistics
- **Endpoint**: `GET /cache/stats`
- **Purpose**: Monitor cache performance and usage
- **Returns**: Total entries, valid entries, expired entries, type breakdown

#### Cache Cleanup
- **Endpoint**: `POST /cache/cleanup`
- **Purpose**: Manually trigger cleanup of expired entries
- **Returns**: Number of deleted entries

#### City Cache Invalidation
- **Endpoint**: `DELETE /cache/city/{city_name}`
- **Purpose**: Invalidate all cache entries for a specific city
- **Optional**: Filter by calculation type

## Performance Benefits

### Expected Improvements
1. **Satellite Coverage Calculations**: 50-90% faster for repeated queries
2. **City Statistics**: 30-60% faster for repeated queries
3. **Coverage Comparisons**: 40-70% faster for repeated queries

### Cache Hit Scenarios
- Same city queried multiple times
- Identical calculation parameters
- Recently calculated results (within expiration window)

## Technical Implementation Details

### Cache Key Generation
```python
def _generate_cache_key(self, **params) -> str:
    sorted_params = sorted(params.items())
    param_string = json.dumps(sorted_params, sort_keys=True)
    return hashlib.sha256(param_string.encode()).hexdigest()
```

### File Hash Integration
For shapefile calculations, file contents are hashed to ensure cache invalidation when input files change:
```python
def _get_file_hash(self, file_path: str) -> str:
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5()
        for chunk in iter(lambda: f.read(4096), b""):
            file_hash.update(chunk)
        return file_hash.hexdigest()
```

### Automatic Cleanup
The system automatically cleans up expired entries during cache operations to maintain database size.

## Database Migration

### Migration Script: `migrate_database.py`
- Creates the `coverage_cache` table
- Adds necessary indexes for performance
- Verifies migration success
- Backwards compatible with existing data

### Running Migration
```bash
python migrate_database.py
```

## Testing

### Direct Cache Testing: `test_cache_direct.py`
- Tests cache service functionality
- Verifies data storage and retrieval
- Confirms statistics tracking
- Validates cleanup operations

### API Integration Testing: `test_cache_functionality.py`
- Tests caching through API endpoints
- Measures performance improvements
- Verifies cache statistics endpoints

## Configuration

### Expiration Times
- **Satellite calculations**: 72 hours (configurable via `SATELLITE_EXPIRATION_HOURS`)
- **Stats calculations**: 12 hours (configurable via `STATS_EXPIRATION_HOURS`)
- **Default**: 24 hours (configurable via `DEFAULT_EXPIRATION_HOURS`)

### Customization
All expiration times can be overridden when calling cache methods:
```python
cache_service.cache_result(
    cache_key=key,
    calculation_type="custom",
    city_name="City",
    data=results,
    expiration_hours=48  # Custom expiration
)
```

## Usage Examples

### Satellite Coverage with Caching
```python
# Automatic caching in shapefile router
coverage_stats = cache_service.get_or_calculate_satellite_coverage(
    city_name="New York",
    ndvi_threshold=0.3,
    # ... other parameters
    calculation_func=calculate_coverage
)
```

### City Stats with Caching
```python
# Automatic caching in main API
stats = cache_service.get_or_calculate_city_stats(
    city_id=1,
    city_name="New York",
    calculation_func=calculate_stats
)
```

### Manual Cache Management
```python
# Get cache statistics
stats = cache_service.get_cache_stats()

# Clean expired entries
deleted_count = cache_service.cleanup_all_expired()

# Invalidate specific city cache
cache_service.invalidate_city_cache("New York", "satellite")
```

## Monitoring and Maintenance

### Cache Statistics Monitoring
Regular monitoring of cache performance through `/cache/stats` endpoint helps:
- Identify cache hit rates
- Monitor storage usage
- Track expiration patterns
- Optimize expiration times

### Maintenance Tasks
1. **Regular Cleanup**: Use `/cache/cleanup` endpoint periodically
2. **Cache Invalidation**: Invalidate city caches when data is updated
3. **Performance Monitoring**: Track response times to verify improvements

## Future Enhancements

### Potential Improvements
1. **Redis Integration**: For distributed caching across multiple servers
2. **Cache Warming**: Pre-populate cache for frequently requested cities
3. **Intelligent Prefetching**: Predict and cache likely future requests
4. **Cache Size Limits**: Implement LRU eviction for storage management
5. **Cache Analytics**: Detailed metrics on hit rates and performance gains

### Configuration Options
- Cache size limits
- Custom expiration policies
- Cache warming strategies
- Performance metrics collection

## Security Considerations

### Data Protection
- Cache keys are hashed to prevent parameter inference
- No sensitive data stored in cache keys
- Automatic expiration prevents stale data issues

### Access Control
- Cache management endpoints can be protected with authentication
- City-specific cache invalidation for data privacy

## Conclusion

The caching implementation provides significant performance improvements for coverage calculations while maintaining data accuracy through intelligent expiration and invalidation strategies. The system is designed to be transparent to existing API consumers while offering powerful cache management capabilities for administrators.

The implementation follows best practices for:
- **Performance**: Optimized database queries and indexing
- **Reliability**: Automatic cleanup and error handling
- **Maintainability**: Clear separation of concerns and modular design
- **Scalability**: Efficient storage and retrieval patterns