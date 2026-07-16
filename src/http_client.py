from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request


class HTTPError(RuntimeError):
    pass


class HTTPClient:
    def __init__(self, timeout: int = 20, concurrency: int = 12):
        self.timeout = timeout
        self._semaphore = asyncio.Semaphore(concurrency)

    async def text(self, url: str, headers: dict[str, str] | None = None) -> str:
        async with self._semaphore:
            return await asyncio.to_thread(self._text_sync, url, headers or {})

    async def json(self, url: str, headers: dict[str, str] | None = None):
        body = await self.text(url, headers=headers)
        return json.loads(body)

    def _text_sync(self, url: str, headers: dict[str, str]) -> str:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "subscope/0.1 (+authorized asset discovery)",
                "Accept": "*/*",
                **headers,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            raise HTTPError(f"{url} returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise HTTPError(f"{url} failed: {exc.reason}") from exc
