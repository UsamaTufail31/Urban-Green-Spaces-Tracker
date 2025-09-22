from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


# Authentication schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    role: str = Field(default="viewer", description="User role (admin or viewer)")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password (min 8 characters)")


# City schemas
class CityBase(BaseModel):
    name: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    population: Optional[int] = Field(None, ge=0)
    area_km2: Optional[float] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    description: Optional[str] = None


class CityCreate(CityBase):
    pass


class City(CityBase):
    id: int
    
    class Config:
        from_attributes = True


# Park schemas
class ParkBase(BaseModel):
    name: str = Field(..., max_length=200)
    city_id: int
    area_hectares: Optional[float] = Field(None, ge=0)
    park_type: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    established_year: Optional[int] = Field(None, ge=1800, le=2030)
    facilities: Optional[str] = None


class ParkCreate(ParkBase):
    pass


class Park(ParkBase):
    id: int
    
    class Config:
        from_attributes = True


# Green Coverage schemas
class GreenCoverageBase(BaseModel):
    city_id: int
    coverage_percentage: float = Field(..., ge=0, le=100)
    year: int = Field(..., ge=1900, le=2030)
    data_source: Optional[str] = Field(None, max_length=200)
    measurement_method: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)


class GreenCoverageCreate(GreenCoverageBase):
    pass


class GreenCoverage(GreenCoverageBase):
    id: int
    city_name: str
    total_area_km2: Optional[float] = None
    green_area_km2: Optional[float] = None
    ndvi_threshold: Optional[float] = None
    mean_ndvi: Optional[float] = None
    std_ndvi: Optional[float] = None
    min_ndvi: Optional[float] = None
    max_ndvi: Optional[float] = None
    coordinate_system: Optional[str] = None
    total_pixels: Optional[int] = None
    green_pixels: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Shapefile-specific schemas
class ShapefileInfo(BaseModel):
    """Information about a shapefile."""
    feature_count: int
    columns: List[str]
    coordinate_system: str
    bounds: List[float]
    geometry_types: List[str]
    sample_names: Optional[List[str]] = None
    name_column: Optional[str] = None


class CoordinateSystemValidation(BaseModel):
    """Validation result for coordinate systems."""
    compatible: bool
    shapefile_crs: Optional[str] = None
    raster_crs: Optional[str] = None
    recommendation: Optional[str] = None
    error: Optional[str] = None


class GreenCoverageCalculationRequest(BaseModel):
    """Request for calculating green coverage from satellite imagery."""
    city_name: str = Field(..., description="Name of the city to analyze")
    ndvi_threshold: float = Field(0.3, ge=0, le=1, description="NDVI threshold for vegetation classification")
    name_column: str = Field("NAME", description="Column name containing city names in shapefile")
    red_band_idx: int = Field(0, ge=0, description="Index of red band in raster (0-based)")
    nir_band_idx: int = Field(1, ge=0, description="Index of NIR band in raster (0-based)")
    year: int = Field(..., ge=1900, le=2030, description="Year of the satellite imagery")


class GreenCoverageCalculationResponse(BaseModel):
    """Response from green coverage calculation."""
    city_name: str
    green_coverage_percentage: float
    total_pixels: int
    green_pixels: int
    total_area_m2: float
    green_area_m2: float
    total_area_km2: float
    green_area_km2: float
    ndvi_threshold: float
    mean_ndvi: float
    std_ndvi: float
    min_ndvi: float
    max_ndvi: float
    data_source: str
    measurement_method: str
    coordinate_system: str
    year: Optional[int] = None


class GreenCoverageEnhancedCreate(BaseModel):
    """Enhanced create schema for green coverage with satellite data."""
    city_id: int
    coverage_percentage: float = Field(..., ge=0, le=100)
    year: int = Field(..., ge=1900, le=2030)
    data_source: str = Field(default="Satellite Imagery Analysis")
    measurement_method: str
    notes: Optional[str] = None
    total_area_km2: Optional[float] = None
    green_area_km2: Optional[float] = None
    ndvi_threshold: Optional[float] = None
    mean_ndvi: Optional[float] = None
    std_ndvi: Optional[float] = None
    min_ndvi: Optional[float] = None
    max_ndvi: Optional[float] = None
    coordinate_system: Optional[str] = None
    total_pixels: Optional[int] = None
    green_pixels: Optional[int] = None
    processing_metadata: Optional[str] = None


# Nearest Parks schemas
class NearestParkResponse(BaseModel):
    id: int
    name: str
    area_hectares: Optional[float]
    amenities: Optional[str] = Field(None, description="Park facilities/amenities")
    distance_km: float = Field(..., description="Distance from user location in kilometers")
    latitude: Optional[float]
    longitude: Optional[float]
    
    class Config:
        from_attributes = True


# Green Coverage Comparison schemas
class GreenCoverageComparisonResponse(BaseModel):
    city_name: str
    city_green_coverage_percentage: float = Field(..., description="City's current green coverage percentage")
    who_recommendation_percentage: float = Field(..., description="WHO recommended green coverage percentage")
    comparison_result: str = Field(..., description="Comparison result description")
    year: int = Field(..., description="Year of the green coverage data")
    
    class Config:
        from_attributes = True


# Green Coverage Trend schemas
class GreenCoverageTrend(BaseModel):
    year: int = Field(..., description="Year of the coverage data")
    coverage_percentage: float = Field(..., description="Green coverage percentage for the year")
    total_area_km2: Optional[float] = Field(None, description="Total city area in km²")
    green_area_km2: Optional[float] = Field(None, description="Green area in km²")
    data_source: Optional[str] = Field(None, description="Source of the coverage data")
    measurement_method: Optional[str] = Field(None, description="Method used to measure coverage")
    mean_ndvi: Optional[float] = Field(None, description="Mean NDVI value")
    created_at: Optional[datetime] = Field(None, description="When the data was created")
    
    class Config:
        from_attributes = True


# Feedback schemas
class FeedbackBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's name")
    email: EmailStr = Field(..., description="User's email address")
    message: str = Field(..., min_length=10, max_length=1000, description="User's feedback message")


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    message: str = Field(..., description="Success message")
    feedback_id: int = Field(..., description="ID of the created feedback")
    
    class Config:
        from_attributes = True