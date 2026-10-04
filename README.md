# Recruitment take-home pipeline

[![Tests](https://github.com/james-bongiorno/recruitment-take-home-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/james-bongiorno/recruitment-take-home-pipeline/actions/workflows/tests.yml)

Run take-home coding challenges entirely on GitHub. One click gives a candidate their own private repository with the challenge in it. They submit by opening a pull request, and everything they do lands in a log you can read. At the deadline their access becomes read-only, and when you're done reviewing, one more click cleans everything up.

- **Candidate repos made for you:** a private repo per candidate, containing only the starter files for the challenges you pick. Answer keys never leave this repo.
- **Submission by pull request:** candidates work on a branch and open a PR. You review a normal diff.
- **Activity log:** PRs opened, closed, reopened or merged, every commit, force-pushes, and anything pushed straight to `main`, all with timestamps. Anything after the deadline is flagged.
- **Snapshots:** a copy of their latest work and a patch of just their changes, saved here every time they push.
- **Deadlines:** access drops to read-only automatically, and unaccepted invitations are cancelled.
- **Close-out:** removes access, archives their repo and files the candidate under `reviewed/`.
- **Included:** three sample take-homes (backend, frontend, data layer) and a live-interview problem in 8 languages, each with rubrics and answer keys.

Built on GitHub Actions and a GitHub App, with Python standard library scripts. **Free to run:** a free GitHub organization holds the candidate repos.

---

## Contents

1. [How it works](#how-it-works)
2. [What's in this repo](#whats-in-this-repo)
3. [Read this first: public vs private](#read-this-first-public-vs-private)
4. [Setup](#setup) (about 20 minutes, once)
5. [Day to day](#day-to-day)
6. [Adding your own challenges](#adding-your-own-challenges)
7. [Security model](#security-model)
8. [Limitations and trade-offs](#limitations-and-trade-offs)
9. [Costs](#costs)
10. [Troubleshooting](#troubleshooting)
11. [Working on the pipeline](#working-on-the-pipeline)

---

## How it works

```
You (Actions tab of your private copy)    Hiring org (free GitHub organization)         Your private copy of this repo
──────────────────────────────────────    ─────────────────────────────────────         ──────────────────────────────
Create coding challenge  ───────────────► <last>-<first>-code-challenge (private)  ───► candidates/under-review/<last>_<first>/
                                            main = starter files only                      candidate.json, activity.log
                                            candidate invited with write access
                                                     │
                                          candidate pushes a branch, opens a PR to main
                                                     │
Sync submissions (hourly) ◄───────────────  PR events, commits, a snapshot of the PR  ───► activity.log, submission/, submission.patch
                                            at the deadline: access becomes read-only
                                                     │
Close out candidate  ───────────────────►  access removed, repo archived           ───► moved to candidates/reviewed/
```

There are three moving parts:

1. **This repo (your private copy)** holds the challenges, the answer keys, the workflows and a folder per candidate. Candidates never get access to it.
2. **A separate free GitHub organization** holds one private repo per candidate. Keeping it separate means a candidate is never a member of anything that matters, and outside collaborators on a free org's private repos cost nothing.
3. **A GitHub App** lets the workflows create repos and manage collaborators in that org. Its token lives only in this repo's secrets.

## What's in this repo

| Path | What it is |
|---|---|
| [`.github/workflows/`](.github/workflows/) | `create-challenge.yml`, `sync-submissions.yml`, `close-out.yml`, plus `tests.yml` (CI for this repo) |
| [`scripts/`](scripts/) | `create_challenge.py`, `sync_submissions.py`, `close_out.py`, shared code in `hiring/`, tests in `tests/`, and helper shell scripts |
| [`coding_challenges/`](coding_challenges/README.md) | Three sample take-homes plus `challenges.json`, which numbers them for the workflow |
| [`interview_material/`](interview_material/README.md) | A 45-minute live problem in JavaScript, TypeScript, Python, Java, C#, Go, PHP and Ruby, with answer keys and an interviewer guide |
| [`candidates/`](candidates/README.md) | Written by the pipeline: one folder per candidate |

## Read this first: public vs private

**This repo is public so you can copy it. Never run the pipeline in a public repo.** The pipeline commits candidates' names, GitHub usernames, activity logs and code into `candidates/`. The workflows check for this and refuse to run in a public repository.

**The sample answer keys are public.** That's fine for trying the pipeline out. Before you hire for real, write your own challenges, or at least change these ones (see [Adding your own challenges](#adding-your-own-challenges)). The same goes for the interview problem.

## Setup

You'll need a GitHub account, and it helps to have a second account you can use as a pretend candidate for testing.

### 1. Make your own private copy

On this repo's page, click **Use this template → Create a new repository**, choose **Private**, and name it something like `hiring`.

> Don't **fork** it. A fork of a public repo is public, and GitHub won't let you make it private.

If you don't see "Use this template," the repo isn't marked as a template. Instead, create an empty **private** repo and push a copy:

```bash
git clone https://github.com/james-bongiorno/recruitment-take-home-pipeline.git hiring
cd hiring
git remote set-url origin https://github.com/<you>/hiring.git
git push -u origin main
```

### 2. Create a free organization for candidate repos

1. Go to **github.com/organizations/plan**, choose **Free**, and give it a neutral name, since candidates will see it (for example `yourcompany-hiring`).
2. In the new org: **Settings → Member privileges**:
   - **Base permissions: No permission**
   - **Repository creation:** untick it for members
3. **Don't** turn on **Settings → Authentication security → Require two-factor authentication**. GitHub removes outside collaborators who don't have 2FA, which would lock candidates out.

### 3. Create a GitHub App

1. Go to **github.com/settings/apps/new**. To have the org own the app instead, use **Org settings → Developer settings → GitHub Apps → New GitHub App**.
2. Fill in:
   - **Name:** anything unique on GitHub, for example `yourcompany-hiring-bot`. Candidates see it as the creator of their repo.
   - **Description:** something neutral, for example "Sets up and manages coding challenge repositories for candidates."
   - **Homepage URL:** your private copy's URL is fine.
   - **Webhook:** untick **Active**.
3. **Repository permissions.** Leave everything else at "No access."

   | Permission | Access | Used for |
   |---|---|---|
   | Administration | Read and write | Creating candidate repos, adding and removing collaborators, archiving |
   | Contents | Read and write | Pushing the starter files, downloading snapshots |
   | Pull requests | Read-only | Reading the candidate's PRs |
   | Issues | Read-only | PR history (opened, closed, reopened, force-pushed) comes from the issue events API |
   | Metadata | Read-only | Set automatically |

4. **Where can this GitHub App be installed?** Choose **Any account**. That lets you install it on your hiring org even when your personal account owns the app. Nobody else can use it without your private key.
5. Click **Create GitHub App**. On the next page:
   - Note the **App ID** near the top.
   - Scroll to **Private keys → Generate a private key**. A `.pem` file downloads.

### 4. Install the app on the hiring org

From the app's page: **Install App → your hiring org → All repositories**. It needs all repositories because it creates new ones.

You don't need to install it on your private copy. The workflows use the built-in `GITHUB_TOKEN` to write there.

### 5. Add secrets and variables to your private copy

In your private copy: **Settings → Secrets and variables → Actions**.

| Name | Type | Value |
|---|---|---|
| `HIRING_APP_PRIVATE_KEY` | **Secret** | The whole `.pem` file, including the `-----BEGIN…` and `-----END…` lines |
| `HIRING_APP_ID` | Variable | The App ID from step 3 |
| `HIRING_ORG` | Variable | The hiring org's name, exactly as GitHub shows it |
| `HIRING_TIMEZONE` | Variable (optional) | How deadlines are shown, as an IANA name like `America/Denver` or `Europe/London`. Leave it out for UTC. |

To copy the key exactly on a Mac, run `pbcopy < ~/Downloads/<app-name>.*.private-key.pem`, then paste it in. **Delete the `.pem` file afterwards.** If a key ever leaks, generate a new one on the app's page and delete the old one.

### 6. Check Actions is allowed

In your private copy: **Settings → Actions → General**.
- **Actions permissions:** allow all actions, or at least GitHub-authored ones. The workflows only use `actions/checkout` and `actions/create-github-app-token`, both pinned to commit SHAs.
- **Workflow permissions** can stay on the read-only default. Each workflow asks for `contents: write` itself.

### 7. Try it

1. **Actions → Create coding challenge → Run workflow.** Fill in a name, challenge `1`, any GitHub username, and tick **Dry run**. The run's **Summary** shows exactly what would be created, including the list of files.
2. Run it for real with your **second** GitHub account as the candidate, and a deadline of `1` hour.
3. From that second account: accept the invitation, create a branch, change a file, open a PR into `main`, then close it and reopen it.
4. **Actions → Sync submissions → Run workflow.** Then look at `candidates/under-review/<last>_<first>/activity.log`.
5. Once the hour has passed, run **Sync submissions** again. The second account should now be read-only.
6. **Actions → Close out candidate** with the folder name. Afterwards, delete the archived test repo in the hiring org if you like.

> If you use your *own* account as the test candidate, you're an owner of the hiring org, not an outside collaborator. The log won't show "accepted the invitation," and the deadline step has nothing to change. Everything else works the same.

## Day to day

### Sending a challenge

1. Get the candidate's **GitHub username**. GitHub can only add outside collaborators by username, not by email.
2. **Actions → Create coding challenge → Run workflow:**

   | Input | Example | Notes |
   |---|---|---|
   | First name / Last name | `James` / `Bongiorno` | Used as typed in the candidate's README, so capitalize them. The repo becomes `bongiorno-james-code-challenge`. Accents and apostrophes are fine. |
   | Challenges | `1, 3` or `1 3` | Numbers from [`challenges.json`](coding_challenges/challenges.json). Several challenges go in one repo, and their time boxes add up. |
   | GitHub usernames | `james-bongiorno` | Comma or space separated if more than one |
   | Deadline hours | `48` | Counted from when you run the workflow |
   | Dry run | ☐ | Shows the plan and creates nothing |

3. GitHub emails the invitation. Send the candidate a note too, for example:

   > Hi James, I've set up your coding challenge in a private GitHub repository. You should have an email from GitHub inviting you to it. If not, sign in and go to https://github.com/&lt;your-hiring-org&gt;/bongiorno-james-code-challenge/invitations. Everything you need is in the README there, including how to submit. You have 48 hours from now. Reply here if anything is unclear.

**The clock starts when you run the workflow,** so run it right before you send that note.

### What the candidate sees

A private repo with one starter commit by your app. It contains the challenge folders and a README with their name, the time box, the deadline in your time zone, and how to submit: create a branch, commit as they go, and open a PR into `main` without merging it. The "send it back as a zip" lines in each challenge's README are rewritten to point at the PR.

### While they work

**Sync submissions** runs every hour, and you can also run it by hand. For each candidate under review, it:
- adds new events to `activity.log`
- refreshes `submission/` (their latest PR's files) and `submission.patch` (only their changes compared with the starter) whenever they push
- at the deadline, makes their access read-only and cancels unaccepted invitations

It rebuilds everything from GitHub's own history each time, so a late or skipped run never loses an event. The folder layout and how to read the log are in [`candidates/README.md`](candidates/README.md).

### Reviewing and closing out

1. Start with `submission.patch` and `activity.log`, then score with the challenge's `_reviewer_only/RUBRIC.md`.
2. To run the reviewer tests, clone their repo (as an org owner you have access) and copy in the test files from `_reviewer_only/`. Do this on your own machine, never in a workflow here, because it's untrusted code.
3. **Actions → Close out candidate** with the folder name (for example `bongiorno_james`) and an optional note. It runs a final sync, removes access, archives their repo and moves the folder to `candidates/reviewed/`.

## Adding your own challenges

A challenge is a folder with the candidate's part and a reviewer part:

```
coding_challenges/my-challenge/
├── README.md              ← for you: what it is, what you checked
├── my-challenge/          ← what the candidate gets (README, starter code, starter tests)
└── _reviewer_only/        ← RUBRIC.md, reference solution, extra tests (never sent)
```

Then give it a number in [`coding_challenges/challenges.json`](coding_challenges/challenges.json):

```json
"4": {
  "title": "My challenge",
  "area": "Backend",
  "minutes": 60,
  "folders": ["coding_challenges/my-challenge/my-challenge"]
}
```

- **`folders`** lists exactly what gets copied, and each folder lands at the top of the candidate repo under its own name. Use more than one folder for multi-part challenges.
- **`minutes`** adds up in the candidate's README when you send several challenges.
- **Nothing reviewer-only can be sent.** Anything named `_reviewer_only` or `solutions` is skipped, and the script stops if one turns up anyway. `node_modules`, `.venv`, `dist`, caches and `.db` files are skipped too.
- **Two phrases are rewritten automatically** in the candidate's READMEs: "(you have 48 hours to send it back)" and any line starting with "- Send it back as a zip." So the same README works whether you send the challenge by hand or through the pipeline.
- **Also update the workflow's input hint:** change the `challenges` input description in `.github/workflows/create-challenge.yml` so it lists your numbers.

**What makes a good take-home** (the samples follow this pattern):
- A short written spec with exact strings or status codes, so your reviewer tests can run against anyone's structure.
- One or two real bugs to find, with failing starter tests, so you see debugging as well as building.
- A clear time box, plus "tell us what you'd do next."
- A `NOTES.md` from the candidate: decisions, time spent, AI use.
- A `_reviewer_only` folder with a rubric, a reference solution and extra tests.

Then prove it works: add a `verify` line for it in [`scripts/verify_challenges.sh`](scripts/verify_challenges.sh), which checks that the starter fails and the reference passes. CI runs it on every push.

## Security model

- **Candidates never touch this repo.** They're outside collaborators on one repo in a separate org, so nothing they can do reaches your challenges, answer keys or other candidates.
- **Candidate repos have no workflows and no secrets.** All the watching happens from here. A workflow inside a candidate repo would be a hole: a candidate with write access could edit it on their branch and read any secret it uses.
- **The app token is short-lived and scoped to the hiring org.** Writes to this repo use the job's own `GITHUB_TOKEN`.
- **Only starter files are pushed,** and the script checks again before pushing that no reviewer material made it in.
- **Workflow inputs never touch the shell directly.** Names and usernames are passed through environment variables, which blocks script injection from a crafted name. Usernames are also validated against GitHub's rules.
- **Snapshots are extracted defensively.** Only regular files are written: no symlinks, no paths that escape the folder, nothing over 2 MB, and no `.github/`, `node_modules` or virtualenvs.
- **The pipeline refuses to run in a public repository**, so candidate data never ends up public by accident. Setting the variable `ALLOW_PUBLIC_REPO=true` overrides this, but don't.
- **Actions are pinned to commit SHAs.** Let Dependabot or Renovate bump them.

## Limitations and trade-offs

- **Free plans have no branch protection on private repos.** A candidate *can* push straight to `main` or merge their own PR. The log records both, and whether a candidate follows the branch-and-PR instructions is a useful signal in itself.
  - *Alternative:* to block it outright for free, invite candidates with **read** access and have them **fork** the repo and open a PR from the fork. That needs "Allow forking of private repositories" turned on in the hiring org, `"permission": "pull"` in `create_challenge.py`, and fork instructions in the candidate README. GitHub deletes the fork when you remove their access.
  - *Or* put the hiring org on a paid plan and add a ruleset to `main`. But see [Costs](#costs): each candidate then uses a paid seat.
- **The deadline starts when you create the challenge,** not when the candidate accepts.
- **Hourly checks:** access drops to read-only at the first sync after the deadline, up to an hour late. Anything pushed in that window is marked `[after deadline]`.
- **Some times are approximate.** "Accepted the invitation" is stamped when the sync noticed it. Commit times come from the commits themselves, which a candidate can set to anything. PR events and force-pushes come from GitHub and can't be faked.
- **One repo per candidate per run.** To re-send, close out first, or use a different name.

## Costs

| | Free plan | Notes |
|---|---|---|
| Hiring org | $0 | Free orgs allow unlimited outside collaborators on private repos. On a paid plan, each candidate would use a seat while they have access. |
| Actions minutes | Your private copy uses about **720 minutes a month** for the hourly sync, out of 2,000 free | Change the cron in `sync-submissions.yml` to every 2 hours (`23 */2 * * *`) to halve that. The sync is skipped entirely until `HIRING_ORG` is set. `tests.yml` adds about 3 minutes per push. |
| GitHub App | $0 | |

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| **Stopped: public repository** | You're running it in a public repo. Make a private copy (step 1). |
| `Not Found` when getting the token | The app isn't installed on the hiring org, or `HIRING_ORG` doesn't match the org's name exactly |
| Token step fails with an error about the private key or a JSON web token | `HIRING_APP_PRIVATE_KEY` is incomplete or has the wrong value. Paste the whole `.pem`, including the BEGIN/END lines. Check that `HIRING_APP_ID` is the App ID and not the Client ID. |
| `Resource not accessible by integration` | The app is missing a permission. Fix it on the app's page, then accept the new permissions on the installation (**org Settings → GitHub Apps → Configure**). |
| **Partly created** | The repo was made, but pushing or inviting failed. Delete that repo in the hiring org and run again. |
| **No GitHub account found** | Typo in the username, or an email was entered instead |
| Commit step can't push | Something else pushed to `main` at the same moment. It retries 3 times. Re-run if it still fails. |
| Candidate can't find the invitation | Send them `https://github.com/<org>/<repo>/invitations`. They must be signed in as that username. |

## Working on the pipeline

```bash
# Try a challenge without GitHub (prints the plan and the file list)
python3 scripts/create_challenge.py --first James --last Bongiorno --challenges "1 3" --usernames james-bongiorno --dry-run

# Pipeline unit tests (a fake GitHub API: creation, events, snapshots, deadline, close-out)
pip install pytest && pytest scripts/tests

# Every take-home: starter fails, reference passes (needs pytest, fastapi, httpx, and Node 20+)
scripts/verify_challenges.sh

# Every interview problem: 5 fail / 2 pass, answer key 7/7 (skips languages you don't have installed)
scripts/verify_interview.sh
```

All four run in CI (`.github/workflows/tests.yml`) on every push and pull request.
