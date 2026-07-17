from fastapi import APIRouter

from app.presentation.api.user_auth import router as user_auth_router
from app.presentation.api.user_profile import router as user_profile_router
from app.presentation.api.user_actions import router as user_actions_router
from app.presentation.api.movie_routers import router as movie_router
from app.presentation.api.movie_recommend import router as movie_recommend_router

router = APIRouter()

router.include_router(user_auth_router)
router.include_router(user_profile_router)
router.include_router(user_actions_router)
router.include_router(movie_router)
router.include_router(movie_recommend_router)