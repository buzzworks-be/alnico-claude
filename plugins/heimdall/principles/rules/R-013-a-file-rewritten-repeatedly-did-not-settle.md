---
id: R-013
title: A file majority-replaced repeatedly in one window did not settle
principle: P-9
severity: warning
status: draft
introduced: 0.8.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

A file whose content was **majority-replaced** — at least half its prior lines
deleted — by three or more distinct landings inside one window was not
understood when it was first written, or its purpose moved under it.

The claim is about the file, not about any landing. No single one of the
rewrites is a finding; the finding is the sequence.

**Scope: files of twenty lines or more** before each rewrite. Below that any
edit is a majority.

**Scope: rewrites, not touches.** This rule is deliberately narrower than its
ancestor. The frame retired a *rework commit ratio* — the share of landings
that touch a previously-touched file — because it measured 84–98% on every
history tried and reported that iteration exists rather than what it cost.
`bin/reversal` prints that retired figure beside this one on every run, so a
reader can see the two are not the same measure: on the three histories this
rule was built against, the retired figure read 89–96% and this one flagged
one, zero and one file.

**Reverts do not count.** A revert replaces a file by design. It is P-9's
correction shape, and counting it here would make the healthy response to a
bad rewrite look like a further bad rewrite.

## Rationale

P-9 holds that the shape of correction is what shows a process learns. This is
the second of the two shapes that show it did not: not backed out and returned,
but replaced and replaced and replaced, inside a window short enough that the
replacements are the same piece of work failing to land.

The measure is deliberately blunt, and stated as such. It cannot tell a file
under active design — where three rewrites in a month is how design happens —
from a file nobody understood. The *Not a violation* section is where that
distinction lives, and it is longer than the rule.

## How to check

```sh
bin/reversal --since "3 months ago"
```

For each landing and each file it changed, the script reads the file's line
count at the landing's parent and the lines deleted; a landing that deletes
at least half is a rewrite. Files with three or more rewrites from distinct
landings are listed with their kind (code, test, doc) and the landing shas.

Limitations to state in a case file:

- **Line count is the unit.** A file whose lines are long, or generated, or
  reformatted, reads as rewritten by a formatter pass. Check the diff.
- **Cost.** One read per changed file per landing; on a busy history a year
  takes minutes.

## Evidence to cite

- The file, the count, and the landing shas in order.
- What each rewrite was, from reading the diffs: the same function restated,
  a different approach, a rename in place. A finding that lists three shas
  and says nothing about what changed between them has not been adjudicated.
- Whether the rewrites came from one arc of work or from unrelated ones. Three
  rewrites inside one design effort are one story; three from three unrelated
  changes are the finding.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A file under active design.** A new module in its first month is rewritten
  because that is how a design converges. The tell is the file's age: a file
  created inside the window and rewritten inside it is being designed. A file
  years old rewritten three times in a month is the shape this rule is for.
- **A test file rewritten alongside its subject.** The one file this rule
  flagged on a large workspace was a test file under a test-refactor series.
  Tests are rewritten when their subject's interface is, and when the test
  style is; neither says the subject did not settle.
- **A generated file, a lockfile, a snapshot, a fixture.** Excluded by path
  pattern where the pattern knows the name; check any that got through.
- **A configuration file every feature touches** — a command registry, a
  route table, a changelog. Its churn is the repository's, not its own.
- **A formatter or lint pass** counted as a rewrite because it touched most
  lines without changing what they do.
- **A file that was split or merged** — a majority deletion that moved the
  content rather than replacing it.

## History

- **Draft, on derivation.** Written after `bin/reversal` ran on three
  histories. The threshold (three rewrites at half the file, twenty-line
  floor) was chosen, not swept; what was measured is that the rule
  discriminates where its retired ancestor did not — one, zero and one file
  flagged against 89%, 91% and 96% for the old measure on the same windows.
  Before reverts were excluded the first history flagged two: a publish-flow
  module and its test, mid-rework, and the module's third "rewrite" was the
  revert of the second — which is why reverts were excluded, and why "under
  active design" leads the exemptions.

  Held at `draft`: thresholds unswept, and the rule has yet to flag a file that
  a reading confirmed as the shape it describes rather than an exemption.
