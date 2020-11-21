from src.utils import is_absolute_url


class TestIsUrl:
    def test_valid_http_urls(self):
        assert is_absolute_url("http://test.fr")
        assert is_absolute_url("http://test.fr/")
        assert is_absolute_url("http://sub.test.fr")
        assert is_absolute_url("http://sub.test.fr/")

    def test_valid_https_urls(self):
        assert is_absolute_url("https://google.com")
        assert is_absolute_url("https://google.com/")
        assert is_absolute_url("https://sub.google.com")
        assert is_absolute_url("https://sub.google.com/")

    def test_valid_http_urls_with_path(self):
        assert is_absolute_url("http://test.fr/path")
        assert is_absolute_url("http://test.fr/path/anotherdir")
        assert is_absolute_url("http://test.fr/path/anotherdir.html")
        assert is_absolute_url("http://sub.test.fr/path")
        assert is_absolute_url("http://sub.test.fr/path/anotherdir.html")

    def test_valid_https_urls_with_path(self):
        assert is_absolute_url("https://test.fr/path")
        assert is_absolute_url("https://test.fr/path/anotherdir")
        assert is_absolute_url("https://test.fr/path/anotherdir.html")
        assert is_absolute_url("https://sub.test.fr/path")
        assert is_absolute_url("https://sub.test.fr/path/anotherdir.html")

    def test_not_valid_urls(self):
        assert not is_absolute_url("test.fr/path")
        assert not is_absolute_url("./test.fr/path/anotherdir")
        assert not is_absolute_url("../../test.fr/path/anotherdir.html")
        assert not is_absolute_url("/sub.test.fr/path")
        assert not is_absolute_url("test.png")
        assert not is_absolute_url(".test.ini")
