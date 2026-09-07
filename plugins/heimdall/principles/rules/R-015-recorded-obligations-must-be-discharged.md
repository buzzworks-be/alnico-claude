---
id: R-015
title: Recorded obligations must be discharged, not only accumulated
principle: P-10
severity: advisory
status: draft
introduced: 0.8.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository records obligations to itself in the tree — `TODO`,
`FIXME`, `HACK`, whatever it writes — the stock of them must not rise across a
span of consecutive windows: up by a quarter or more over the span, and net
positive in most windows of it.

The claim is a trajectory, which is why the severity is advisory. No marker is
a defect; a marker is a good practice. The finding is that the practice has
become a place obligations are stored rather than a place they are worked from.

**Scope: conditional on the repository using markers at all.** The script
counts markers added and removed over the span; below ten, the repository does
not evidently record obligations this way, there is no trend to read, and the
outcome is **not applicable**. A stock of zero is silence, not cleanliness —
measured: one mature history carried none over two years — and a rule that
reported it as a pass would be rewarding the repository for not writing things
down.

**Scope: the repository's own trend, never its level.** Comparing one
repository's count against another's says nothing. The default marker set is
configurable to what the repository actually writes.

**Vendored, generated, fixture and snapshot paths are excluded.**

## Rationale

P-10 holds that work begun is work owed. A marker is the smallest unit of
begun work the repository records: an obligation written at the moment someone
saw it and chose not to discharge it. That choice is often right. A stream of
them never discharged is the same shape as the branch stock in R-014, at a
finer grain and with a far weaker signal, which is why this rule is advisory
where that one is a warning.

## How to check

```sh
bin/marker-debt
bin/marker-debt --window 60 --windows 6 --markers 'TODO|FIXME|HACK'
```

The script reports, per window, the stock at the window's end and the gross
added and removed; the stock at the start of the span; and, from blame on the
files holding markers, the median and oldest age of what survives and how
many predate the whole span read.

Limitations to state in a case file:

- **The marker set is a guess** until it is set to the repository's own
  vocabulary. A repository that writes `NOTE:` for obligations reads as
  silent.
- **Word-bounded and case-sensitive**, so prose that happens to contain a
  marker word in lower case is not counted and a marker written in lower case
  is missed.
- **Blame is capped** at three hundred files; on a marker-heavy repository the
  age figures are from the files holding the most.
- **Short windows are noisy.** On a small repository the stock sat flat for
  four windows and moved in two; read the gross figures, not just the net.

## Evidence to cite

- The span, the stock at each end, and the per-window table.
- The age distribution of what survives, and specifically how many predate
  the span — those are the obligations nobody is working from.
- What kind of markers they are, from reading a sample. A finding that reports
  a count and cannot say whether the markers are index entries, deferred
  design questions, or known defects has not been adjudicated.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Markers used as an index.** Some repositories write `TODO` as a
  cross-reference or a placeholder in generated documentation; the stock
  tracks the documentation, not the debt.
- **A deliberate, maintained backlog** — a documented convention that markers
  are the issue tracker, with evidence they are worked from.
- **A window of pure feature work** on a repository that clears markers in
  dedicated passes; check the gross removals in the windows before the span.
- **Markers in a newly imported or vendored area** that the path patterns did
  not recognise as such.
- **A marker vocabulary the default set does not know**, which reads as no
  markers rather than as many.

## History

- **Draft, on derivation.** Built in the house order on three histories. It
  stood down on one (zero markers, two removed in two years), read a flat
  stock on another (ten to fifteen over a year, activity of twenty-five, five
  markers older than the span), and read a flat stock at scale on the third
  (340 to 339 over a year with 230 added and removed, median age of a
  surviving marker over two years, 257 predating the span). None met the
  growth bar; the third is the shape a reader would want to see anyway, and
  the signal reports it whether or not the rule engages.

  Held at `draft`: the growth bar and activity floor were chosen, and the rule
  has engaged nowhere.
