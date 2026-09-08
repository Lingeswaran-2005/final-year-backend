from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.model import Credential
from src.schema.cred import (
    CredentialCreate,
    CredentialUpdate,
    CredentialResponse,
)
from src.core.exceptions import AppException
from src.db.database import get_session


async def create_credential(
    db: AsyncSession,
    request: CredentialCreate,
) -> Credential:

    credential = Credential(
        name=request.name,
        type=request.type,
        username=request.username,
        password=request.password,
        host=request.host,
        port=request.port,
    )

    db.add(credential)

    await db.commit()
    await db.refresh(credential)

    return credential


async def get_credentials(
    db: AsyncSession,
) -> list[Credential]:

    result = await db.execute(
        select(Credential)
        .order_by(Credential.created_at.desc())
    )

    return list(result.scalars().all())


async def get_credential(
    db: AsyncSession,
    credential_id: int,
) -> Credential:

    result = await db.execute(
        select(Credential)
        .where(Credential.id == credential_id)
    )

    credential = result.scalar_one_or_none()

    if credential is None:
        raise AppException(
            message="Credential not found.",
            status_code=404,
        )

    return credential


async def update_credential(
    db: AsyncSession,
    credential_id: int,
    request: CredentialUpdate,
) -> Credential:

    credential = await get_credential(
        db=db,
        credential_id=credential_id,
    )

    update_data = request.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(credential, field, value)

    credential.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(credential)

    return credential


async def delete_credential(
    db: AsyncSession,
    credential_id: int,
) -> None:

    credential = await get_credential(
        db=db,
        credential_id=credential_id,
    )

    await db.delete(credential)

    await db.commit()
    

async def get_credential_by_name(
    name: str,
) -> Credential:

    async with get_session() as db:

        result = await db.execute(
            select(Credential)
            .where(Credential.name == name)
        )

        credential = result.scalar_one_or_none()

        if credential is None:
            raise AppException(
                message=f"Credential '{name}' not found.",
                status_code=404,
            )

        return credential