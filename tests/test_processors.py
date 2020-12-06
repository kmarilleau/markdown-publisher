import pytest
from bs4 import BeautifulSoup
from path import Path

from src import Post
from src.processors import (
    BasicPostCanonicalURLProcessor,
    BasicPostPathToUrlContentProcessor,
    PostProcessingError,
)

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


class TestBasicPostPathToUrlContentProcessor:
    def test_abspath(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        path = "/absolute/path/image.png"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=URL + path)

    def test_no_trailing_slash(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        path = "/absolute/path/trailing_slash/"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=URL + path.rstrip("/"))

    def test_relpath_to_itself(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        post = Post(
            filepath=filepath,
            content=content.format(path="."),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=f"{URL}/{filepath.name}")

    def test_href_tag(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        path = "test.html"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=f"{URL}/{path}")

    def test_src_tag(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<audio src="{path}">', "lxml").body.prettify()
        path = "test.mp3"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=f"{URL}/{path}")

    def test_relpath_to_baseurl(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        post = Post(
            filepath=filepath,
            content=content.format(path="/"),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=URL)

    def test_no_relpath(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup(
            """
<a href="https://google.com/test">Test</a>
<div>
    <img src="http://test.fr/path/image.jpeg">
    <p>https://github.com/post<p>
    <p>../workdir/subdir/posts.md<p>
    Download src="test/dir/file.html"
    <ul>
      <li><a href="https://example.com">Website</a></li>
      <li><a href="mailto:m.bluth@example.com">Email</a></li>
      <li><a href="tel:+123456789">Phone</a></li>
      <li><a href="#"></a></li>
      <li><a href="#test">Anchor</a></li>
    </ul>
</div>
<audio src="ftp://google.com/test">Test</a>
<video src="https://google.com/test.mp4">./post.md</a>
""",
            "lxml",
        ).body.prettify()
        post = Post(
            filepath=filepath,
            content=content,
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content

    def test_relpath_from_subdir_post(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "subdir1/post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        path = "anotherfile.html"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=f"{URL}/subdir1/{path}")

    def test_current_dir_relpath(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        path = "./anotherfile.html"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=f"{URL}/{path[2:]}")

    def test_relpath_to_subdir_file(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        path = "subdir1/anotherfile.html"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=f"{URL}/{path}")

    def test_relpath_to_file_in_parent_folder(self, post):
        postsdir = Path("/postsdir")
        filepath = postsdir / "subdir1/subdir2/post.md"
        content = BeautifulSoup('<a href="{path}">Test</a>', "lxml").body.prettify()
        path = "../test.html"
        post = Post(
            filepath=filepath,
            content=content.format(path=path),
            **post.dict(exclude={"filepath", "content"}),
        )

        processor = BasicPostPathToUrlContentProcessor(baseurl=URL, postsdir=postsdir)
        processed_post = processor.process(post)

        assert processed_post.content == content.format(path=f"{URL}/subdir1/test.html")
