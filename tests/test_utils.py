import pytest
from src.utils.misc import (is_absolute_url, list_to_nested_dicts,
                            merge_nested_dicts)


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


class TestListToNestedDicts:
    def test_one_element(self):
        keys, value = [1], None

        nested_dicts = list_to_nested_dicts(keys, value)

        assert nested_dicts == {1: None}

    def test_multiple_elements(self):
        keys, value = range(10), None

        nested_dicts = list_to_nested_dicts(keys, value)

        assert nested_dicts == {0: {1: {2: {3: {4: {5: {6: {7: {8: {9: None}}}}}}}}}}

    def test_not_subscriptable_type(self):
        keys, value = (i for i in range(10)), None

        with pytest.raises(TypeError):
            list_to_nested_dicts(keys, value)

    def test_unhashable_type(self):
        keys, value = [[1, 2, 3], [4, 5, 6], [7, 8, 9]], None

        with pytest.raises(TypeError, match="unhashable type: 'list'"):
            list_to_nested_dicts(keys, value)

    def test_empty_list(self):
        keys, value = [], None

        with pytest.raises(IndexError):
            list_to_nested_dicts(keys, value)


class TestMergeNestedDicts:
    def test_simple_dicts(self):
        a = {1: 2}
        b = {3: 4}

        merged_dict = merge_nested_dicts(a, b)

        assert merged_dict == {1: 2, 3: 4}

    def test_empty_dicts(self):
        a = dict()
        b = dict()

        merged_dict = merge_nested_dicts(a, b)

        assert merged_dict == dict()

    def test_a_empty(self):
        a = dict()
        b = {3: {4: {5: 6, 7: 8}}}

        merged_dict = merge_nested_dicts(a, b)

        assert merged_dict == {3: {4: {5: 6, 7: 8}}}

    def test_b_empty(self):
        a = {1: {2: {3: 4, 5: 6}}}
        b = dict()

        merged_dict = merge_nested_dicts(a, b)

        assert merged_dict == {1: {2: {3: 4, 5: 6}}}

    def test_same_dicts(self):
        a = {1: {2: {3: 4, 5: 6}}}
        b = {1: {2: {3: 4, 5: 6}}}

        merged_dict = merge_nested_dicts(a, b)

        assert merged_dict == {1: {2: {3: 4, 5: 6}}}

    def test_b_override_a_values(self):
        a = {1: 2, 3: {4: 5, 6: 7}, 8: 9}
        b = {1: 2, 3: {4: 10, 6: 7}}

        merged_dict = merge_nested_dicts(a, b)

        assert merged_dict == {1: 2, 3: {4: 10, 6: 7}, 8: 9}
