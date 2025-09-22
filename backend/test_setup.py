#!/usr/bin/env python3
"""
Test script to verify the FastAPI backend setup
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported successfully."""
    try:
        from app.database import engine, Base, get_db
        print("✓ Database module imported successfully")
        
        from app.models import City, Park, GreenCoverage
        print("✓ Models imported successfully")
        
        from app import schemas
        print("✓ Schemas imported successfully")
        
        from app.main import app
        print("✓ FastAPI app imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_database_connection():
    """Test database connection and table creation."""
    try:
        from app.database import engine
        from app.models import City, Park, GreenCoverage
        
        # Test connection
        with engine.connect() as connection:
            print("✓ Database connection successful")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['cities', 'parks', 'green_coverage']
        for table in expected_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' missing")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_model_operations():
    """Test basic model operations."""
    try:
        from app.database import SessionLocal
        from app.models import City, Park, GreenCoverage
        
        db = SessionLocal()
        
        # Test query operations
        city_count = db.query(City).count()
        park_count = db.query(Park).count()
        coverage_count = db.query(GreenCoverage).count()
        
        print(f"✓ Database queries successful:")
        print(f"  - Cities: {city_count}")
        print(f"  - Parks: {park_count}")
        print(f"  - Green Coverage records: {coverage_count}")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Model operation error: {e}")
        return False


def main():
    """Run all tests."""
    print("FastAPI Backend Setup Test")
    print("=" * 40)
    
    success = True
    
    print("\n1. Testing imports...")
    success &= test_imports()
    
    print("\n2. Testing database connection...")
    success &= test_database_connection()
    
    print("\n3. Testing model operations...")
    success &= test_model_operations()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! Backend setup is working correctly.")
        print("\nTo start the development server:")
        print("cd backend")
        print("python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\nAPI will be available at: http://localhost:8000")
        print("Interactive docs at: http://localhost:8000/docs")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())