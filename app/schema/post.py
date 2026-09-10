from __future__ import annotations

from typing import Optional, List, Annotated

from fastapi import Form
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .category import CategoryPublic
from .tag import Tag
from ..auth.schemas import UserPublic


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)
    user: Optional[UserPublic] = None
    image_url: Optional[str] = None
    category: Optional[CategoryPublic] = None

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Title of the post (3-100 characters)",
        examples=[
            "My First Post"
        ]
    )
    content: Optional[str] = Field(
        default="Value for content",
        min_length=10,
        description="Content of the post (at least 10 characters)",
        examples=[
            "This is the updated content of the post."
        ]
    )
    category_id: Optional[int] = None
    tags: List["Tag"] = Field(
        default_factory=list,
        description="List of tags associated with the post")

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("Title cannot contain the word 'spam'")
        return value

    @classmethod
    def as_form(
            cls,
            title: Annotated[str, Form(min_length=3)],
            content: Annotated[str, Form(min_length=10)],
            category_id: Annotated[int, Form(ge=1)],
            tags: Annotated[Optional[List[str]], Form()] = None
    ):
        tag_objs = [Tag(name=tag) for tag in (tags or [])]
        return cls(title=title, content=content, category_id=category_id, tags=tag_objs)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int
    slug: str

    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)
