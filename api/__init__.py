from fastapi import APIRouter
from .routes import router as main_router
from .scheduled_leaderboard_api import router as scheduled_leaderboard_router

router = APIRouter()
router.include_router(main_router)
router.include_router(scheduled_leaderboard_router, prefix="/scheduled")
