#!/usr/bin/env bash
#
# Attach a target repository to Heimdall for read-only observation.
#
# The target is cloned as a BARE mirror: no working tree, so there is no file
# for an agent to open and edit. Read-only is a property of the clone, not a
# promise. All observation goes through bin/target-git.
#
# Usage:
#   bin/attach-target.sh <git-url>   attach (or re-attach to a different URL)
#   bin/attach-target.sh             refresh the currently attached target

set -euo pipefail
# When something fails under set -e, say WHERE and under WHICH bash. Every
# macOS field report so far carried the symptom and not the line, and each
# took a guess to fix. bash 3.2 supports an ERR trap; $LINENO and
# $BASH_VERSION are enough to turn the next report into a diagnosis.
trap 'echo "heimdall: $(basename "$0") failed at line $LINENO under bash $BASH_VERSION" >&2' ERR
trap 'rm -rf "${STAGE:-}"' EXIT

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Code root above; state root below. In a checkout they are the same directory;
# installed as a plugin they must not be. See bin/heimdall-state.
STATE="$("$ROOT/bin/heimdall-state")"
DIR="$STATE/.heimdall"
TARGET="$DIR/target.git"
META="$DIR/target.json"

NO_PUSH="heimdall://push-disabled"

url="${1:-}"

if [ -z "$url" ]; then
  [ -f "$META" ] || { echo "heimdall: nothing attached. Usage: $0 <git-url>" >&2; exit 2; }
  url="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["url"])' "$META")"
fi

# Heimdall does not investigate the repository the session is standing in.
# Reading a target you can also write to is not read-only observation, it is
# editing with extra steps, and the one rule stops being structural.
project="${CLAUDE_PROJECT_DIR:-$PWD}"
if [ -d "$url" ]; then
  tgt_git="$(git -C "$url" rev-parse --absolute-git-dir 2>/dev/null || true)"
  own_git="$(git -C "$project" rev-parse --absolute-git-dir 2>/dev/null || true)"
  if [ -n "$tgt_git" ] && [ "$tgt_git" = "$own_git" ]; then
    echo "heimdall: refusing — this session is inside the target." >&2
    echo "  $tgt_git" >&2
    echo "Heimdall does not investigate the precinct it is standing in. Open a" >&2
    echo "session outside that repository and attach the path from there." >&2
    exit 9
  fi
fi

mkdir -p "$DIR"

# Clone into a staging path and swap only on success. Destroying the current
# target before the replacement is known good loses the attachment *and* leaves
# target.json describing a repo that is no longer here — and bin/check-no-leak
# reads its identifiers from that file, so a stale one makes the leak guard
# search for the wrong strings.
STAGE="$DIR/.staging.git"
rm -rf "$STAGE"

clone_fresh() {
  echo "heimdall: cloning $url (bare, read-only)"
  git clone --bare "$url" "$STAGE"
  # A bare clone leaves no fetch refspec; observation needs one to refresh.
  git --git-dir="$STAGE" config remote.origin.fetch '+refs/heads/*:refs/heads/*'
  rm -rf "$TARGET"
  mv "$STAGE" "$TARGET"
}

if [ -d "$TARGET" ] && [ "$(git --git-dir="$TARGET" remote get-url origin)" = "$url" ]; then
  echo "heimdall: refreshing $url"
  git --git-dir="$TARGET" fetch --prune --tags origin '+refs/heads/*:refs/heads/*'
else
  if [ -d "$TARGET" ]; then
    echo "heimdall: attached target is $(git --git-dir="$TARGET" remote get-url origin);" \
         "re-attaching to $url" >&2
  fi
  clone_fresh
fi

# Belt: no reachable push destination, and never a mirror push.
git --git-dir="$TARGET" remote set-url --push origin "$NO_PUSH"
git --git-dir="$TARGET" config --unset-all remote.origin.mirror 2>/dev/null || true

head_branch="$(git --git-dir="$TARGET" symbolic-ref --short HEAD)"
head_sha="$(git --git-dir="$TARGET" rev-parse HEAD)"

codename="$(HEIMDALL_HOME="$ROOT" python3 - "$META" "$url" "$STATE" <<'PY'
import json, os, random, sys
from pathlib import Path

meta, url, state = sys.argv[1:4]
state = Path(state)

# A codename is stable for the life of a case. Re-attaching or refreshing the
# same URL keeps it; case files already carry it, and a case that renamed
# itself mid-investigation would orphan them.
if os.path.isfile(meta):
    try:
        prev = json.load(open(meta))
        if prev.get("url") == url and prev.get("codename"):
            print(prev["codename"])
            sys.exit(0)
    except (ValueError, OSError):
        pass

words = [w.strip() for w in Path(os.environ["HEIMDALL_HOME"]).joinpath(
    "bin", "codenames.txt").read_text().splitlines()
         if w.strip() and not w.startswith("#")]

# Drawn, never derived. A codename computed from the URL could be reversed by
# anyone holding the wordlist, which would make the directory name a statement
# about the repository under investigation.
taken = {d.name for d in (state / "cases").iterdir()} if (state / "cases").is_dir() else set()
free = [w for w in words if w not in taken]
if free:
    print(random.choice(free))
else:
    base = random.choice(words)
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    print(f"{base}-{n}")
PY
)"

python3 - "$META" "$url" "$head_branch" "$head_sha" "$codename" <<'PY'
import json, sys, datetime
meta, url, branch, sha, codename = sys.argv[1:6]
json.dump({
    "url": url,
    "codename": codename,
    "defaultBranch": branch,
    "headSha": sha,
    "attachedAt": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
}, open(meta, "w"), indent=2)
open(meta, "a").write("\n")
PY

# The case directory and its own metadata, which records the reading and never
# the target: no URL, no owner, no paths. The target's identity stays in
# .heimdall/, which is gitignored for that reason.
case_dir="$("$ROOT/bin/case-dir")"
python3 - "$STATE/cases/$codename/case.json" "$codename" <<'PY'
import json, os, sys, datetime
path, codename = sys.argv[1:3]
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
data = {"codename": codename, "opened": now, "closed": None, "readings": 0}
if os.path.isfile(path):
    try:
        data = {**data, **json.load(open(path))}
    except ValueError:
        pass
data["codename"] = codename
json.dump(data, open(path, "w"), indent=2)
open(path, "a").write("\n")
PY

echo "heimdall: attached $url @ $head_branch ${head_sha:0:12}"
# `tr`, not ${codename^^}: case conversion in the shell is bash 4+, and
# macOS ships bash 3.2, where it is a "bad substitution" that killed this
# script on its last line. The attach had already completed; only the
# confirmation banner was lost, which is the worst kind of failure — the
# work is done and the operator is told it broke.
echo "heimdall: case $(printf %s "$codename" | tr '[:lower:]' '[:upper:]') — files under $case_dir"
echo "heimdall: read it with bin/target-git <args>"
