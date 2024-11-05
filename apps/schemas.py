import re
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.functional_validators import AfterValidator


def check_password(password: str) -> str:
    assert len(password) >= 8, "Password is sholter than 8 characters"
    assert not re.search(
        r"[а-яА-Я]", password
    ), "Password must contain only English letters"
    return password


Password = Annotated[str, AfterValidator(check_password)]


class Token(BaseModel):
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    email: EmailStr


class CreateUser(User):
    password: Password


class UserResponse(User):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UpdateUser(BaseModel):
    email: str | None = None
    password: str | None = None


class TagsCreate(BaseModel):
    name: str


class TagsResponse(TagsCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Image(BaseModel):
    title: str
    file_path: str
    data: datetime
    resolution: str
    size: int


@dataclass
class ImageCreate:
    resolutions: list[str] = Form(...)
    tags: list[int] = Form(...)


class ImageResponse(Image):
    id: int
    tags: list[TagsResponse]
    model_config = ConfigDict(from_attributes=True)


class ImageUpdate(BaseModel):
    title: str | None = None
    tags: list[int] | None = None
