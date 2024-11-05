from fastapi import FastAPI

from api import image_router, tags_router, user_router


app = FastAPI()

app.include_router(image_router)
app.include_router(user_router)
app.include_router(tags_router)
