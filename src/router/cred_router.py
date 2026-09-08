from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db

from src.schema.cred import (
    CredentialCreate,
    CredentialUpdate,
    CredentialResponse,
)

from src.service.cred_service import (
    create_credential,
    get_credentials,
    get_credential,
    update_credential,
    delete_credential,
)


router = APIRouter(
    prefix="/credentials",
    tags=["Credentials"],
)


@router.post(
    "",
    response_model=CredentialResponse,
)
async def create(
    request: CredentialCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_credential(
        db=db,
        request=request,
    )


@router.get(
    "",
    response_model=list[CredentialResponse],
)
async def get_all(
    db: AsyncSession = Depends(get_db),
):
    return await get_credentials(db=db)


@router.get(
    "/{credential_id}",
    response_model=CredentialResponse,
)
async def get_one(
    credential_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_credential(
        db=db,
        credential_id=credential_id,
    )


@router.put(
    "/{credential_id}",
    response_model=CredentialResponse,
)
async def update(
    credential_id: int,
    request: CredentialUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_credential(
        db=db,
        credential_id=credential_id,
        request=request,
    )


@router.delete(
    "/{credential_id}",
)
async def delete(
    credential_id: int,
    db: AsyncSession = Depends(get_db),
):
    await delete_credential(
        db=db,
        credential_id=credential_id,
    )

    return {
        "message": "Credential deleted successfully."
    }