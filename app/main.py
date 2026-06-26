from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from uuid import uuid4
from app.routes import (movie_routers,
                        user_profile,
                        user_auth, user_actions,movie_recomend)

app = FastAPI(
    title='Cinema search service',
    version="0.1.1",redirect_slashes=False
)

logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue=True)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info('Successfully accessed ' + request.url.path)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response


# CORS конфигурация
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
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
app.include_router(movie_recomend.router)

@app.get('/')
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {'message': "Все работает можно тестить другое :)"}
