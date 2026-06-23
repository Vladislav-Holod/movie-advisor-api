from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (movie_routers,
                        user_profile,
                        user_auth, user_actions)

app = FastAPI(
    title='Cinema search service',
    version="0.1.1"
)

# CORS конфигурация
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],  # Для локальной разработки
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(movie_routers.router)
app.include_router(user_auth.router)
app.include_router(user_profile.router)
app.include_router(user_actions.router)

@app.get('/')
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {'message': "Все работает можно тестить другое :)"}
