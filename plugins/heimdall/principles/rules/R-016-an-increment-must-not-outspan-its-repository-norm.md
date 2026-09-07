---
id: R-016
title: An increment must not span more declared areas than the repository's own norm for its size
principle: P-11
severity: advisory
status: draft
introduced: 0.8.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

A landing must not reach into more of the repository's **own declared areas**
than landings of its size normally do in the same repository. "Normally" is
three conditions at once: at least three areas, at least twice the median
spread of its size band, and beyond the band's 90th percentile.

The claim is width, and nothing else. Not that the change was wrong, not that
it should have been several changes — only that, in this repository, a change
of this size does not usually touch this much, so a reader could not have taken
it as one decision the way the repository's other changes of that size can be.

**Scope: the repository's own partition.** In order: its ownership file's
path patterns, where there are at least two and no catch-all; its workspace
manifest; its top-level directories, descending into a lone code directory
until two code areas exist. Where none yields a partition, the outcome is
**not applicable**. Areas Heimdall inferred from the code would be an opinion
about someone else's architecture.

**Accompaniment is not spread.** Areas that are the repository's tests,
documentation, examples or tooling never count. A change that lands with its
tests and its docs is R-003 and R-011 being satisfied.

**Hubs are not spread.** An area most landings touch — a release-notes directory,
a core package — is cross-cutting by the repository's own behaviour, and is
excluded.

**Mechanical width is not spread.** Renames, lockfiles, manifests, changelogs;
a sweep (twenty or more files at four lines or fewer each — a lint fix, a
toolchain migration); one edit applied everywhere (the added lines collapse to
three or fewer distinct lines). All reported, none candidates.

**Stratified by size band, and the smallest band never yields a finding**, as
in R-011.

## Rationale

P-11 holds that an increment must be separable to be reviewable, and that this
is orthogonal to whether the time to review existed. This is its one rule.

The three-condition bar has a history worth keeping. The first criterion was
the band's 90th percentile alone, which flags a tenth of any distribution by
construction — a finding machine. The second was a multiple of the median
alone, which collapses onto the absolute floor wherever the median is one,
and on a 41-area workspace reported 17% of landings. Requiring all three means
a tight distribution yields nothing, a wide one yields its outliers, and the
median-of-one bands are governed by the percentile rather than the floor. On
that workspace the survivors were 6% of eligible landings, and reading them,
they were the list a reviewer would want: cross-workspace API refactors, a
toolchain migration, and a landing whose own subject called it work in
progress.

Advisory, because most of what it lists is legitimately wide, and the rule's
value is the list, not the count.

## How to check

```sh
bin/increment-spread --since "3 months ago"
bin/increment-spread --since 2026-01-01 --partition toplevel
```

The script names the partition it used, the hubs and accompaniment areas it
excluded, the mechanical landings it set aside, the distribution by band with
the bar for each, and the candidates with their spread, size and subject.

Limitations to state in a case file:

- **The partition is the measurement.** Ownership patterns declare stakes, not
  modules; a workspace manifest declares packages, fine or coarse; directories
  declare whatever the repository chose to nest. Say which was used.
- **The landing unit matters here more than anywhere.** A one-file dependency
  bump read as 586 files across 18 areas until squash landings stopped being
  grouped by time. The unit is fixed; the lesson is that a wide landing should
  be read before it is believed.
- **The mechanical exemptions are heuristics.** A dependency migration that
  touches every package for real reasons is not a sweep and is not uniform,
  and it will be listed.

## Evidence to cite

- The partition, the band, the bar, and the landing's spread and size.
- The areas touched, named as the partition names them.
- What the change was, from reading it: one concern propagated everywhere
  (an API rename, a signature change) or several concerns in one landing. The
  first is wide; the second is the shape this rule exists for, and only a
  reading can tell them apart.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A cross-cutting change that is one concern** — an API rename, a signature
  change, an error-type migration — propagated to every caller. Wide by
  necessity, reviewable as one decision once the decision is understood. The
  most common survivor on every history tried.
- **A toolchain, language-edition or dependency migration** whose per-file
  edits are too varied to read as a sweep.
- **A landing that arrived with its reasoning** — a decision record, a design
  note — saying why the change had to be wide. R-003 has been satisfied and
  the width was declared.
- **A monorepo whose declared areas are finer than its real modules**, where
  three "areas" are one component. The workspace manifest is the repository's
  statement, and it can overstate.
- **A merge of a long-lived branch**, whose first-parent diff is many landings'
  worth of work by construction. R-001 is the rule for that; this one should
  read the branch's own commits.
- **A landing the repository itself labels as batched or integrative** — a
  release integration, a sync from a fork — where the label is the reasoning.

## History

- **Draft, on derivation.** Built in the house order on three histories, and
  nearly every exemption above came from the top of a run's list rather than
  from design: a release bot's version bump touching every package, a snapshot
  regeneration, a five-file find-and-replace, a 341-file test refactor, a
  581-file lint fix, and — on a single-package repository — a change landing
  with its tests and docs, which the first version reported as width. Each of
  those became a mechanical exclusion. What remained on the largest history,
  41 of 688 eligible landings, was read and found to be genuinely wide.

  The run also exposed a defect in the landing unit shared with R-003, R-009
  and R-011 (see `principles/README.md`), which this rule's numbers were the
  first to make visible because it is the one rule for which fusing two
  landings changes the answer by an order of magnitude.

  Held at `draft`, and `advisory`: the floor, multiple and percentile were
  chosen, and the rule lists legitimately wide work by design.
