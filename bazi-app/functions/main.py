import logging
from firebase_functions import https_fn
from firebase_admin import initialize_app
from fastapi import FastAPI, HTTPException
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict
from bazi import bazi
import functions_framework
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
import json
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import sys
import os

# Add the parent directory to sys.path to import yijing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from bazi.yijing import phone_to_hexagram_json
    YIJING_AVAILABLE = True
    logging.info("Successfully imported yijing module")
except ImportError as e:
    YIJING_AVAILABLE = False
    logging.error(f"Failed to import yijing module: {str(e)}")

# Set version
VERSION = "1.0.1"

initialize_app()
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Log version when function starts
# logger.info(f"Bazi package version: {__version__}")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PillarData(BaseModel):

    stems: str
    hidden_stems: str
    combined: Optional[str] = None
    combined_hidden: Optional[str] = None
    harmed: Optional[str] = None
    harmed_hidden: Optional[str] = None
    clashed: Optional[str] = None
    clashed_hidden: Optional[str] = None
    fan: Optional[str] = None
    fan_hidden: Optional[str] = None

class DayunData(BaseModel):
    stem: str
    branch: str
    chinese: str
    starting_age: float

class SiyunData(BaseModel):
    stem: str
    branch: str
    chinese: str
    starting_age: float

class BaziResponse(BaseModel):
    year_pillar: PillarData
    month_pillar: PillarData
    day_pillar: PillarData
    hour_pillar: PillarData
    datetime: str
    dayun: Optional[List[DayunData]] = None
    siyun: Optional[List[SiyunData]] = None
    
def format_bazi_data(bazi_data: Dict[str, str]) -> dict:
    """Convert bazi data dictionary into a structured response."""
    logger.info(f"Formatting bazi data: {bazi_data}")

    try:
        return {
            "year_pillar" : {
                "stems": bazi_data.get("年", ""),
                "hidden_stems": bazi_data.get("-年", ""),
                "combined": bazi_data.get("合年", ""),
                "combined_hidden": bazi_data.get("-合年", ""),
                "harmed": bazi_data.get("害年", ""),
                "harmed_hidden": bazi_data.get("-害年", ""),
                "clashed": bazi_data.get("破年", ""),
                "clashed_hidden": bazi_data.get("-破年", ""),
                "fan": bazi_data.get("反年", ""),
                "fan_hidden": bazi_data.get("-反年", "")
            },
            "month_pillar": {
                "stems": bazi_data.get("月", ""),
                "hidden_stems": bazi_data.get("-月", ""),
                "combined": bazi_data.get("合月", ""),
                "combined_hidden": bazi_data.get("-合月", ""),
                "harmed": bazi_data.get("害月", ""),
                "harmed_hidden": bazi_data.get("-害月", ""),
                "clashed": bazi_data.get("破月", ""),
                "clashed_hidden": bazi_data.get("-破月", ""),
                "fan": bazi_data.get("反月", ""),
                "fan_hidden": bazi_data.get("-反月", "")
            },
            "day_pillar": {
                "stems": bazi_data.get("日", ""),
                "hidden_stems": bazi_data.get("-日", ""),
                "combined": bazi_data.get("合日", ""),
                "combined_hidden": bazi_data.get("-合日", ""),
                "harmed": bazi_data.get("害日", ""),
                "harmed_hidden": bazi_data.get("-害日", ""),
                "clashed": bazi_data.get("破日", ""),
                "clashed_hidden": bazi_data.get("-破日", ""),
                "fan": bazi_data.get("反日", ""),
                "fan_hidden": bazi_data.get("-反日", "")
            },
            "hour_pillar": {
                "stems": bazi_data.get("時", ""),
                "hidden_stems": bazi_data.get("-時", ""),
                "combined": bazi_data.get("合時", ""),
                "combined_hidden": bazi_data.get("-合時", ""),
                "harmed": bazi_data.get("害時", ""),
                "harmed_hidden": bazi_data.get("-害時", ""),
                "clashed": bazi_data.get("破時", ""),
                "clashed_hidden": bazi_data.get("-破時", ""),
                "fan": bazi_data.get("反時", ""),
                "fan_hidden": bazi_data.get("-反時", "")
            },
            "dayun": bazi_data.get("大運", []),  # Add the 大運 section directly
            "siyun": bazi_data.get("時運", [])  # Add the 時運 section directly
        }
    except Exception as e:
        logger.error(f"Error formatting bazi data: {e}")
        raise ValueError(f"Error formatting bazi data: {e}")

# @app.get("/api/bazi/current")
def get_current_bazi(
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = 9
):
    try:
        logger.debug(f"Calculating current bazi for {year}-{month}-{day} {hour}")

        if hour is None:
            hour = datetime.now().hour

        input_date = datetime(year, month, day, hour)
        bazi_data = bazi.get_ymdh_current(year, month, day, hour)

        logger.info(f"Received bazi data: {bazi_data}")
        formatted_data = format_bazi_data(bazi_data)
        logger.info(f"Formatted data: {formatted_data}")

        response = BaziResponse(
            **formatted_data,
            datetime=input_date.isoformat()
        )
        data = json.loads(response.model_dump_json())
        return json.dumps(data, ensure_ascii = False, indent=2)
        # .dumps(data, ensure_ascii=False, indent=2)
        # return JSONResponse(
        #     content=response.model_dump(),
        #     headers={'Content-Type': 'application/json; charset=utf-8'},
        #     media_type='application/json'
        # )  
        # return response
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating Bazi: {str(e)}")

# @app.get("/api/bazi/base")
def get_base_bazi(
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = 9
):
    try:
        logger.info(f"Calculating base bazi for {year}-{month}-{day} {hour}")

        if hour is None:
            hour = datetime.now().hour

        input_date = datetime(year, month, day, hour)
        bazi_data = bazi.get_ymdh_base(year, month, day, hour)

        logger.info(f"Received bazi data: {bazi_data}")
        formatted_data = format_bazi_data(bazi_data)
        logger.info(f"Formatted data: {formatted_data}")

        response = BaziResponse(
            **formatted_data,
            datetime=input_date.isoformat()
        )
        data = json.loads(response.model_dump_json())
        return json.dumps(data, ensure_ascii = False, indent=2)
        # return JSONResponse(
        #     content=jsonable_encoder(response),
        #     headers={'Content-Type': 'application/json; charset=utf-8'},
        #     media_type='application/json'
        # )   
        # return response
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating Bazi: {str(e)}")

# @app.get("/api/bazi/wuxi")
def get_wuxi_data(
    year: int,
    month: int,
    day: int,
    hour: Optional[int] = 9
):
    try:
        logger.debug(f"Calculating wuxi data for {year}-{month}-{day} {hour}")

        if hour is None:
            hour = datetime.now().hour

        input_date = datetime(year, month, day, hour)
        wuxi_data = bazi.get_complete_wuxi_data(year, month, day, hour)

        logger.debug(f"Received wuxi data: {wuxi_data}")

        # Return the raw wuxi data as JSON
        return json.dumps(wuxi_data, ensure_ascii=False, indent=2)

    except ValueError as e:
        logger.error(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating Wuxi data: {str(e)}")

def get_phone_yijing(phone_number: str):
    """
    Get the Yi Jing hexagram for a Hong Kong phone number.
    
    Args:
        phone_number: An 8-digit Hong Kong phone number
        
    Returns:
        JSON with the hexagram information
    """
    if not YIJING_AVAILABLE:
        error_result = {
            "success": False,
            "error": "Yi Jing module not available"
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    try:
        logger.debug(f"Looking up Yi Jing hexagram for phone number: {phone_number}")
        result = phone_to_hexagram_json(phone_number)
        logger.debug(f"Yi Jing result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing phone number: {str(e)}")
        error_result = {
            "success": False,
            "phone_number": phone_number,
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

def validate_datetime_params(year: int, month: int, day: int, hour: int) -> None:
    if not (1900 <= year <= 2100):  # adjust range as needed
        raise ValueError("Year must be between 1900 and 2100")
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")
    if not (1 <= day <= 31):
        raise ValueError("Day must be between 1 and 31")
    if not (0 <= hour <= 23):
        raise ValueError("Hour must be between 0 and 23")

# from asgiref.wsgi import WsgiToAsgi
from fastapi.middleware.wsgi import WSGIMiddleware

@https_fn.on_request()
def api_handler(req: https_fn.Request) -> https_fn.Response:
    """Handle all API requests"""
    logger.debug(f"Received request: {req.path}")
    logger.info(f"Successfully imported bazi version")

    try:
        # Route to FastAPI endpoints
        if "/hello" in req.path:
            name = req.args.get('name', 'World')
            response_data = {"message": f"Hello, {name}!"}
        elif "/bazi_test" in req.path:
            year = int(req.args.get('year', 2023))
            month = int(req.args.get('month', 1))
            day = int(req.args.get('day', 1))
            hour = int(req.args.get('hour', 0))
            response_data = {"bazi": f"Year: {year}, Month: {month}, Day: {day}, Hour: {hour}"}
        elif "/api/bazi/base" in req.path:
            year = int(req.args.get('year', 2023))
            month = int(req.args.get('month', 1))
            day = int(req.args.get('day', 1))
            hour = int(req.args.get('hour', 0))
            bazi_response = get_base_bazi(year, month, day, hour)
            response_data = bazi_response
        elif "/api/bazi/current" in req.path:
            year = int(req.args.get('year', 2023))
            month = int(req.args.get('month', 1))
            day = int(req.args.get('day', 1))
            hour = int(req.args.get('hour', 0))
            bazi_response = get_current_bazi(year, month, day, hour)
            response_data = bazi_response
        elif "/api/bazi/wuxi" in req.path:
            year = int(req.args.get('year', 2023))
            month = int(req.args.get('month', 1))
            day = int(req.args.get('day', 1))
            hour = int(req.args.get('hour', 0))
            logger.info(f"Calculating wuxi data for {year}-{month}-{day} {hour}")
            wuxi_response = get_wuxi_data(year, month, day, hour)
            response_data = wuxi_response
        elif "/api/yijing/phone" in req.path:
            phone_number = req.args.get('phone', '')
            logger.info(f"Looking up Yi Jing hexagram for phone number: {phone_number}")
            yijing_response = get_phone_yijing(phone_number)
            # Since yijing_response is already a JSON string, we need to parse it
            response_data = json.loads(yijing_response)
        elif "/api/version" in req.path:
            response_data = {
                "version": VERSION,
                "timestamp": datetime.now().isoformat(),
                "environment": "production"
            }
        else:
            response_data = {"error": "Not found"}
            return https_fn.Response(
                json.dumps(response_data),
                status=404,
                headers={'Content-Type': 'application/json'}
            )

        return https_fn.Response(
            json.dumps(response_data),
            status=200,
            headers={'Content-Type': 'application/json; charset=utf-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",}
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={'Content-Type': 'application/json'}
        )