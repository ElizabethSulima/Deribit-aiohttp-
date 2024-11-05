import json
from pathlib import Path
from typing import Any, Sequence

import models
import redis
import sqlalchemy as sa
import utils
from celery import Celery
from PIL import Image
from settings import config
from sqlalchemy.orm import Session


celery_app = Celery(
    "crypto", broker=config.rabbit_url, broker_connection_retry_on_startup=True
)
engine = sa.create_engine(config.dsn)  # type:ignore[call-overload]

redis_app = redis.Redis().from_url(config.redis_url)  # type:ignore[arg-type]


def write_tags_to_images(
    session: Session, data: dict[str, Any], tags_list: Sequence[models.Tag]
):
    stmt = sa.insert(models.Image).returning(models.Image).values(**data)
    image = session.scalar(stmt)
    session.flush()
    image.tags = tags_list  # type:ignore[union-attr]
    session.flush()


@celery_app.task
def image_convertor(dict_str: str):  # pylint:disable=R0914
    dict_ = json.loads(dict_str)
    media_dir = Path(dict_["media_dir"])
    file_name = dict_["file_name"]
    identifier = dict_["uuid"]

    with Session(engine) as session:
        tags = session.scalars(
            sa.select(models.Tag).where(models.Tag.id.in_(dict_["tags"]))
        )
        tags_list = tags.all()
        image_pillow = Image.open(dict_["media_image"])
        format_ = image_pillow.format

        for resolution in dict_["resolutions"]:
            width, height = resolution.split("x")
            new_image = image_pillow.resize((int(width), int(height)))

            title = f"{file_name}_{width}x{height}"
            file_path = str(media_dir / f"{title}.{format_}")
            new_image.save(file_path)

            dict_image = utils.make_image_data(
                file_path, title, resolution, identifier
            )
            write_tags_to_images(session, dict_image, tags_list)

        image_gray = image_pillow.convert("L")
        file_path = str(media_dir / f"{file_name}_L.{format_}")
        image_gray.save(file_path)
        dict_image = utils.make_image_data(
            file_path,
            f"{file_name}_L",
            "x".join(str(x) for x in image_gray.size),
            identifier,
        )
        write_tags_to_images(session, dict_image, tags_list)
        session.commit()
        redis_app.set(dict_["user_email"], identifier)
