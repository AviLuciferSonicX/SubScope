from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Candidate:
    host: str
    source: str


@dataclass
class Finding:
    host: str
    sources: set[str] = field(default_factory=set)
    ips: list[str] = field(default_factory=list)
    resolved: bool = False
    wildcard: bool = False

    @property
    def confidence(self) -> int:
        score = min(len(self.sources) * 20, 80)
        if self.resolved:
            score += 20
        return min(score, 100)
