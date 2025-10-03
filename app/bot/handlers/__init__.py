# Purpose: Bot handlers module.

from .start import router as start_router
from .tasks import router as tasks_router  
from .admin import router as admin_router
from .webapp import webapp_router

__all__ = ["start_router", "tasks_router", "admin_router", "webapp_router"]