#!/usr/bin/env bash
# Prove every take-home still works the way its README says:
#   - the starter's own tests FAIL (there's work for the candidate to do)
#   - the starter with the reference solution laid over it PASSES every test, reviewer tests included
# Usage: scripts/verify_challenges.sh   (needs python3 with pytest/fastapi/httpx, and node + npm)
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cc="$root/coding_challenges"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
failures=0

# verify <label> <starter dir> <reference overlay dir> <test command>
verify() {
  local label=$1 starter=$2 overlay=$3 cmd=$4
  rm -rf "$work/starter" "$work/reference"
  cp -R "$starter" "$work/starter"
  if [ -d "$work/cache/node_modules" ]; then cp -R "$work/cache/node_modules" "$work/starter/"; fi

  if (cd "$work/starter" && eval "$cmd") > "$work/starter.log" 2>&1; then
    echo "FAIL  $label: the starter's tests pass, but they should fail until the candidate does the work"
    failures=$((failures + 1))
  else
    echo "ok    $label: starter fails as intended"
  fi

  cp -R "$work/starter" "$work/reference"
  cp -R "$overlay/." "$work/reference/"
  if (cd "$work/reference" && eval "$cmd") > "$work/reference.log" 2>&1; then
    echo "ok    $label: reference passes"
  else
    echo "FAIL  $label: the reference solution fails its tests:"
    tail -25 "$work/reference.log"
    failures=$((failures + 1))
  fi
}

pytest_cmd="python3 -m pytest -q -p no:cacheprovider"
verify "1a RSVP API" "$cc/event-rsvp-take-home/01-rsvp-api" "$cc/event-rsvp-take-home/_reviewer_only/01-rsvp-api" "$pytest_cmd"
verify "1b invoice bug hunt" "$cc/event-rsvp-take-home/02-invoice-bug-hunt" "$cc/event-rsvp-take-home/_reviewer_only/02-invoice-bug-hunt" "$pytest_cmd"
verify "3  ticket sales" "$cc/ticket-sales/ticket-sales" "$cc/ticket-sales/_reviewer_only/ticket-sales" "$pytest_cmd"

# Frontend: install once, then reuse node_modules for both runs.
mkdir -p "$work/cache"
cp "$cc/attendee-checkin/checkin/package.json" "$cc/attendee-checkin/checkin/package-lock.json" "$work/cache/"
(cd "$work/cache" && npm ci --no-audit --no-fund --silent)
verify "2  check-in list" "$cc/attendee-checkin/checkin" "$cc/attendee-checkin/_reviewer_only" "npx vitest run && npx tsc --noEmit"
rm -rf "$work/cache/node_modules"

# Nothing a candidate receives may contain reviewer material.
python3 - "$root" <<'PY' || failures=$((failures + 1))
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
bad = [str(p) for entry in json.loads((root / "coding_challenges/challenges.json").read_text()).values()
       for folder in entry["folders"] for p in (root / folder).rglob("*")
       if p.name in {"_reviewer_only", "solutions"}]
if bad:
    print("FAIL  reviewer material inside a candidate folder:", *bad, sep="\n  ")
    sys.exit(1)
print("ok    no reviewer material inside candidate folders")
PY

if [ "$failures" -gt 0 ]; then
  echo "$failures check(s) failed"
  exit 1
fi
echo "All challenges verified."
