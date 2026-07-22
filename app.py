"""
main.py
-------
FastAPI backend service for Land Boundary Prediction System.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from models import PredictionRequest, PredictionResponse
from predictor import predict_boundaries

app = FastAPI(
    title="Land Boundary AI API",
    description="Backend service for predicting land boundary dimensions.",
    version="1.0.0",
)

# Enable CORS for local Streamlit integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_200_OK)
def health_check() -> dict:
    """Health check endpoint to verify server status."""
    return {"status": "Running"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
)
def predict(payload: PredictionRequest) -> PredictionResponse:
    """
    Predict North, South, East, and West boundary dimensions based on 
    the survey number, area, and optional shape.
    """
    try:
        results = predict_boundaries(
            area_sqft=payload.area_sqft,
            land_shape=payload.land_shape,
        )
        return PredictionResponse(
            survey_no=payload.survey_no,
            area_sqft=payload.area_sqft,
            land_shape=payload.land_shape,
            north_ft=results["north_ft"],
            south_ft=results["south_ft"],
            east_ft=results["east_ft"],
            west_ft=results["west_ft"],
            calculated_area_sqft=results["calculated_area_sqft"],
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during calculation: {str(err)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
