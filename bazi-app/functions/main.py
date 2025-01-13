# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app

# initialize_app()
#
#
# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     return https_fn.Response("Hello world!")


from fastapi import FastAPI, HTTPException
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from bazi import get_ymdh_current, get_ymdh_base

app = FastAPI()

class BaziResponse(BaseModel):
    year_pillar: dict
    month_pillar: dict
    day_pillar: dict
    hour_pillar: dict
    datetime: str

def format_bazi_data(bazi_data) -> dict:
    """Convert bazi data into a structured dictionary"""
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

@app.get("/api/bazi/current")
async def get_current_bazi(
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = None
):
    """
    Get current Bazi calculation for a given datetime

    Parameters:
    - year: Year (e.g., 2024)
    - month: Month (1-12)
    - day: Day (1-31)
    - hour: Hour in 24-hour format (0-23, optional)
    """
    try:
        # If hour is not provided, use current hour
        if hour is None:
            hour = datetime.now().hour

        # Validate input date
        input_date = datetime(year, month, day, hour)

        # Get bazi calculation
        bazi_data = bazi.get_ymdh_current(year, month, day, hour)

        # Format response
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
    """
    Get base Bazi calculation for a given datetime

    Parameters:
    - year: Year (e.g., 2024)
    - month: Month (1-12)
    - day: Day (1-31)
    - hour: Hour in 24-hour format (0-23, optional)
    """
    try:
        # If hour is not provided, use current hour
        if hour is None:
            hour = datetime.now().hour

        # Validate input date
        input_date = datetime(year, month, day, hour)

        # Get bazi calculation
        bazi_data = bazi.get_ymdh_base(year, month, day, hour)

        # Format response
        response = BaziResponse(
            **format_bazi_data(bazi_data),
            datetime=input_date.isoformat()
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Bazi: {str(e)}")