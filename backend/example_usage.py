"""
Example script demonstrating the satellite imagery and shapefile integration.
This script shows how to use the new green coverage calculation features.
"""

import requests
import json
import tempfile
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import box
import os

# API base URL (adjust if your server runs on a different port)
API_BASE = "http://localhost:8001"


def create_sample_data():
    """Create sample shapefile and raster for demonstration."""
    print("Creating sample data...")
    
    # Create a sample city polygon (representing Manhattan area)
    city_polygon = box(-74.05, 40.75, -73.95, 40.85)
    
    # Create GeoDataFrame with sample city
    gdf = gpd.GeoDataFrame({
        'NAME': ['Sample City'],
        'COUNTRY': ['USA'],
        'STATE': ['NY'],
        'POPULATION': [1500000]
    }, geometry=[city_polygon], crs='EPSG:4326')
    
    # Save shapefile
    temp_dir = tempfile.mkdtemp()
    shapefile_path = os.path.join(temp_dir, 'sample_city.shp')
    gdf.to_file(shapefile_path)
    
    # Create sample satellite imagery
    width, height = 500, 500
    bounds = (-74.05, 40.75, -73.95, 40.85)
    transform = from_bounds(*bounds, width, height)
    
    # Simulate realistic urban imagery
    # Red band - urban areas have higher red values
    red_band = np.random.randint(80, 150, (height, width), dtype=np.uint8)
    
    # NIR band - vegetation areas have higher NIR values
    nir_band = np.random.randint(60, 120, (height, width), dtype=np.uint8)
    
    # Create some "park" areas with higher vegetation (higher NIR, lower Red)
    park_areas = [
        (100, 150, 50, 100),   # Central park area
        (350, 400, 200, 250),  # Another park
        (200, 250, 350, 400),  # Riverside area
    ]
    
    for x1, x2, y1, y2 in park_areas:
        # High vegetation areas
        nir_band[y1:y2, x1:x2] = np.random.randint(180, 250, (y2-y1, x2-x1))
        red_band[y1:y2, x1:x2] = np.random.randint(30, 80, (y2-y1, x2-x1))
    
    # Stack bands (Red=0, NIR=1)
    raster_data = np.stack([red_band, nir_band])
    
    # Save as GeoTIFF
    raster_path = os.path.join(temp_dir, 'sample_satellite.tif')
    
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
    
    print(f"✓ Created sample shapefile: {shapefile_path}")
    print(f"✓ Created sample raster: {raster_path}")
    return shapefile_path, raster_path, temp_dir


def test_api_endpoints():
    """Test the new API endpoints with sample data."""
    print("\n" + "="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    # Create sample data
    shapefile_path, raster_path, temp_dir = create_sample_data()
    
    try:
        # Test 1: Get supported formats
        print("\n1. Testing supported formats endpoint...")
        response = requests.get(f"{API_BASE}/shapefile/supported-formats")
        if response.status_code == 200:
            formats = response.json()
            print("✓ Supported formats retrieved")
            print(f"  Shapefile formats: {list(formats['shapefile_formats'].keys())}")
            print(f"  Raster formats: {list(formats['raster_formats'].keys())}")
        else:
            print(f"✗ Error: {response.status_code}")
        
        # Test 2: Get shapefile info
        print("\n2. Testing shapefile info endpoint...")
        with open(shapefile_path, 'rb') as f:
            files = {'shapefile': f}
            response = requests.post(f"{API_BASE}/shapefile/info", files=files)
        
        if response.status_code == 200:
            info = response.json()
            print("✓ Shapefile info retrieved")
            print(f"  Features: {info['feature_count']}")
            print(f"  CRS: {info['coordinate_system']}")
            print(f"  Sample cities: {info.get('sample_names', [])}")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
        
        # Test 3: Validate coordinate systems
        print("\n3. Testing CRS validation...")
        with open(shapefile_path, 'rb') as shp_f, open(raster_path, 'rb') as raster_f:
            files = {
                'shapefile': shp_f,
                'raster': raster_f
            }
            response = requests.post(f"{API_BASE}/shapefile/validate-crs", files=files)
        
        if response.status_code == 200:
            validation = response.json()
            print("✓ CRS validation completed")
            print(f"  Compatible: {validation['compatible']}")
            print(f"  Recommendation: {validation.get('recommendation', 'N/A')}")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
        
        # Test 4: Calculate green coverage
        print("\n4. Testing green coverage calculation...")
        
        request_data = {
            "city_name": "Sample City",
            "ndvi_threshold": 0.3,
            "name_column": "NAME",
            "red_band_idx": 0,
            "nir_band_idx": 1,
            "year": 2023
        }
        
        with open(shapefile_path, 'rb') as shp_f, open(raster_path, 'rb') as raster_f:
            files = {
                'shapefile': shp_f,
                'raster': raster_f
            }
            data = {
                'request_data': json.dumps(request_data),
                'save_to_database': False  # Don't save to database for demo
            }
            response = requests.post(
                f"{API_BASE}/shapefile/calculate-green-coverage",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Green coverage calculation successful!")
            print(f"  City: {result['city_name']}")
            print(f"  Green Coverage: {result['green_coverage_percentage']:.2f}%")
            print(f"  Total Area: {result['total_area_km2']:.4f} km²")
            print(f"  Green Area: {result['green_area_km2']:.4f} km²")
            print(f"  NDVI Range: {result['min_ndvi']:.3f} to {result['max_ndvi']:.3f}")
            print(f"  Mean NDVI: {result['mean_ndvi']:.3f}")
            print(f"  Total Pixels: {result['total_pixels']:,}")
            print(f"  Green Pixels: {result['green_pixels']:,}")
            print(f"  Data Source: {result['data_source']}")
            print(f"  Method: {result['measurement_method']}")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API server")
        print("  Make sure the FastAPI server is running on http://localhost:8001")
        print("  Start it with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    finally:
        # Clean up temporary files
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n✓ Cleaned up temporary files from {temp_dir}")


def demonstrate_batch_processing():
    """Demonstrate processing multiple cities."""
    print("\n" + "="*60)
    print("BATCH PROCESSING DEMONSTRATION")
    print("="*60)
    
    # Create sample data with multiple cities
    print("Creating multi-city dataset...")
    
    cities = [
        {"name": "Downtown", "bounds": (-74.05, 40.75, -73.95, 40.85)},
        {"name": "Midtown", "bounds": (-74.00, 40.80, -73.90, 40.90)},
        {"name": "Uptown", "bounds": (-73.98, 40.85, -73.88, 40.95)},
    ]
    
    # Create polygons for each city
    geometries = []
    names = []
    for city in cities:
        polygon = box(*city["bounds"])
        geometries.append(polygon)
        names.append(city["name"])
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'NAME': names,
        'COUNTRY': ['USA'] * len(cities),
        'POPULATION': [500000 + i * 100000 for i in range(len(cities))]
    }, geometry=geometries, crs='EPSG:4326')
    
    # Save multi-city shapefile
    temp_dir = tempfile.mkdtemp()
    shapefile_path = os.path.join(temp_dir, 'multi_cities.shp')
    gdf.to_file(shapefile_path)
    
    # Create larger raster covering all cities
    overall_bounds = (-74.05, 40.75, -73.85, 40.95)
    width, height = 800, 800
    transform = from_bounds(*overall_bounds, width, height)
    
    # Create diverse landscape
    red_band = np.random.randint(70, 160, (height, width), dtype=np.uint8)
    nir_band = np.random.randint(50, 140, (height, width), dtype=np.uint8)
    
    # Add varied vegetation patterns
    for i in range(10):
        x = np.random.randint(50, width-50)
        y = np.random.randint(50, height-50)
        size = np.random.randint(30, 80)
        
        # Create vegetation patches
        nir_band[y:y+size, x:x+size] = np.random.randint(180, 250, (size, size))
        red_band[y:y+size, x:x+size] = np.random.randint(30, 80, (size, size))
    
    raster_data = np.stack([red_band, nir_band])
    raster_path = os.path.join(temp_dir, 'multi_satellite.tif')
    
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
    
    print(f"✓ Created multi-city shapefile with {len(cities)} cities")
    print(f"✓ Created larger raster: {width}x{height} pixels")
    
    # Process each city
    results = []
    for city_name in names:
        print(f"\nProcessing {city_name}...")
        
        request_data = {
            "city_name": city_name,
            "ndvi_threshold": 0.3,
            "year": 2023
        }
        
        try:
            with open(shapefile_path, 'rb') as shp_f, open(raster_path, 'rb') as raster_f:
                files = {'shapefile': shp_f, 'raster': raster_f}
                data = {
                    'request_data': json.dumps(request_data),
                    'save_to_database': False
                }
                response = requests.post(
                    f"{API_BASE}/shapefile/calculate-green-coverage",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                results.append(result)
                print(f"  ✓ {city_name}: {result['green_coverage_percentage']:.1f}% green coverage")
            else:
                print(f"  ✗ Error processing {city_name}: {response.status_code}")
        
        except Exception as e:
            print(f"  ✗ Error processing {city_name}: {e}")
    
    # Summary
    if results:
        print(f"\n{'='*40}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*40}")
        print(f"{'City':<12} {'Coverage':<10} {'Area (km²)':<12} {'Green (km²)':<12}")
        print("-" * 50)
        
        total_area = 0
        total_green = 0
        
        for result in results:
            city = result['city_name']
            coverage = result['green_coverage_percentage']
            area = result['total_area_km2']
            green = result['green_area_km2']
            
            print(f"{city:<12} {coverage:>6.1f}%    {area:>8.4f}    {green:>8.4f}")
            total_area += area
            total_green += green
        
        print("-" * 50)
        overall_coverage = (total_green / total_area * 100) if total_area > 0 else 0
        print(f"{'TOTAL':<12} {overall_coverage:>6.1f}%    {total_area:>8.4f}    {total_green:>8.4f}")
    
    # Clean up
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("SATELLITE IMAGERY API DEMONSTRATION")
    print("="*60)
    print("This script demonstrates the new satellite imagery and")
    print("shapefile integration capabilities of the Urban Green Spaces API.")
    print("\nMake sure the FastAPI server is running before proceeding!")
    print("Start it with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload")
    
    input("\nPress Enter to continue...")
    
    # Test basic API endpoints
    test_api_endpoints()
    
    # Demonstrate batch processing
    demonstrate_batch_processing()
    
    print("\n" + "="*60)
    print("🎉 DEMONSTRATION COMPLETED!")
    print("="*60)
    print("\nThe satellite imagery integration is working successfully!")
    print("\nNext steps:")
    print("1. Try the interactive API docs at: http://localhost:8001/docs")
    print("2. Upload your own shapefiles and satellite imagery")
    print("3. Experiment with different NDVI thresholds")
    print("4. Integrate with your frontend application")
    print("\nFor more information, see: SHAPEFILE_INTEGRATION.md")