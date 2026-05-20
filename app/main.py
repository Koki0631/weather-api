from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.logging_config import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import auth, favorites, weather
from app.seed import seed_test_user

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_test_user()
    yield


app = FastAPI(
    title="Weather API",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(auth.router)
app.include_router(favorites.router)
app.include_router(weather.router)
