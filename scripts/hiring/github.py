"""A small GitHub REST client using only the standard library."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"


class GitHubError(RuntimeError):
    def __init__(self, status: int, method: str, path: str, message: str):
        super().__init__(f"GitHub API {method} {path} failed ({status}): {message}")
        self.status = status


class GitHub:
    def __init__(self, token: str, api: str = API):
        if not token:
            raise ValueError("No GitHub token. Set GH_TOKEN.")
        self.token = token
        self.api = api.rstrip("/")

    def request(self, method: str, path: str, body: dict | None = None,
                accept: str = "application/vnd.github+json", raw: bool = False):
        """Call the API. Returns parsed JSON, raw bytes (raw=True) or None for empty replies."""
        url = path if path.startswith("http") else f"{self.api}{path}"
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(3):
            req = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": accept,
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "recruitment-take-home-pipeline",
                **({"Content-Type": "application/json"} if data else {}),
            })
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    payload = resp.read()
                    self._last_headers = resp.headers
                    if raw:
                        return payload
                    return json.loads(payload) if payload else None
            except urllib.error.HTTPError as err:
                if err.code in (502, 503, 504) and attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                detail = err.read().decode(errors="replace")
                try:
                    detail = json.loads(detail).get("message", detail)
                except ValueError:
                    pass
                raise GitHubError(err.code, method, urllib.parse.urlparse(url).path, detail) from None
        raise AssertionError("unreachable")

    def get(self, path: str, **kw):
        return self.request("GET", path, **kw)

    def exists(self, path: str) -> bool:
        try:
            self.get(path)
            return True
        except GitHubError as err:
            if err.status == 404:
                return False
            raise

    def paginate(self, path: str) -> list:
        """GET every page of a list endpoint."""
        sep = "&" if "?" in path else "?"
        url, items = f"{self.api}{path}{sep}per_page=100", []
        while url:
            items.extend(self.request("GET", url))
            url = _next_link(self._last_headers.get("Link", ""))
        return items


def _next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        if 'rel="next"' in part:
            return part[part.index("<") + 1: part.index(">")]
    return None
