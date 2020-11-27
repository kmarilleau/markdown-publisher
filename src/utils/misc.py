from typing import Any, Dict, Sequence
from urllib.parse import urlparse


def is_absolute_url(maybe_url: str) -> bool:
    url_parsed = urlparse(maybe_url)

    return all([url_parsed.scheme, url_parsed.netloc])


def list_to_nested_dicts(keys: Sequence[Any], value: Any) -> Dict[Any, Any]:

    if len(keys) > 1:
        return {keys[0]: list_to_nested_dicts(keys[1:], value)}
    else:
        return {keys[0]: value}


def merge_nested_dicts(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            merge_nested_dicts(a[key], b[key])
        else:
            a[key] = b[key]

    return a
