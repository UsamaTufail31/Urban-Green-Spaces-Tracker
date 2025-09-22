from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class CoverageCache(Base):
    """Cache table for storing coverage calculation results with expiration."""
    __tablename__ = "coverage_cache"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, nullable=True, index=True)  # Nullable for shapefile-based calculations
    city_name = Column(String(100), nullable=False, index=True)
    cache_key = Column(String(500), nullable=False, index=True)  # Hash of calculation parameters
    cached_data = Column(Text, nullable=False)  # JSON string of calculation results
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    calculation_type = Column(String(50), nullable=False, index=True)  # 'satellite', 'stored', 'stats'
    
    # Composite index for efficient cache lookups
    __table_args__ = (
        Index('idx_cache_lookup', 'cache_key', 'calculation_type', 'expires_at'),
        Index('idx_city_cache', 'city_name', 'calculation_type', 'expires_at'),
    )

    def __repr__(self):
        return f"<CoverageCache(city_name='{self.city_name}', type='{self.calculation_type}', expires_at='{self.expires_at}')>"