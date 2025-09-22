from app.database import engine, Base, SessionLocal
from app.models import City, Park, GreenCoverage, CoverageCache, Feedback, User, UserRole
from app.services.auth_service import AuthService
from app import schemas
import os


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_tables():
    """Drop all tables in the database."""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped!")


def create_default_admin():
    """Create default admin user if none exists."""
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        
        # Check if any admin user exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username}")
            return existing_admin
        
        # Create default admin user
        admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@urbanproject.com")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "AdminPass123!")
        admin_full_name = os.getenv("DEFAULT_ADMIN_FULL_NAME", "System Administrator")
        
        try:
            admin_user = auth_service.create_admin_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                full_name=admin_full_name
            )
            
            print(f"Default admin user created successfully!")
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print("Please change the default password after first login!")
            
            return admin_user
            
        except Exception as e:
            print(f"Error creating admin user: {e}")
            return None
            
    finally:
        db.close()


def init_database():
    """Initialize database with tables and default admin user."""
    print("Initializing Urban Project database...")
    
    # Create tables
    create_tables()
    
    # Create default admin user
    create_default_admin()
    
    print("Database initialization completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "drop":
            drop_tables()
        elif sys.argv[1] == "create":
            create_tables()
        elif sys.argv[1] == "admin":
            create_default_admin()
        elif sys.argv[1] == "init":
            init_database()
        else:
            print("Usage: python init_db.py [create|drop|admin|init]")
            print("  create: Create tables only")
            print("  drop: Drop all tables")
            print("  admin: Create default admin user only")
            print("  init: Full initialization (tables + admin user)")
    else:
        init_database()