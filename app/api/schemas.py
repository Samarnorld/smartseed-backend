# app/api/schemas.py
"""
Pydantic validation models for all API endpoints.
Provides strict input validation and type safety.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from enum import Enum


# ============ Common Validators ============

class GeoJSONGeometry(BaseModel):
    """Validate GeoJSON geometry objects."""
    type: str = Field(..., pattern="^(Point|Polygon|MultiPolygon|Feature|FeatureCollection)$")
    coordinates: Optional[List] = None
    geometry: Optional[Dict] = None
    features: Optional[List] = None
    
    @field_validator("coordinates", mode="before")
    def validate_coordinates(cls, v, info):
        geo_type = info.data.get("type")
        if geo_type not in ("Feature", "FeatureCollection"):
            if v is None:
                raise ValueError("coordinates required for this geometry type")
        return v
    
    model_config = ConfigDict(extra="forbid")  # Reject unknown fields


# ============ Rainfall Endpoints ============

class RainfallAnalysisRequest(BaseModel):
    """Validate rainfall analysis requests."""
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")
    
    @field_validator("start_date")
    def validate_start_date(cls, v):
        min_date = date(1981, 1, 1)
        if v < min_date:
            raise ValueError("start_date must be >= 1981-01-01")
        return v
    
    @field_validator("end_date")
    def validate_end_date(cls, v):
        today = date.today()
        if v > today:
            raise ValueError("end_date cannot be in the future")
        return v
    
    @field_validator("end_date")
    def validate_date_range(cls, v, info):
        if info.data.get("start_date") is not None and v < info.data.get("start_date"):
            raise ValueError("end_date must be after start_date")
        return v
    
    model_config = ConfigDict(extra="forbid")


class RainfallAnnualRequest(BaseModel):
    """Validate annual rainfall requests."""
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    year: int = Field(..., ge=1981, le=2100)
    
    model_config = ConfigDict(extra="forbid")


# ============ NDVI Endpoints ============

class NDVIAnalysisRequest(BaseModel):
    """Validate NDVI analysis requests."""
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    start_year: int = Field(..., ge=1981, le=2100)
    end_year: int = Field(..., ge=1981, le=2100)
    
    @field_validator("end_year")
    def validate_year_range(cls, v, info):
        if info.data.get("start_year") is not None and v < info.data.get("start_year"):
            raise ValueError("end_year must be >= start_year")
        return v
    
    model_config = ConfigDict(extra="forbid")


# ============ Temperature Endpoints ============

class TemperatureRequest(BaseModel):
    """Validate temperature requests."""
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    start_date: date = Field(default_factory=lambda: date(2024, 1, 1))
    end_date: date = Field(default_factory=lambda: date(2024, 12, 31))
    
    @field_validator("end_date")
    def validate_end_date(cls, v):
        today = date.today()
        if v > today:
            raise ValueError("end_date cannot be in the future")
        return v
    
    @field_validator("end_date")
    def validate_date_range(cls, v, info):
        if info.data.get("start_date") is not None and v < info.data.get("start_date"):
            raise ValueError("end_date must be after start_date")
        return v
    
    model_config = ConfigDict(extra="forbid")


# ============ Soil Analysis ============

class SoilDepthEnum(str, Enum):
    SHALLOW = "0-20cm"
    MEDIUM = "20-50cm"
    DEEP = "50-100cm"


class SoilAnalysisRequest(BaseModel):
    """Validate soil analysis requests."""
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    depth: SoilDepthEnum = Field(default=SoilDepthEnum.SHALLOW)
    
    model_config = ConfigDict(extra="forbid")


# ============ Location Endpoints ============

class LocationRequest(BaseModel):
    """Validate location queries."""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    
    model_config = ConfigDict(extra="forbid")


# ============ Nandi Recommendations ============

class SeasonEnum(str, Enum):
    LONG_RAINS = "LongRains"
    SHORT_RAINS = "ShortRains"


class NandiPixelRequest(BaseModel):
    """Validate pixel-level nandi recommendations."""
    lon: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)
    season: SeasonEnum = Field(...)
    
    model_config = ConfigDict(extra="forbid")


class NandiWardRequest(BaseModel):
    """Validate ward-level nandi recommendations."""
    ward_name: str = Field(..., min_length=1, max_length=100)
    season: SeasonEnum = Field(...)
    
    model_config = ConfigDict(extra="forbid")


class NandiCountyRequest(BaseModel):
    """Validate county-level nandi recommendations."""
    season: SeasonEnum = Field(...)
    
    model_config = ConfigDict(extra="forbid")


# ============ Maize Suitability ============

class MaizeSuitabilityRequest(BaseModel):
    """Validate maize suitability requests."""
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    year: int = Field(..., ge=2000, le=2100)
    season: SeasonEnum = Field(...)
    
    model_config = ConfigDict(extra="forbid")


class MaizeTimeseriesRequest(BaseModel):
    """Validate maize timeseries requests."""
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    start_year: int = Field(..., ge=2000, le=2100)
    end_year: int = Field(..., ge=2000, le=2100)
    season: SeasonEnum = Field(...)
    
    @field_validator("end_year")
    def validate_year_range(cls, v, info):
        if info.data.get("start_year") is not None and v < info.data.get("start_year"):
            raise ValueError("end_year must be >= start_year")
        return v
    
    model_config = ConfigDict(extra="forbid")


# ============ Account Deletion ============

class DeleteAccountRequest(BaseModel):
    """Validate account deletion confirmation."""
    token: str = Field(..., min_length=20, max_length=500)
    
    model_config = ConfigDict(extra="forbid")


# ============ USSD ============

class USSDRequest(BaseModel):
    """Validate USSD requests."""
    sessionId: str = Field(..., min_length=1, max_length=100)
    phoneNumber: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    text: str = Field(..., max_length=500)
    
    model_config = ConfigDict(extra="forbid")


# ============ Boundaries ============

class CountyRequest(BaseModel):
    """Validate county boundary requests."""
    county: str = Field(..., min_length=1, max_length=100)
    
    @field_validator("county")
    def validate_county(cls, v):
        allowed = ["nandi"]
        if v.lower() not in allowed:
            raise ValueError(f"County must be one of: {', '.join(allowed)}")
        return v
    
    model_config = ConfigDict(extra="forbid")
