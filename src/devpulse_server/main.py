from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger
import asyncio
from devpulse_server.database.connection import create_tables, drop_tables, async_engine, Base
from devpulse_server.api.credentials.router import router as credentials_router
from devpulse_server.api.ingest.router import router as ingest_router

from devpulse_server.logger.logger_setup import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup: Create all tables
    setup_logger()
    logger.info("Creating database tables...")
    await create_tables()
    logger.info("Database tables created successfully")
    logger.info("Server connection established")

    yield  # Application runs here
    
    # Example: Drop tables asynchronously
    await drop_tables()
    # Uncomment to drop tables on shutdown:
    # asyncio.run(_drop())

    await async_engine.dispose()

    logger.info("Database engine disposed")


app = FastAPI(lifespan=lifespan)
app.include_router(credentials_router)
app.include_router(ingest_router)


@app.get("/")
def root() -> dict:
    """Root endpoint for the API."""
    return {"message": "Welcome to DevPulse API"}


@app.get("/health")
def health() -> dict:
    """Health check endpoint for the API."""
    return {"message": "OK"}


def main() -> None:
    """Entrypoint for devpulse-server CLI."""
    uvicorn.run("devpulse_server.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
