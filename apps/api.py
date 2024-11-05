import json
import os
from datetime import timedelta
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import crud
import fastapi as fa
import models
import schemas
import sqlalchemy as sa
from celery_app import image_convertor, redis_app
from dependency import AsyncSessionDepency, GetCurrentUser, get_current_user
from security import authenticate_user, create_access_token, get_password_hash
from settings import config
from utils import write_file


user_router = fa.APIRouter(prefix="/users", tags=["users"])
image_router = fa.APIRouter(prefix="/images", tags=["images"])
tags_router = fa.APIRouter(prefix="/tags", tags=["tags"])


@user_router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    session: AsyncSessionDepency,
    data: schemas.UserLogin,
):
    user = await authenticate_user(session, **data.model_dump())
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        {"user_email": user.email}, access_token_expires
    )
    return schemas.Token(token=access_token)


@user_router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=fa.status.HTTP_201_CREATED,
)
async def create_user(
    session: AsyncSessionDepency, user_data: schemas.CreateUser
):
    data = user_data.model_dump()
    data["password"] = get_password_hash(data["password"])
    result = await crud.create_or_update_user(
        session, models.User, data, crud.create_item
    )
    return result


@tags_router.post(
    "/",
    response_model=schemas.TagsResponse,
    status_code=fa.status.HTTP_201_CREATED,
)
async def create_tags(
    session: AsyncSessionDepency, tags_data: schemas.TagsCreate
):
    data = tags_data.model_dump()
    return await crud.create_item(session, models.Tag, data)


@image_router.get(
    "/",
    response_model=list[schemas.ImageResponse],
    dependencies=[fa.Depends(get_current_user)],
)
async def get_images(session: AsyncSessionDepency):
    return await session.scalars(sa.select(models.Image))


@image_router.post("/", response_class=fa.responses.JSONResponse)
async def create_image(
    image_data: Annotated[schemas.ImageCreate, fa.Depends()],
    image: Annotated[fa.UploadFile, fa.File()],
    user: GetCurrentUser,
):
    file_name = Path(image.filename).stem  # type:ignore[arg-type]
    identifier = str(uuid4())
    media_dir_image = config.MEDIA_DIR / identifier
    media_dir_image.mkdir()
    media_image = write_file(
        image.filename,  # type:ignore[arg-type]
        await image.read(),
        media_dir_image,
    )
    dict_ = image_data.__dict__
    dict_.update(
        {
            "media_dir": str(media_dir_image),
            "media_image": media_image,
            "file_name": file_name,
            "user_email": user.email,
            "uuid": identifier,
        }
    )
    image_convertor.delay(json.dumps(dict_))
    return fa.responses.JSONResponse(
        content="Create image", status_code=fa.status.HTTP_201_CREATED
    )


@image_router.get("/result/", response_model=list[schemas.ImageResponse])
async def get_result(session: AsyncSessionDepency, user: GetCurrentUser):
    identifier = redis_app.get(user.email)
    stmt = sa.select(models.Image).where(models.Image.uuid == identifier)
    images = await session.scalars(stmt)
    return images


@image_router.patch("/{image_id}/", response_model=schemas.ImageResponse)
async def update_images(
    image_id: int,
    data_image: schemas.ImageUpdate,
    session: AsyncSessionDepency,
):
    image: models.Image = await crud.get_item_id(
        session, models.Image, image_id
    )
    data = data_image.model_dump(exclude_unset=True)
    if "tags" in data:
        tags = data.pop("tags")
        tags_set = set(tags).difference(set(tag.id for tag in image.tags))
        tags_list = await session.scalars(
            sa.select(models.Tag).where(models.Tag.id.in_(tags_set))
        )
        tags_all = tags_list.all()
        for tag in tags_all:
            image.tags.append(tag)
    if len(data.keys()) > 0:
        data["id"] = image_id
        await crud.update_item(session, models.Image, data)
    await session.commit()
    await session.refresh(image)
    return image


@image_router.delete("/{image_id}/", response_class=fa.responses.JSONResponse)
async def delete_images(image_id: int, session: AsyncSessionDepency):
    image: models.Image = await crud.get_item_id(
        session, models.Image, image_id
    )
    if image.file_path:
        os.remove(image.file_path)

    await session.execute(
        sa.delete(models.Image).filter(
            image.id == image_id  # type:ignore[arg-type]
        )
    )
    await session.commit()
    return fa.responses.JSONResponse(
        content="Image delete", status_code=fa.status.HTTP_200_OK
    )
