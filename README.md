# SubScope

Fast, cross-platform subdomain enumeration tool with async passive sources,
strict normalization, source attribution, confidence scoring, and optional DNS
validation with wildcard filtering.

`SubScope` is designed for authorized asset discovery, bug bounty
reconnaissance, and internal security inventory work.

Compared with older scraper-heavy tools, SubScope centralizes normalization,
deduplication, source attribution, timeout handling, and DNS validation. Sources
stay small and the engine stays predictable.

## Features

- Async passive enumeration across multiple public sources
- Strong hostname normalization and scope filtering
- Per-source attribution and confidence scoring
- Optional DNS validation with wildcard filtering
- Text and JSONL output
- Zero required third-party Python packages
- Optional `SECURITYTRAILS_API_KEY` support

## Quick Start

```powershell
cd "C:\Users\Lucifer\Documents\Sub Domain Enumeration\subscope"
C:\Users\Lucifer\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\run_subscope.py -d example.com
```

With DNS validation:

```powershell
C:\Users\Lucifer\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\run_subscope.py -d example.com --resolve
```

JSONL output:

```powershell
C:\Users\Lucifer\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\run_subscope.py -d example.com --resolve --json -o results.jsonl
```

## Notes

Only run this against domains you own or are authorized to test. Passive sources
can still impose rate limits, block requests, or return incomplete data.
