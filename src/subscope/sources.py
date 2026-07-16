from __future__ import annotations

import os
from abc import ABC, abstractmethod
from urllib.parse import quote, urlparse

from .http import HTTPClient
from .models import Candidate
from .normalize import extract_hosts, normalize_domain


class Source(ABC):
    name: str

    @abstractmethod
    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        raise NotImplementedError

    def candidates(self, hosts: set[str]) -> list[Candidate]:
        return [Candidate(host=host, source=self.name) for host in sorted(hosts)]


class Crtsh(Source):
    name = "crtsh"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        rows = await http.json(f"https://crt.sh/?q=%25.{quote(domain)}&output=json")
        hosts: set[str] = set()
        for row in rows if isinstance(rows, list) else []:
            hosts.update(extract_hosts(str(row.get("name_value", "")), domain))
            hosts.update(extract_hosts(str(row.get("common_name", "")), domain))
        return self.candidates(hosts)


class CertSpotter(Source):
    name = "certspotter"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        url = (
            "https://api.certspotter.com/v1/issuances?"
            f"domain={quote(domain)}&include_subdomains=true&expand=dns_names"
        )
        rows = await http.json(url)
        hosts: set[str] = set()
        for row in rows if isinstance(rows, list) else []:
            for dns_name in row.get("dns_names", []):
                hosts.update(extract_hosts(str(dns_name), domain))
        return self.candidates(hosts)


class AlienVault(Source):
    name = "alienvault"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        data = await http.json(
            f"https://otx.alienvault.com/api/v1/indicators/domain/{quote(domain)}/passive_dns"
        )
        hosts: set[str] = set()
        for row in data.get("passive_dns", []) if isinstance(data, dict) else []:
            hosts.update(extract_hosts(str(row.get("hostname", "")), domain))
        return self.candidates(hosts)


class HackerTarget(Source):
    name = "hackertarget"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        body = await http.text(f"https://api.hackertarget.com/hostsearch/?q={quote(domain)}")
        hosts = {normalize_domain(line.split(",", 1)[0]) for line in body.splitlines() if "," in line}
        return self.candidates({host for host in hosts if host.endswith("." + domain)})


class RapidDNS(Source):
    name = "rapiddns"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        body = await http.text(f"https://rapiddns.io/subdomain/{quote(domain)}?full=1")
        return self.candidates(extract_hosts(body, domain))


class Wayback(Source):
    name = "wayback"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        url = (
            "https://web.archive.org/cdx?output=json&collapse=urlkey&fl=original&url="
            f"*.{quote(domain)}/*"
        )
        rows = await http.json(url)
        hosts: set[str] = set()
        for row in rows[1:] if isinstance(rows, list) else []:
            raw_url = row[0] if isinstance(row, list) and row else str(row)
            netloc = urlparse(raw_url).netloc
            hosts.update(extract_hosts(netloc, domain))
        return self.candidates(hosts)


class Urlscan(Source):
    name = "urlscan"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        data = await http.json(f"https://urlscan.io/api/v1/search/?q=domain:{quote(domain)}&size=100")
        hosts: set[str] = set()
        for result in data.get("results", []) if isinstance(data, dict) else []:
            page = result.get("page", {})
            hosts.update(extract_hosts(str(page.get("domain", "")), domain))
            hosts.update(extract_hosts(str(page.get("url", "")), domain))
        return self.candidates(hosts)


class SecurityTrails(Source):
    name = "securitytrails"

    async def enumerate(self, domain: str, http: HTTPClient) -> list[Candidate]:
        key = os.getenv("SECURITYTRAILS_API_KEY")
        if not key:
            return []
        data = await http.json(
            f"https://api.securitytrails.com/v1/domain/{quote(domain)}/subdomains?children_only=false",
            headers={"APIKEY": key},
        )
        hosts = {normalize_domain(f"{item}.{domain}") for item in data.get("subdomains", [])}
        return self.candidates(hosts)


DEFAULT_SOURCES: list[Source] = [
    Crtsh(),
    CertSpotter(),
    AlienVault(),
    HackerTarget(),
    RapidDNS(),
    Wayback(),
    Urlscan(),
    SecurityTrails(),
]
