from typing import Any, Awaitable, Callable, Type

import sqlalchemy as sa
from fastapi import HTTPException, status
from models import MODEL, TypeModel, User
from sqlalchemy.engine import ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def create_item(
    session: AsyncSession, model: TypeModel, data: dict[str, Any]
) -> MODEL:
    stmt = sa.insert(model).returning(model).values(**data)
    item = await session.scalar(stmt)
    await session.commit()
    await session.refresh(item)
    return item  # type: ignore


async def get_items(
    session: AsyncSession, model: TypeModel
) -> ScalarResult[MODEL]:
    result = await session.scalars(sa.select(model))
    return result


async def get_item_id(
    session: AsyncSession, model: TypeModel, item_id: int
) -> MODEL:
    stmt = sa.select(model).where(model.id == item_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found",
        )
    return result


async def update_item(
    session: AsyncSession,
    model: TypeModel,
    data: dict[str, Any],
) -> MODEL:
    item_id = data.pop("id")
    stmt = (
        sa.update(model)
        .returning(model)
        .where(model.id == item_id)
        .values(**data)
    )
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found",
        )
    await session.commit()
    await session.refresh(result)
    return result


async def create_or_update_user(
    session: AsyncSession,
    model: Type[User],
    data: dict[str, Any],
    callback: Callable[
        [AsyncSession, Type[User], dict[str, Any]], Awaitable[User]
    ],
) -> User:
    try:
        result = await callback(session, model, data)
    except IntegrityError as err:
        if "ix_users_email" in err.orig.args[0]:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with {data['email']} already exist",
            ) from err
        raise err

    return result


async def get_user(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(sa.select(User).where(User.email == email))
