"""
DataPurify FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import auth, clean, database, export, scan, upload, visualize

app = FastAPI(
    title="DataPurify API",
    description="Intelligent Data Analysis, Purification, & Visualization Platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during dev/test, use CORS_ORIGINS in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(database.router)
app.include_router(scan.router)
app.include_router(clean.router)
app.include_router(visualize.router)
app.include_router(export.router)


@app.get("/")
async def root():
    return {
        "app": "DataPurify API",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
