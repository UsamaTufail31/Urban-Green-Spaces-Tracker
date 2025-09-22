from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class GreenCoverage(Base):
    __tablename__ = "green_coverage"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    city_name = Column(String(100), nullable=False, index=True)  # Denormalized for easier queries
    coverage_percentage = Column(Float, nullable=False)
    year = Column(Integer, nullable=False, index=True)
    data_source = Column(String(200))  # Source of the data
    measurement_method = Column(String(200))  # How the coverage was measured
    notes = Column(String(500))
    
    # New fields for satellite imagery and shapefile integration
    total_area_km2 = Column(Float)  # Total city area in km²
    green_area_km2 = Column(Float)  # Green area in km²
    ndvi_threshold = Column(Float)  # NDVI threshold used for classification
    mean_ndvi = Column(Float)  # Mean NDVI value
    std_ndvi = Column(Float)  # Standard deviation of NDVI
    min_ndvi = Column(Float)  # Minimum NDVI value
    max_ndvi = Column(Float)  # Maximum NDVI value
    coordinate_system = Column(String(100))  # CRS/projection used
    shapefile_path = Column(String(500))  # Path to source shapefile
    raster_path = Column(String(500))  # Path to source raster data
    total_pixels = Column(Integer)  # Total pixels analyzed
    green_pixels = Column(Integer)  # Pixels classified as vegetation
    processing_metadata = Column(Text)  # JSON metadata about processing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    city = relationship("City", back_populates="green_coverage")
    
    # Ensure unique combination of city and year
    __table_args__ = (
        UniqueConstraint('city_id', 'year', name='unique_city_year_coverage'),
    )

    def __repr__(self):
        return f"<GreenCoverage(city_name='{self.city_name}', year={self.year}, coverage={self.coverage_percentage}%)>"