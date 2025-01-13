from firebase_functions import https_fn
from firebase_admin import initialize_app
from fastapi import FastAPI, HTTPException
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app import bazi  # Update this import to match your package structure
import functions_framework
from fastapi.middleware.cors import CORSMiddleware

initialize_app()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Your BaziResponse class and format_bazi_data function remain the same
class BaziResponse(BaseModel):
    year_pillar: dict
    month_pillar: dict
    day_pillar: dict
    hour_pillar: dict
    datetime: str

def format_bazi_data(bazi_data) -> dict:
    return {
        "year_pillar": {
            "heavenly_stem": bazi_data[0],
            "earthly_branch": bazi_data[1],
            "hidden_stems": bazi_data[8]
        },
        "month_pillar": {
            "heavenly_stem": bazi_data[2],
            "earthly_branch": bazi_data[3],
            "hidden_stems": bazi_data[9]
        },
        "day_pillar": {
            "heavenly_stem": bazi_data[4],
            "earthly_branch": bazi_data[5],
            "hidden_stems": bazi_data[10]
        },
        "hour_pillar": {
            "heavenly_stem": bazi_data[6],
            "earthly_branch": bazi_data[7],
            "hidden_stems": bazi_data[11]
        }
    }

# Your endpoint definitions remain the same
@app.get("/api/bazi/current")
async def get_current_bazi(
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = None
):
    try:
        if hour is None:
            hour = datetime.now().hour
        input_date = datetime(year, month, day, hour)
        bazi_data = bazi.get_ymdh_current(year, month, day, hour)
        response = BaziResponse(
            **format_bazi_data(bazi_data),
            datetime=input_date.isoformat()
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Bazi: {str(e)}")

@app.get("/api/bazi/base")
async def get_base_bazi(
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = None
):
    try:
        if hour is None:
            hour = datetime.now().hour
        input_date = datetime(year, month, day, hour)
        bazi_data = bazi.get_ymdh_base(year, month, day, hour)
        response = BaziResponse(
            **format_bazi_data(bazi_data),
            datetime=input_date.isoformat()
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Bazi: {str(e)}")

# Create the Firebase Function handler
@https_fn.on_request()
def bazi_api(req: https_fn.Request) -> https_fn.Response:
    """Handle requests to the Bazi API"""
    import asgiref.wsgi
    wsgi_app = asgiref.wsgi.WsgiToAsgi(app)
    return wsgi_app(req)