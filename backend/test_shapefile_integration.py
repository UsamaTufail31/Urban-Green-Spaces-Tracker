"""
Test script for shapefile service and green coverage calculation functionality.
This script tests the integration of satellite imagery and shapefile processing.
"""

import os
import sys
import numpy as np
import tempfile
from pathlib import Path
import json

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.shapefile_service import ShapefileService
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import box, Polygon


def create_test_shapefile(temp_dir: str) -> str:
    """Create a test shapefile with a simple city polygon."""
    # Create a simple polygon representing a city
    city_polygon = box(-74.1, 40.7, -73.9, 40.8)  # Roughly Manhattan-sized
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'NAME': ['Test City'],
        'COUNTRY': ['Test Country'],
        'POPULATION': [1000000]
    }, geometry=[city_polygon], crs='EPSG:4326')
    
    # Save as shapefile
    shapefile_path = os.path.join(temp_dir, 'test_cities.shp')
    gdf.to_file(shapefile_path)
    return shapefile_path


def create_test_raster(temp_dir: str) -> str:
    """Create a test raster with simulated satellite imagery."""
    # Define raster properties
    width, height = 1000, 1000
    bounds = (-74.1, 40.7, -73.9, 40.8)  # Same bounds as test city
    transform = from_bounds(*bounds, width, height)
    
    # Create synthetic data
    # Red band (Band 1) - simulate various land cover types
    red_band = np.random.randint(50, 200, (height, width), dtype=np.uint8)
    
    # NIR band (Band 2) - simulate vegetation response
    nir_band = np.zeros((height, width), dtype=np.uint8)
    
    # Create areas with different vegetation levels
    # High vegetation area (NDVI > 0.3)
    nir_band[200:400, 200:400] = np.random.randint(180, 250, (200, 200))
    red_band[200:400, 200:400] = np.random.randint(30, 80, (200, 200))
    
    # Medium vegetation area
    nir_band[600:800, 600:800] = np.random.randint(120, 180, (200, 200))
    red_band[600:800, 600:800] = np.random.randint(60, 120, (200, 200))
    
    # Low vegetation/urban area
    nir_band[100:300, 600:800] = np.random.randint(60, 120, (200, 200))
    red_band[100:300, 600:800] = np.random.randint(100, 200, (200, 200))
    
    # Stack bands
    raster_data = np.stack([red_band, nir_band])
    
    # Save as GeoTIFF
    raster_path = os.path.join(temp_dir, 'test_satellite.tif')
    
    with rasterio.open(
        raster_path, 'w',
        driver='GTiff',
        height=height,
        width=width,
        count=2,
        dtype=raster_data.dtype,
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        dst.write(raster_data)
    
    return raster_path


def test_shapefile_service():
    """Test the ShapefileService functionality."""
    print("=" * 50)
    print("TESTING SHAPEFILE SERVICE")
    print("=" * 50)
    
    service = ShapefileService()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Create test data
        print("\n1. Creating test shapefile and raster...")
        shapefile_path = create_test_shapefile(temp_dir)
        raster_path = create_test_raster(temp_dir)
        print(f"✓ Created shapefile: {shapefile_path}")
        print(f"✓ Created raster: {raster_path}")
        
        # Test shapefile loading
        print("\n2. Testing shapefile loading...")
        try:
            gdf = service.load_shapefile(shapefile_path)
            print(f"✓ Loaded shapefile with {len(gdf)} features")
            print(f"  Columns: {list(gdf.columns)}")
            print(f"  CRS: {gdf.crs}")
        except Exception as e:
            print(f"✗ Error loading shapefile: {e}")
            return False
        
        # Test shapefile info
        print("\n3. Testing shapefile info...")
        try:
            info = service.get_shapefile_info(shapefile_path)
            print(f"✓ Shapefile info: {json.dumps(info, indent=2)}")
        except Exception as e:
            print(f"✗ Error getting shapefile info: {e}")
            return False
        
        # Test city polygon extraction
        print("\n4. Testing city polygon extraction...")
        try:
            city_polygon = service.extract_city_polygon(gdf, "Test City", "NAME")
            print(f"✓ Extracted city polygon with bounds: {city_polygon.bounds}")
        except Exception as e:
            print(f"✗ Error extracting city polygon: {e}")
            return False
        
        # Test raster loading
        print("\n5. Testing raster loading...")
        try:
            raster_data, raster_metadata = service.load_raster_data(raster_path)
            print(f"✓ Loaded raster with shape: {raster_data.shape}")
            print(f"  CRS: {raster_metadata.get('crs')}")
            print(f"  Transform: {raster_metadata.get('transform')}")
        except Exception as e:
            print(f"✗ Error loading raster: {e}")
            return False
        
        # Test NDVI calculation
        print("\n6. Testing NDVI calculation...")
        try:
            red_band = raster_data[0].astype(np.float32)
            nir_band = raster_data[1].astype(np.float32)
            ndvi = service.calculate_ndvi(red_band, nir_band)
            print(f"✓ Calculated NDVI with shape: {ndvi.shape}")
            valid_ndvi = ndvi[ndvi != -9999]
            print(f"  NDVI range: {valid_ndvi.min():.3f} to {valid_ndvi.max():.3f}")
            print(f"  Mean NDVI: {valid_ndvi.mean():.3f}")
        except Exception as e:
            print(f"✗ Error calculating NDVI: {e}")
            return False
        
        # Test green coverage calculation
        print("\n7. Testing green coverage calculation...")
        try:
            coverage_stats = service.calculate_green_coverage_from_raster(
                raster_data, city_polygon, raster_metadata,
                ndvi_threshold=0.3, red_band_idx=0, nir_band_idx=1
            )
            print(f"✓ Green coverage calculation successful!")
            print(f"  Green coverage: {coverage_stats['green_coverage_percentage']:.2f}%")
            print(f"  Total area: {coverage_stats['total_area_km2']:.4f} km²")
            print(f"  Green area: {coverage_stats['green_area_km2']:.4f} km²")
            print(f"  Total pixels: {coverage_stats['total_pixels']}")
            print(f"  Green pixels: {coverage_stats['green_pixels']}")
            print(f"  Mean NDVI: {coverage_stats['mean_ndvi']:.3f}")
        except Exception as e:
            print(f"✗ Error calculating green coverage: {e}")
            return False
        
        # Test complete workflow
        print("\n8. Testing complete workflow...")
        try:
            complete_stats = service.calculate_green_coverage_from_files(
                shapefile_path=shapefile_path,
                raster_path=raster_path,
                city_name="Test City",
                ndvi_threshold=0.3,
                name_column="NAME",
                red_band_idx=0,
                nir_band_idx=1
            )
            print(f"✓ Complete workflow successful!")
            print(f"  Results: {json.dumps({k: v for k, v in complete_stats.items() if k not in ['shapefile_path', 'raster_path']}, indent=2)}")
        except Exception as e:
            print(f"✗ Error in complete workflow: {e}")
            return False
        
        # Test coordinate system validation
        print("\n9. Testing coordinate system validation...")
        try:
            validation = service.validate_coordinate_systems(shapefile_path, raster_path)
            print(f"✓ Coordinate system validation: {json.dumps(validation, indent=2)}")
        except Exception as e:
            print(f"✗ Error validating coordinate systems: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED! 🎉")
    print("=" * 50)
    return True


def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "=" * 50)
    print("TESTING ERROR HANDLING")
    print("=" * 50)
    
    service = ShapefileService()
    
    # Test file not found
    print("\n1. Testing file not found...")
    try:
        service.load_shapefile("nonexistent.shp")
        print("✗ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("✓ FileNotFoundError raised correctly")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Test unsupported format
    print("\n2. Testing unsupported file format...")
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
        tmp.write(b"test content")
        tmp_path = tmp.name
    
    try:
        service.load_shapefile(tmp_path)
        print("✗ Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"✓ ValueError raised correctly: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        os.unlink(tmp_path)
    
    print("\n✓ Error handling tests passed!")
    return True


def run_performance_test():
    """Run a performance test with larger data."""
    print("\n" + "=" * 50)
    print("PERFORMANCE TEST")
    print("=" * 50)
    
    service = ShapefileService()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create larger test data
        print("\n1. Creating larger test data...")
        
        # Larger raster (2000x2000 pixels)
        width, height = 2000, 2000
        bounds = (-74.2, 40.6, -73.8, 40.9)
        transform = from_bounds(*bounds, width, height)
        
        red_band = np.random.randint(50, 200, (height, width), dtype=np.uint8)
        nir_band = np.random.randint(60, 250, (height, width), dtype=np.uint8)
        raster_data = np.stack([red_band, nir_band])
        
        raster_path = os.path.join(temp_dir, 'large_test.tif')
        with rasterio.open(
            raster_path, 'w',
            driver='GTiff',
            height=height,
            width=width,
            count=2,
            dtype=raster_data.dtype,
            crs='EPSG:4326',
            transform=transform
        ) as dst:
            dst.write(raster_data)
        
        # Create multiple city polygons
        cities = []
        for i in range(5):
            x_offset = i * 0.08
            city_polygon = box(-74.1 + x_offset, 40.7, -73.95 + x_offset, 40.8)
            cities.append(city_polygon)
        
        gdf = gpd.GeoDataFrame({
            'NAME': [f'City_{i}' for i in range(5)],
            'COUNTRY': ['Test Country'] * 5,
            'POPULATION': [1000000 + i * 100000 for i in range(5)]
        }, geometry=cities, crs='EPSG:4326')
        
        shapefile_path = os.path.join(temp_dir, 'large_cities.shp')
        gdf.to_file(shapefile_path)
        
        print(f"✓ Created large raster: {width}x{height} pixels")
        print(f"✓ Created shapefile with {len(cities)} cities")
        
        # Test performance
        print("\n2. Running performance test...")
        import time
        
        start_time = time.time()
        try:
            coverage_stats = service.calculate_green_coverage_from_files(
                shapefile_path=shapefile_path,
                raster_path=raster_path,
                city_name="City_2",
                ndvi_threshold=0.3
            )
            end_time = time.time()
            
            processing_time = end_time - start_time
            total_pixels = coverage_stats['total_pixels']
            pixels_per_second = total_pixels / processing_time if processing_time > 0 else 0
            
            print(f"✓ Performance test completed!")
            print(f"  Processing time: {processing_time:.2f} seconds")
            print(f"  Total pixels: {total_pixels:,}")
            print(f"  Pixels per second: {pixels_per_second:,.0f}")
            print(f"  Green coverage: {coverage_stats['green_coverage_percentage']:.2f}%")
            
            return True
            
        except Exception as e:
            print(f"✗ Performance test failed: {e}")
            return False


if __name__ == "__main__":
    print("SHAPEFILE SERVICE TEST SUITE")
    print("=" * 60)
    
    success = True
    
    # Run main functionality tests
    if not test_shapefile_service():
        success = False
    
    # Run error handling tests
    if not test_error_handling():
        success = False
    
    # Run performance test
    if not run_performance_test():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉")
        print("\nThe shapefile integration is working correctly.")
        print("You can now:")
        print("1. Install the new dependencies: pip install -r requirements.txt")
        print("2. Update your database schema for the new green coverage fields")
        print("3. Start the FastAPI server and test the new endpoints")
        print("4. Upload shapefiles and satellite imagery via the API")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the error messages above.")
    print("=" * 60)