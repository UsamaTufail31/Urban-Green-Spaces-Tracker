from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Park(Base):
    __tablename__ = "parks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    area_hectares = Column(Float)
    park_type = Column(String(100))  # e.g., "urban park", "national park", "botanical garden"
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)
    address = Column(String(500))
    established_year = Column(Integer)
    facilities = Column(Text)  # JSON string or comma-separated facilities
    
    # Relationship
    city = relationship("City", back_populates="parks")

    def __repr__(self):
        return f"<Park(name='{self.name}', city_id={self.city_id})>"