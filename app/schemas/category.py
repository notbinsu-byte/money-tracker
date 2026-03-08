from pydantic import BaseModel, Field
from typing import Union

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: str = Field(..., pattern="^(expense|income)$")
    icon: str = Field(default="📁", max_length=50)
    color: str = Field(default="#6c757d", max_length=7, pattern="^#[0-9a-fA-F]{6}$")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Union[str, None] = Field(None, max_length=100)
    type: Union[str, None] = Field(None, pattern="^(expense|income)$")
    icon: Union[str, None] = Field(None, max_length=50)
    color: Union[str, None] = Field(None, max_length=7, pattern="^#[0-9a-fA-F]{6}$")

class CategoryResponse(CategoryBase):
    id: int
    is_default: bool

    model_config = {"from_attributes": True}
