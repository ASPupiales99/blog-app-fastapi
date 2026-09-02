from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class Author(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Name of the author (3-50 characters)",
        examples=[
            "John Doe",
            "Jane Smith"
        ]
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Email of the author",
        examples=[
            "john.doe@example.com",
            "jane.smith@example.com"
        ]
    )

    model_config = ConfigDict(from_attributes=True)
