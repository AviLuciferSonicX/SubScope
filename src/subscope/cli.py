from __future__ import annotations

import argparse
import asyncio
import sys

from .engine import Enumerator
from .normalize import normalize_domain
from .output import write_jsonl, write_text
from .sources import DEFAULT_SOURCES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="subscope",
        description="Fast passive subdomain enumeration with optional DNS validation.",
    )
    parser.add_argument("-d", "--domain", required=True, help="domain to enumerate")
    parser.add_argument("-o", "--output", help="write output to a file")
    parser.add_argument("--json", action="store_true", help="write JSONL output")
    parser.add_argument("--resolve", action="store_true", help="verify DNS and remove wildcard/dead hosts")
    parser.add_argument("--timeout", type=int, default=20, help="per-request timeout in seconds")
    parser.add_argument("--max-time", type=int, default=120, help="overall passive timeout in seconds")
    parser.add_argument("--list-sources", action="store_true", help="list source names and exit")
    parser.add_argument(
        "--sources",
        help="comma-separated source allowlist, e.g. crtsh,alienvault,wayback",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_sources:
        for source in DEFAULT_SOURCES:
            print(source.name)
        return 0

    source_map = {source.name: source for source in DEFAULT_SOURCES}
    sources = DEFAULT_SOURCES
    if args.sources:
        wanted = [item.strip().lower() for item in args.sources.split(",") if item.strip()]
        unknown = [item for item in wanted if item not in source_map]
        if unknown:
            parser.error(f"unknown source(s): {', '.join(unknown)}")
        sources = [source_map[item] for item in wanted]

    domain = normalize_domain(args.domain)
    enumerator = Enumerator(sources=sources, timeout=args.timeout, max_time=args.max_time)
    findings, errors = asyncio.run(enumerator.run(domain, resolve=args.resolve))

    stream = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        if args.json:
            write_jsonl(findings, stream)
        else:
            write_text(findings, stream)
    finally:
        if args.output:
            stream.close()

    if errors:
        sys.stderr.write("Source warnings:\n")
        for source, error in sorted(errors.items()):
            sys.stderr.write(f"  {source}: {error}\n")

    return 0
