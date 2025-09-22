from pydantic import BaseModel, Field 
from typing import Optional

class GroupModel(BaseModel):
    name: str = Field(..., example="Group A")
    members_id: Optional[list[str]] = Field(default=[], example=["user_id_1", "user_id_2"])

class AddMembersModel(BaseModel):
    members_id: list[str] = Field(..., example=["68d1101e5f759ee5b8186525", "68d1147241b456c064c56fa6"])
     