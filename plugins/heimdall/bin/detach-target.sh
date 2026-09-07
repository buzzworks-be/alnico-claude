#!/usr/bin/env bash
#
# Close the case: final leak sweep, then detach the target.
#
# A cold Heimdall checkout is target-agnostic — that is what makes it
# shareable. A checkout with .heimdall/ attached is not: the gitignore keeps
# the target out of history, not out of backups, archives, or anything else
# that reads the filesystem. Closing the case restores the shareable state.
#
# The ordering is the point. bin/check-no-leak reads its search terms from the
# attachment's own metadata; delete the attachment first and the guard goes
# blind. So the sweep runs BEFORE detachment, and this script refuses to
# detach past a failed sweep.
#
# Case files under cases/ carry the target and live only on this machine.
# They are listed, never silently deleted: pass --purge-case-files only once
# they have been handed over.
#
# The same ordering has a second consequence, and it is why this script refuses
# on a checkout that holds readings with nothing attached. In that state the
# guard has no identifiers to search for, so it reports success without having
# looked — and from the exit code alone, "swept and clean" and "never swept"
# are the same answer. Closing a case is a claim that the sweep happened.
#
# Usage:
#   bin/detach-target.sh                      sweep, list case files, detach
#   bin/detach-target.sh --purge-case-files   also delete them
#
# Exit: 7 sweep failed, 8 readings held with nothing to sweep against.

set -euo pipefail
# When something fails under set -e, say WHERE and under WHICH bash. Every
# macOS field report so far carried the symptom and not the line, and each
# took a guess to fix. bash 3.2 supports an ERR trap; $LINENO and
# $BASH_VERSION are enough to turn the next report into a diagnosis.
trap 'echo "heimdall: $(basename "$0") failed at line $LINENO under bash $BASH_VERSION" >&2' ERR

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Code root above; state root below. In a checkout they are the same directory;
# installed as a plugin they must not be. See bin/heimdall-state.
STATE="$("$ROOT/bin/heimdall-state")"
cd "$STATE"

# Refuse anything that is not the one flag. This used to accept any argument
# silently as "not --purge-case-files" and close the case anyway, so probing
# `detach-target.sh --help` — which does not exist — detached a live target
# instead of printing usage. Closing a case is not something to discover by
# accident from a flag that was meant to be inert.
purge=0
case "${1:-}" in
  "")                  ;;
  --purge-case-files)  purge=1 ;;
  *)
    echo "heimdall: unrecognised argument '$1'." >&2
    echo "usage: detach-target.sh [--purge-case-files]" >&2
    echo "There is no --help; this script closes a case and detaches the" >&2
    echo "target, so it refuses rather than guessing what you meant." >&2
    exit 2 ;;
esac
if [ "$#" -gt 1 ]; then
  echo "heimdall: too many arguments; expected at most --purge-case-files." >&2
  exit 2
fi

# Empty shells: a case directory holding bookkeeping and no reading. Left by
# an attach that never profiled, or by readings handed over and deleted by
# hand. A shell carries nothing about any target — the codename is drawn, the
# metadata is dates and a count — but each one holds a name out of the
# wordlist for ever and is listed as "held" at every close, and the only way
# to tidy one was by hand. The closer does it: any case directory with no
# case file is removed and named, except the case being closed right now,
# whose directory is the record that it was.
tidy_shells() {  # $1: codename to leave alone, or empty
  python3 - "$STATE" "${1:-}" <<'PY2' || true
import shutil, sys
from pathlib import Path
root, keep = Path(sys.argv[1]), sys.argv[2]
cases = root / "cases"
gone = []
if cases.is_dir():
    for d in sorted(cases.iterdir()):
        if not d.is_dir() or d.name == keep or d.name.startswith("_"):
            continue
        if any(d.glob("*.md")):
            continue
        shutil.rmtree(d)
        gone.append(d.name.upper())
if gone:
    print("heimdall: tidied " + str(len(gone)) + " empty case shell(s), no readings in any: "
          + ", ".join(gone), file=sys.stderr)
PY2
}

# Readings held on this machine, by codename. Safe to print: a codename is
# drawn at random and names no repository — that is what it is for.
held=()
total=0
for d in cases/*/; do
  [ -d "$d" ] || continue
  # `while read`, not mapfile: mapfile is bash 4+ and macOS ships 3.2, where
  # this whole script would die at the first case-file count.
  md=()
  while IFS= read -r line; do md+=("$line"); done \
    < <(find "$d" -maxdepth 1 -name '*.md' 2>/dev/null | sort)
  [ "${#md[@]}" -gt 0 ] || continue
  held+=("$(basename "$d" | tr '[:lower:]' '[:upper:]') (${#md[@]})")
  total=$((total + ${#md[@]}))
done

if [ ! -d ".heimdall" ] || { [ ! -f ".heimdall/target.json" ] && [ ! -d ".heimdall/target.git" ]; }; then
  tidy_shells ""
  if [ "$total" -eq 0 ]; then
    echo "heimdall: no case open — nothing attached, no readings held." >&2
    exit 0
  fi
  echo "heimdall: refusing to report a clean close." >&2
  echo >&2
  echo "$total reading(s) are on this machine, and they carry a target:" >&2
  printf '  %s\n' ${held[@]+"${held[@]}"} >&2
  echo >&2
  echo "Nothing is attached, so bin/check-no-leak has no identifiers to search" >&2
  echo "for. It would exit 0 without having looked, and this is the one state in" >&2
  echo "which a clean sweep and no sweep at all are indistinguishable from the" >&2
  echo "outside. Closing a case asserts the sweep happened; here it cannot." >&2
  echo >&2
  echo "Either re-attach the target these readings are about and close properly" >&2
  echo "(bin/attach-target.sh <url>, then re-run this), or hand them over and" >&2
  echo "delete them by hand. This script will not purge what it cannot sweep." >&2
  exit 8
fi

# Final sweep, while the guard still knows what to look for. A failed or
# inconsistent sweep blocks detachment: fix the leak first, or re-attach to
# restore consistent metadata, then close again.
if ! "$ROOT/bin/check-no-leak"; then
  echo >&2
  echo "heimdall: refusing to close the case over a failed sweep — detaching now" >&2
  echo "would blind the guard while a leak may be standing. Resolve it first." >&2
  exit 7
fi

# This case only. A purge that crossed cases would delete readings of a
# repository the operator was not closing — the hazard the plugin work order
# records for a shared state root, and the reason cases are separate here too.
case_dir="$("$ROOT/bin/case-dir" --check 2>/dev/null || true)"
codename="$(basename "${case_dir:-unknown}")"
if [ -n "$case_dir" ]; then
  case_files=()
  while IFS= read -r line; do case_files+=("$line"); done \
    < <(find "$case_dir" -maxdepth 1 -name '*.md' 2>/dev/null | sort)
else
  case_files=()
fi

# Mark the case closed before detaching. A case whose metadata still says open
# is indistinguishable from one abandoned mid-reading.
if [ -n "$case_dir" ]; then
  python3 - "$STATE/$case_dir/case.json" "${#case_files[@]}" <<'PY' || true
import json, os, sys, datetime
path, n = sys.argv[1], int(sys.argv[2])
if os.path.isfile(path):
    try:
        d = json.load(open(path))
    except ValueError:
        d = {}
    d["closed"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    d["readings"] = n
    json.dump(d, open(path, "w"), indent=2)
    open(path, "a").write("\n")
PY
fi

if [ "${#case_files[@]}" -gt 0 ]; then
  CODENAME_UC="$(printf %s "$codename" | tr '[:lower:]' '[:upper:]')"   # bash 3.2 has no ${x^^}
  echo "heimdall: ${#case_files[@]} case file(s) in ${CODENAME_UC}:" >&2
  printf '  %s\n' ${case_files[@]+"${case_files[@]}"} >&2
  if [ "$purge" -eq 1 ]; then
    rm -f -- ${case_files[@]+"${case_files[@]}"}
    echo "heimdall: case files purged (--purge-case-files)." >&2
  else
    echo "heimdall: kept. They carry the target — hand them over, then re-run" >&2
    echo "with --purge-case-files to remove them." >&2
  fi
fi

rm -rf .heimdall
# Files under other codenames are invisible from here otherwise, and an
# operator who purges one case can believe the machine is clean when it is not.
# Codenames are safe to print; they name no repository. The case just closed
# is not spared: an attach that never profiled is a shell like any other, and
# the first version left exactly that one standing while naming the rest.
tidy_shells ""
python3 - "$STATE" "${codename:-}" <<'PY' || true
import sys
from pathlib import Path
root, current = Path(sys.argv[1]), sys.argv[2]
cases = root / "cases"
if cases.is_dir():
    others = []
    for d in sorted(cases.iterdir()):
        if not d.is_dir() or d.name == current:
            continue
        n = len([f for f in d.glob("*.md")])
        if n:
            others.append(f"{d.name.upper()} ({n})")
    if others:
        print("heimdall: other cases still hold files on this machine: "
              + ", ".join(others), file=sys.stderr)
        print("heimdall: each is closed separately — re-attach its target to close "
              "it, or hand its files over and delete them; the shell is tidied at "
              "the next close.", file=sys.stderr)
PY

echo "heimdall: case closed — target detached, checkout is target-agnostic again." >&2
echo "heimdall: bin/attach-target.sh <url> opens the next one." >&2
