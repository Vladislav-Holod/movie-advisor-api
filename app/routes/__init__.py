from fastapi import APIRouter

from app.routes.movie_recomend import router as movie_recommend_router
from app.routes.movie_routers import router as movie_router
from app.routes.user_actions import router as user_actions_router
from app.routes.user_profile import router as user_profile_router
from app.routes.user_auth import router as user_auth_router

router = APIRouter(prefix ='/api/v1')
router.include_router(movie_recommend_router)
router.include_router(movie_router)
router.include_router(user_actions_router)
router.include_router(user_profile_router)
router.include_router(user_auth_router)