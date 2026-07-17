from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.core.config import settings
from app.infrastructure.database.session import async_engine
from app.presentation.api import router as api_router

logger.add(
    "info.log",
    format="Log: [{extra[log_id]}:{time} - {level} - {message}]",
    level="INFO",
    enqueue=True,
)

logger = logger.bind(log_id="system")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for the API"""
    logger.info('Starting API_Main')
    yield
    await async_engine.dispose()
    logger.info('Database engine disposed')


app = FastAPI(
    title='Cinema search service',
    version=settings.APP_VERSION,
    redirect_slashes=False,
    lifespan=lifespan,
)
app.include_router(api_router, prefix="/api/v1")

app.mount(
    "/profile_images",
    StaticFiles(directory="profile_images"),
    name="profile_images",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get('/')
async def root():
    """Корневой маршрут, подтверждающий, что API работает."""
    return {'message': "Все работает можно тестить другое :)"}