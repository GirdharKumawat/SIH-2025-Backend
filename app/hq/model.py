from pydantic import BaseModel
from typing import Optional

class GroupModel(BaseModel):
    name: str
    members: Optional[list[str]]

class AddMembersModel(BaseModel):
    members: list[str]
