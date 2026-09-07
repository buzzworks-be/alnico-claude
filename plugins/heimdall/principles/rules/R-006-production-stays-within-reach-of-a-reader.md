---
id: R-006
title: Sustained production stays within reach of a reader
principle: P-1
severity: warning
status: active
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Over a run of closely spaced commits, the pace of production must not exceed
what a person reading continuously for the whole interval could have covered.
Where it does, the output was not absorbed as it was produced — by anyone,
including its own director — and P-1's debt began accumulating at that moment.

A **run** is a sequence of at least `--min-commits` non-merge commits, each
within `--burst-gap` minutes of the previous, carrying at least the churn
floor. Single commits are not runs: a lone large commit is R-001's or R-004's
business. This rule measures *sustained* pace, which needs a sequence.

This is a **necessary-condition** test in the same family as R-001 and R-002:
if the pace exceeded the reading ceiling, then even a dedicated reader
following the work live could not have kept up. It never claims nobody was
watching — it claims watching could not have sufficed.

**Scope: commits whose timestamp records when the work was done.** Where a
hosting platform created the commit by accepting a pull request, the timestamp
is when the work was *let in*; the branch commits carrying the real timing were
discarded by the squash. A run measured across such commits reports merge
cadence as production rate — on the history that exposed this, three pull
requests merged two minutes apart read as **242,588 lines an hour**. Nobody
wrote 6,469 lines in two minutes. `bin/digest-rate` excludes them by committer
identity and reports how many it skipped; where most of a window is skipped the
outcome is **not applicable**, and a run count of zero is not a clean result.

**Scope: this rule applies to solo and agent-directed work.** That is a
deliberate contrast with R-001 and R-004, which measure a *second party's*
reading window and go not-applicable with one contributor. Digestion is not
review: the person directing an agent is themselves the reader P-1 cares
about, and a run produced faster than its own director could read it is
exactly the case this rule exists for.

## Rationale

P-1 says work that outruns digestion is not done. R-001 and R-004 test that at
increment boundaries; this rule tests it inside the flow of production, where
machine-generated work changes the physics. A human producing work by hand is
rate-limited into absorbing it — you cannot type faster than you can think.
A directed machine has no such limit, so volume can outrun the director's
absorption *while the director is present and attentive*. The measure bounds
absorption from above (S-2's stated confound): a pace under the ceiling never
proves reading happened, but a pace over it proves reading could not have kept
up, which is the smaller and stronger claim.

The reading rate matches R-001 and R-002 deliberately: three rules making the
same claim about how fast a person reads must not disagree about it.

## How to check

```sh
bin/digest-rate --since "<window start>" --until "<window end>"
```

For each run: churn (generated files excluded) over elapsed time, as
lines/hour. A run fails when its rate meets `--read-rate`. Cite the share of
the window's churn produced at unreadable pace, alongside the individual runs —
the share is the P-1 reading; a single fast run is much weaker.

## Evidence to cite

The run's first commit, commit count, churn, elapsed minutes, computed rate,
and the parameters. State the comparison plainly: "N lines in M minutes is a
sustained rate of R lines/hour against a ceiling of C."
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Mechanical or generated churn.** A rename pass, a format sweep, codegen, or
  a vendored import produces enormous rates at near-zero reading cost.
  Generated files are excluded by path; mechanical change to hand-written
  files is not detectable and must be checked in the diff before citing.
- **Work staged after the fact.** Commit timestamps record when commits were
  made, not when work was done. A person who builds a change over days and
  then carves it into commits in twenty minutes produces a run whose pace
  describes the carving, not the production. Interleaved coherent tests and
  messages do not settle this either way; where the history suggests staging,
  say "cannot tell" rather than citing.
- **A revert or restore** of previously read work.
- **Boundary runs.** The gap, floor and minimum length are parameters; a run
  just over any of them is not meaningfully different from one just under.
- **The first-commit artefact — now mechanical.** The first commit's churn was
  produced before the measured interval began, so at short run lengths it
  inflates the rate with work the window never saw. The check reports the rate
  excluding it; where that figure falls under the ceiling the run is tagged a
  `boundary_artefact` and is exempt without further reading. This was first
  found by an adjudicator doing the arithmetic by hand; the tool now does it.

A **warning**: the staged-work confound is real and undetectable from git
alone, so a finding is a strong prompt to ask how the work was produced, not a
conclusion that it went unread.

**Expect "cannot tell" to dominate on build-then-land workflows.** Where work
is built over a session and carved into commits at the end — the normal shape
of directed agent work — commit timestamps record the landing, and most
findings under this rule will be undecidable from git. That is the rule working,
not failing: its text prefers "cannot tell" to a false finding. The deciding
evidence — session transcripts, branch push timestamps, CI runs on intermediate
pushes — lives outside the repository; where an assessment receives an evidence
bundle, that is what belongs in it, and a case file should name the missing
evidence rather than lowering the bar.

## History

- The first-commit sensitivity figure and the build-then-land expectation were
  both added after the rule's first assessment round: four candidates yielded
  three "cannot tell" (staging signals in every case, each adjudicator
  independently naming the same missing evidence) and one boundary exemption
  computed by hand that the check now computes itself. Zero citable violations
  from four flags is recorded here deliberately — a rule whose first outing
  produces mostly undecidable findings owes its readers that expectation up
  front.
