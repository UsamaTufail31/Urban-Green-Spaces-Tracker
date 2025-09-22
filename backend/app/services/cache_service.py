import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.cache import CoverageCache


class CacheService:
    """Service for managing coverage calculation caching with expiration."""
    
    DEFAULT_EXPIRATION_HOURS = 24  # Default cache expiration: 24 hours
    SATELLITE_EXPIRATION_HOURS = 72  # Satellite calculations are more expensive, cache longer
    STATS_EXPIRATION_HOURS = 12  # Stats calculations cache for shorter time
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def _generate_cache_key(self, **params) -> str:
        """Generate a cache key from parameters."""
        # Sort parameters for consistent hashing
        sorted_params = sorted(params.items())
        param_string = json.dumps(sorted_params, sort_keys=True)
        return hashlib.sha256(param_string.encode()).hexdigest()
    
    def _cleanup_expired_cache(self, city_name: Optional[str] = None):
        """Remove expired cache entries."""
        now = datetime.now(timezone.utc)
        query = self.db.query(CoverageCache).filter(CoverageCache.expires_at < now)
        
        if city_name:
            query = query.filter(CoverageCache.city_name == city_name)
        
        expired_count = query.count()
        if expired_count > 0:
            query.delete(synchronize_session=False)
            self.db.commit()
            print(f"Cleaned up {expired_count} expired cache entries")
    
    def get_cached_result(self, cache_key: str, calculation_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if it exists and hasn't expired."""
        now = datetime.now(timezone.utc)
        
        cache_entry = self.db.query(CoverageCache).filter(
            and_(
                CoverageCache.cache_key == cache_key,
                CoverageCache.calculation_type == calculation_type,
                CoverageCache.expires_at > now
            )
        ).first()
        
        if cache_entry:
            try:
                return json.loads(cache_entry.cached_data)
            except json.JSONDecodeError:
                # If cached data is corrupted, remove the entry
                self.db.delete(cache_entry)
                self.db.commit()
                return None
        
        return None
    
    def cache_result(self, 
                    cache_key: str, 
                    calculation_type: str,
                    city_name: str,
                    data: Dict[str, Any],
                    city_id: Optional[int] = None,
                    expiration_hours: Optional[int] = None) -> None:
        """Store calculation result in cache."""
        if expiration_hours is None:
            if calculation_type == 'satellite':
                expiration_hours = self.SATELLITE_EXPIRATION_HOURS
            elif calculation_type == 'stats':
                expiration_hours = self.STATS_EXPIRATION_HOURS
            else:
                expiration_hours = self.DEFAULT_EXPIRATION_HOURS
        
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expiration_hours)
        
        # Check if cache entry already exists
        existing_entry = self.db.query(CoverageCache).filter(
            and_(
                CoverageCache.cache_key == cache_key,
                CoverageCache.calculation_type == calculation_type
            )
        ).first()
        
        if existing_entry:
            # Update existing entry
            existing_entry.cached_data = json.dumps(data)
            existing_entry.expires_at = expires_at
            existing_entry.city_name = city_name
            existing_entry.city_id = city_id
        else:
            # Create new cache entry
            cache_entry = CoverageCache(
                city_id=city_id,
                city_name=city_name,
                cache_key=cache_key,
                cached_data=json.dumps(data),
                expires_at=expires_at,
                calculation_type=calculation_type
            )
            self.db.add(cache_entry)
        
        self.db.commit()
    
    def get_or_calculate_satellite_coverage(self,
                                          city_name: str,
                                          ndvi_threshold: float,
                                          name_column: str,
                                          red_band_idx: int,
                                          nir_band_idx: int,
                                          year: int,
                                          shapefile_path: str,
                                          raster_path: str,
                                          calculation_func) -> Dict[str, Any]:
        """Get satellite coverage from cache or calculate if not cached."""
        # Generate cache key from calculation parameters
        cache_params = {
            'city_name': city_name,
            'ndvi_threshold': ndvi_threshold,
            'name_column': name_column,
            'red_band_idx': red_band_idx,
            'nir_band_idx': nir_band_idx,
            'year': year,
            'shapefile_hash': self._get_file_hash(shapefile_path),
            'raster_hash': self._get_file_hash(raster_path)
        }
        
        cache_key = self._generate_cache_key(**cache_params)
        
        # Try to get from cache first
        cached_result = self.get_cached_result(cache_key, 'satellite')
        if cached_result:
            print(f"Retrieved satellite coverage for {city_name} from cache")
            return cached_result
        
        # Calculate if not in cache
        print(f"Calculating satellite coverage for {city_name} (not in cache)")
        result = calculation_func(
            shapefile_path=shapefile_path,
            raster_path=raster_path,
            city_name=city_name,
            ndvi_threshold=ndvi_threshold,
            name_column=name_column,
            red_band_idx=red_band_idx,
            nir_band_idx=nir_band_idx
        )
        
        # Cache the result
        self.cache_result(cache_key, 'satellite', city_name, result)
        
        # Clean up expired entries for this city
        self._cleanup_expired_cache(city_name)
        
        return result
    
    def get_or_calculate_city_stats(self,
                                  city_id: int,
                                  city_name: str,
                                  calculation_func) -> Dict[str, Any]:
        """Get city stats from cache or calculate if not cached."""
        cache_params = {
            'city_id': city_id,
            'operation': 'city_stats'
        }
        
        cache_key = self._generate_cache_key(**cache_params)
        
        # Try to get from cache first
        cached_result = self.get_cached_result(cache_key, 'stats')
        if cached_result:
            print(f"Retrieved city stats for {city_name} from cache")
            return cached_result
        
        # Calculate if not in cache
        print(f"Calculating city stats for {city_name} (not in cache)")
        result = calculation_func()
        
        # Cache the result
        self.cache_result(cache_key, 'stats', city_name, result, city_id)
        
        return result
    
    def get_or_calculate_coverage_comparison(self,
                                           city_name: str,
                                           calculation_func) -> Dict[str, Any]:
        """Get coverage comparison from cache or calculate if not cached."""
        cache_params = {
            'city_name': city_name,
            'operation': 'coverage_comparison'
        }
        
        cache_key = self._generate_cache_key(**cache_params)
        
        # Try to get from cache first
        cached_result = self.get_cached_result(cache_key, 'stats')
        if cached_result:
            print(f"Retrieved coverage comparison for {city_name} from cache")
            return cached_result
        
        # Calculate if not in cache
        print(f"Calculating coverage comparison for {city_name} (not in cache)")
        result = calculation_func()
        
        # Cache the result
        self.cache_result(cache_key, 'stats', city_name, result)
        
        return result
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash of file contents for cache key."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception:
            # If file doesn't exist or can't be read, use path as fallback
            return hashlib.md5(file_path.encode()).hexdigest()
    
    def invalidate_city_cache(self, city_name: str, calculation_type: Optional[str] = None):
        """Invalidate all cache entries for a specific city."""
        query = self.db.query(CoverageCache).filter(CoverageCache.city_name == city_name)
        
        if calculation_type:
            query = query.filter(CoverageCache.calculation_type == calculation_type)
        
        deleted_count = query.count()
        query.delete(synchronize_session=False)
        self.db.commit()
        
        print(f"Invalidated {deleted_count} cache entries for {city_name}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        now = datetime.now(timezone.utc)
        
        total_entries = self.db.query(CoverageCache).count()
        expired_entries = self.db.query(CoverageCache).filter(CoverageCache.expires_at < now).count()
        valid_entries = total_entries - expired_entries
        
        # Count by calculation type
        type_counts = {}
        for calc_type in ['satellite', 'stats', 'stored']:
            count = self.db.query(CoverageCache).filter(
                and_(
                    CoverageCache.calculation_type == calc_type,
                    CoverageCache.expires_at > now
                )
            ).count()
            type_counts[calc_type] = count
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'type_counts': type_counts
        }
    
    def cleanup_all_expired(self) -> int:
        """Clean up all expired cache entries and return count of deleted entries."""
        now = datetime.now(timezone.utc)
        
        expired_count = self.db.query(CoverageCache).filter(CoverageCache.expires_at < now).count()
        self.db.query(CoverageCache).filter(CoverageCache.expires_at < now).delete(synchronize_session=False)
        self.db.commit()
        
        return expired_count
    
    def invalidate_all_coverage_cache(self):
        """Invalidate all coverage-related cache entries."""
        query = self.db.query(CoverageCache).filter(
            or_(
                CoverageCache.calculation_type == 'satellite',
                CoverageCache.calculation_type == 'stats'
            )
        )
        
        deleted_count = query.count()
        query.delete(synchronize_session=False)
        self.db.commit()
        
        print(f"Invalidated {deleted_count} coverage cache entries")
        return deleted_count
    
    def get_cached_cities(self) -> List[str]:
        """Get list of cities that have cached data."""
        cities = self.db.query(CoverageCache.city_name).distinct().all()
        return [city[0] for city in cities if city[0]]