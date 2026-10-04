#!/usr/bin/env python3
"""Create a candidate's coding challenge repo in the hiring org and their folder in this repo.

Run by .github/workflows/create-challenge.yml. Locally, try it with --dry-run:

    python3 scripts/create_challenge.py --first James --last Bongiorno \
        --challenges "1, 3" --usernames james-bongiorno --dry-run
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hiring.common import (REPO_ROOT, REVIEWED, UNDER_REVIEW, InputError, append_log, folder_name,
                           human_time, iso, load_registry, now_utc, parse_challenges,
                           parse_usernames, repo_name, summary, write_json)

# Never copied into a candidate repo, wherever they appear.
IGNORE = shutil.ignore_patterns("_reviewer_only", "solutions", "node_modules", "dist", ".venv",
                                "__pycache__", ".pytest_cache", "*.pyc", ".DS_Store", "*.db")
FORBIDDEN = {"_reviewer_only", "solutions"}

CANDIDATE_GITIGNORE = """node_modules/
dist/
.venv/
__pycache__/
.pytest_cache/
*.pyc
*.db
.DS_Store
"""


def build_starter(dest: Path, first: str, challenge_ids: list[str], registry: dict,
                  deadline_text: str) -> int:
    """Copy the chosen challenges into dest with a top-level README. Returns total minutes."""
    total = 0
    rows = []
    for cid in challenge_ids:
        entry = registry[cid]
        total += entry["minutes"]
        for rel in entry["folders"]:
            src = REPO_ROOT / rel
            if not src.is_dir():
                raise InputError(f"Challenge {cid} points at a missing folder: {rel}")
            shutil.copytree(src, dest / src.name, ignore=IGNORE)
            rows.append(f"| `{src.name}/` | {entry['title']} ({entry['area']}) |")

    for readme in dest.rglob("README.md"):
        readme.write_text(_point_at_pr_submission(readme.read_text()))

    leaked = [p for p in dest.rglob("*") if p.name in FORBIDDEN]
    if leaked:
        raise RuntimeError(f"Refusing to continue: reviewer material found in starter: {leaked}")

    (dest / ".gitignore").write_text(CANDIDATE_GITIGNORE)
    (dest / "README.md").write_text(_candidate_readme(first, rows, total, deadline_text))
    return total


def _point_at_pr_submission(text: str) -> str:
    """The challenge READMEs say 'send it back as a zip'. In a repo, they submit with a PR."""
    text = text.replace("(you have 48 hours to send it back)",
                        "(see the deadline in the README at the top of this repository)")
    return re.sub(r"^- Send it back as a zip.*$",
                  "- Submit by opening a pull request in this repository (see the README at the "
                  "top level). Please don't post it publicly.",
                  text, flags=re.MULTILINE)


def _candidate_readme(first: str, rows: list[str], total: int, deadline_text: str) -> str:
    table = "\n".join(rows)
    return f"""# Coding challenge

Hi {first}, thanks for taking the time to do this.

## What's here

| Folder | Challenge |
|---|---|
{table}

**About {total} minutes of work in total.** Each folder has its own README with the setup steps and tasks. Please stop at the time box in each one even if you're not finished. Telling us what you'd do next is worth more than rushing.

## Deadline

**{deadline_text}.** After that, this repository becomes read-only for you.

## How to submit

1. Clone this repository and create a branch: `git checkout -b submission`
2. Work on that branch and commit as you go. We like seeing how your work progressed.
3. Push the branch and open a **pull request into `main`**.
4. You can keep pushing to the same pull request until the deadline. Please don't merge it.

If something is unclear or broken, reply to the email this came with. Good luck!
"""


def push_starter(src: Path, org: str, repo: str, token: str, bot_name: str, bot_email: str) -> str:
    """Commit src as the first commit on main and push it. Returns the commit SHA."""
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    git = ["git", "-C", str(src), "-c", f"user.name={bot_name}", "-c", f"user.email={bot_email}"]
    subprocess.run(["git", "init", "-q", "-b", "main", str(src)], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "Coding challenge starter"], check=True)
    subprocess.run([*git, "-c", f"http.extraheader=AUTHORIZATION: basic {basic}",
                    "push", "-q", f"https://github.com/{org}/{repo}.git", "main"], check=True)
    return subprocess.run([*git, "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--first", required=True)
    ap.add_argument("--last", required=True)
    ap.add_argument("--challenges", required=True, help='Numbers, e.g. "1, 3" or "1 3"')
    ap.add_argument("--usernames", required=True, help="GitHub usernames, comma or space separated")
    ap.add_argument("--deadline-hours", type=int, default=48)
    ap.add_argument("--org", default=os.environ.get("HIRING_ORG", ""))
    ap.add_argument("--dry-run", action="store_true", help="Show the plan; create nothing")
    args = ap.parse_args(argv)

    try:
        first, last = args.first.strip(), args.last.strip()
        registry = load_registry()
        challenge_ids = parse_challenges(args.challenges, registry)
        usernames = parse_usernames(args.usernames)
        repo, folder = repo_name(first, last), folder_name(first, last)
        if not 1 <= args.deadline_hours <= 336:
            raise InputError("Deadline must be between 1 and 336 hours (2 weeks).")
        if not args.org and not args.dry_run:
            raise InputError("No hiring org. Set the HIRING_ORG repository variable.")
        if (UNDER_REVIEW / folder).exists() or (REVIEWED / folder).exists():
            raise InputError(f"A candidate folder named {folder} already exists in candidates/.")
    except InputError as err:
        summary(f"### Not created\n\n{err}")
        return 2

    created = now_utc()
    deadline = created + timedelta(hours=args.deadline_hours)
    org = args.org or "<hiring org>"
    full_repo = f"{org}/{repo}"

    with tempfile.TemporaryDirectory() as tmp:
        starter = Path(tmp) / repo
        starter.mkdir()
        try:
            total = build_starter(starter, first, challenge_ids, registry, human_time(deadline))
        except InputError as err:
            summary(f"### Not created\n\n{err}")
            return 2
        files = sorted(str(p.relative_to(starter)) for p in starter.rglob("*") if p.is_file())

        chosen = ", ".join(f"{c} ({registry[c]['title']})" for c in challenge_ids)
        plan = (f"| | |\n|---|---|\n| Candidate | {first} {last} |\n| Repo | `{full_repo}` |\n"
                f"| Candidate folder | `candidates/under-review/{folder}/` |\n"
                f"| Challenges | {chosen} |\n"
                f"| Time box | about {total} minutes |\n"
                f"| Access for | {', '.join('@' + u for u in usernames)} (write until the deadline) |\n"
                f"| Deadline | {human_time(deadline)} |\n")

        if args.dry_run:
            summary(f"### Dry run: nothing was created\n\n{plan}\n<details><summary>{len(files)} "
                    f"files would be pushed</summary>\n\n```\n" + "\n".join(files) + "\n```\n</details>")
            return 0

        from hiring.github import GitHub, GitHubError
        gh = GitHub(os.environ.get("GH_TOKEN", ""))
        try:
            missing = [u for u in usernames if not gh.exists(f"/users/{u}")]
            if missing:
                raise InputError(f"No GitHub account found for: {', '.join(missing)}.")
            if gh.exists(f"/repos/{full_repo}"):
                raise InputError(f"{full_repo} already exists.")
        except InputError as err:
            summary(f"### Not created\n\n{err}")
            return 2

        bot_slug = os.environ.get("APP_SLUG", "")
        bot_name = f"{bot_slug}[bot]" if bot_slug else "Hiring Bot"
        bot_email = "hiring@users.noreply.github.com"
        if bot_slug:
            try:
                bot_id = gh.get(f"/users/{bot_slug}%5Bbot%5D")["id"]
                bot_email = f"{bot_id}+{bot_slug}[bot]@users.noreply.github.com"
            except GitHubError:
                pass

        gh.request("POST", f"/orgs/{org}/repos", body={
            "name": repo, "private": True, "auto_init": False,
            "description": f"Coding challenge for {first} {last}",
            "has_issues": False, "has_projects": False, "has_wiki": False, "has_discussions": False,
        })
        invites = []
        try:
            base_sha = push_starter(starter, org, repo, gh.token, bot_name, bot_email)
            for user in usernames:
                gh.request("PUT", f"/repos/{full_repo}/collaborators/{user}",
                           body={"permission": "push"})
                invites.append(user)
        except (subprocess.CalledProcessError, GitHubError) as err:
            summary(f"### Partly created\n\nThe repo **{full_repo}** was created, but then this "
                    f"failed:\n\n```\n{err}\n```\nInvitations sent: {invites or 'none'}. Delete "
                    f"the repo (Settings → Delete this repository) and run the workflow again.")
            return 1

    dest = UNDER_REVIEW / folder
    dest.mkdir(parents=True)
    write_json(dest / "candidate.json", {
        "first_name": first, "last_name": last, "folder": folder,
        "repo": full_repo, "repo_url": f"https://github.com/{full_repo}",
        "challenges": challenge_ids,
        "challenge_titles": [registry[c]["title"] for c in challenge_ids],
        "github_usernames": usernames,
        "created_at": iso(created), "deadline": iso(deadline), "base_sha": base_sha,
        "status": "active", "created_by": os.environ.get("GITHUB_ACTOR", "unknown"),
    })
    write_json(dest / "sync_state.json", {"seen": [], "snapshot_sha": None, "accepted": []})
    append_log(dest, [
        (created, f"Challenge created by @{os.environ.get('GITHUB_ACTOR', 'unknown')}: "
                  f"{', '.join(registry[c]['title'] for c in challenge_ids)} → {full_repo}"),
        *[(created, f"Invitation sent to @{u} (write access)") for u in invites],
        (created, f"Deadline set: {iso(deadline)}"),
    ])

    summary(f"### Challenge created\n\n{plan}\n"
            f"GitHub has emailed an invitation to each username. If a candidate can't find it, "
            f"send them **https://github.com/{full_repo}/invitations** (they must be signed in).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
