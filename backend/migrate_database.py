"""
Database migration script to update green_coverage table with new satellite imagery fields.
Run this script after installing the new dependencies.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine, get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_green_coverage_table():
    """Migrate the green_coverage table to include new fields."""
    
    migration_sql = """
    -- Add new columns for satellite imagery data
    ALTER TABLE green_coverage ADD COLUMN total_area_km2 REAL;
    ALTER TABLE green_coverage ADD COLUMN green_area_km2 REAL;
    ALTER TABLE green_coverage ADD COLUMN ndvi_threshold REAL;
    ALTER TABLE green_coverage ADD COLUMN mean_ndvi REAL;
    ALTER TABLE green_coverage ADD COLUMN std_ndvi REAL;
    ALTER TABLE green_coverage ADD COLUMN min_ndvi REAL;
    ALTER TABLE green_coverage ADD COLUMN max_ndvi REAL;
    ALTER TABLE green_coverage ADD COLUMN coordinate_system VARCHAR(100);
    ALTER TABLE green_coverage ADD COLUMN shapefile_path VARCHAR(500);
    ALTER TABLE green_coverage ADD COLUMN raster_path VARCHAR(500);
    ALTER TABLE green_coverage ADD COLUMN total_pixels INTEGER;
    ALTER TABLE green_coverage ADD COLUMN green_pixels INTEGER;
    ALTER TABLE green_coverage ADD COLUMN processing_metadata TEXT;
    ALTER TABLE green_coverage ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE green_coverage ADD COLUMN updated_at TIMESTAMP;
    """
    
    try:
        with engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("PRAGMA table_info(green_coverage);"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            new_columns = [
                'total_area_km2', 'green_area_km2', 'ndvi_threshold', 'mean_ndvi',
                'std_ndvi', 'min_ndvi', 'max_ndvi', 'coordinate_system',
                'shapefile_path', 'raster_path', 'total_pixels', 'green_pixels',
                'processing_metadata', 'created_at', 'updated_at'
            ]
            
            columns_to_add = [col for col in new_columns if col not in existing_columns]
            
            if not columns_to_add:
                logger.info("All new columns already exist. Migration not needed.")
            else:
                logger.info(f"Adding columns: {columns_to_add}")
                
                # Add columns one by one for better error handling
                for column in columns_to_add:
                    if column == 'total_area_km2':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN total_area_km2 REAL;"))
                    elif column == 'green_area_km2':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN green_area_km2 REAL;"))
                    elif column == 'ndvi_threshold':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN ndvi_threshold REAL;"))
                    elif column == 'mean_ndvi':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN mean_ndvi REAL;"))
                    elif column == 'std_ndvi':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN std_ndvi REAL;"))
                    elif column == 'min_ndvi':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN min_ndvi REAL;"))
                    elif column == 'max_ndvi':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN max_ndvi REAL;"))
                    elif column == 'coordinate_system':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN coordinate_system VARCHAR(100);"))
                    elif column == 'shapefile_path':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN shapefile_path VARCHAR(500);"))
                    elif column == 'raster_path':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN raster_path VARCHAR(500);"))
                    elif column == 'total_pixels':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN total_pixels INTEGER;"))
                    elif column == 'green_pixels':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN green_pixels INTEGER;"))
                    elif column == 'processing_metadata':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN processing_metadata TEXT;"))
                    elif column == 'created_at':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN created_at TIMESTAMP;"))
                    elif column == 'updated_at':
                        connection.execute(text("ALTER TABLE green_coverage ADD COLUMN updated_at TIMESTAMP;"))
                    
                    logger.info(f"Added column: {column}")
            
            connection.commit()
            logger.info("Green coverage table migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Green coverage migration failed: {e}")
        return False


def create_cache_table():
    """Create the cache table for storing calculation results."""
    
    cache_table_sql = """
    CREATE TABLE IF NOT EXISTS coverage_cache (
        id INTEGER PRIMARY KEY,
        city_id INTEGER,
        city_name VARCHAR(100) NOT NULL,
        cache_key VARCHAR(500) NOT NULL,
        cached_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        calculation_type VARCHAR(50) NOT NULL
    );
    
    CREATE INDEX IF NOT EXISTS idx_cache_lookup 
    ON coverage_cache(cache_key, calculation_type, expires_at);
    
    CREATE INDEX IF NOT EXISTS idx_city_cache 
    ON coverage_cache(city_name, calculation_type, expires_at);
    
    CREATE INDEX IF NOT EXISTS idx_city_id_cache 
    ON coverage_cache(city_id);
    
    CREATE INDEX IF NOT EXISTS idx_created_at_cache 
    ON coverage_cache(created_at);
    """
    
    try:
        with engine.connect() as connection:
            # Check if table already exists
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='coverage_cache';"))
            table_exists = result.fetchone() is not None
            
            if table_exists:
                logger.info("Coverage cache table already exists.")
                return True
            
            logger.info("Creating coverage cache table...")
            
            # Execute the SQL statements
            for statement in cache_table_sql.split(';'):
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))
            
            connection.commit()
            logger.info("Coverage cache table created successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Cache table creation failed: {e}")
        return False


def verify_migration():
    """Verify that the migration was successful."""
    try:
        with engine.connect() as connection:
            # Check green_coverage table
            result = connection.execute(text("PRAGMA table_info(green_coverage);"))
            columns = [row[1] for row in result.fetchall()]
            
            expected_columns = [
                'id', 'city_id', 'city_name', 'coverage_percentage', 'year',
                'data_source', 'measurement_method', 'notes',
                'total_area_km2', 'green_area_km2', 'ndvi_threshold', 'mean_ndvi',
                'std_ndvi', 'min_ndvi', 'max_ndvi', 'coordinate_system',
                'shapefile_path', 'raster_path', 'total_pixels', 'green_pixels',
                'processing_metadata', 'created_at', 'updated_at'
            ]
            
            missing_columns = [col for col in expected_columns if col not in columns]
            
            if missing_columns:
                logger.error(f"Green coverage migration verification failed. Missing columns: {missing_columns}")
                return False
            else:
                logger.info("Green coverage migration verification successful!")
                logger.info(f"Green coverage table now has {len(columns)} columns")
            
            # Check cache table
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='coverage_cache';"))
            cache_table_exists = result.fetchone() is not None
            
            if not cache_table_exists:
                logger.error("Cache table verification failed. Coverage cache table not found.")
                return False
            
            # Check cache table structure
            result = connection.execute(text("PRAGMA table_info(coverage_cache);"))
            cache_columns = [row[1] for row in result.fetchall()]
            
            expected_cache_columns = [
                'id', 'city_id', 'city_name', 'cache_key', 'cached_data',
                'created_at', 'expires_at', 'calculation_type'
            ]
            
            missing_cache_columns = [col for col in expected_cache_columns if col not in cache_columns]
            
            if missing_cache_columns:
                logger.error(f"Cache table verification failed. Missing columns: {missing_cache_columns}")
                return False
            else:
                logger.info("Cache table verification successful!")
                logger.info(f"Coverage cache table has {len(cache_columns)} columns")
            
            logger.info("All migration verifications passed!")
            return True
                
    except Exception as e:
        logger.error(f"Migration verification failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("DATABASE MIGRATION FOR SATELLITE IMAGERY & CACHING INTEGRATION")
    print("=" * 70)
    
    print("\n1. Running green coverage table migration...")
    coverage_migration_success = migrate_green_coverage_table()
    
    print("\n2. Creating cache table...")
    cache_creation_success = create_cache_table()
    
    if coverage_migration_success and cache_creation_success:
        print("\n✓ All database migrations completed successfully!")
        
        print("\n3. Verifying migration...")
        if verify_migration():
            print("✓ Migration verification successful!")
            
            print("\n" + "=" * 70)
            print("🎉 DATABASE MIGRATION COMPLETED SUCCESSFULLY! 🎉")
            print("\nNew features added:")
            print("✓ Enhanced green coverage calculations with satellite imagery")
            print("✓ Coverage calculation caching with automatic expiration")
            print("✓ Cache management endpoints for monitoring and cleanup")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Start the FastAPI server: python -m uvicorn app.main:app --reload")
            print("3. Visit http://localhost:8000/docs to see the new API endpoints")
            print("4. Test caching with repeated requests to coverage endpoints")
            print("5. Monitor cache performance with /cache/stats endpoint")
            print("=" * 70)
        else:
            print("✗ Migration verification failed!")
            sys.exit(1)
    else:
        print("✗ Database migration failed!")
        if not coverage_migration_success:
            print("  - Green coverage table migration failed")
        if not cache_creation_success:
            print("  - Cache table creation failed")
        sys.exit(1)