#!/usr/bin/env python3
"""Check every candidate under candidates/under-review and record what happened in their repo.

For each candidate it:
  - appends new events to activity.log: invitations accepted, PRs opened / closed / reopened /
    merged, commits pushed, force-pushes, commits landing on main
  - saves a snapshot of their latest PR to submission/ plus submission.patch (their changes
    compared with the starter)
  - at the deadline, makes their access read-only and cancels unaccepted invitations

All of this reads GitHub's own records, so it doesn't matter if a run is late or skipped.
Run by .github/workflows/sync-submissions.yml (hourly) and by close-out.
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hiring.common import (UNDER_REVIEW, append_log, iso, now_utc, parse_iso, read_json, summary,
                           write_json)

SKIP_DIRS = {".git", ".github", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
             "dist", "build"}
MAX_FILE_BYTES = 2 * 1024 * 1024

ISSUE_EVENTS = {
    "closed": "PR #{n} closed by @{actor}",
    "reopened": "PR #{n} reopened by @{actor}",
    "merged": "PR #{n} merged by @{actor} (it was supposed to stay open)",
    "head_ref_force_pushed": "PR #{n}: branch force-pushed by @{actor} (earlier commits rewritten)",
    "head_ref_deleted": "PR #{n}: branch deleted by @{actor}",
    "head_ref_restored": "PR #{n}: branch restored by @{actor}",
    "convert_to_draft": "PR #{n} converted to draft by @{actor}",
    "ready_for_review": "PR #{n} marked ready for review by @{actor}",
    "base_ref_changed": "PR #{n}: target branch changed by @{actor}",
}


def collect_events(gh, cand: dict, state: dict, now: datetime,
                   prs: list[dict]) -> list[tuple[datetime, str, str]]:
    """Return (time, key, message) for everything not already in state['seen']."""
    repo, seen = cand["repo"], set(state["seen"])
    events: list[tuple[datetime, str, str]] = []

    def add(when: datetime, key: str, message: str) -> None:
        if key not in seen:
            seen.add(key)
            events.append((when, key, message))

    collaborators = {c["login"].lower() for c in gh.paginate(f"/repos/{repo}/collaborators?affiliation=outside")}
    for user in cand["github_usernames"]:
        if user.lower() in collaborators and user.lower() not in state["accepted"]:
            state["accepted"].append(user.lower())
            add(now, f"accepted:{user.lower()}", f"@{user} accepted the invitation (noticed by this check)")

    for pr in sorted(prs, key=lambda p: p["number"]):
        n = pr["number"]
        target = pr["base"]["ref"]
        add(parse_iso(pr["created_at"]), f"opened:{n}",
            f"PR #{n} opened by @{pr['user']['login']}: \"{pr['title']}\" "
            f"({pr['head']['ref']} → {target})" + ("" if target == "main" else "  [not targeting main]"))
        for ev in gh.paginate(f"/repos/{repo}/issues/{n}/events"):
            template = ISSUE_EVENTS.get(ev["event"])
            if template:
                actor = (ev.get("actor") or {}).get("login", "unknown")
                add(parse_iso(ev["created_at"]), f"event:{ev['id']}", template.format(n=n, actor=actor))
        for c in gh.paginate(f"/repos/{repo}/pulls/{n}/commits"):
            first_line = c["commit"]["message"].splitlines()[0][:80]
            add(parse_iso(c["commit"]["committer"]["date"]), f"commit:{c['sha']}",
                f"Commit {c['sha'][:7]} on PR #{n}: {first_line}  (time from the commit itself)")

    for c in gh.paginate(f"/repos/{repo}/commits?sha=main"):
        if c["sha"] != cand["base_sha"]:
            first_line = c["commit"]["message"].splitlines()[0][:80]
            add(parse_iso(c["commit"]["committer"]["date"]), f"main:{c['sha']}",
                f"Commit {c['sha'][:7]} is on main: {first_line}  (main should only hold the starter)")

    deadline = parse_iso(cand["deadline"])
    flagged = [(w, k, m + ("  [after deadline]" if w > deadline and not k.startswith("accepted:") else ""))
               for w, k, m in events]
    state["seen"] = sorted(seen)
    return sorted(flagged, key=lambda e: e[0])


def pick_submission(prs: list[dict]) -> dict | None:
    """The PR to snapshot: the newest open PR, else the most recently updated closed one."""
    if not prs:
        return None
    return max(prs, key=lambda p: (p["state"] == "open", p["updated_at"]))


def save_snapshot(gh, cand: dict, folder: Path, pr: dict) -> list[str]:
    """Replace submission/ with the PR head's files and write submission.patch. Returns skipped paths."""
    repo, sha = cand["repo"], pr["head"]["sha"]
    tarball = gh.request("GET", f"/repos/{repo}/tarball/{sha}", raw=True)
    out = folder / "submission"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    skipped = extract_safely(tarball, out)

    patch = gh.request("GET", f"/repos/{repo}/compare/{cand['base_sha']}...{sha}",
                       accept="application/vnd.github.diff", raw=True)
    (folder / "submission.patch").write_bytes(patch)
    return skipped


def extract_safely(tarball: bytes, out: Path) -> list[str]:
    """Extract regular files only, never outside `out`, skipping junk, workflows and big files."""
    skipped = []
    root = out.resolve()
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tar:
        for member in tar.getmembers():
            parts = Path(member.name).parts[1:]  # drop GitHub's "<owner>-<repo>-<sha>/" folder
            if not parts or member.isdir():
                continue
            rel = Path(*parts)
            if not member.isfile():
                skipped.append(f"{rel} (not a regular file)")
                continue
            if any(p in SKIP_DIRS for p in rel.parts):
                continue
            target = (root / rel).resolve()
            if root not in target.parents:
                skipped.append(f"{rel} (path outside the folder)")
                continue
            if member.size > MAX_FILE_BYTES:
                skipped.append(f"{rel} ({member.size // 1024} KB, over the size limit)")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    return skipped


def enforce_deadline(gh, cand: dict, now: datetime) -> list[tuple[datetime, str]]:
    """At the deadline: collaborators drop to read-only, pending invitations are cancelled."""
    if cand["status"] != "active" or now < parse_iso(cand["deadline"]):
        return []
    repo, lines = cand["repo"], []
    for inv in gh.paginate(f"/repos/{repo}/invitations"):
        gh.request("DELETE", f"/repos/{repo}/invitations/{inv['id']}")
        lines.append((now, f"Deadline passed: invitation for @{inv['invitee']['login']} was never "
                           "accepted, so it was cancelled"))
    for collab in gh.paginate(f"/repos/{repo}/collaborators?affiliation=outside"):
        gh.request("PUT", f"/repos/{repo}/collaborators/{collab['login']}", body={"permission": "pull"})
        lines.append((now, f"Deadline passed: @{collab['login']} is now read-only"))
    cand["status"] = "deadline_passed"
    cand["deadline_enforced_at"] = iso(now)
    if not lines:
        lines.append((now, "Deadline passed (no access to change)"))
    return lines


def sync_candidate(gh, folder: Path, now: datetime | None = None) -> str:
    """Sync one candidate folder. Returns a one-line summary."""
    now = now or now_utc()
    cand = read_json(folder / "candidate.json")
    state = read_json(folder / "sync_state.json", {"seen": [], "snapshot_sha": None, "accepted": []})
    state.setdefault("accepted", [])

    prs = gh.paginate(f"/repos/{cand['repo']}/pulls?state=all")
    events = collect_events(gh, cand, state, now, prs)
    log = [(when, message) for when, _, message in events]

    pr = pick_submission(prs)
    if pr and pr["head"]["sha"] != state.get("snapshot_sha"):
        skipped = save_snapshot(gh, cand, folder, pr)
        state["snapshot_sha"] = pr["head"]["sha"]
        state["snapshot_pr"] = pr["number"]
        state["snapshot_at"] = iso(now)
        note = f"; skipped {len(skipped)} file(s): {', '.join(skipped)}" if skipped else ""
        log.append((now, f"Snapshot saved from PR #{pr['number']} at {pr['head']['sha'][:7]}{note}"))

    log += enforce_deadline(gh, cand, now)

    append_log(folder, log)
    write_json(folder / "candidate.json", cand)
    write_json(folder / "sync_state.json", state)
    return f"{cand['folder']}: {len(log)} new log line(s), status {cand['status']}"


def main() -> int:
    folders = sorted(p.parent for p in UNDER_REVIEW.glob("*/candidate.json"))
    if not folders:
        summary("No candidates under review.")
        return 0
    from hiring.github import GitHub
    gh = GitHub(os.environ.get("GH_TOKEN", ""))
    results, failed = [], 0
    for folder in folders:
        try:
            results.append(f"- {sync_candidate(gh, folder)}")
        except Exception as err:  # noqa: BLE001  keep going for the other candidates
            failed += 1
            results.append(f"- **{folder.name}: failed**: {err}")
    summary("### Submission sync\n\n" + "\n".join(results))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
