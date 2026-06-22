from fastapi import FastAPI
from app.routes import (book,
                        user_profile,
                        users,user_actions)

app = FastAPI(
    title='Book search service',
    version="0.1.0"
)
app.include_router(book.router)
app.include_router(users.router)
app.include_router(user_profile.router)
app.include_router(user_actions.router)

@app.get('/')
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {'message': "Все работает можно тестить другое :)"}
