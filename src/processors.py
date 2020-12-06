from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from path import Path

from . import Post
from .utils.misc import is_absolute_url


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
    def get_absolute_url(self, path: Path, _from: Optional[Path] = None) -> str:
        ...

    def process(self, post: Post) -> Post:
        if not post.filepath.startswith(self.postsdir):
            raise PostProcessingError(f"{post.filepath} is not in {self.postsdir}.")

        return Post(
            canonical_url=self.get_absolute_url(path=post.filepath),
            **post.dict(exclude={"canonical_url"}),
        )


class IPathToUrlContentProcessor(IProcessor):
    @abstractmethod
    def get_absolute_url(self, path: Path, _from: Optional[Path] = None) -> str:
        ...

    def process(self, post: Post) -> Post:
        html_tree = BeautifulSoup(post.content, "lxml")

        for tag in html_tree.find_all(href=True):
            if not is_absolute_url(tag["href"]) and not any(
                tag["href"].startswith(pattern) for pattern in ("tel:", "mailto:", "#")
            ):
                tag["href"] = self.get_absolute_url(
                    path=Path(tag["href"]), _from=post.filepath
                )

        for tag in html_tree.find_all(src=True):
            if not is_absolute_url(tag["src"]):
                tag["src"] = self.get_absolute_url(
                    path=Path(tag["src"]), _from=post.filepath
                )

        return Post(
            content=html_tree.body.prettify(), **post.dict(exclude={"content"}),
        )


class BasicPostGetAbsURLMixin(IProcessor):
    def get_absolute_url(self, path: Path, _from: Optional[Path] = None) -> str:
        if path.isabs():
            abspath = path
        elif _from:
            if path == ".":
                abspath = _from
            else:
                abspath = _from.parent.joinpath(path).abspath()
        else:
            abspath = path.abspath()

        return urljoin(self.baseurl, self.postsdir.relpathto(abspath)).rstrip("/")


class BasicPostCanonicalURLProcessor(BasicPostGetAbsURLMixin, ICanonicalURLProcessor):
    pass


class BasicPostPathToUrlContentProcessor(
    BasicPostGetAbsURLMixin, IPathToUrlContentProcessor
):
    pass
