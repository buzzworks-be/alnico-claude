---
id: R-003
title: Substantial implementation arrives with the reasoning behind it
principle: P-2
severity: warning
status: active
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

**Where a repository keeps its reasoning alongside its code**, a substantial
increment of implementation must carry some change to that reasoning —
specification, decision record, requirement, design note.

The condition is not decoration. Many repositories keep their reasoning in
another system entirely and are not doing anything wrong. This rule establishes
that the convention exists in a given repository before it reports anything
against it, and stands down when it does not.

**Scope: stratified by change size, against this repository's own rate.** The
question is not "did this landing carry reasoning" but "does this repository carry
reasoning on landings of this size". Landings are binned by lines of code changed
— 1-24, 25-99, 100-299, 300-999, 1000+ — and each band is judged only where
this repository's own rate in that band reaches the convention bar. A band
below the bar is **not a pass**: it says the repository does not do this at that
size, which is a fact about the repository and not about any change in it. A
band with fewer than five landings is thin and its rate is an accident.

**The smallest band never yields a finding.** A change of 1-24 lines is a typo
fix, a version bump, a URI correction. Demanding ceremony of it is the
over-spending P-5 warns about exactly as loudly as under-spending, and the
whole value of such a change is that it is cheap.

**Why stratified — and why this rule, unlike R-011, judges every band on its
own.** A single threshold asked the same thing of a 100-line landing and a
10,000-line one, and nothing at all of a 99-line one. First measured across
three repositories and 304 landings; re-swept on the corrected landing unit
across five histories and about 2,180 landings. The *test* rate climbs to a
plateau at 100 lines, and R-011 pools the bands above it. The *reasoning* rate
does not plateau: it rose into the 1000+ band on two histories (10% → 19% →
62% on one) and fell on another. Pooling hid the one band where a repository
did explain itself — 62% against a pooled 29% — so here each band is judged
against its own rate, and the two sibling rules differ on this one point for
a measured reason.

This is also how P-5 is served without a declaration. Reading stakes off the
code is forbidden — it would be Heimdall holding an opinion about someone
else's architecture. Comparing a change against how the same repository treats
changes of the same size is not an inference about stakes at all; the standard
stays the target's own, and only the comparison group narrows. `bin/care-by-size`
is the measurement, and both bands and bar remain **chosen rather than
calibrated**, which is why this rule is still draft.

## Rationale

P-2 holds that where the reasoning lives in the repository, code arriving
without it is a gap in the process rather than a matter of taste: the reasoning
existed at the moment of writing and was discarded.

The convention is established **from practice, not from structure.** A `docs/`
directory proves nothing — it may hold a stale README. What proves the
convention is that substantial work in this repository usually does arrive with
reasoning attached. That makes the repository its own yardstick, the same way
`--baseline` does for process readings, and it means the rule cannot be pointed
at a repository whose norms it does not already fit.

The unit is an **increment**: a merged branch, or a run of consecutive commits
landing directly on the trunk within `--act-gap` minutes. Both are required.
Measured on real history, a substantial share of code can land without ever
passing through a branch, and a rule that only examined merges would silently
ignore most of the work while appearing to cover it.

## How to check

```sh
bin/reasoning-with-code --since "<window start>" --until "<window end>"
```

Two stages:

1. **Establish the convention.** Of increments carrying at least `--code-min`
   lines of code, what share also change documentation? Below
   `--convention-min`, the rule does not apply and reports so. Nothing is
   flagged.
2. **Apply it.** Where the convention holds, flag substantial increments that
   changed **no** documentation at all.

Zero is deliberate. "Not enough reasoning" is a judgement about sufficiency that
this check cannot make; "none" is a fact.

## Evidence to cite

The increment, its kind (merged branch or direct to trunk), its code churn, its
commit count, **and the convention measurement that made the rule applicable**.
A finding is meaningless without the second — a reader must be able to see that
this repository does usually attach reasoning, or the rule has no standing.

Cite the **rate** as the primary finding, not the individual increments. One
increment without reasoning is weak evidence, for the reasons below. A
persistent share of them, against a repository that mostly does attach
reasoning, is the actual signal.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A landing that is mostly documentation.** A change that *is* a document
  carries no reasoning about code, and counting it as though it did inflated the
  small bands with README edits — 67% before the exclusion against 11% after, on
  the same history. Landings at or above half documentation by line are excluded
  from the rate and from findings entirely.
- **A merge that absorbed an independent history.** Whether some other project
  kept reasoning with its code is not a fact about this repository's practice.
  Such merges have no common ancestor with the trunk; they are excluded from
  the convention rate rather than diluting it, and the count excluded is
  reported.
- **The reasoning predates the increment.** A specification written last week
  and implemented across several increments this week leaves every one of those
  increments without a documentation change. This is the most common false
  positive and the check cannot see past it — it has no way to link
  implementation back to reasoning that landed earlier. It is the main reason
  the rate matters more than any single finding.
- **The reasoning is in the commit message.** A commit body that explains why is
  reasoning, and this check only looks at files. A repository whose custom is to
  reason in messages rather than documents will be flagged wholesale, and its
  convention share may still pass because *other* work touches docs.
- **Work that owes no explanation.** Dependency bumps, mechanical refactors,
  formatting passes, generated code, reverts, and moves carry churn without
  raising a question anyone needs answered.
- **The act grouping is arbitrary.** Direct commits separated by more than
  `--act-gap` become two increments, and the reasoning may sit in the other one.
  Widen the gap and findings will merge; this is a parameter, not a truth.
- **Reasoning kept partly elsewhere.** A repository that documents some concerns
  in-tree and others externally can pass the convention test on the strength of
  the first, and then be judged for the second.

This rule is a **warning**, and it is the weakest of the three active rules. R-001
and R-002 assert impossibility — that no time existed for reading or deciding,
which no explanation can undo. R-003 asserts only that a file did not change in a
particular window, and there are several innocent reasons for that. Use it to
decide **where to look**, never as a conclusion on its own.

## History

- **Re-swept on 2026-09-02, after the landing unit was corrected.** This
  rule's own extractor grouped direct commits by time gap and, on a
  squash-landing repository, welded independent pull requests into one
  increment. A forge-committed commit is now its own increment. R-011's
  plateau pooling was tried here and reverted the same day: the reasoning rate
  keeps a gradient at the top, and pooling demoted a 62% band to "below the
  bar". A divergence surfaced in the same sweep: this rule counted code by an
  extension allowlist where R-011 counted anything not test, doc or noise, so
  the same landing could sit in different bands under the two sibling rules.
  **Closed the same day** by `bin/classify.py`, one classifier imported by
  both; verified on the history that exposed it, where the two now bin the
  same landings into the same bands with identical rates.
