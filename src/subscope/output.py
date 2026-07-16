from __future__ import annotations

import json
from collections.abc import Iterable
from typing import TextIO

from .models import Finding


def write_text(findings: Iterable[Finding], stream: TextIO) -> None:
    for finding in findings:
        stream.write(f"{finding.host}\n")


def write_jsonl(findings: Iterable[Finding], stream: TextIO) -> None:
    for finding in findings:
        stream.write(
            json.dumps(
                {
                    "host": finding.host,
                    "sources": sorted(finding.sources),
                    "source_count": len(finding.sources),
                    "ips": finding.ips,
                    "resolved": finding.resolved,
                    "confidence": finding.confidence,
                },
                sort_keys=True,
            )
            + "\n"
        )
