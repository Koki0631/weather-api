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
