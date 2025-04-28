# listener.py
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import logging
import os

# Basic logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Push Listener")

@app.post("/receive_push") # You can change this path if needed
async def handle_push(request: Request):
    """
    Endpoint to catch incoming push notifications (POST requests with JSON).
    It logs the received payload and returns a success message.
    """
    source_ip = request.client.host
    logger.info(f"Received POST request on /receive_push from {source_ip}")

    try:
        # Check content type header (optional but good practice)
        content_type = request.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            logger.warning(f"Received request with unexpected Content-Type: {content_type}")
            # Decide if you want to reject or still try parsing
            # For simplicity here, we'll still try parsing

        # Get and parse the JSON body
        payload = await request.json()

        logger.info("Successfully parsed JSON payload.")

        # Print the payload to the console (nicely formatted)
        print("\n✅ --- Payload Received --- ✅")
        print(json.dumps(payload, indent=2))
        print("----------------------------\n")

        # Send back a simple success response
        return JSONResponse(
            content={
                "status": "success",
                "message": "Received and logged payload.",
                "source_ip": source_ip
            },
            status_code=200
        )

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from request body.")
        # Optionally, log the raw body if possible/needed for debugging
        # raw_body = await request.body()
        # logger.debug(f"Raw body: {raw_body.decode(errors='ignore')}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload received.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """Basic GET endpoint to confirm the listener is running."""
    logger.info("Received GET request on /")
    return {"message": "Simple Push Listener is alive. Send POST requests with JSON data to /receive_push"}

if __name__ == "__main__":
    # Use environment variable for port or default to 9999
    listen_port = int(os.getenv("LISTENER_PORT", 9999))
    # Listen on 0.0.0.0 to be accessible from other containers/machines on the network
    # Use localhost (127.0.0.1) if you only want it accessible from the same machine
    listen_host = os.getenv("LISTENER_HOST", "0.0.0.0")

    print("-------------------------------------------")
    logger.info(f"🚀 Starting Simple Push Listener...")
    logger.info(f"👂 Listening on: http://{listen_host}:{listen_port}")
    logger.info(f"👉 Send POST requests to: http://<listener_ip>:{listen_port}/receive_push")
    logger.info("   (Use localhost or 127.0.0.1 if running agent on the same machine)")
    logger.info("   (Use machine's local IP if agent is on another machine/container)")
    print("-------------------------------------------")

    # Run the Uvicorn server
    uvicorn.run(app, host=listen_host, port=listen_port)