from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import City, Park, GreenCoverage


def seed_data():
    """Seed the database with sample data."""
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(City).first():
            print("Database already contains data. Skipping seeding.")
            return
        
        # Sample cities
        cities_data = [
            {
                "name": "New York",
                "country": "USA",
                "state_province": "New York",
                "population": 8336817,
                "area_km2": 783.8,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "description": "The most populous city in the United States"
            },
            {
                "name": "London",
                "country": "United Kingdom",
                "state_province": "England",
                "population": 8982000,
                "area_km2": 1572.0,
                "latitude": 51.5074,
                "longitude": -0.1278,
                "description": "The capital and largest city of England and the United Kingdom"
            },
            {
                "name": "Tokyo",
                "country": "Japan",
                "state_province": "Tokyo",
                "population": 13960000,
                "area_km2": 2194.0,
                "latitude": 35.6762,
                "longitude": 139.6503,
                "description": "The capital and most populous city of Japan"
            },
            {
                "name": "Lahore",
                "country": "Pakistan",
                "state_province": "Punjab",
                "population": 11126285,
                "area_km2": 1772.0,
                "latitude": 31.5204,
                "longitude": 74.3587,
                "description": "The capital city of Punjab province and second-largest city in Pakistan"
            }
        ]
        
        # Create cities
        cities = []
        for city_data in cities_data:
            city = City(**city_data)
            db.add(city)
            cities.append(city)
        
        db.commit()
        
        # Sample parks
        parks_data = [
            # New York parks
            {
                "name": "Central Park",
                "city_id": 1,
                "area_hectares": 341.0,
                "park_type": "urban park",
                "latitude": 40.7829,
                "longitude": -73.9654,
                "description": "Large public park in Manhattan",
                "address": "New York, NY 10024",
                "established_year": 1857,
                "facilities": "playgrounds, lakes, walking paths, zoo"
            },
            {
                "name": "Prospect Park",
                "city_id": 1,
                "area_hectares": 237.0,
                "park_type": "urban park",
                "latitude": 40.6602,
                "longitude": -73.9690,
                "description": "Public park in Brooklyn",
                "address": "Brooklyn, NY 11225",
                "established_year": 1867,
                "facilities": "lake, zoo, botanical garden, concert venue"
            },
            # London parks
            {
                "name": "Hyde Park",
                "city_id": 2,
                "area_hectares": 142.0,
                "park_type": "royal park",
                "latitude": 51.5073,
                "longitude": -0.1657,
                "description": "Large royal park in central London",
                "address": "London W2 2UH, UK",
                "established_year": 1637,
                "facilities": "speakers corner, serpentine lake, riding paths"
            },
            # Tokyo parks
            {
                "name": "Ueno Park",
                "city_id": 3,
                "area_hectares": 53.0,
                "park_type": "public park",
                "latitude": 35.7153,
                "longitude": 139.7738,
                "description": "Large public park in central Tokyo",
                "address": "Taito City, Tokyo 110-0007, Japan",
                "established_year": 1873,
                "facilities": "museums, zoo, temples, cherry blossoms"
            },
            # Lahore parks
            {
                "name": "Lawrence Gardens",
                "city_id": 4,
                "area_hectares": 27.0,
                "park_type": "public park",
                "latitude": 31.5519,
                "longitude": 74.3292,
                "description": "Historic public park in the heart of Lahore",
                "address": "Lawrence Road, Lahore, Punjab, Pakistan",
                "established_year": 1860,
                "facilities": "library, sports complex, walking paths, gardens"
            },
            {
                "name": "Shalimar Gardens",
                "city_id": 4,
                "area_hectares": 16.0,
                "park_type": "heritage garden",
                "latitude": 31.5858,
                "longitude": 74.3828,
                "description": "Mughal garden built by Emperor Shah Jahan",
                "address": "Grand Trunk Road, Lahore, Punjab, Pakistan",
                "established_year": 1641,
                "facilities": "fountains, terraced gardens, historical monuments"
            }
        ]
        
        # Create parks
        for park_data in parks_data:
            park = Park(**park_data)
            db.add(park)
        
        db.commit()
        
        # Sample green coverage data
        green_coverage_data = [
            # New York green coverage over years
            {
                "city_id": 1,
                "city_name": "New York",
                "coverage_percentage": 21.0,
                "year": 2020,
                "data_source": "NYC Parks Department",
                "measurement_method": "satellite imagery analysis"
            },
            {
                "city_id": 1,
                "city_name": "New York",
                "coverage_percentage": 20.5,
                "year": 2019,
                "data_source": "NYC Parks Department",
                "measurement_method": "satellite imagery analysis"
            },
            {
                "city_id": 1,
                "city_name": "New York",
                "coverage_percentage": 20.2,
                "year": 2018,
                "data_source": "NYC Parks Department",
                "measurement_method": "satellite imagery analysis"
            },
            # London green coverage
            {
                "city_id": 2,
                "city_name": "London",
                "coverage_percentage": 33.0,
                "year": 2020,
                "data_source": "Greater London Authority",
                "measurement_method": "GIS mapping and surveys"
            },
            {
                "city_id": 2,
                "city_name": "London",
                "coverage_percentage": 32.8,
                "year": 2019,
                "data_source": "Greater London Authority",
                "measurement_method": "GIS mapping and surveys"
            },
            # Tokyo green coverage
            {
                "city_id": 3,
                "city_name": "Tokyo",
                "coverage_percentage": 13.6,
                "year": 2020,
                "data_source": "Tokyo Metropolitan Government",
                "measurement_method": "aerial photography and ground surveys"
            },
            {
                "city_id": 3,
                "city_name": "Tokyo",
                "coverage_percentage": 13.2,
                "year": 2019,
                "data_source": "Tokyo Metropolitan Government",
                "measurement_method": "aerial photography and ground surveys"
            },
            # Lahore green coverage
            {
                "city_id": 4,
                "city_name": "Lahore",
                "coverage_percentage": 8.5,
                "year": 2020,
                "data_source": "Punjab Forest Department",
                "measurement_method": "satellite imagery analysis"
            },
            {
                "city_id": 4,
                "city_name": "Lahore",
                "coverage_percentage": 8.2,
                "year": 2019,
                "data_source": "Punjab Forest Department",
                "measurement_method": "satellite imagery analysis"
            },
            {
                "city_id": 4,
                "city_name": "Lahore",
                "coverage_percentage": 7.9,
                "year": 2018,
                "data_source": "Punjab Forest Department",
                "measurement_method": "satellite imagery analysis"
            }
        ]
        
        # Create green coverage records
        for coverage_data in green_coverage_data:
            coverage = GreenCoverage(**coverage_data)
            db.add(coverage)
        
        db.commit()
        print("Database seeded successfully with sample data!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()