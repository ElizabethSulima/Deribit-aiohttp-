from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from settings import config

from api import image_router, tags_router, user_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    config.MEDIA_DIR.mkdir(exist_ok=True)
    application.mount(
        "/media", StaticFiles(directory=config.MEDIA_DIR), name="media"
    )

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(image_router)
app.include_router(user_router)
app.include_router(tags_router)
