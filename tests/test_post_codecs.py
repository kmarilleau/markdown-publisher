import pytest
from path import Path

from src.post_codecs import (
    ContentFormats,
    Post,
    PostCodec,
    PostDecodeError,
    PostPublisher,
)


@pytest.fixture
def expected_post(scope="function"):
    return Post(
        filepath=Path(),
        post_publisher=PostPublisher(),
        title="My First Post",
        canonical_url=None,
        content="<h1>Content</h1><p>paragraph</p>",
        tags=frozenset(["tag1", "tag2"]),
        categories=frozenset(["cat1", "cat2"]),
        is_draft=True,
    )


class TestPostCodec:
    def test_dump_load_post(self, tmpdir, expected_post):
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = (postsdir / "test_post.md").touch()
        expected_post.filepath = filepath

        codec = PostCodec(postsdir=postsdir)

        codec.dump(expected_post)

        test_post = codec.load(filepath)

        assert test_post == expected_post
        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)

    def test_file_not_found(self, tmpdir, expected_post):
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"
        expected_post.filepath = filepath

        codec = PostCodec(postsdir=postsdir)

        assert not codec.is_post(filepath)
        assert codec.is_publishable(filepath)

        with pytest.raises(FileNotFoundError):
            codec.dump_app_data(expected_post)

        with pytest.raises(FileNotFoundError):
            codec.load(filepath)

    def test_file_is_as_directory(self, tmpdir, expected_post):
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = (postsdir / "test_post").mkdir()
        expected_post.filepath = filepath

        codec = PostCodec(postsdir=postsdir)

        assert not codec.is_post(filepath)
        assert codec.is_publishable(filepath)

        with pytest.raises(IsADirectoryError):
            codec.dump_app_data(expected_post)

        with pytest.raises(IsADirectoryError):
            codec.load(filepath)

    def test_post_is_not_publishable(self, tmpdir):
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        (postsdir / "otherdir").mkdir()
        (postsdir / "otherdir/bar").mkdir()
        file_not_publishable_1 = (postsdir / "otherdir/foo.md").touch()
        file_publishable_1 = (postsdir / "otherdir/bar/spam.md").touch()
        file_publishable_2 = (postsdir / "publishable.md").touch()

        codec = PostCodec(postsdir=postsdir, ignore_globs=["otherdir/*"])

        assert not codec.is_publishable(file_not_publishable_1)
        assert codec.is_publishable(file_publishable_1)
        assert codec.is_publishable(file_publishable_2)

    def test_file_formats(self, tmpdir, expected_post):
        tmpdir = Path(tmpdir)
        for ext in [*ContentFormats.MARKDOWN.value]:
            postsdir = (tmpdir / "posts").mkdir()
            filepath = postsdir / f"test_post{ext}"
            expected_post.filepath = filepath

            codec = PostCodec(postsdir=postsdir)

            codec.dump(expected_post)
            test_post = codec.load(filepath)

            err_msg = f"Error with '{ext}' file extension: test_post != EXPECTED_POST\n"
            for field_a, field_b in zip(test_post, expected_post):
                err_msg += f"test_post.{field_a[0]} = {field_a[1]};"
                err_msg += f" EXPECTED_POST.{field_b[0]} = {field_b[1]};\n"

            assert test_post == expected_post, err_msg
            assert codec.is_post(filepath)
            assert codec.is_publishable(filepath)

    def test_invalid_frontmatter_data(self, tmpdir):
        invalid_post = """---
invalid_var: false
foo: 0
---
# Test

paragraph
"""
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"

        filepath.write_text(invalid_post, encoding="utf-8")

        codec = PostCodec(postsdir=postsdir)

        with pytest.raises(PostDecodeError, match=r"'.+' key is missing."):
            codec.load(filepath)

        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)

    def test_error_frontmatter_separators(self, tmpdir):
        invalid_post = """+++
invalid: {}
test_post == 0
---
        # Test
        """
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"

        filepath.write_text(invalid_post, encoding="utf-8")

        codec = PostCodec(postsdir=postsdir)

        with pytest.raises(PostDecodeError, match="Frontmatter not found."):
            codec.load(filepath)

        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)

    def test_no_frontmatter(self, tmpdir):
        invalid_post = "# Test"
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"

        filepath.write_text(invalid_post, encoding="utf-8")

        codec = PostCodec(postsdir=postsdir)

        with pytest.raises(PostDecodeError, match="Frontmatter not found."):
            codec.load(filepath)

        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)

    def test_frontmatter_toml_decode_error(self, tmpdir):
        invalid_post = """+++
title: Test
is_draft = true
+++
"""
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"

        filepath.write_text(invalid_post, encoding="utf-8")

        codec = PostCodec(postsdir=postsdir)

        with pytest.raises(PostDecodeError, match=r"Error in TOML Frontmatter.*"):
            codec.load(filepath)

        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)

    def test_frontmatter_yaml_decode_error(self, tmpdir):
        invalid_post = """---
title: Test
is_draft = true
---
"""
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"

        filepath.write_text(invalid_post, encoding="utf-8")

        codec = PostCodec(postsdir=postsdir)

        with pytest.raises(PostDecodeError, match=r"Error in YAML Frontmatter.*"):
            codec.load(filepath)

        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)

    def test_frontmatter_json_decode_error(self, tmpdir):
        invalid_post = """{
    "title": "Test",
    "is_draft" = true
}
"""
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"

        filepath.write_text(invalid_post, encoding="utf-8")

        codec = PostCodec(postsdir=postsdir)

        with pytest.raises(PostDecodeError, match=r"Error in JSON Frontmatter.*"):
            codec.load(filepath)

        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)

    def test_no_content(self, tmpdir):
        invalid_post = """+++
title = "Test"
is_draft = true
+++
"""
        tmpdir = Path(tmpdir)
        postsdir = (tmpdir / "posts").mkdir()
        filepath = postsdir / "test_post.md"

        filepath.write_text(invalid_post, encoding="utf-8")

        codec = PostCodec(postsdir=postsdir)

        with pytest.raises(PostDecodeError, match="Content not found."):
            codec.load(filepath)

        assert codec.is_post(filepath)
        assert codec.is_publishable(filepath)
