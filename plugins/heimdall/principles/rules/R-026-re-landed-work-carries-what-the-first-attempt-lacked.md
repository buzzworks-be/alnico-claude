---
id: R-026
title: Re-landed work carries the verification the first attempt lacked
principle: P-9
severity: warning
status: draft
introduced: 0.10.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository ships tests with its code, work that was reverted and
then landed again — changed or not — must carry a test change, if the first
attempt carried none.

The revert was the repository saying the first attempt was wrong enough to
remove. The re-land is the attempt that learned, or did not, and a test
arriving with it is the smallest visible sign of which.

**Scope: conditional on the test convention**, established as R-011
establishes it — half of the window's substantial landings carry a test
change, from at least ten measured. Below that, not applicable.

**Scope: re-lands `bin/reversal` can pair with their revert** — byte-identical
by patch-id, or same subject — and re-lands of twenty-five source lines or
more.

## Rationale

P-9 holds that a process which never revisits does not correct, and R-012
finds the shape where nothing was learned at all: the same diff returning.
This rule asks a smaller question of the re-lands that did change: whether
what changed included the thing that would have caught the first attempt.
It says nothing about whether the test is any good — that is R-011's
boundary and this rule stays behind it.

## How to check

```sh
bin/reversal --since "6 months ago"
```

After the R-012 section the script prints the convention it measured, then
each revert-and-re-land pair with the test and source churn of both
attempts, marking those where verification was added.

Limitations to state in a case file:

- **Pairing is by patch-id or subject**, with R-012's limitations.
- **Tests are recognised by the shared classifier's paths and inline
  markers**; a repository that verifies another way reads as untested.

## Evidence to cite

- The three shas, both attempts' test and source churn, and the convention.
- What the revert was for, from its message: a test could only have caught
  some reasons.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A revert taken for a reason no test could catch** — release timing, a
  dependency, a flaky pipeline, a policy hold. The first exemption and the
  most common.
- **Verification that arrived in a neighbouring landing**, before or after
  the re-land.
- **A re-land whose change was to the tests' subject** so that existing
  tests now pass — the verification existed; the code was wrong.

## History

- **Draft, on derivation.** Built alongside P-14 and P-15 as the small rule
  P-9 lacked. No real history in the calibration set had a pairable re-land
  in its window; it engaged on a synthetic fixture — twelve tested landings,
  one untested one reverted and re-landed changed and still untested — and
  reported it. The fixture also found a defect: "later than the revert" was
  a timestamp comparison, and a re-land in the same second as its revert
  was invisible. It is log order now.

  Held at `draft`: it has never engaged on a real history.

- **Held-out sweep, 2026-09-07.** Three public histories none of the rules had
  run on, each chosen for a shape and used only to confirm: K, a web framework
  with a formal deprecation policy (about a thousand landings a year, all
  applied patches); L, a continuous-delivery tool with per-path code owners
  (about two thousand, squash); M, an editor that reverts often (about four
  thousand, merges and squash).
  Formed its comparison on a real history for the first time, on K: one
  change reverted and re-landed changed, thirty code lines with eighteen of
  tests where the first attempt had eight with nineteen — verification on
  both sides, a pass. On L the one pair was a bot's dependency bump of six
  code lines, reverted and returned identical, untested both times: under
  the twenty-five-line floor, so listed and not judged. Twenty reverts on
  M, none re-landed within the window. The sweep changed the no-finding
  line: it had said no re-land arrived without a test change, when what it
  can say is that none *above the floor* did, and the ones under it are
  listed beside it. Still `draft`: one engagement, a pass; it has yet to
  find on a real history what it found on its fixture.

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
  Engaged on three. O: one re-land without tests, a generated dependency
  sync — a change no test bears on, exempt. S: five re-lands of 35 to 91
  code lines, each reverted by its own pull request with no reason in the
  message — cannot tell. R: two re-lands of kernel work, 110 and 127 code
  lines, without tests at a 56% convention — unadjudicated. Still `draft`:
  engaged with its shape, nothing decidable from git.

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
  Re-lands on four histories, every one carrying tests where the convention
  holds (U at 74%, W at 68%, Y at 60%); X and V stand down on convention.
  Still `draft`: it has yet to find on a real history what it found on its
  fixture.
