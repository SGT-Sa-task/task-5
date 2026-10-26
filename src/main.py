"""FastAPI application entrypoint for Odoo CRM Integration."""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import leads

app = FastAPI(
    title="SaigonTrade Odoo CRM API",
    description="RESTful API service to integrate CRM Lead data into Odoo ERP.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(leads.router, prefix="/api")


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Health Check",
    description="Check whether the API service is alive and healthy.",
)
def health_check() -> dict[str, str]:
    """Return service health status.

    Returns:
        dict[str, str]: Service status information.
    """
    return {
        "status": "healthy",
        "service": "SaigonTrade Odoo CRM API",
        "version": "1.0.0",
    }


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Root Endpoint",
    description="Service greeting and link to interactive documentation.",
)
def root() -> dict[str, str]:
    """Return welcome message and documentation link.

    Returns:
        dict[str, str]: Welcome message and docs URL.
    """
    return {
        "message": "Welcome to SaigonTrade Odoo CRM API",
        "docs_url": "/docs",
        "health_check": "/health",
    }
