---
id: R-005
title: A living document keeps its claims about the code true
principle: P-3
severity: warning
status: active
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*.md"
  - "**/*.rst"
  - "**/*.adoc"
---

## Statement

A living document that names code paths is making claims about the repository,
and those claims must stay true: the named files must exist, and the document
must not stand still for weeks while the code it names is substantially
rewritten.

Two findings of different strength, and a case file must not blur them:

- **Phantom reference** — the document names a file that existed when the
  document was last written and no longer does. The claim is simply false; no
  threshold is involved.
- **Drift** — the named files have accumulated substantial churn since the
  document last changed, *and* the document has stood still for a meaningful
  time behind its subject's most recent change. Both conditions, because drift
  alone describes a well-maintained document that names many files: churn since
  its latest touch is a document keeping up, not one left behind.

Unlike the other rules, this one reads the repository's **state at a ref**, not
an increment. Rot is invisible in any single increment — no commit records the
update that did not happen — and only accumulates into visibility.

## Rationale

P-3 rules out documentation grown faster than it can be read, "which becomes
documentation nobody reads and then documentation nobody maintains." This rule
measures the terminal stage of that decay: the point where the documentation
asserts things about the code that are no longer so. A stale document is worse
than none — an absent document sends the reader to the code, a rotten one sends
them somewhere the code has left.

The crux is linkage: which code does a document describe? Guessing from
directory layout would manufacture findings from fiction. The link is instead
derived from the document's own content — **a named path is a claim**. This is
deliberately narrower than "describes": a document can rot without naming any
file, and this rule will not see it. Narrow and checkable beats broad and
imagined.

## How to check

```sh
bin/doc-drift                      # state at the target's HEAD
bin/doc-drift --ref <ref>          # state at the head of the range under assessment
```

For each document that names at least one code path, at the given ref:

- **phantoms** — named paths absent from the tree, counted only when the path
  existed in the tree at the document's own last change (this guards against
  counting placeholders, templates and paths that never existed)
- **drift** — churn in the named files since the document's last change
- **staleness** — days between the document's last change and the named files'
  most recent one

A document is adrift when drift ≥ `--drift-min` **and** staleness ≥
`--stale-min`, or when it carries any phantom.

**Generated documents are checked, and marked.** A document carrying a
generation marker (`@generated`, "do not edit by hand") rots for its reader
exactly as a hand-written one does — but the remedy differs: re-run the
generator, do not edit the prose. The check tags such findings and states the
remedy, and a case file must carry the distinction; "this report is stale" and
"this document is unmaintained" are different asks to different people. A
generated document adrift may also indicate the generator itself is no longer
being run, which is a process observation worth making separately.

**Record-kind documents are excluded by default**: decision records,
changelogs, postmortems, review records. They are records of a moment,
immutable by convention, and their staleness is their nature. `--include-records`
overrides.

The tool reports how many documents were **unlinked** — naming no code at all.
Unlinked is unmeasured, not passing: those documents can rot invisibly to this
rule, and a case file should say how much of the documentation surface that is.

## Evidence to cite

For a phantom: the document, the named path, the commit that removed the path,
and what the document tells its reader to do with it. For drift: the document,
its last-change date, the named files, the churn and staleness figures, and the
thresholds used.

Cite drift as a **rate and a worst-list**, not as individual accusations — one
drifting document is weak evidence, a growing share of them is the trajectory
P-3 warns about. Phantoms are individually citable; the claim is checkable and
false.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Named is not described.** A contributing guide naming a file as an example,
  a tutorial citing a path illustratively — the reference is incidental and the
  document owes it no currency. Read the sentence around the path before citing
  drift; the tool matches strings, not intent.
- **The churn missed the described aspect.** A document describing a module's
  contract stays true through an internal refactor of any size. Drift bounds
  the *opportunity* for rot; it never demonstrates it. This is the rule's
  weakest joint and the reason drift findings are cited as a rate.
- **A renamed file.** The content lives on elsewhere; the phantom is real but
  shallow — the document needs a path update, not a rewrite. Check for a rename
  (`bin/target-git log --follow --diff-filter=AD -- <path>`) before presenting
  a phantom as deep rot.
- **A document scheduled for the same fate as its subject.** Where the code
  named was removed as part of retiring a feature and the document is the
  feature's own, the finding is "delete this document", not "update it" — still
  worth saying, but a different ask.
- **Record-kind documents** that slipped past the path filter — check what the
  document is before citing; the exclusion list is a heuristic.
- **Thresholds are parameters.** A document at 195 lines of drift or 13 days of
  staleness is not meaningfully different from one just over; where a finding
  sits near a boundary, say so.

A **warning**. Phantoms are hard facts and drift is a bounded inference; the
rule as a whole is a strong prompt to look at the documentation surface, and
for phantoms specifically, to fix a claim that is now false.

## History

- The generated-document category was added after the rule's first full
  assessment: two findings were generated compliance reports, stale because
  their generator had not been re-run, and the rule as first written could only
  ask for them to be "updated" — the wrong ask, aimed at the wrong thing.
