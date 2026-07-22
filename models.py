"""
models.py
---------
Data models and request/response schemas for Land Boundary Prediction API.
"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


LandShapeType = Literal["Square", "Rectangular", "Other / Unknown"]


class PredictionRequest(BaseModel):
    """
    Incoming request schema for boundary prediction.
    """

    survey_no: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Survey number of the land property",
    )

    area_sqft: float = Field(
        ...,
        gt=0,
        description="Total land area in square feet",
    )

    land_shape: LandShapeType = Field(
        default="Other / Unknown",
        description="Shape of the land (Square, Rectangular, or Other / Unknown)",
    )

    @field_validator("survey_no")
    @classmethod
    def validate_survey_number(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Survey number cannot be empty.")
        return cleaned

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "survey_no": "123/4A",
                "area_sqft": 1652,
                "land_shape": "Square",
            }
        }
    )
    def validate_inputs(
    survey_no: str,
    area_sqft: float,
    land_shape: str
    ):
        if land_shape not in [
        "Square",
        "Rectangle",
        "Others / Unknown"
    ]:
            return False, "Please select a valid land shape."

class PredictionResponse(BaseModel):
    """
    Outgoing response schema containing predicted boundaries and calculated metrics.
    """

    survey_no: str = Field(..., description="Survey number of the land property")
    area_sqft: float = Field(..., description="Input total land area in sq.ft")
    land_shape: str = Field(..., description="Selected land shape mode")

    north_ft: float = Field(..., description="Predicted North boundary length in feet")
    south_ft: float = Field(..., description="Predicted South boundary length in feet")
    east_ft: float = Field(..., description="Predicted East boundary length in feet")
    west_ft: float = Field(..., description="Predicted West boundary length in feet")

    calculated_area_sqft: float = Field(
        ..., description="Calculated total land area in sq.ft matching input area"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "survey_no": "123/4A",
                "area_sqft": 1652,
                "land_shape": "Square",
                "north_ft": 40.62,
                "south_ft": 40.35,
                "east_ft": 40.88,
                "west_ft": 40.11,
                "calculated_area_sqft": 1652,
            }
        }
    )