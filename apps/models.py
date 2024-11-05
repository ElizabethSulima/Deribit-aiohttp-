import uuid
from datetime import datetime
from typing import Type, TypeVar

import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, MetaData, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%"
            "(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


MODEL = TypeVar("MODEL", bound=Base)

TypeModel = Type[MODEL]

image_tags = Table(
    "image_tags",
    Base.metadata,
    Column("image_id", ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(
        sa.String(length=50), unique=True, index=True
    )


class Image(Base):
    __tablename__ = "images"
    # pylint:disable=E1136
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    file_path: Mapped[str]
    # pylint:disable=E1102
    data: Mapped[datetime] = mapped_column(server_default=sa.func.now())
    resolution: Mapped[str]
    size: Mapped[int]
    uuid: Mapped[uuid.UUID]
    tags: Mapped[list["Tag"]] = relationship(
        secondary=image_tags, lazy="selectin", cascade="all, delete"
    )


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
