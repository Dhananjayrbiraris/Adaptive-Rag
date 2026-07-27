"""
Main FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.config.settings import settings
from backend.database.mongo_client import client as mongo_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Adaptive RAG API...")
    
    # Validate settings
    if not settings.validate_settings():
        logger.error("Critical settings validation failed")
        raise ValueError("Configuration validation failed")
    
    # Test MongoDB connection
    try:
        await mongo_client.admin.command('ping')
        logger.info("MongoDB connection verified")
    except Exception as e:
        logger.warning(f"MongoDB connection test failed: {e}")
    
    app.state.description_ = ""
    logger.info("Adaptive RAG API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Adaptive RAG API...")
    mongo_client.close()
    logger.info("MongoDB connection closed")


app = FastAPI(
    title="Adaptive RAG API",
    description="RAG-based question answering system with adaptive retrieval",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint to verify API is running."""
    return {
        "message": "Adaptive RAG API is running",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "adaptive-rag-api"
    }
