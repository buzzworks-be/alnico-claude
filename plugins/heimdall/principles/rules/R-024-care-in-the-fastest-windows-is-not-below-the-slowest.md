---
id: R-024
title: Care in the fastest windows is not below the slowest
principle: P-15
severity: warning
status: draft
introduced: 0.10.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Rank a repository's windows by how much landed in each. The
test-accompaniment rate of substantial landings in the fastest quarter of
windows must not be fifteen points below the rate in the slowest quarter.

The claim is about the repository's own pace and its own care, compared
across its own time. Not that fast is bad — the fastest windows on one
history tried were also the best tested — only that where the two move
against each other, the history has traded rigor for throughput and no
single window would show it.

**Scope: eight windows with ten substantial landings each.** Below that the
outcome is **cannot tell**, and on a young or quiet history that is the
ordinary outcome rather than a gap.

**An observation travels with it:** the rate in the earlier half of the
windows against the later half, in time rather than by pace. A drift down
is worth a reader's eye whatever the pace comparison says.

## Rationale

P-15 holds that rigor must not erode as pace rises. Every window-based
reading in the frame compares a window against the one before it; a slow
erosion is invisible to that, because each window is only slightly worse
than its predecessor. Ranking windows by throughput and comparing the ends
is the smallest test of the trajectory that a reader can check by hand.

## How to check

```sh
bin/care-over-time --windows 8 --window 90
```

The script prints the per-window table, names the slowest and fastest
windows with their pooled test rates, and prints the earlier-half and
later-half rates as an observation.

Limitations to state in a case file:

- **Windows are calendar quarters by default** and a regime change inside
  the span — a documented convention switch — makes the comparison one of
  two processes. Split at it.
- **Fifteen points is chosen.**

## Evidence to cite

- The per-window table, the two pooled rates and their landing counts.
- What landed untested in the fastest windows, from reading a sample.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A release burst of mechanical landings** — version bumps, generated
  updates — that inflates a window's throughput with work that owes no
  test. The floor excludes the small ones; the large ones a reader should
  name.
- **A convention change inside the span** that moved tests elsewhere.

## History

- **Draft, on derivation.** Built on four histories. Two were too quiet to
  tell. On a busy application the fastest two windows were twelve points
  below the slowest — under the bar — with a time drift from 77% to 71%
  reported alongside. On a busy workspace the fastest windows were the best
  tested, 72% against 51%, and care rose over time from 52% to 64%.

  Held at `draft`: the margin is chosen and the rule has not engaged.
