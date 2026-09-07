---
id: R-025
title: Care must not quietly withdraw from an area
principle: P-15
severity: warning
status: draft
introduced: 0.10.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Under the repository's own partition — its ownership patterns, its workspace,
its top-level directories — no area's test-accompaniment rate may fall by
twenty points from the first half of the span to the second while the
repository's overall rate falls by less than five.

The claim is divergence: one area losing care that the repository as a whole
kept. P-5 permits differentiated care where the repository declares it; an
area whose care withdrew with nothing declared is the undeclared
differentiation P-5 names.

**Scope: ten substantial landings in each half for the area**, and a
partition the frame can read (as R-016 reads it).

## Rationale

P-15 holds that rigor must not erode as pace rises, and erosion is rarely
uniform: it starts where attention left. A repository-wide rate can hold
steady while one component quietly stops being tested, and nothing in the
frame that reads the whole window would see it.

## How to check

```sh
bin/care-over-time --windows 8 --window 90
```

The script names the partition, prints the repository's two half-rates, and
lists any area whose rate fell by the margin against a steady whole.

Limitations to state in a case file:

- **The partition is the measurement**, with R-016's caveats: ownership
  patterns declare stakes, a workspace declares packages, directories
  declare whatever was nested.
- **Halves, not windows.** A withdrawal in the last quarter is diluted by
  the one before it.

## Evidence to cite

- The area, its two rates and landing counts, and the repository's.
- What landed untested in the area's second half.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **An area that changed character** — a package that became generated, a
  directory that became configuration — where the test rate fell because
  the work no longer owes one.
- **An area being wound down**, where the repository documents it.
- **Tests that moved** to another area's directory under a restructuring.

## History

- **Draft, on derivation.** Built on four histories; on the two with enough
  landings, five and thirty-five areas were judged and none had withdrawn.

  Held at `draft`: margins chosen, no engagement yet.
