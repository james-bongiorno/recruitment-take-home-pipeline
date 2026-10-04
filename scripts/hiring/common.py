"""Shared helpers for the hiring scripts: names, inputs, paths, the challenge registry and logs."""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "coding_challenges" / "challenges.json"
UNDER_REVIEW = REPO_ROOT / "candidates" / "under-review"
REVIEWED = REPO_ROOT / "candidates" / "reviewed"

USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")


class InputError(ValueError):
    """Bad workflow input. The message is shown to whoever ran the workflow."""


# ---------- inputs ----------

def split_list(value: str) -> list[str]:
    """'1, 2 3' -> ['1', '2', '3']. Commas, spaces or both."""
    return [part for part in re.split(r"[,\s]+", value or "") if part]


def slug(name: str) -> str:
    """'José' -> 'jose', "O'Malley" -> 'omalley', 'De La Cruz' -> 'de-la-cruz'."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    ascii_name = re.sub(r"['’`]", "", ascii_name.lower())
    result = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
    if not result:
        raise InputError(f"Can't make a name out of {name!r}. Use letters A–Z.")
    return result


def repo_name(first: str, last: str) -> str:
    return f"{slug(last)}-{slug(first)}-code-challenge"


def folder_name(first: str, last: str) -> str:
    return f"{slug(last)}_{slug(first)}"


def parse_challenges(value: str, registry: dict) -> list[str]:
    ids = split_list(value)
    if not ids:
        raise InputError("Pick at least one challenge number.")
    unknown = [i for i in ids if i not in registry]
    if unknown:
        options = ", ".join(f"{k} = {v['title']}" for k, v in registry.items())
        raise InputError(f"Unknown challenge number(s): {', '.join(unknown)}. Options: {options}.")
    return sorted(set(ids), key=int)


def parse_usernames(value: str) -> list[str]:
    names = [n.lstrip("@") for n in split_list(value)]
    if not names:
        raise InputError("Add at least one GitHub username.")
    emails = [n for n in names if "@" in n]
    if emails:
        raise InputError(
            f"These look like email addresses: {', '.join(emails)}. GitHub can only add "
            "outside collaborators by username, so ask the candidate for their GitHub username."
        )
    bad = [n for n in names if not USERNAME_RE.match(n)]
    if bad:
        raise InputError(f"Not valid GitHub usernames: {', '.join(bad)}.")
    seen, unique = set(), []
    for n in names:
        if n.lower() not in seen:
            seen.add(n.lower())
            unique.append(n)
    return unique


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text())


# ---------- time and logs ----------

def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def human_time(dt: datetime) -> str:
    """'Sat Oct 4, 2026 3:02 PM MDT (21:02 UTC)' in the HIRING_TIMEZONE time zone (default UTC)."""
    import os
    utc = dt.astimezone(timezone.utc)
    zone = os.environ.get("HIRING_TIMEZONE") or "UTC"
    if zone == "UTC":
        return f"{utc:%a %b} {utc.day}, {utc:%Y %H:%M} UTC"
    try:
        from zoneinfo import ZoneInfo
        local = dt.astimezone(ZoneInfo(zone))
        return (f"{local:%a %b} {local.day}, {local:%Y} {local:%I:%M %p %Z}".replace(" 0", " ")
                + f" ({utc:%H:%M} UTC)")
    except Exception:  # noqa: BLE001  (no tzdata on this machine)
        return f"{utc:%a %b} {utc.day}, {utc:%Y %H:%M} UTC"


def append_log(folder: Path, lines: list[tuple[datetime, str]]) -> None:
    """Append '2026-10-04 15:02:11 UTC  message' lines to the candidate's activity.log."""
    if not lines:
        return
    with (folder / "activity.log").open("a") as log:
        for when, message in lines:
            log.write(f"{when.astimezone(timezone.utc):%Y-%m-%d %H:%M:%S} UTC  {message}\n")


def read_json(path: Path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def summary(markdown: str) -> None:
    """Write to the GitHub Actions job summary when running in Actions, and always print."""
    import os
    print(markdown)
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as fh:
            fh.write(markdown + "\n")
