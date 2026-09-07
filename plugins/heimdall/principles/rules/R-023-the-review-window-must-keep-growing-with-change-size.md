---
id: R-023
title: The review window must keep growing with change size
principle: P-14
severity: advisory
status: draft
introduced: 0.10.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository lands by merge commit, the rank correlation between a
merge's size and the interval its branch waited before landing must not
fall to nothing over time: from at least a modest positive value in the
earlier half of the windows to none in the later half.

R-001 says a big change needs a longer window. This says the relationship
itself — how much longer the wait gets as the change gets bigger — is a
scalar per window, and a repository can lose it. A process in which every
change waits the same time whatever its size is the uniformity P-5 names as
the opposite of discipline, and this rule measures its arrival.

**Scope: merge-commit histories**, with at least thirty measurable merges
across the span. Squash and applied-patch landings carry no branch interval
and the outcome is **not applicable**.

**Scope: a flattening, not a flat.** A history whose correlation was never
positive is reported as an observation — a flat process, as a fact about the
repository — and never as a finding. The finding is the loss.

**Ranks, not regression**, so a reader can recompute it by hand.

## Rationale

P-14 holds that care must rise where risk rises, and size is the one risk
proxy the frame has always been allowed to use — not inferred from the
code, just counted. The elasticity of the review window to size is the
most direct expression of care scaling with change the history offers, and
its disappearance is the clearest longitudinal signal that a process has
become a queue.

## How to check

```sh
bin/care-over-time --windows 8 --window 90
```

The script prints the rank correlation per window where there are enough
merges, and the medians of the earlier and later halves.

Limitations to state in a case file:

- **The interval is branch-tip to merge**, as R-001 measures it, and carries
  R-001's confound: a branch reviewed early and fixed late reads as short.
- **Thirty merges is chosen**, as is the modest-positive threshold.
- **Platform merge queues** flatten the interval by construction and will
  read as a flat process.

## Evidence to cite

- The per-window correlations and the two medians.
- The merges in the later windows that waited least relative to their size.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A merge queue or auto-merge adopted mid-span**, which flattens the
  interval by design and is a convention change to split at.
- **A shift in what lands by merge** — large work moving to squash, leaving
  only small merges — which drains the range the correlation needs.

## History

- **Draft, on derivation.** Built on three histories: two with no merges,
  where it stood down, and one merge-commit application with 256 merges
  whose correlation was near zero in every window — a flat process, reported
  as the observation it is, not a flattening.

  Held at `draft`, `advisory`: it has seen one merge history and has not
  engaged.
