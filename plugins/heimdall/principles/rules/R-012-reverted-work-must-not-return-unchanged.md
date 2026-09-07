---
id: R-012
title: Reverted work must not return unchanged
principle: P-9
severity: warning
status: draft
introduced: 0.8.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

A change that was backed out must not land again, within the window, with
the same content: the same diff, line for line, as the one that was reverted.

This is a **hard fact about the record**, in the shape of R-005's phantom
half. The comparison is by patch-id — a fingerprint of the diff independent of
sha, date and message — so equality means the change came back with nothing in
it altered. It says nothing about why it was reverted, whether the revert was
right, or whether the re-land was: only that between the two events, the
change itself did not move.

**Scope: reverts whose target can be identified.** A revert names its target by
git's own trailer, or — on a squash-landing repository, which keeps only the
branch's subject — by quoting the subject of the reverted commit. Where
neither resolves to a commit in the history, the revert is reported and the
rule cannot run on it.

**A re-land that differs is not this rule's concern.** Reverted, changed, and
returned is the healthy shape P-9 describes; `bin/reversal` reports it as an
observation so a reader can see the correction happened, and it is never a
finding.

## Rationale

P-9 holds that a process which never revisits does not correct, and that the
concern is not correction happening — that is the healthy shape — but the two
shapes that show nothing was learned. This is the first of them. A revert is
the repository saying, in the record, that something was wrong enough to
remove. The same content returning unchanged is the record saying that
whatever was wrong was not in the change. Both can be true; the rule asks the
reader to find out which.

It sharpens now for a specific reason. Generated work is cheap to regenerate,
and a revert followed by an identical re-land is the shape a regenerate-and-
retry loop leaves behind when the retry is the same as the first attempt.

## How to check

```sh
bin/reversal --since "3 months ago"
bin/reversal --since 2026-01-01 --until 2026-04-01
```

The script lists every revert in the window with the target it resolved, then
for each target fingerprints the reverted diff and searches later commits in
the window for the same fingerprint. An exact match is a candidate finding. A
later commit with the same subject and a different fingerprint is reported as
an observation.

Two limitations to state in any case file citing this rule:

- **Resolution by quoted subject is a heuristic.** It takes the most recent
  earlier commit whose subject matches the quoted one, which is right for the
  common `Revert "<subject>"` form and wrong for a subject that recurs.
- **The window bounds both events.** A revert of a change older than the
  window, or a re-land after it, is out of reach; the script says "target not
  in window" for the first case and nothing for the second.

## Evidence to cite

- The three shas — original, revert, re-land — and the interval between the
  last two.
- The revert's stated reason, quoted from its message, and whether the re-land's
  message addresses it. A finding that does not say what the revert was for
  has not been adjudicated, only echoed.
- Anything that landed between the revert and the re-land touching the same
  paths, since that is where the "fixed elsewhere" exemption lives.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A revert taken for release timing**, with the change re-landed after the
  release. The content was never wrong; the schedule was. The revert message
  usually says so.
- **A re-land after the cause was fixed elsewhere.** The reverted change
  exposed a defect in something it depended on; that was fixed; the change
  returned unchanged because it was right all along. Check what landed between
  the two events.
- **A revert of a revert as a merge mechanic** — undoing an accidental revert,
  or restoring a branch that was closed by mistake.
- **A revert taken to unblock**, re-landed once the blocking condition (a
  failing unrelated test, a broken pipeline, a policy hold) cleared.
- **A re-land whose difference is outside the diff** — a changed commit
  message, a different author, a rebased base. Patch-id ignores all of those,
  which is the point of using it, and none of them is a change to the work.

## History

- **Draft, on derivation.** The first rule under P-9. Built in the house
  order — extractor first, run on three histories of different landing shapes
  (a small package workspace landing by squash, a mature single package
  landing by merge commit, a large workspace landing by squash at over a
  thousand landings a year) — and it produced **no finding on any of them**:
  nine reverts across the three, none re-landed identical, one re-landed
  changed. That is the expected rate for a rule about a rare shape, and no
  objection: R-008 has never populated either. What the runs did produce was
  the resolution rule for squash repositories, where a revert's body carries no
  trailer and the quoted subject is all there is — two of five reverts on the
  large workspace resolved only that way.

  Held at `draft` until it has engaged on a real history.
