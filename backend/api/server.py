"""
backend/api/server.py
---------------------
Main entry point for the FastAPI application.
Initialises the router, CORS, and background tasks (Kafka consumer).
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.api.routes import manager
from backend.streaming.kafka_consumer import consume_events

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI app.
    Starts the Kafka consumer background task on startup,
    and cancels it on shutdown.
    """
    logger.info("Starting up FastAPI server. Launching Kafka consumer task...")
    
    # Run the Kafka consumer in the background, passing the WebSocket
    # broadcast method as a callback to send events to clients.
    consumer_task = asyncio.create_task(consume_events(broadcast_callback=manager.broadcast))
    
    yield  # Let the FastAPI app run
    
    logger.info("Shutting down FastAPI server. Cancelling Kafka consumer task...")
    consumer_task.cancel()
    # Wait briefly for task to clean up
    try:
        await asyncio.wait_for(consumer_task, timeout=3.0)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        pass


app = FastAPI(
    title="Real-Time Anomaly Detection API",
    description="Backend API for streaming anomalies and system metrics.",
    version="1.0.0",
    lifespan=lifespan
)

# Allow CORS for Next.js frontend (assuming it runs on port 3000 locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # In production, restrict to actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Real-Time Anomaly Detection API is running."}
