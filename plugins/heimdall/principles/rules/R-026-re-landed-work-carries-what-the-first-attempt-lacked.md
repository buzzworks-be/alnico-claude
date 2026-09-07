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
