import pytest
from path import Path

from src import Post
from src.processors import BasicPostCanonicalURLProcessor, PostProcessingError

URL = "https://test.fr"


class TestBasicPostCanonicalURLProcessor:
    def test_post_in_postsdir(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        post = Post(filepath=filepath, **post.dict(exclude={"filepath"}))

        processor = BasicPostCanonicalURLProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert (
            processed_post.canonical_url
            == f"{URL}/{postsdir.relpathto(processed_post.filepath)}"
        )

    def test_post_in_subdirs(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "subdir/anothersubdir/post.md"
        post = Post(filepath=filepath, **post.dict(exclude={"filepath"}))

        processor = BasicPostCanonicalURLProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert (
            processed_post.canonical_url
            == f"{URL}/{postsdir.relpathto(processed_post.filepath)}"
        )

    def test_post_not_in_postsdir(self, post):
        postsdir = Path("/workdir/postsdir")
        filepath = Path("/workdir/anotherdir/post.md")
        post = Post(filepath=filepath, **post.dict(exclude={"filepath"}))

        processor = BasicPostCanonicalURLProcessor(baseurl=URL, postsdir=postsdir)

        with pytest.raises(
            PostProcessingError, match=f"{post.filepath} is not in {postsdir}."
        ):
            processor.process(post)

    def test_relative_postsdir(self, post):
        postsdir = Path("workdir/postsdir")
        filepath = (postsdir / "subdir/anothersubdir/post.md").abspath()
        post = Post(filepath=filepath, **post.dict(exclude={"filepath"}))

        processor = BasicPostCanonicalURLProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert (
            processed_post.canonical_url
            == f"{URL}/{postsdir.relpathto(processed_post.filepath)}"
        )
