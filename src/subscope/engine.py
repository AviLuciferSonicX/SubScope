from __future__ import annotations

import asyncio
from collections.abc import Iterable

from .http import HTTPClient
from .models import Candidate, Finding
from .normalize import in_scope, normalize_domain
from .resolver import DNSResolver
from .sources import DEFAULT_SOURCES, Source


class Enumerator:
    def __init__(
        self,
        sources: Iterable[Source] = DEFAULT_SOURCES,
        timeout: int = 20,
        max_time: int = 120,
        http_concurrency: int = 12,
        dns_concurrency: int = 80,
    ):
        self.sources = list(sources)
        self.timeout = timeout
        self.max_time = max_time
        self.http = HTTPClient(timeout=timeout, concurrency=http_concurrency)
        self.resolver = DNSResolver(concurrency=dns_concurrency)

    async def run(self, domain: str, resolve: bool = False) -> tuple[list[Finding], dict[str, str]]:
        domain = normalize_domain(domain)
        findings: dict[str, Finding] = {}
        errors: dict[str, str] = {}

        async def run_source(source: Source) -> list[Candidate]:
            return await source.enumerate(domain, self.http)

        tasks = {asyncio.create_task(run_source(source)): source.name for source in self.sources}
        done, pending = await asyncio.wait(tasks, timeout=self.max_time)
        for task in pending:
            task.cancel()
            errors[tasks[task]] = "timed out"

        for task in done:
            source_name = tasks[task]
            try:
                candidates = task.result()
            except Exception as exc:  # source failure should not kill the run
                errors[source_name] = str(exc)
                continue
            self._merge(findings, candidates, domain)

        if resolve:
            await self._resolve(domain, findings)

        ordered = sorted(
            findings.values(),
            key=lambda item: (-item.confidence, item.host.count("."), item.host),
        )
        return ordered, errors

    def _merge(self, findings: dict[str, Finding], candidates: Iterable[Candidate], domain: str) -> None:
        for candidate in candidates:
            host = normalize_domain(candidate.host)
            if host == domain or not in_scope(host, domain):
                continue
            finding = findings.setdefault(host, Finding(host=host))
            finding.sources.add(candidate.source)

    async def _resolve(self, domain: str, findings: dict[str, Finding]) -> None:
        wildcard_ips = await self.resolver.wildcard_ips(domain)

        async def resolve_one(finding: Finding) -> None:
            ips = await self.resolver.lookup(finding.host)
            finding.ips = ips
            finding.resolved = bool(ips)
            finding.wildcard = bool(ips and wildcard_ips and set(ips).issubset(wildcard_ips))

        await asyncio.gather(*(resolve_one(finding) for finding in findings.values()))
        for host in [host for host, finding in findings.items() if finding.wildcard or not finding.resolved]:
            del findings[host]
