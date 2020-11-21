from urllib.parse import urlparse


def is_absolute_url(maybe_url: str) -> bool:
    url_parsed = urlparse(maybe_url)

    return all([url_parsed.scheme, url_parsed.netloc])
