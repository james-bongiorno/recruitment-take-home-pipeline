#!/usr/bin/env python3
"""Close out a candidate once you've reviewed them.

  1. Runs one last sync so the log and snapshot are current
  2. Removes everyone's access to their repo and cancels pending invitations
  3. Archives the repo (read-only for everyone, still there if you need it)
  4. Moves candidates/under-review/<folder> to candidates/reviewed/<folder>

Run by .github/workflows/close-out.yml.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hiring.common import (REVIEWED, UNDER_REVIEW, InputError, append_log, iso, now_utc, read_json,
                           summary, write_json)
from sync_submissions import sync_candidate


def close_out(gh, folder: Path, note: str, closed_by: str) -> Path:
    sync_candidate(gh, folder)
    cand = read_json(folder / "candidate.json")
    repo, now, lines = cand["repo"], now_utc(), []

    for inv in gh.paginate(f"/repos/{repo}/invitations"):
        gh.request("DELETE", f"/repos/{repo}/invitations/{inv['id']}")
        lines.append((now, f"Close-out: cancelled invitation for @{inv['invitee']['login']}"))
    for collab in gh.paginate(f"/repos/{repo}/collaborators?affiliation=outside"):
        gh.request("DELETE", f"/repos/{repo}/collaborators/{collab['login']}")
        lines.append((now, f"Close-out: removed @{collab['login']}"))
    gh.request("PATCH", f"/repos/{repo}", body={"archived": True})
    lines.append((now, f"Close-out by @{closed_by}: repo archived" + (f". Note: {note}" if note else "")))

    cand.update(status="closed", closed_at=iso(now), closed_by=closed_by, close_note=note)
    write_json(folder / "candidate.json", cand)
    append_log(folder, lines)

    REVIEWED.mkdir(parents=True, exist_ok=True)
    dest = REVIEWED / folder.name
    shutil.move(str(folder), dest)
    return dest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--candidate", required=True, help="Folder name, e.g. bongiorno_james")
    ap.add_argument("--note", default="", help="Optional note for the log, e.g. 'advance to onsite'")
    args = ap.parse_args(argv)

    folder = UNDER_REVIEW / args.candidate.strip()
    try:
        if not args.candidate.strip() or "/" in args.candidate or not (folder / "candidate.json").exists():
            options = ", ".join(sorted(p.parent.name for p in UNDER_REVIEW.glob("*/candidate.json")))
            raise InputError(f"No candidate folder named {args.candidate!r} under review. "
                             f"Under review now: {options or 'nobody'}.")
    except InputError as err:
        summary(f"### Not closed\n\n{err}")
        return 2

    from hiring.github import GitHub
    gh = GitHub(os.environ.get("GH_TOKEN", ""))
    dest = close_out(gh, folder, args.note.strip(), os.environ.get("GITHUB_ACTOR", "unknown"))
    summary(f"### Closed out {args.candidate}\n\nAccess removed, repo archived, folder moved to "
            f"`{dest.relative_to(dest.parents[2])}`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
