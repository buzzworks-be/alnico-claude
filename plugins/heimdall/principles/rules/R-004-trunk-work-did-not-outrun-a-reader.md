---
id: R-004
title: Work landing on the trunk must not outrun a reader
principle: P-1
severity: warning
status: active
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where work lands directly on the trunk, it must accumulate slowly enough that a
person could have kept up with it: the elapsed time over which an increment was
committed must be at least as long as a reader would need to cover what it
carries, at a generous reading rate.

An increment here is a **run of consecutive commits landing directly on the
trunk**, separated by no more than the act gap.

**Scope: repositories with more than one active contributor in the window.**
Like R-001, this rule measures whether a party other than the author could have
kept up; with a single contributor there is no such party and the outcome is
**not applicable** — report the volumes and elapsed times as observations of the
workflow, not as findings. Establish the contributor count first, discounting
bots.

**Scope: commits a person actually pushed.** A commit created by a hosting
platform when it accepted a pull request — a squash or rebase merge — is *not*
work landing directly on the trunk, however much it looks like one in the
graph. Something was proposed and a review window existed; it is simply not in
git. Such landings are excluded by committer identity
(`FORGE_COMMITTERS` in `bin/reviewability`) and reported as not measurable.

This scope line was bought expensively. Without it, on a repository landing 96%
of its work through reviewed pull requests, this rule produced **119 findings
covering 295,341 lines — every one of them false**, and the coverage split
reported 100% direct against a true figure near 2%. Squash merge is a
hosting-platform default, so the failure was not exotic; it simply had not been
measured against.

**This rule is not about the route.** Committing straight to the trunk is a
deliberate, well-regarded practice, and some repositories adopt it explicitly
and document the choice. A finding never means "this should have been a pull
request". It means the volume that arrived could not have been absorbed as it
arrived — which is equally true of a badly-sized pull request, and is R-001's
business there.

## Rationale

P-1 holds that work outrunning digestion is not done. R-001 tests that for
merged branches, where a branch's lifetime is a genuine review window: someone
could have read the change at any point during it.

Trunk commits have no such window. The commit *is* the landing; there is no
interval between proposing and accepting, because nothing was proposed. That
premise is what the scope line above protects: it holds only for a commit a
person pushed. Applied to a squashed pull request the sentence is simply
untrue — something was proposed, and reasoning from a false premise produced
findings that were confident, numerous and wrong. So the
question has to change. Not "was there time to review this before it landed" —
there never is — but "did this arrive slowly enough that a person following the
work could have kept up".

That is a weaker claim than R-001's, and separating the two rules is what keeps
it honest. Both were briefly one rule. A case file citing it could not say which
claim it was making, and the two are not interchangeable: "no review window
existed" and "nobody could have kept up" mean different things to whoever reads
the case file and different things about what to change.

The separation is not a way of excusing trunk-based work. On the history this
rule was calibrated against, the largest unreadable increments by far were on
the trunk, not on branches — an order of magnitude larger than the worst branch
finding. Trunk work is where the volume hides.

## How to check

```sh
bin/reviewability --since "<window start>" --until "<window end>"
```

The same check serves R-001 and R-004; findings are tagged with the rule that
governs them, and the summary reports each separately along with the coverage
split — how much churn arrived by each route.

For each trunk increment it computes:

- **reviewable churn** — lines changed, excluding lockfiles and other generated
  artefacts whose size says nothing about reading effort
- **elapsed time** — first commit of the run to the last
- **reading time needed** — churn ÷ rate

An increment fails when `elapsed < needed` and churn is at or above the floor.

Note what a single large commit scores: elapsed time zero, so it fails whenever
it clears the floor. That is the intended reading — a thousand lines arriving in
one commit offered nobody a moment to keep up — but it means `--act-gap` and the
floor deserve a look before the findings are believed.

The rate matches R-001 and R-002 on purpose: rules making the same claim about
how fast a person reads should not disagree about it.

## Evidence to cite

The increment's first commit, its commit count, reviewable churn, elapsed time,
reading time needed, and the rate, floor and act gap used. Say that it is
**R-004** and therefore about trunk work — a reader who sees only "had no time
to be read" will assume a review window was missed, which is not the claim.

Cite the coverage split alongside it. R-004 findings mean something different in
a repository where a tenth of the work lands on the trunk than in one where most
of it does.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Small changes.** Below the floor, reading time is not measurable.
- **Mechanical change.** A mass rename, formatting pass, codegen output, vendored
  update or dependency bump carries churn at near-zero reading cost. Generated
  files are excluded by path; mechanical changes to hand-written files are not
  detectable this way. Read the diff before citing.
- **The initial import.** A repository's first commits are large by necessity and
  will always fail. That is an artefact of where history begins.
- **The act gap is a parameter, not a truth.** Commits separated by slightly more
  than the gap become two increments and each may pass; slightly less and they
  merge into one that fails. Where a finding sits near the boundary, say so.
- **A revert** of a change that was itself read.
- (Solo and agent-directed work is not an exemption but a scope question — see
  the Statement: with one contributor the rule is not applicable at all.)

A **warning**, not blocking, for the same reason as R-001: several of these are
common and legitimate, and a finding is a prompt to look rather than a
conclusion.

## History

- The solo-work scope condition was added together with R-001's, after two
  independent assessments split on whether solo work exempted findings or merely
  caveated them. The same ambiguity lived here word for word; fixing one rule and
  not the other would only have moved the next divergence.
