from pydantic import BaseModel, Field


class StoreContent(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=2000)
    welcome_message: str = Field(min_length=1, max_length=500)
    about_us: str = Field(min_length=1, max_length=2000)
    categories: list[str] = Field(default_factory=list, max_length=20)
    theme: str = Field(default="modern", max_length=50)