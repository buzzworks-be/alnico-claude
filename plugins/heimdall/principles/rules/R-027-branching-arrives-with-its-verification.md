---
id: R-027
title: A landing that opens new ways through the code arrives with its verification
principle: P-8
severity: warning
status: draft
introduced: 0.11.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository's established practice is to ship an executable check
alongside code that adds branching, a landing that adds substantial branching
must not arrive with no test change at all — whatever its size in lines.

This is R-011 on a second axis. R-011 asks the question by size in lines and,
by design, never of a landing under 25 lines and only against its band's rate
under 100. That leaves a zone it cannot see: the change that is small in
lines and dense in decisions — a fifteen-line landing that adds eight
conditions is a different object from a fifteen-line landing that renames a
field, and R-011 treats them identically. This rule asks the same question of
that zone, measured by what the change could do rather than how long it is.

The claim is **accompaniment, and nothing else**, exactly as in R-011. Not
that the tests are good, not that the branches are covered, not that the
branching was warranted. The only thing available is that a landing which
opened new ways through the code arrived with nothing beside it that
exercises them, in a repository whose other such landings carry something.

**Scope: conditional on the repository's own practice.** The convention is
the share of landings in the window adding at least the decision floor (five,
net) that arrived with a test change, across every line band. The rule
applies only above the bar (50%); below it the outcome is **not applicable**,
and under the floor of eight such landings it is **cannot tell**. Report the
share either way; it is not a pass and not a finding.

**Scope: dense landings.** A candidate is a landing of at most 99 code lines
that adds at least five decisions net of those it removed, with no test file
changed and no test marker added inline. Landings of 100 lines and over are
R-011's, and are not reported here twice.

**The measure is net.** Decisions added less decisions removed. A landing
that swaps one condition for another, fixes lint, or migrates an API across
ten files adds no new way through the code, and the first run of the
extractor listed exactly those first when it counted gross. Net removes them
mechanically; the exemptions below cover what net cannot.

**The unit is a landing, as in R-009 and R-011.**

## Rationale

P-8 holds that where a repository verifies its work, code arrives with its
verification, and that the conditional is essential. R-011 serves it by size,
and size is the axis every band in this frame uses. This rule exists because
that axis has a blind spot that the repositories themselves do not share:
measured on four histories, the rate at which a test arrived with a landing
rose more steeply with decisions added than with lines changed, and among
landings under 100 lines the dense ones carried a test at 59-100% where the
rest carried one at 39-59%. The repositories scale their care with branching
inside the band where R-011 is silent. A dense landing that arrives bare is
therefore an anomaly in the repository's own terms, and until now nothing in
the frame could say so.

This is not a code-quality judgement, and the line is the one P-8 draws. The
number is not a claim about whether the code is too complex; it is a count of
what the landing added, used only to pick the comparison group. Whether the
branching should exist is not this instrument's question.

## How to check

```sh
bin/decision-points --since "2 weeks ago"
bin/decision-points --since 2026-01-01 --until 2026-02-01
```

Section 3 of the output establishes the convention, states the verdict —
applies, not applicable, cannot tell — and lists the candidates with their
net and gross decision counts and file counts. Sections 1, 2 and 4 are the
signal and belong in the case file as shape.

Limitations to state in any case file citing this rule:

- **The count is by token on the diff.** No parser: a keyword in a string
  counts, a language outside the family table is counted by a generic
  pattern, and configuration counts as code in lines but never in decisions.
  Read the diff before believing a number.
- **Test detection is by path convention**, as in R-011, plus the inline
  markers the classifier knows.
- **Every threshold is chosen.** The decision floor, the line ceiling, the
  bar and the sample floor were set from four histories, not calibrated
  against any that had no hand in them. This is why the rule is `draft`.

## Evidence to cite

- The convention share, the bar and the count behind it, always.
- The landing: sha, code lines, net and gross decisions, files touched, that
  the test churn was zero, and its subject.
- What the branching was, from reading the diff. A finding that does not say
  whether the new decisions were a feature's logic, a platform-specific path,
  an error-handling cascade or a deprecation guard has not been adjudicated,
  only echoed.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A refactor or a performance change under an existing suite.** The tests
  that already exercise the path are the verification, and passing them
  unchanged is the evidence. The top candidate on two of the four calibration
  histories was a performance change of this shape, and it is innocent.
- **A dependency upgrade whose API change forced edits in source.** The
  branching is the upgrade's, not the landing's; it was on the second run's
  list and reads as a bump.
- **Platform-specific code the repository's suite cannot run** — a service
  integration for one operating system, a driver for hardware the CI has
  not got. The repository may verify it by hand, and this rule cannot see
  that.
- **A deprecation guard**: branches that only warn, on a path whose removal
  is announced. The behaviour under test is unchanged.
- **A revert, or a re-land** — R-012 and R-026's shapes, verified before or
  judged there.
- **Error handling added to an existing call**, where the repository's
  practice is to test the call and not each failure branch. Read the
  repository's own tests before citing.
- **Configuration-directive parsing.** A new option in a configuration
  language adds a `case`, an argument check and an error check per option;
  the branching is the parser's boilerplate, not new behaviour, and such
  repositories test it with adapt fixtures or not at all. Two of the
  candidates on the calibration history were this shape.
- **One idiom stamped across files.** The same guard added in six places —
  a cause attached to every context cancellation, say — is six decisions
  by count and one by reading. Net removes a substitution; it cannot remove
  a repetition, and this is the shape it leaves.
- **Verification that is not a test file** — type checks, schema validation,
  a contract, a compiler — and **tests that live outside the repository**,
  as in R-011.
- **Tests added in a nearby landing.** Look at what landed next.

## History

- **Draft, on derivation.** The second rule under P-8, and the first in the
  frame to use a code measurement as anything other than a line count. It
  began as research rather than as a field report: the literature has the
  cyclomatic number as a poor product metric — a proxy for lines for most
  software, outperformed by process measures at predicting defects — and
  the question was whether it had any place in an instrument that measures
  process. The answer was as a second size axis and nothing else.

  Built in the house order on four histories none of which prompted it: a
  large application landing by squash and merge (296 landings in a year), a
  package manager landing by squash (156), a web framework landing by squash
  (190), and a small library (37). The extractor's first run counted gross
  decisions and listed as its top candidates an atomic-API substitution, a
  lint fix and a linter enabled across ten files — decisions moved, none
  added — which is why the measure is net. On net, the convention among
  landings adding five or more decisions was 100% on two histories with no
  candidate, 63% on the large application with fifteen candidates, of which
  the first was a 97-line feature adding sixteen decisions with no test, and
  cannot tell on the small library under the sample floor. The conditional
  stood down once for the right reason.

  What the runs established about the axis itself: the rank correlation
  between lines and net decisions per landing was +0.31 to +0.60; landings
  adding no decisions carried a test at 29-49% and landings adding one to
  four at 43-91%, a steeper climb than the line bands show; and among
  landings under 100 lines, the dense ones were tested at 59-100% against
  39-59% for the rest. That last gap is the rule.

  Held at `draft`: every threshold chosen, the token count unparsed, and the
  rule has engaged on one history whose candidates have been read only at
  the top of the list.

- **Read in full on 2026-09-07.** The fifteen candidates on the large
  application were read to the end rather than at the top of the list.
  Two of them carried a test after all: the repository keeps its suite in a
  directory whose name ends in "test" rather than being "test", which the
  shared classifier did not recognise — a defect with reach beyond this
  rule, since every rule that reads verification through the classifier
  saw that repository as less tested than it is. Fixed in the classifier
  the same day; the convention on that history moved from 63% to 70% and
  the candidates from fifteen to thirteen. Of the thirteen: one
  platform-specific service integration the suite cannot run, one
  dependency upgrade whose new types forced a type switch, two
  configuration-directive parsers, one idiom stamped across six files, and
  eight landings that add real behaviour with real branching and no test —
  the shape the rule describes, on a history where roughly three in ten
  such landings go untested as a matter of course. The two new exemptions
  above came from this read. Still `draft`: engaged on one history, and
  what it lists there is as much the repository's habit as an anomaly,
  which is the reading the convention share must carry into any case file.
