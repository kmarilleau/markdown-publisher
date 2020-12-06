import pytest
import requests_cache
from path import Path

from src import Post, PostPublisher

requests_cache.install_cache()


@pytest.fixture
def expected_post(scope="function"):
    return Post(
        filepath=Path("/workdir/postsdir/post.md"),
        post_publisher=PostPublisher(),
        title="My First Post",
        canonical_url=None,
        content="<h1>Content</h1><p>paragraph</p>",
        tags=frozenset(["tag1", "tag2"]),
        categories=frozenset(["cat1", "cat2"]),
        is_draft=True,
    )
