from datetime import datetime

from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    city: str = Field(..., description="Requested city name")
    temperature_celsius: float = Field(
        ..., description="Current temperature in Celsius"
    )
    description: str = Field(..., description="Weather condition summary")
    humidity: int = Field(..., ge=0, le=100, description="Relative humidity (%)")
    wind_speed_mps: float = Field(
        ..., ge=0, description="Wind speed in meters per second"
    )


class WeatherHistoryItem(BaseModel):
    id: int = Field(..., description="Database record ID")
    city: str = Field(..., description="City name")
    temperature_celsius: float = Field(
        ..., description="Temperature in Celsius when recorded"
    )
    description: str = Field(..., description="Weather condition summary")
    humidity: int = Field(..., ge=0, le=100, description="Relative humidity (%)")
    wind_speed_mps: float = Field(
        ..., ge=0, description="Wind speed in meters per second"
    )
    created_at: datetime = Field(..., description="When the record was stored")


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, description="User email address")
    password: str = Field(..., min_length=1, description="Plain-text password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(
        default="bearer", description="Token type for Authorization header"
    )


class WeatherHistoryResponse(BaseModel):
    city: str = Field(..., description="City filter applied to the query")
    items: list[WeatherHistoryItem] = Field(
        default_factory=list,
        description="Stored weather records, newest first",
    )
