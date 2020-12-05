import json
from abc import ABC, abstractmethod
from enum import Enum, unique
from glob import glob
from json.decoder import JSONDecodeError
from typing import Any, ClassVar, Dict, List, Optional

import frontmatter
from markdown import markdown
from markdownify import markdownify
from path import Path
from toml.decoder import TomlDecodeError
from yaml.scanner import ScannerError

from . import Post, PostPublisher


class PostDecodeError(ValueError):
    pass


@unique
class ContentFormats(Enum):
    MARKDOWN = [
        ".md",
    ]


class IPostCodec(ABC):
    CONTENT_FORMATS: ClassVar[List[ContentFormats]]

    def __init__(self, postsdir, ignore_globs: Optional[List[str]] = None):
        self.postsdir = postsdir
        self.ignore_globs = ignore_globs if ignore_globs else list()

    @abstractmethod
    def _get_post(self, metadata: Dict[str, Any], partial_dict: Dict[str, Any]) -> Post:
        ...

    def load(self, filepath: Path) -> Post:
        try:
            metadata, content = frontmatter.parse(filepath.read_text(encoding="utf-8"))
        except TomlDecodeError as e:
            raise PostDecodeError(f"Error in TOML Frontmatter: {e}")
        except ScannerError as e:
            raise PostDecodeError(f"Error in YAML Frontmatter: {e}")
        except JSONDecodeError as e:
            raise PostDecodeError(f"Error in JSON Frontmatter: {e}")

        if not metadata:
            raise PostDecodeError("Frontmatter not found.")
        if not content:
            raise PostDecodeError("Content not found.")

        post_publisher = metadata.get("post_publisher") or dict()

        return self._get_post(
            metadata,
            {
                "filepath": filepath,
                "post_publisher": PostPublisher(**post_publisher),
                "content": markdown(content),
            },
        )

    def dump_app_data(self, modified_post: Post) -> None:
        post = frontmatter.load(modified_post.filepath, encoding="utf-8")

        post.metadata["post_publisher"] = post.post_publisher.dict()

        frontmatter.dump(post, modified_post.filepath)

    def is_publishable(self, path: Path) -> bool:
        files_to_ignore = []
        for glob_pattern in self.ignore_globs:
            for filepath in glob(self.postsdir / glob_pattern, recursive=True):
                files_to_ignore.append(Path(filepath).abspath())

        return path.abspath() not in files_to_ignore

    def dump(self, post: Post) -> None:
        metadata = json.loads(post.json(exclude={"canonical_url", "filepath"}))

        content = markdownify(metadata.pop("content"))

        frontmatter_post = frontmatter.Post(content, **metadata)

        frontmatter.dump(frontmatter_post, post.filepath, encoding="utf-8")

    def is_post(self, path: Path) -> bool:
        if path.exists() and path.isfile():
            return any(path.ext in cf.value for cf in self.CONTENT_FORMATS)
        else:
            return False


class PostCodec(IPostCodec):
    CONTENT_FORMATS = [
        ContentFormats.MARKDOWN,
    ]

    def _get_post(self, metadata: Dict[str, Any], partial_dict: Dict[str, Any]) -> Post:
        try:
            return Post(
                is_draft=metadata["is_draft"],
                title=metadata["title"],
                tags=metadata["tags"],
                categories=metadata["categories"],
                **partial_dict,
            )
        except KeyError as e:
            raise PostDecodeError(f"'{e}' key is missing.")


class HugoPostCodec(IPostCodec):
    CONTENT_FORMATS = [
        ContentFormats.MARKDOWN,
    ]

    def _get_post(self, metadata: Dict[str, Any], partial_dict: Dict[str, Any]) -> Post:
        try:
            return Post(
                is_draft=metadata["is_draft"],
                title=metadata["title"],
                tags=metadata["tags"],
                categories=metadata["categories"],
                **partial_dict,
            )
        except KeyError as e:
            raise PostDecodeError(f"'{e}' key is missing.")
