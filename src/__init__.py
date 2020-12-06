from typing import Any, FrozenSet, Optional
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from path import Path
from pydantic import BaseModel, Field, HttpUrl


class PostPublisher(BaseModel):
    class Config:
        extra = "forbid"

    id: UUID = Field(default_factory=uuid4)


class Post(BaseModel):
    class Config:
        extra = "forbid"
        allow_mutation = False

    filepath: Path
    post_publisher: PostPublisher

    title: str
    content: str

    canonical_url: Optional[HttpUrl] = None

    tags: FrozenSet[str]
    categories: FrozenSet[str]

    is_draft: bool

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Post):
            return (
                self.dict(exclude={"content"}) == other.dict(exclude={"content"})
                and BeautifulSoup(self.content, "lxml").prettify()
                == BeautifulSoup(other.content, "lxml").prettify()
            )
        else:
            return self.dict() == other
