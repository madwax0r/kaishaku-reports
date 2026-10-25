#!/usr/bin/env python3
"""Check every report under reports/ against the rules kaishaku.ch imports by.

Usage: python3 scripts/validate.py [path ...]   (default: every .md file under reports/)
Exits non-zero and prints one line per problem when anything fails.
"""
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIED_URL = "https://kaishaku.ch/data/verified.json"
FALLBACK_LAYERS = {"KytyPS5", "SharpEmu", "RPCSX", "AnyPS5"}
FIELDS = ["title", "serial", "layer", "status", "commit", "version", "host_os", "gpu", "driver", "tested_date", "proof_url"]
OPTIONAL = {"commit", "version"}
STATUSES = ["Nothing", "Boots", "Intro", "Ingame", "Playable"]
ALLOWED_HOSTS = {"github.com", "www.github.com", "youtube.com", "www.youtube.com"}
PROOF_RE = re.compile(r"^https://(github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(issues|pull)/[0-9]+|(www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]{11})$")
URL_RE = re.compile(r"(?i)\b(?:https?|ftp|magnet):[^\s\"'<>)\]]*|\bwww\.[^\s\"'<>)\]]+")
FORBIDDEN = ["magnet:", ".torrent", "fpkg", "prod.keys", ".sprx", "bios download", "free download",
             "mega.nz", "mediafire", "1fichier", "rapidgator", "pkg dump"]
NAME_RE = re.compile(r"^(PPSA|CUSA)\d{5}-(windows|linux|macos|freebsd)-\d{4}-\d{2}-\d{2}\.md$")


def verified_layers():
    try:
        with urllib.request.urlopen(VERIFIED_URL, timeout=15) as resp:
            return {p["name"] for p in json.load(resp)["projects"]}
    except Exception as exc:  # the site being unreachable should not block review
        print(f"note: could not load {VERIFIED_URL} ({exc}); using the built-in list", file=sys.stderr)
        return FALLBACK_LAYERS


def front_matter(text):
    m = re.match(r"^﻿?---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return None, text
    fields = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            return None, text
        value = value.strip()
        try:
            fields[key.strip()] = json.loads(value)
        except ValueError:
            fields[key.strip()] = value.strip('"')
    return fields, m.group(2)


def check(path, layers):
    rel = path.relative_to(ROOT) if path.is_absolute() else path
    problems = []
    parts = rel.parts
    if len(parts) != 3 or parts[0] != "reports":
        return [f"{rel}: reports go in reports/<layer>/<file>.md"]
    text = path.read_text(encoding="utf-8", errors="replace")
    fields, body = front_matter(text)
    if fields is None:
        return [f"{rel}: no front matter; copy templates/report.md"]
    unknown = set(fields) - set(FIELDS)
    if unknown:
        problems.append(f"unknown fields {sorted(unknown)}")
    for key in FIELDS:
        if key not in OPTIONAL and not str(fields.get(key, "")).strip():
            problems.append(f"{key} is empty (write Not reported if unknown)" if key in ("gpu", "driver") else f"{key} is empty")
    layer = str(fields.get("layer", ""))
    if layer and layer not in layers:
        problems.append(f"layer {layer!r} is not on the verified list ({', '.join(sorted(layers))})")
    if layer and parts[1] != layer:
        problems.append(f"file is in reports/{parts[1]}/ but layer is {layer!r}")
    serial = str(fields.get("serial", ""))
    if serial and not re.fullmatch(r"(PPSA|CUSA)\d{5}", serial):
        problems.append(f"serial {serial!r} must look like PPSA01234 or CUSA01234")
    if not NAME_RE.match(parts[2]):
        problems.append("file name must be <serial>-<os>-<yyyy-mm-dd>.md, e.g. PPSA01234-linux-2026-10-25.md")
    elif serial and not parts[2].startswith(serial + "-"):
        problems.append("file name does not start with the serial")
    status = str(fields.get("status", ""))
    if status and status not in STATUSES:
        problems.append(f"status {status!r} must be one of {', '.join(STATUSES)}")
    commit = str(fields.get("commit", "")).strip()
    if commit and not re.fullmatch(r"[0-9a-f]{7,40}", commit):
        problems.append(f"commit {commit!r} must be a 7 to 40 character lowercase hex SHA")
    if not commit and not str(fields.get("version", "")).strip():
        problems.append("give the commit SHA, or at least the version you tested")
    date = str(fields.get("tested_date", ""))
    if date:
        try:
            if dt.date.fromisoformat(date) > dt.date.today() + dt.timedelta(days=1):
                problems.append("tested_date is in the future")
        except ValueError:
            problems.append(f"tested_date {date!r} must be YYYY-MM-DD")
    proof = str(fields.get("proof_url", ""))
    if proof and not PROOF_RE.match(proof):
        problems.append("proof_url must be a github.com issue or pull request, or a youtube.com/watch?v= video")
    for limit, key in ((120, "title"), (80, "host_os"), (80, "gpu"), (40, "driver"), (160, "version")):
        if len(str(fields.get(key, ""))) > limit:
            problems.append(f"{key} is longer than {limit} characters")
    for url in URL_RE.findall(text):
        host = urllib.parse.urlparse(url if "://" in url else "https://" + url).hostname
        if host not in ALLOWED_HOSTS:
            problems.append(f"link to {url!r}: only github.com and youtube.com links are allowed")
    lowered = text.lower()
    for term in FORBIDDEN:
        if term in lowered:
            problems.append(f"contains {term!r}, which is never allowed here")
    return [f"{rel}: {p}" for p in problems]


def main(argv):
    layers = verified_layers()
    if argv:
        paths = [Path(a).resolve() for a in argv if a.endswith(".md") and Path(a).exists()]
    else:
        paths = sorted((ROOT / "reports").rglob("*.md"))
    paths = [p for p in paths if p.name.lower() != "readme.md"]
    problems = []
    for path in paths:
        problems += check(path, layers)
    for p in problems:
        print(p)
    print(f"checked {len(paths)} report(s): {'OK' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
