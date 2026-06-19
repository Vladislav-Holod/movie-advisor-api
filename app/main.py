from fastapi import FastAPI
from app.routes import (book,
                        users,
                        profile)

app = FastAPI(
    title='Book search service',
    version="0.1.0"
)
app.include_router(book.router)
app.include_router(users.router)
app.include_router(profile.router)

@app.get('/')
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {'message': "Все работает можно тестить другое :)"}
