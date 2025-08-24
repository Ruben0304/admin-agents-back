# Routers for specific assistants
from .suncar_router import router as suncar_router
from .moneytracker_router import router as moneytracker_router

__all__ = ["suncar_router", "moneytracker_router"] 