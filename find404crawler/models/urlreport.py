"""Contains models and functions related to a report on a single unique URL."""

from typing import Any


class LinkInfo:
    """Information about a link on a page."""

    def __init__(self, url: str, in_scope: bool):
        self.url = url
        self.in_scope = in_scope

    def to_dict(self) -> dict:
        """Return a dictionary representation of this LinkInfo."""
        return {"url": self.url, "in-scope": self.in_scope}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LinkInfo":
        """Create a LinkInfo from a dictionary."""
        return cls(url=data["url"], in_scope=data["in-scope"])


class URLReport:
    """A report on a single unique URL."""

    def __init__(self, url: str):
        self.url = url
        self.links: dict[str, LinkInfo] = {}

    def add_link(self, url: str, in_scope: bool) -> None:
        """Append a link to the report."""
        assert url not in self.links
        self.links[url] = LinkInfo(url=url, in_scope=in_scope)

    def to_dict(self) -> dict:
        """Return a dictionary representation of this URLReport."""
        return {
            "url": self.url,
            "links": {key: value.to_dict() for key, value in self.links.items()},
        }
