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
- **A dependency bot's bump, reverted and re-landed.** The bump has nothing
  to change: its content is the version it names, and the reason for its
  revert lives outside the change — a broken pipeline, a downstream failure,
  a bump landed out of order. The first real engagement of this rule was
  exactly this, five days apart, byte-identical, and innocent.

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

- **Held-out sweep, 2026-09-07.** Three public histories none of the rules had
  run on, each chosen for a shape and used only to confirm: K, a web framework
  with a formal deprecation policy (about a thousand landings a year, all
  applied patches); L, a continuous-delivery tool with per-path code owners
  (about two thousand, squash); M, an editor that reverts often (about four
  thousand, merges and squash).
  Engaged for the first time on a real history, on L: a bot's dependency bump
  reverted and re-landed byte-identical 118 hours later. The shape the rule
  tests, and the exemption above. Twenty reverts on M, the history chosen for
  this rule, read after the extractor was re-run untimed: none returned
  unchanged, and none re-landed by subject within the window at all — the
  reverts there are reverts, the healthy shape at scale. On K, one revert
  re-landed changed, the healthy shape. Still `draft`: its one engagement was an exemption.

- **Second held-out sweep, 2026-09-07.** Five public histories chosen for the
  shapes the drafts still needed, and used only to confirm: O, an
  infrastructure tool landing by merge commit, applied patch and squash, with
  a catch-all ownership file (about nine hundred trunk commits a year); P, a
  numerical library landing by merge commit with a formal deprecation policy
  (about fourteen hundred); Q, a UI library that reverts and re-lands, landing
  by squash, with a fixture-driven suite (about eight hundred and fifty); R,
  an inference engine whose pace tripled in the year, landing by squash (about
  eleven and a half thousand); S, a framework typing every subject, landing by
  rebase (about four thousand).
  Engaged with its shape for the first time, on S: a stack of five commits
  from one pull request, reverted together and re-landed byte-identical
  twenty hours later. The revert carries no reason, and the exemptions —
  release timing, a cause fixed elsewhere — are exactly what git does not
  record: **cannot tell**, not exempt. On R, eighty reverts and three
  re-lands, every one changed; on O, P and Q none identical. Still `draft`:
  its first non-exempt engagement is undecidable from the record, which is
  the limitation the rule states.

- **Third held-out sweep, 2026-09-09.** Six public histories chosen from a
  survey of twenty-six for the shapes the drafts still needed *and* for a
  record that carries what their exemptions turn on — reverts that say why,
  an ownership file, a stated policy — and used only to confirm: T, a
  terminal emulator landing by merge commit with an ownership file (about two
  thousand trunk commits a year); U, a JavaScript runtime landing by squash,
  typing nearly every subject and writing a reason on most reverts (about
  three thousand); V, a version-control system landing by maintainer merges
  with cover letters (about a thousand); W, an agent-framework library
  landing by squash with a release most days (about two and a half thousand);
  X, an editor landing by squash with the largest revert record in the survey
  (about nine thousand); Y, a server runtime landing by rebase under a stated
  deprecation policy (about three thousand).
  Seven byte-identical re-lands on four histories, and for the first time
  the record decided most of them. U: a test fix reverted because "random
  kills" appeared on one platform after it landed, "reverting to see if it
  will help", re-landed unchanged a day later — a diagnostic revert, the
  change cleared, exempt; and a feature reverted with "will be relanded in
  v2.8" and re-landed unchanged four weeks later — release timing, exempt.
  V: two commits reverted with "let's not use writev() for now" and re-landed
  identical four months later — a deferral, exempt. X: one reverted with "I'm
  going to remerge this tomorrow after releases so we get a full week in
  nightly" — release timing, exempt; one reverted with no reason and back
  four hours later — cannot tell. W: an infrastructure fix reverted without a
  reason and back a day later — cannot tell. Nothing on T or Y. The rule ran
  end to end on real histories: it found the shape, and where the history
  wrote down why, the listed exemptions were readable and applied. Still
  `draft`: every decidable engagement was exempt, and a rule whose findings
  have all dissolved on reading has not yet shown a finding that stands.
