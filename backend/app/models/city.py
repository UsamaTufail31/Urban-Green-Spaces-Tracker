from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    country = Column(String(100), nullable=False)
    state_province = Column(String(100))
    population = Column(Integer)
    area_km2 = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)
    
    # Relationships
    parks = relationship("Park", back_populates="city", cascade="all, delete-orphan")
    green_coverage = relationship("GreenCoverage", back_populates="city", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<City(name='{self.name}', country='{self.country}')>"