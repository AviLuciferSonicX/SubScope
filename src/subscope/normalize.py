from __future__ import annotations

import re
from urllib.parse import urlparse


LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
HOST_RE = re.compile(rf"(?i)(?:\*\.)?(?:{LABEL}\.)+{LABEL}")


def normalize_domain(value: str) -> str:
    host = value.strip().lower()
    if "://" in host:
        host = urlparse(host).netloc
    host = host.split("@")[-1].split(":")[0].strip(".")
    if host.startswith("*."):
        host = host[2:]
    return host.encode("idna").decode("ascii")


def in_scope(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def extract_hosts(text: str, domain: str) -> set[str]:
    found: set[str] = set()
    for match in HOST_RE.findall(text):
        host = normalize_domain(match)
        if in_scope(host, domain):
            found.add(host)
    return found
