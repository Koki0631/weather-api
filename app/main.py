from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Weather API",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(weather.router)
