"""
Background task service for scheduled operations.
Handles weekly updates of green coverage data from satellite shapefiles.
"""

import asyncio
import logging
import os
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import SessionLocal
from app.models import City, GreenCoverage
from app.services.shapefile_service import shapefile_service
from app.services.cache_service import CacheService
from app.config import settings
from app.logging_config import (
    get_task_logger, log_background_task_start, log_background_task_end,
    log_satellite_processing, log_performance
)

# Set up logging
logger = get_task_logger('background_service')


class BackgroundTaskService:
    """Service for managing background tasks and scheduled operations."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.is_running = False
        self.logger = get_task_logger('background_service')
        
        # Use configuration from settings
        self.config = settings.get_processing_settings()
        self.config.update({
            "satellite_data_dir": settings.satellite_data_dir,
            "shapefile_dir": settings.shapefile_dir,
            "temp_dir": settings.temp_dir,
            "cache_ttl_hours": settings.cache_ttl_hours,
        })
    
    async def start_scheduler(self):
        """Start the background task scheduler."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        if not settings.enable_background_tasks:
            self.logger.info("Background tasks are disabled in configuration")
            return
        
        self.scheduler = AsyncIOScheduler()
        
        # Get schedule settings
        schedule = settings.get_cron_schedule()
        
        # Add weekly green coverage update task
        self.scheduler.add_job(
            self.update_green_coverage_weekly,
            trigger=CronTrigger(
                day_of_week=schedule["day_of_week"],
                hour=schedule["hour"],
                minute=schedule["minute"]
            ),
            id="weekly_green_coverage_update",
            name="Weekly Green Coverage Update",
            max_instances=1,
            misfire_grace_time=3600  # Allow 1 hour grace period
        )
        
        # Add cache cleanup task
        cache_settings = settings.get_cache_settings()
        self.scheduler.add_job(
            self.cleanup_expired_cache,
            trigger=CronTrigger(hour=cache_settings["cleanup_hour"], minute=0),
            id="daily_cache_cleanup",
            name="Daily Cache Cleanup",
            max_instances=1
        )
        
        self.scheduler.start()
        self.is_running = True
        self.logger.info("Background task scheduler started")
        log_background_task_start("scheduler", {"schedule": schedule, "cache_settings": cache_settings})
    
    async def stop_scheduler(self):
        """Stop the background task scheduler."""
        if not self.is_running or not self.scheduler:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        self.logger.info("Background task scheduler stopped")
        log_background_task_end("scheduler", True, {"message": "Scheduler shutdown"})
    
    @log_performance
    async def update_green_coverage_weekly(self):
        """
        Main background task to update green coverage data from satellite shapefiles.
        This runs weekly and processes all cities that have satellite data available.
        """
        start_time = datetime.now()
        task_name = "weekly_green_coverage_update"
        
        log_background_task_start(task_name, {
            "scheduled_time": start_time.isoformat(),
            "config": self.config
        })
        
        db = SessionLocal()
        try:
            # Get current year for data
            current_year = start_time.year
            
            # Get all cities that need updates
            cities = await self._get_cities_for_update(db, current_year)
            self.logger.info(f"Found {len(cities)} cities to process")
            
            if not cities:
                self.logger.info("No cities require green coverage updates")
                log_background_task_end(task_name, True, {"processed": 0, "message": "No updates needed"})
                return
            
            # Process cities in batches
            batch_size = self.config["batch_size"]
            total_processed = 0
            total_errors = 0
            
            for i in range(0, len(cities), batch_size):
                batch = cities[i:i + batch_size]
                self.logger.info(f"Processing batch {i//batch_size + 1} with {len(batch)} cities")
                
                for city in batch:
                    try:
                        success = await self._process_city_green_coverage(db, city, current_year)
                        if success:
                            total_processed += 1
                        else:
                            total_errors += 1
                    except Exception as e:
                        self.logger.error(f"Error processing city {city.name}: {e}")
                        total_errors += 1
                
                # Small delay between batches to avoid overwhelming the system
                await asyncio.sleep(5)
            
            # Invalidate related cache
            cache_service = CacheService(db)
            cache_service.invalidate_all_coverage_cache()
            
            # Log summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            success = total_errors == 0
            log_background_task_end(task_name, success, {
                "total_processed": total_processed,
                "total_errors": total_errors,
                "duration_seconds": duration.total_seconds(),
                "cities_processed": [city.name for city in cities[:total_processed]]
            })
            
            self.logger.info(
                f"Weekly green coverage update completed. "
                f"Processed: {total_processed}, Errors: {total_errors}, "
                f"Duration: {duration.total_seconds():.1f}s"
            )
            
        except Exception as e:
            self.logger.error(f"Critical error in weekly green coverage update: {e}")
            log_background_task_end(task_name, False, {"error": str(e)})
        finally:
            db.close()
    
    async def _get_cities_for_update(self, db: Session, current_year: int) -> List[City]:
        """
        Get list of cities that need green coverage updates.
        
        Args:
            db: Database session
            current_year: Current year to check for data
            
        Returns:
            List of cities that need updates
        """
        # Get all cities
        all_cities = db.query(City).all()
        cities_to_update = []
        
        for city in all_cities:
            # Check if city has recent green coverage data
            recent_coverage = db.query(GreenCoverage).filter(
                and_(
                    GreenCoverage.city_id == city.id,
                    GreenCoverage.year == current_year
                )
            ).first()
            
            # Check if satellite data is available for this city
            has_satellite_data = await self._check_satellite_data_availability(city)
            
            if has_satellite_data and not recent_coverage:
                cities_to_update.append(city)
                self.logger.info(f"City {city.name} scheduled for green coverage update")
            elif has_satellite_data and recent_coverage:
                # Check if data is older than configured update interval
                update_threshold = datetime.now() - timedelta(days=7)
                if recent_coverage.updated_at and recent_coverage.updated_at < update_threshold:
                    cities_to_update.append(city)
                    self.logger.info(f"City {city.name} scheduled for green coverage refresh")
        
        return cities_to_update
    
    async def _check_satellite_data_availability(self, city: City) -> bool:
        """
        Check if satellite data is available for a city.
        
        Args:
            city: City object to check
            
        Returns:
            True if satellite data is available, False otherwise
        """
        try:
            satellite_dir = Path(self.config["satellite_data_dir"])
            shapefile_dir = Path(self.config["shapefile_dir"])
            
            # Look for city-specific satellite data
            city_patterns = [
                city.name.lower().replace(" ", "_"),
                city.name.lower().replace(" ", "-"),
                city.name.lower()
            ]
            
            for pattern in city_patterns:
                # Check for raster files
                raster_files = list(satellite_dir.glob(f"*{pattern}*.tif")) + \
                              list(satellite_dir.glob(f"*{pattern}*.tiff"))
                
                # Check for shapefile data
                shapefile_files = list(shapefile_dir.glob(f"*{pattern}*.shp")) + \
                                 list(shapefile_dir.glob(f"*{pattern}*.geojson"))
                
                if raster_files and shapefile_files:
                    self.logger.debug(f"Found satellite data for {city.name}")
                    return True
            
            # Check for general regional data that might cover this city
            general_files = list(satellite_dir.glob("*.tif")) + list(satellite_dir.glob("*.tiff"))
            general_shapefiles = list(shapefile_dir.glob("*.shp")) + list(shapefile_dir.glob("*.geojson"))
            
            if general_files and general_shapefiles:
                self.logger.debug(f"Found general satellite data that may cover {city.name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking satellite data availability for {city.name}: {e}")
            return False
    
    async def _process_city_green_coverage(self, db: Session, city: City, year: int) -> bool:
        """
        Process green coverage data for a specific city.
        
        Args:
            db: Database session
            city: City to process
            year: Year for the data
            
        Returns:
            True if successful, False otherwise
        """
        city_logger = get_task_logger(f'process_city_{city.name.replace(" ", "_").lower()}')
        city_logger.info(f"Processing green coverage for {city.name}")
        
        try:
            # Find satellite data files for this city
            raster_file, shapefile_file = await self._find_city_data_files(city)
            
            if not raster_file or not shapefile_file:
                city_logger.warning(f"Could not find complete satellite data for {city.name}")
                return False
            
            # Calculate green coverage using shapefile service
            coverage_stats = shapefile_service.calculate_green_coverage_from_files(
                shapefile_path=str(shapefile_file),
                raster_path=str(raster_file),
                city_name=city.name,
                ndvi_threshold=self.config["ndvi_threshold"]
            )
            
            # Log satellite processing
            log_satellite_processing(city.name, {
                "coverage_percentage": coverage_stats["green_coverage_percentage"],
                "total_area_km2": coverage_stats["total_area_km2"],
                "green_area_km2": coverage_stats["green_area_km2"],
                "ndvi_stats": {
                    "mean": coverage_stats["mean_ndvi"],
                    "min": coverage_stats["min_ndvi"],
                    "max": coverage_stats["max_ndvi"]
                }
            })
            
            # Create or update green coverage record
            existing_coverage = db.query(GreenCoverage).filter(
                and_(
                    GreenCoverage.city_id == city.id,
                    GreenCoverage.year == year
                )
            ).first()
            
            coverage_data = {
                "city_id": city.id,
                "city_name": city.name,
                "coverage_percentage": coverage_stats["green_coverage_percentage"],
                "year": year,
                "data_source": "Weekly Satellite Update",
                "measurement_method": coverage_stats["measurement_method"],
                "total_area_km2": coverage_stats["total_area_km2"],
                "green_area_km2": coverage_stats["green_area_km2"],
                "ndvi_threshold": coverage_stats["ndvi_threshold"],
                "mean_ndvi": coverage_stats["mean_ndvi"],
                "std_ndvi": coverage_stats["std_ndvi"],
                "min_ndvi": coverage_stats["min_ndvi"],
                "max_ndvi": coverage_stats["max_ndvi"],
                "coordinate_system": coverage_stats["coordinate_system"],
                "shapefile_path": coverage_stats["shapefile_path"],
                "raster_path": coverage_stats["raster_path"],
                "total_pixels": coverage_stats["total_pixels"],
                "green_pixels": coverage_stats["green_pixels"],
                "processing_metadata": json.dumps({
                    "processed_at": datetime.now().isoformat(),
                    "processing_method": "automated_weekly_update",
                    "ndvi_threshold": self.config["ndvi_threshold"],
                    "batch_processing": True
                })
            }
            
            if existing_coverage:
                # Update existing record
                for key, value in coverage_data.items():
                    if key not in ["city_id", "year"]:  # Don't update primary key fields
                        setattr(existing_coverage, key, value)
                db.commit()
                city_logger.info(f"Updated green coverage for {city.name}: {coverage_stats['green_coverage_percentage']:.2f}%")
            else:
                # Create new record
                new_coverage = GreenCoverage(**coverage_data)
                db.add(new_coverage)
                db.commit()
                city_logger.info(f"Created green coverage for {city.name}: {coverage_stats['green_coverage_percentage']:.2f}%")
            
            return True
            
        except Exception as e:
            city_logger.error(f"Error processing green coverage for {city.name}: {e}")
            db.rollback()
            return False
    
    async def _find_city_data_files(self, city: City) -> tuple[Optional[Path], Optional[Path]]:
        """
        Find the appropriate satellite data files for a city.
        
        Args:
            city: City to find data for
            
        Returns:
            Tuple of (raster_file, shapefile_file) or (None, None) if not found
        """
        satellite_dir = Path(self.config["satellite_data_dir"])
        shapefile_dir = Path(self.config["shapefile_dir"])
        
        city_patterns = [
            city.name.lower().replace(" ", "_"),
            city.name.lower().replace(" ", "-"),
            city.name.lower()
        ]
        
        raster_file = None
        shapefile_file = None
        
        # Look for city-specific files first
        for pattern in city_patterns:
            if not raster_file:
                raster_candidates = list(satellite_dir.glob(f"*{pattern}*.tif")) + \
                                  list(satellite_dir.glob(f"*{pattern}*.tiff"))
                if raster_candidates:
                    raster_file = raster_candidates[0]
            
            if not shapefile_file:
                shapefile_candidates = list(shapefile_dir.glob(f"*{pattern}*.shp")) + \
                                     list(shapefile_dir.glob(f"*{pattern}*.geojson"))
                if shapefile_candidates:
                    shapefile_file = shapefile_candidates[0]
        
        # If city-specific files not found, use general regional files
        if not raster_file:
            general_rasters = list(satellite_dir.glob("*.tif")) + list(satellite_dir.glob("*.tiff"))
            if general_rasters:
                raster_file = general_rasters[0]
        
        if not shapefile_file:
            general_shapefiles = list(shapefile_dir.glob("*.shp")) + list(shapefile_dir.glob("*.geojson"))
            if general_shapefiles:
                shapefile_file = general_shapefiles[0]
        
        return raster_file, shapefile_file
    
    async def cleanup_expired_cache(self):
        """Clean up expired cache entries."""
        task_name = "cache_cleanup"
        log_background_task_start(task_name)
        
        db = SessionLocal()
        try:
            cache_service = CacheService(db)
            deleted_count = cache_service.cleanup_all_expired()
            
            log_background_task_end(task_name, True, {"deleted_entries": deleted_count})
            self.logger.info(f"Cleaned up {deleted_count} expired cache entries")
        except Exception as e:
            log_background_task_end(task_name, False, {"error": str(e)})
            self.logger.error(f"Error during cache cleanup: {e}")
        finally:
            db.close()
    
    async def trigger_manual_update(self, city_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Manually trigger green coverage update for all cities or a specific city.
        
        Args:
            city_name: Optional city name to update specifically
            
        Returns:
            Dictionary with update results
        """
        start_time = datetime.now()
        task_name = f"manual_update_{city_name or 'all_cities'}"
        
        log_background_task_start(task_name, {
            "city_name": city_name,
            "triggered_at": start_time.isoformat()
        })
        
        db = SessionLocal()
        try:
            current_year = start_time.year
            
            if city_name:
                # Update specific city
                city = db.query(City).filter(City.name.ilike(city_name)).first()
                if not city:
                    return {"error": f"City '{city_name}' not found"}
                
                cities = [city]
            else:
                # Update all cities
                cities = await self._get_cities_for_update(db, current_year)
            
            total_processed = 0
            total_errors = 0
            results = []
            
            for city in cities:
                try:
                    success = await self._process_city_green_coverage(db, city, current_year)
                    if success:
                        total_processed += 1
                        results.append({"city": city.name, "status": "success"})
                    else:
                        total_errors += 1
                        results.append({"city": city.name, "status": "failed"})
                except Exception as e:
                    total_errors += 1
                    results.append({"city": city.name, "status": "error", "error": str(e)})
            
            # Invalidate cache
            cache_service = CacheService(db)
            if city_name:
                cache_service.invalidate_city_cache(city_name)
            else:
                cache_service.invalidate_all_coverage_cache()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            success = total_errors == 0
            result = {
                "message": "Manual update completed",
                "total_processed": total_processed,
                "total_errors": total_errors,
                "duration_seconds": duration.total_seconds(),
                "results": results
            }
            
            log_background_task_end(task_name, success, result)
            return result
            
        except Exception as e:
            error_result = {"error": str(e)}
            log_background_task_end(task_name, False, error_result)
            self.logger.error(f"Error in manual update: {e}")
            return error_result
        finally:
            db.close()
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get current status of background tasks."""
        if not self.scheduler:
            return {"status": "not_started", "jobs": []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": next_run.isoformat() if next_run else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running" if self.is_running else "stopped",
            "jobs": jobs,
            "config": self.config,
            "settings": {
                "enabled": settings.enable_background_tasks,
                "schedule": settings.get_cron_schedule(),
                "cache_settings": settings.get_cache_settings()
            }
        }


# Global instance
background_task_service = BackgroundTaskService()