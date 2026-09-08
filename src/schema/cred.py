from pydantic import BaseModel


class CredentialCreate(BaseModel):
    name: str
    type: str
    username: str
    password: str
    host: str
    port: int


class CredentialUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None


class CredentialResponse(BaseModel):
    id: int
    name: str
    type: str
    username: str
    host: str
    port: int

    class Config:
        from_attributes = True