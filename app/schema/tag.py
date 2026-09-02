from pydantic import BaseModel, Field, ConfigDict


class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Name of the tag (1-30 characters)",
        examples=[
            "Python",
            "FastAPI"
        ]
    )

    model_config = ConfigDict(from_attributes=True)
