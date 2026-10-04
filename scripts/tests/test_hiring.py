"""Tests for the hiring scripts, against a fake GitHub. Run from the repo root: pytest scripts/tests"""
import io
import json
import sys
import tarfile
from datetime import timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import close_out  # noqa: E402
import create_challenge  # noqa: E402
import sync_submissions  # noqa: E402
from hiring import common  # noqa: E402
from hiring.common import InputError, parse_iso  # noqa: E402

REPO = "Hiring-Org/bongiorno-james-code-challenge"
BASE = "b" * 40


# ---------- a fake GitHub ----------

class FakeGitHub:
    token = "fake-token"

    def __init__(self, lists=None, raw=None, existing=()):
        self.lists = lists or {}
        self.raw = raw or {}
        self.existing = set(existing)
        self.calls = []

    def paginate(self, path):
        return [dict(x) for x in self.lists.get(path, [])]

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def exists(self, path):
        return path in self.existing

    def request(self, method, path, body=None, accept=None, raw=False):
        self.calls.append((method, path, body))
        if raw:
            return self.raw[path]
        if path.endswith("%5Bbot%5D"):
            return {"id": 4242}
        return {}


def tarball(files: dict, symlink=None) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in files.items():
            info = tarfile.TarInfo(f"Hiring-Org-repo-abc123/{name}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        if symlink:
            info = tarfile.TarInfo(f"Hiring-Org-repo-abc123/{symlink}")
            info.type = tarfile.SYMTYPE
            info.linkname = "/etc/passwd"
            tar.addfile(info)
    return buf.getvalue()


@pytest.fixture
def candidates(tmp_path, monkeypatch):
    """Point every script at a temporary candidates/ folder."""
    under, reviewed = tmp_path / "under-review", tmp_path / "reviewed"
    under.mkdir()
    for mod in (common, create_challenge, sync_submissions, close_out):
        monkeypatch.setattr(mod, "UNDER_REVIEW", under, raising=False)
        monkeypatch.setattr(mod, "REVIEWED", reviewed, raising=False)
    return under, reviewed


def make_candidate(under: Path, deadline_offset_hours=48) -> Path:
    folder = under / "bongiorno_james"
    folder.mkdir()
    created = common.now_utc() - timedelta(hours=1)
    common.write_json(folder / "candidate.json", {
        "first_name": "James", "last_name": "Bongiorno", "folder": "bongiorno_james",
        "repo": REPO, "challenges": ["1"], "github_usernames": ["james-bongiorno", "second-user"],
        "created_at": common.iso(created),
        "deadline": common.iso(created + timedelta(hours=deadline_offset_hours)),
        "base_sha": BASE, "status": "active",
    })
    common.write_json(folder / "sync_state.json", {"seen": [], "snapshot_sha": None, "accepted": []})
    return folder


def commit(sha, message, date):
    return {"sha": sha, "commit": {"message": message, "committer": {"date": date}}}


def repo_activity(head_sha="h" * 40, late_commit=False):
    pr1 = {"number": 1, "state": "closed", "title": "First try", "created_at": "2026-10-04T10:00:00Z",
           "updated_at": "2026-10-04T10:30:00Z", "user": {"login": "james-bongiorno"},
           "head": {"ref": "submission", "sha": "a" * 40}, "base": {"ref": "main"}}
    pr2 = {"number": 2, "state": "open", "title": "James's submission", "created_at": "2026-10-04T11:00:00Z",
           "updated_at": "2026-10-04T12:00:00Z", "user": {"login": "james-bongiorno"},
           "head": {"ref": "submission", "sha": head_sha}, "base": {"ref": "main"}}
    pr2_commits = [commit("c" * 40, "Implement register\n\nDetails", "2026-10-04T11:30:00Z")]
    if late_commit:
        pr2_commits.append(commit(head_sha, "One more fix", "2026-12-01T00:00:00Z"))
    return FakeGitHub(lists={
        f"/repos/{REPO}/collaborators?affiliation=outside": [{"login": "James-Bongiorno"}],
        f"/repos/{REPO}/invitations": [{"id": 77, "invitee": {"login": "second-user"}}],
        f"/repos/{REPO}/pulls?state=all": [pr2, pr1],
        f"/repos/{REPO}/issues/1/events": [
            {"id": 501, "event": "closed", "actor": {"login": "james-bongiorno"}, "created_at": "2026-10-04T10:30:00Z"},
            {"id": 502, "event": "labeled", "actor": {"login": "x"}, "created_at": "2026-10-04T10:31:00Z"}],
        f"/repos/{REPO}/issues/2/events": [
            {"id": 601, "event": "head_ref_force_pushed", "actor": {"login": "james-bongiorno"},
             "created_at": "2026-10-04T11:45:00Z"}],
        f"/repos/{REPO}/pulls/1/commits": [commit("a" * 40, "WIP", "2026-10-04T09:50:00Z")],
        f"/repos/{REPO}/pulls/2/commits": pr2_commits,
        f"/repos/{REPO}/commits?sha=main": [commit(BASE, "Coding challenge starter", "2026-10-04T08:00:00Z")],
    }, raw={
        f"/repos/{REPO}/tarball/{head_sha}": tarball({
            "README.md": b"# challenge\n",
            "01-rsvp-api/app/rsvps.py": b"def register(): ...\n",
            ".github/workflows/steal.yml": b"on: push\n",
            "checkin/node_modules/x.js": b"junk",
            "../escape.txt": b"nope",
            "big.bin": b"0" * (sync_submissions.MAX_FILE_BYTES + 1),
        }, symlink="link-to-passwd"),
        f"/repos/{REPO}/compare/{BASE}...{head_sha}": b"diff --git a/qc.py b/qc.py\n",
    })


# ---------- input parsing ----------

def test_split_list_accepts_commas_and_spaces():
    assert common.split_list(" 1, 2 3,,4 ") == ["1", "2", "3", "4"]


@pytest.mark.parametrize("name, expected", [
    ("James", "james"), ("O'Malley", "omalley"), ("José", "jose"), ("De La Cruz", "de-la-cruz"),
    ("Anne-Marie", "anne-marie"),
])
def test_slug(name, expected):
    assert common.slug(name) == expected


def test_names():
    assert common.repo_name("James", "Bongiorno") == "bongiorno-james-code-challenge"
    assert common.folder_name("María", "De La Cruz") == "de-la-cruz_maria"
    with pytest.raises(InputError):
        common.slug("!!!")


def test_usernames():
    assert common.parse_usernames("@james-bongiorno, other-user james-bongiorno") == ["james-bongiorno", "other-user"]
    with pytest.raises(InputError, match="email"):
        common.parse_usernames("matt@example.com")
    with pytest.raises(InputError):
        common.parse_usernames("-bad-")


def test_challenges():
    reg = common.load_registry()
    assert common.parse_challenges("3 1, 3", reg) == ["1", "3"]
    with pytest.raises(InputError, match="Unknown"):
        common.parse_challenges("1 9", reg)


def test_registry_folders_exist_and_have_no_reviewer_material():
    for cid, entry in common.load_registry().items():
        for rel in entry["folders"]:
            folder = common.REPO_ROOT / rel
            assert folder.is_dir(), f"challenge {cid}: {rel} missing"
            assert not any(p.name == "_reviewer_only" for p in folder.rglob("*"))


# ---------- creating a challenge ----------

def test_build_starter(tmp_path):
    reg = common.load_registry()
    total = create_challenge.build_starter(tmp_path, "James", ["1", "2", "3"], reg, "Mon Oct 5")
    assert total == 250
    names = {p.name for p in tmp_path.rglob("*")}
    assert "_reviewer_only" not in names and "node_modules" not in names
    assert {"01-rsvp-api", "02-invoice-bug-hunt", "checkin", "ticket-sales"} <= names
    readme = (tmp_path / "README.md").read_text()
    assert "Hi James" in readme and "Mon Oct 5" in readme and "pull request into `main`" in readme
    for r in tmp_path.rglob("README.md"):
        text = r.read_text()
        assert "Send it back as a zip" not in text
        assert "48 hours to send it back" not in text


def test_create_dry_run_creates_nothing(candidates, monkeypatch, capsys):
    under, _ = candidates
    rc = create_challenge.main(["--first", "James", "--last", "Bongiorno", "--challenges", "1",
                                "--usernames", "james-bongiorno", "--dry-run"])
    assert rc == 0
    assert "Dry run" in capsys.readouterr().out
    assert not any(under.iterdir())


def test_create_rejects_bad_input(candidates, capsys):
    rc = create_challenge.main(["--first", "M", "--last", "D", "--challenges", "7",
                                "--usernames", "m", "--org", "Hiring-Org"])
    assert rc == 2 and "Unknown challenge" in capsys.readouterr().out


def test_create_end_to_end(candidates, monkeypatch):
    under, _ = candidates
    fake = FakeGitHub(existing={"/users/james-bongiorno"})
    monkeypatch.setattr("hiring.github.GitHub", lambda token: fake)
    pushed = {}

    def fake_push(src, org, repo, token, name, email):
        pushed.update(files=sorted(str(p.relative_to(src)) for p in src.rglob("*") if p.is_file()),
                      name=name, email=email)
        return BASE

    monkeypatch.setattr(create_challenge, "push_starter", fake_push)
    monkeypatch.setenv("GH_TOKEN", "x")
    monkeypatch.setenv("APP_SLUG", "take-home-bot")
    monkeypatch.setenv("GITHUB_ACTOR", "jclinton")

    rc = create_challenge.main(["--first", "James", "--last", "Bongiorno", "--challenges", "3",
                                "--usernames", "james-bongiorno", "--org", "Hiring-Org"])
    assert rc == 0
    assert ("POST", "/orgs/Hiring-Org/repos") in [(m, p) for m, p, _ in fake.calls]
    repo_body = next(b for m, p, b in fake.calls if p == "/orgs/Hiring-Org/repos")
    assert repo_body["private"] is True and repo_body["name"] == "bongiorno-james-code-challenge"
    assert ("PUT", f"/repos/{REPO}/collaborators/james-bongiorno", {"permission": "push"}) in fake.calls
    assert "ticket-sales/sales/db.py" in pushed["files"]
    assert pushed["email"] == "4242+take-home-bot[bot]@users.noreply.github.com"

    cand = json.loads((under / "bongiorno_james" / "candidate.json").read_text())
    assert cand["repo"] == REPO and cand["base_sha"] == BASE and cand["status"] == "active"
    assert parse_iso(cand["deadline"]) - parse_iso(cand["created_at"]) == timedelta(hours=48)
    log = (under / "bongiorno_james" / "activity.log").read_text()
    assert "Challenge created by @jclinton" in log and "Invitation sent to @james-bongiorno" in log


def test_create_refuses_existing_repo(candidates, monkeypatch, capsys):
    fake = FakeGitHub(existing={"/users/james-bongiorno", f"/repos/{REPO}"})
    monkeypatch.setattr("hiring.github.GitHub", lambda token: fake)
    rc = create_challenge.main(["--first", "James", "--last", "Bongiorno", "--challenges", "1",
                                "--usernames", "james-bongiorno", "--org", "Hiring-Org"])
    assert rc == 2 and "already exists" in capsys.readouterr().out
    assert not [c for c in fake.calls if c[0] != "GET"]


# ---------- syncing ----------

def test_sync_logs_events_and_snapshots(candidates):
    under, _ = candidates
    folder = make_candidate(under)
    gh = repo_activity()
    sync_submissions.sync_candidate(gh, folder)

    log = (folder / "activity.log").read_text()
    for expected in ["@james-bongiorno accepted the invitation", "PR #1 opened by @james-bongiorno",
                     "PR #1 closed by @james-bongiorno", "PR #2 opened", "force-pushed",
                     "Commit ccccccc on PR #2: Implement register", "Snapshot saved from PR #2"]:
        assert expected in log, expected
    assert "labeled" not in log
    lines = log.strip().splitlines()
    assert lines.index(next(l for l in lines if "PR #1 opened" in l)) < \
        lines.index(next(l for l in lines if "PR #2 opened" in l))  # in time order

    snap = folder / "submission"
    assert (snap / "01-rsvp-api/app/rsvps.py").exists()
    assert not (snap / ".github").exists() and not (snap / "checkin/node_modules").exists()
    assert not (snap / "big.bin").exists() and not (snap / "link-to-passwd").exists()
    assert not (folder / "escape.txt").exists() and not (folder.parent / "escape.txt").exists()
    assert "over the size limit" in log and "not a regular file" in log and "path outside" in log
    assert (folder / "submission.patch").read_bytes().startswith(b"diff --git")

    # nothing was changed in their repo before the deadline
    assert not [c for c in gh.calls if c[0] in ("PUT", "DELETE", "PATCH")]


def test_sync_is_idempotent(candidates):
    under, _ = candidates
    folder = make_candidate(under)
    gh = repo_activity()
    sync_submissions.sync_candidate(gh, folder)
    before = (folder / "activity.log").read_text()
    sync_submissions.sync_candidate(gh, folder)
    assert (folder / "activity.log").read_text() == before


def test_new_push_takes_a_new_snapshot(candidates):
    under, _ = candidates
    folder = make_candidate(under)
    sync_submissions.sync_candidate(repo_activity(head_sha="1" * 40), folder)
    sync_submissions.sync_candidate(repo_activity(head_sha="2" * 40), folder)
    log = (folder / "activity.log").read_text()
    assert log.count("Snapshot saved") == 2
    assert json.loads((folder / "sync_state.json").read_text())["snapshot_sha"] == "2" * 40


def test_direct_push_to_main_is_logged(candidates):
    under, _ = candidates
    folder = make_candidate(under)
    gh = repo_activity()
    gh.lists[f"/repos/{REPO}/commits?sha=main"].insert(0, commit("d" * 40, "oops", "2026-10-04T13:00:00Z"))
    sync_submissions.sync_candidate(gh, folder)
    assert "Commit ddddddd is on main" in (folder / "activity.log").read_text()


def test_deadline_makes_access_read_only(candidates):
    under, _ = candidates
    folder = make_candidate(under, deadline_offset_hours=0.5)  # deadline was 30 minutes ago
    gh = repo_activity(late_commit=True)
    sync_submissions.sync_candidate(gh, folder)

    assert ("PUT", f"/repos/{REPO}/collaborators/James-Bongiorno", {"permission": "pull"}) in gh.calls
    assert ("DELETE", f"/repos/{REPO}/invitations/77", None) in gh.calls
    cand = json.loads((folder / "candidate.json").read_text())
    assert cand["status"] == "deadline_passed"
    log = (folder / "activity.log").read_text()
    assert "@James-Bongiorno is now read-only" in log and "never accepted" in log
    assert "One more fix  (time from the commit itself)  [after deadline]" in log

    # only once
    gh.calls.clear()
    sync_submissions.sync_candidate(gh, folder)
    assert not [c for c in gh.calls if c[0] in ("PUT", "DELETE")]


def test_sync_main_keeps_going_when_one_candidate_fails(candidates, monkeypatch):
    under, _ = candidates
    make_candidate(under)
    broken = under / "broken_candidate"
    broken.mkdir()
    (broken / "candidate.json").write_text("{not json")
    monkeypatch.setattr("hiring.github.GitHub", lambda token: repo_activity())
    assert sync_submissions.main() == 1
    assert (under / "bongiorno_james" / "activity.log").exists()


# ---------- closing out ----------

def test_close_out(candidates, monkeypatch):
    under, reviewed = candidates
    folder = make_candidate(under)
    gh = repo_activity()
    dest = close_out.close_out(gh, folder, "advance to onsite", "jclinton")

    assert dest == reviewed / "bongiorno_james" and not folder.exists()
    assert ("DELETE", f"/repos/{REPO}/collaborators/James-Bongiorno", None) in gh.calls
    assert ("DELETE", f"/repos/{REPO}/invitations/77", None) in gh.calls
    assert ("PATCH", f"/repos/{REPO}", {"archived": True}) in gh.calls
    calls = [(m, p) for m, p, _ in gh.calls]
    assert calls.index(("PATCH", f"/repos/{REPO}")) > calls.index(("DELETE", f"/repos/{REPO}/collaborators/James-Bongiorno"))
    cand = json.loads((dest / "candidate.json").read_text())
    assert cand["status"] == "closed" and cand["close_note"] == "advance to onsite"
    assert "repo archived. Note: advance to onsite" in (dest / "activity.log").read_text()


def test_close_out_unknown_candidate(candidates, capsys):
    assert close_out.main(["--candidate", "nobody_here"]) == 2
    assert "No candidate folder" in capsys.readouterr().out


# ---------- time zone ----------

def test_deadline_shown_in_utc_by_default(monkeypatch):
    monkeypatch.delenv("HIRING_TIMEZONE", raising=False)
    assert common.human_time(parse_iso("2026-10-05T02:07:00Z")) == "Mon Oct 5, 2026 02:07 UTC"


def test_deadline_shown_in_the_configured_time_zone(monkeypatch):
    monkeypatch.setenv("HIRING_TIMEZONE", "America/Denver")
    assert common.human_time(parse_iso("2026-10-05T02:07:00Z")) == "Sun Oct 4, 2026 8:07 PM MDT (02:07 UTC)"
