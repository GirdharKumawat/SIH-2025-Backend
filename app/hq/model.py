from pydantic import BaseModel

class GroupModel(BaseModel):
    name: str
    members: list[str]

class AddMembersModel(BaseModel):
    members: list[str]
