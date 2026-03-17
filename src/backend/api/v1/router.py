"""Routeur principal API v1."""

from fastapi import APIRouter

from api.v1.sites import router as sites_router
from api.v1.inspections import router as inspections_router
from api.v1.flights import router as flights_router
from api.v1.processing import router as processing_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(sites_router, prefix="/sites", tags=["sites"])
api_router.include_router(inspections_router, prefix="/inspections", tags=["inspections"])
api_router.include_router(flights_router, prefix="/flights", tags=["flights"])
api_router.include_router(processing_router, prefix="/processing", tags=["processing"])
