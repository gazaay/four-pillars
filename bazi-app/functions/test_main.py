import json
import logging
from firebase_functions import https_fn
from firebase_admin import initialize_app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize Firebase app
initialize_app()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Remove async since we're not using FastAPI's async features here
@app.get("/hello")
def hello(name: str = "World"):
    logger.debug(f"Received request with name: {name}")
    return {"message": f"Hello, {name}!"}

# Remove async from the Firebase function
@https_fn.on_request()
def hello_api(req: https_fn.Request) -> https_fn.Response:
    """Handle requests to the Hello API"""
    logger.debug("Received request to hello_api function")
    logger.debug(f"Request path: {req.path}")

    try:
        # Simple path routing
        if "/hello" in req.path:
            name = req.args.get('name', 'World')
            response_data = {"message": f"Hello, {name}!"}
            return https_fn.Response(
                json.dumps(response_data),
                status=200,
                headers={'Content-Type': 'application/json'}
            )
        else:
            return https_fn.Response(
                json.dumps({"error": "Not found"}),
                status=404,
                headers={'Content-Type': 'application/json'}
            )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={'Content-Type': 'application/json'}
        )