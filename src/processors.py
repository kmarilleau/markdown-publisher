from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urljoin

from path import Path

from . import Post


class PostProcessingError(ValueError):
    pass


class IProcessor(ABC):
    def __init__(self, baseurl: str, postsdir: Path):
        self.baseurl = baseurl
        self.postsdir = postsdir.abspath()

    @abstractmethod
    def process(self, post: Post) -> Post:
        ...


class ICanonicalURLProcessor(IProcessor):
    @abstractmethod
    def get_absolute_url(self, relpath: Path, _from: Optional[Path] = None) -> str:
        ...

    def process(self, post: Post) -> Post:
        if not post.filepath.startswith(self.postsdir):
            raise PostProcessingError(f"{post.filepath} is not in {self.postsdir}.")

        return Post(
            canonical_url=self.get_absolute_url(relpath=post.filepath),
            **post.dict(exclude={"canonical_url"}),
        )


class BasicPostGetAbsURLMixin(IProcessor):
    def get_absolute_url(self, relpath: Path, _from: Optional[Path] = None) -> str:
        if _from:
            abspath = _from.parent.joinpath(relpath).abspath()
        else:
            abspath = relpath.abspath()

        return urljoin(self.baseurl, self.postsdir.relpathto(abspath))


class BasicPostCanonicalURLProcessor(BasicPostGetAbsURLMixin, ICanonicalURLProcessor):
    pass
