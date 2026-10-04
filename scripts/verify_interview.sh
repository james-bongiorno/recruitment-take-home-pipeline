#!/usr/bin/env bash
# Each interview problem must fail exactly the 5 bug/implement checks and pass the other 2;
# each answer key must pass all 7. Languages without a toolchain on this machine are skipped.
set -uo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)/interview_material"
failures=0

run() { # run <label> <dir> <command...>  -> prints the PASS/FAIL lines
  local dir=$2; shift 2
  (cd "$dir" && "$@" 2>&1) | grep -E '^(PASS|FAIL) '
}

check() { # check <label> <tool> <command...>
  local label=$1 tool=$2; shift 2
  if ! command -v "$tool" > /dev/null; then
    echo "skip  $label ($tool not installed)"
    return
  fi
  local p s
  p=$(run "$label" "$root/problems" "$@")
  s=$(run "$label" "$root/solutions" "$@")
  local p_fail p_pass s_pass
  p_fail=$(grep -c '^FAIL' <<< "$p"); p_pass=$(grep -c '^PASS' <<< "$p"); s_pass=$(grep -c '^PASS' <<< "$s")
  if [ "$p_fail" -eq 5 ] && [ "$p_pass" -eq 2 ] && [ "$s_pass" -eq 7 ]; then
    echo "ok    $label: problem 5 fail / 2 pass, answer key 7/7"
  else
    echo "FAIL  $label: problem $p_fail fail / $p_pass pass, answer key $s_pass/7"
    failures=$((failures + 1))
  fi
}

check "Python" python3 python3 problem.py
check "JavaScript" node node problem.js
if node --experimental-strip-types --no-warnings -e "" 2>/dev/null; then
  check "TypeScript" node node --experimental-strip-types --no-warnings problem.ts
else
  echo "skip  TypeScript (this Node can't strip types; npx tsx problem.ts works anywhere)"
fi
check "Java" java java Problem.java
check "Go" go go run problem.go
check "PHP" php php problem.php
check "Ruby" ruby ruby problem.rb
echo "note  C# isn't run here: it needs .NET 10's 'dotnet run Problem.cs' or a console project"

if [ "$failures" -gt 0 ]; then
  echo "$failures failed"
  exit 1
fi
echo "All available interview problems verified."
