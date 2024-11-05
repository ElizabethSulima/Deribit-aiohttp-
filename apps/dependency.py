from typing import Annotated, AsyncIterator

import jwt
import models
import schemas
from crud import get_user
from fastapi import Depends, security, status
from fastapi.exceptions import HTTPException
from jwt.exceptions import InvalidTokenError
from settings import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


async def get_async_session() -> AsyncIterator[AsyncSession]:
    # pylint: disable=C0301
    async with AsyncSession(create_async_engine(config.async_dsn)) as session:  # type: ignore
        yield session


AsyncSessionDepency = Annotated[
    AsyncSession, Depends(get_async_session, use_cache=True)
]


async def get_current_user(
    token: Annotated[
        security.HTTPAuthorizationCredentials, Depends(security.HTTPBearer())
    ],
    session: AsyncSessionDepency,
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token.credentials,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
        )
        email: str = payload.get("user_email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError as err:
        raise credentials_exception from err
    user = await get_user(session, email)
    if user is None:
        raise credentials_exception
    return user


GetCurrentUser = Annotated[schemas.UserResponse, Depends(get_current_user)]
