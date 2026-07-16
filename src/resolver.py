from __future__ import annotations

import asyncio
import socket
import uuid


class DNSResolver:
    def __init__(self, concurrency: int = 80):
        self._semaphore = asyncio.Semaphore(concurrency)

    async def lookup(self, host: str) -> list[str]:
        async with self._semaphore:
            return await asyncio.to_thread(self._lookup_sync, host)

    async def wildcard_ips(self, domain: str, checks: int = 3) -> set[str]:
        ips: set[str] = set()
        for _ in range(checks):
            random_host = f"{uuid.uuid4().hex}.{domain}"
            ips.update(await self.lookup(random_host))
        return ips

    def _lookup_sync(self, host: str) -> list[str]:
        try:
            records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except socket.gaierror:
            return []
        ips = {record[4][0] for record in records if record and record[4]}
        return sorted(ips)
