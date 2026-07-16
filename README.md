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

## Requirements

- Python 3.10 or newer
- Git for downloading with `git clone`
- Internet access for passive sources
- DNS/network access when using `--resolve`

SubScope uses only Python standard-library modules, so no external package
installation is required.

## Download, Installation, and Execution

### Windows

```powershell
# Download
git clone <repository-url>
cd SubScope

# Check Python version
py -3 --version

# Run passive enumeration
py -3 .\subscope.py -d example.com

# Run with DNS validation and wildcard filtering
py -3 .\subscope.py -d example.com --resolve

# Save JSONL output
py -3 .\subscope.py -d example.com --resolve --json -o results.jsonl
```

### Linux

```bash
# Download
git clone <repository-url>
cd SubScope

# Check Python version
python3 --version

# Run passive enumeration
python3 subscope.py -d example.com

# Run with DNS validation and wildcard filtering
python3 subscope.py -d example.com --resolve

# Save JSONL output
python3 subscope.py -d example.com --resolve --json -o results.jsonl
```

### macOS

```bash
# Download
git clone <repository-url>
cd SubScope

# Check Python version
python3 --version

# Run passive enumeration
python3 subscope.py -d example.com

# Run with DNS validation and wildcard filtering
python3 subscope.py -d example.com --resolve

# Save JSONL output
python3 subscope.py -d example.com --resolve --json -o results.jsonl
```

## Notes

Only run this against domains you own or are authorized to test. Passive sources
can still impose rate limits, block requests, or return incomplete data.
