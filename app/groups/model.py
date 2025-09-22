from pydantic import BaseModel

# Group create schema
class GroupCreate(BaseModel):
    name: str
    description: str | None = None
    members: list[str] = []
