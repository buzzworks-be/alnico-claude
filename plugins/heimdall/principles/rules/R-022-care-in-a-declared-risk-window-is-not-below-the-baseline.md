---
id: R-022
title: Care in a declared risk window is not below the baseline
principle: P-14
severity: warning
status: draft
introduced: 0.10.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

In the windows a repository itself marks as risk — the run-up to a release
tag, the fortnight around a major version, the fortnight after a revert, the
week around a change it labels breaking — the test-accompaniment rate of
substantial landings must not be fifteen points below the rate everywhere
else.

The claim is a comparison against the repository's own baseline, kind by
kind. Not that care should be higher in those windows — a repository whose
care is uniform has answered P-5 its own way — only that it must not be
lower exactly where the repository said it mattered.

**Scope: risk the repository declared.** Tags, version numbers, revert
commits, breaking-change markers. Nothing inferred from the code.

**Each kind is compared separately, and a kind whose windows cover most of
the span is set aside.** A repository that tags every twelve days has no
run-up to a release distinct from the rest of its life; a repository that
labels a change breaking every other day has made breaking its normal
state. The release run-up is a quarter of the median gap between tags,
capped at fourteen days, for the same reason.

**Scope: twenty landings on each side**, above the twenty-five-line floor.

## Rationale

P-14 holds that care must rise where the repository says risk rose. This is
the direct reading, and the runs made it modest: on three histories care in
declared-risk windows was at or above the baseline every time, which is the
expected shape and worth confirming. The rule exists for the history where
it is not — where the run-up to a release is where the untested landings
concentrate — and no history tried so far was that one.

## How to check

```sh
bin/care-over-time --windows 8 --window 90
```

The script lists the risk moments by kind, the run-up length it derived, and
for each kind the landings inside and outside its windows with the test rate
on each side, marking any kind set aside for covering the span.

Limitations to state in a case file:

- **Risk is only what was declared.** A repository that declares nothing has
  no risk windows and the rule cannot tell.
- **The fortnight and the fifteen points are chosen.**
- **A revert's window is after it**; a release's is before. Both are
  assumptions about where care would show.

## Evidence to cite

- The kinds, their counts and window lengths, and for each kind the two
  rates with their landing counts.
- For a finding: what the untested landings in the risk windows were, from
  reading them.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A release cut from a branch the trunk does not show.** The run-up
  happened elsewhere; the trunk's landings in that window were unrelated.
- **A repository whose release process is itself the verification** — a
  release candidate, a soak — where care around the tag lives outside git.
- **Revert windows on a repository that reverts to unblock**, where the
  fortnight after is ordinary work.

## History

- **Draft, on derivation.** Built in the house order on three histories.
  The first version used a fixed fourteen-day window and one pooled
  comparison; on a history that tags every twelve days, 84% of landings sat
  inside a risk window and the baseline was the leftover, and on a workspace
  that labels 282 changes breaking in two years the pooled comparison could
  say nothing. Kinds are now compared separately, the release run-up scales
  to the tag cadence, and a saturated kind is set aside. Care inside was at
  or above the baseline on every history tried.

  Held at `draft`: window lengths and the margin are chosen, and the rule
  has not engaged.

- **Held-out sweep, 2026-09-07.** Three public histories none of the rules had
  run on, each chosen for a shape and used only to confirm: K, a web framework
  with a formal deprecation policy (about a thousand landings a year, all
  applied patches); L, a continuous-delivery tool with per-path code owners
  (about two thousand, squash); M, an editor that reverts often (about four
  thousand, merges and squash).
  Judged four kinds of declared risk on L across 192 moments and three on M across 98, none below baseline; on K, 74 releases, not below. Still `draft`: engaged on every history and found nothing, which is
  consistent with the three being healthy and is not yet a demonstration.

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
  Not below the baseline on any of the five, across release, post-revert
  and breaking kinds. Still `draft`: engaged everywhere, found nothing.

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
  One candidate, on U: care at 46% in the fortnight around the one major
  release against 79% elsewhere. The moment sits at the far edge of the span,
  where the repository's care was lowest in time (66% to 85% by halves), so
  the reading is confounded with time — the extractor should compare a risk
  window against its neighbours, not the whole span. Not below on T, V, W,
  X and Y. Still `draft`: one engagement, confounded.
