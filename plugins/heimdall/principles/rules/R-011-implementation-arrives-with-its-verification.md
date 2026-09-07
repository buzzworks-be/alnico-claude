---
id: R-011
title: Substantial implementation arrives with its verification
principle: P-8
severity: warning
status: draft
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository's established practice is to ship an executable check
alongside the code it covers, a substantial code landing must not arrive with no
test change at all.

The claim is **accompaniment, and nothing else**. Not that the tests are good,
not that coverage is adequate, not that the right things are covered — none of
that is visible from a repository and none of it is this instrument's business.
The only thing available is that a substantial change landed with no
verification beside it, in a repository whose other substantial changes carry
one.

**Scope: conditional on the repository's own practice.** The check measures what
share of substantial landings in the window arrive with a test change, and
applies only above the convention bar. Below it the outcome is **not
applicable** — a repository that keeps its suite elsewhere, verifies by
construction, or has decided tests are not how it works has not adopted the
standard this rule would apply. Report the share as an observation; it is not a
pass and not a finding.

**Scope: substantial landings.** Below the code floor there is nothing to owe a
check.

**The unit is a landing, as in R-009.** A merge counts once by what it brought
to the trunk; runs of consecutive direct commits group by the act gap. A branch
that puts code in one commit and its tests in the next arrived with tests.

**Scope: stratified by change size, against this repository's own rate.** The
question is not "did this landing carry a test change" but "does this repository carry
a test change on landings of this size". Landings are binned by lines of code changed
— 1-24, 25-99, 100-299, 300-999, 1000+ — and each band is judged only where
this repository's own rate in that band reaches the convention bar. A band
below the bar is **not a pass**: it says the repository does not do this at that
size, which is a fact about the repository and not about any change in it. A
band with fewer than five landings is thin and its rate is an accident.

**The smallest band never yields a finding.** A change of 1-24 lines is a typo
fix, a version bump, a URI correction. Demanding ceremony of it is the
over-spending P-5 warns about exactly as loudly as under-spending, and the
whole value of such a change is that it is cheap.

**Why stratified, and why the bands above 100 lines share a rate.** A single
threshold asked the same thing of a 100-line landing and a 10,000-line one,
and nothing at all of a 99-line one. First measured across three repositories
and 304 landings; re-swept on the corrected landing unit across five histories
and about 2,180 landings, with a different result. The test rate climbs
steeply from 1-24 (12-30%) through 25-99 (42-72%) to 100-299 (69-86%), then
**plateaus**: above 100 lines every history sat at 74-80%, and the 300-999 and
1000+ bands moved in no consistent direction from 100-299. So the 25-99 band
is judged on its own rate — the five histories straddle the bar there, and an
untested 60-line landing is an anomaly on some and unremarkable on others —
while the three bands from 100 lines up are **one regime**: reported
separately, judged against their pooled rate. Judging them separately bought
nothing and cost samples where they matter most; on a single-package
repository the top two bands held six and two landings, so its largest
changes could not be judged at all.

This is also how P-5 is served without a declaration. Reading stakes off the
code is forbidden — it would be Heimdall holding an opinion about someone
else's architecture. Comparing a change against how the same repository treats
changes of the same size is not an inference about stakes at all; the standard
stays the target's own, and only the comparison group narrows. `bin/care-by-size`
is the measurement, and both bands and bar remain **chosen rather than
calibrated**, which is why this rule is still draft.

## Rationale

P-8 holds that where a repository verifies its work, code arrives with its
verification, and that the conditional is essential.

R-003 is this rule's sibling and the reason it exists separately. R-003 asks
whether *reasoning* arrived; a repository can satisfy it entirely on prose while
shipping code nothing checks, and a case file citing a clean R-003 would be
reporting less than a reader assumes it means. That gap was raised
independently twice — by a field run watching tests land with their subject
throughout an arc with no rule able to say so, and by this repository's own
review of what `bin/unenforced-practice` already measured but no rule consumed.

The two are kept apart for the reason R-001 and R-004 are: the sentence a case
file must write differs. "The reasoning did not arrive" and "the verification
did not arrive" mean different things and imply different remedies.

This rule is deliberately weak, in the same way R-003 is weak. It establishes
that a file did not change within a landing. It is a pointer to where to look,
never a conclusion — and the *Not a violation* section below is longer than the
rule because most of what it flags on a healthy repository will be innocent.

## How to check

```sh
bin/tests-with-code --since "2 weeks ago"
bin/tests-with-code --since 2026-01-01 --until 2026-02-01
```

The script computes landings, classifies each changed path as test, code,
documentation or noise (vendored, generated, lockfiles, binaries), establishes
the convention from the window's own substantial landings, and disables itself
below the bar.

Two limitations to state in any case file citing this rule:

- **Test detection is by path convention.** Common layouts and suffixes are
  recognised; a repository that keeps tests beside their subject under a name
  the pattern does not know will read as untested. Check the layout before
  believing a finding.
- **The floors were chosen, not calibrated.** They are R-003's, borrowed because
  the rules are siblings and comparable figures are worth more than separately
  tuned ones. This is why the rule is `draft`.

## Evidence to cite

- The convention share and the bar, always — a finding is meaningless without
  the practice that licenses it.
- The landing: sha, code lines, that the test churn was zero, and its subject.
- What kind of change it was, from reading the diff. A finding that does not say
  whether the code was new behaviour, a refactor or a rename has not been
  adjudicated, only echoed.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A refactor that changes no behaviour.** The existing tests *are* the
  verification, and passing them unchanged is the evidence the refactor was
  sound. Changing them would weaken it. This is the most important entry here:
  flagging a clean refactor inverts good practice, and a rule that did so would
  be worse than no rule.
- **A rename, a formatter pass, or generated code.** Nothing to verify that the
  existing suite does not already cover.
- **A dependency bump or configuration change** classed as code by path
  heuristics.
- **A revert**, which restores a state that was verified before.
- **Verification that is not a test file.** Type checking, schema validation,
  contract tests, property assertions, a gate script, a compiler that will not
  build the wrong thing. A repository may verify by construction, and this check
  sees only files whose paths look like tests.
- **Tests that live outside the repository** — a separate suite, a QA
  environment, an integration harness elsewhere.
- **Tests added in a nearby landing.** The landing unit catches a branch that
  splits code and tests across commits, but not a follow-up branch merged
  shortly after. Look at what landed next before citing.
- **A spike or prototype the repository marks as such**, where the intent was to
  find out rather than to ship.
- **Infrastructure, migrations and fixtures** that the repository verifies by
  running rather than by testing.

## History

- **Draft, on derivation.** The first rule under P-8, and the closing of a gap
  that two independent sources found within a week of each other: a field run
  that watched `test_evidence.py` (+133) land beside `evidence.py` (+314)
  throughout an arc and noted that nothing in the frame could say so, and this
  repository's own observation that `bin/unenforced-practice` already computed
  the tests-alongside-code rate for R-009 — where it answers who *carries* a
  practice — with no rule asking whether an increment had one. The measurement
  existed before the rule, which is the second time that order has produced a
  better rule than the reverse would have.

  Verified in both directions: on a synthetic repository with the convention
  established at 80%, the one substantial landing without tests is reported; on
  real history the convention measured 42% and the rule **stood itself down**,
  which is the outcome that matters most. R-003 did the same thing at 32% on an
  arm's-length repository, and a conditional rule that never declines to apply
  is not conditional.

  Held at `draft`: the floors are borrowed from R-003 rather than calibrated
  here, and test-path detection has been exercised on two repositories.

- **Re-swept on 2026-09-02, after the landing unit was corrected.** The unit
  had welded squash landings merged within an hour into one; on one history
  over a year, 722 binned landings became 1,131 and this rule's candidate list
  grew from 152 to 227. Re-measured across five histories of different landing
  shapes (~2,180 landings): the gradient the first sweep reported as monotonic
  is a climb to a plateau at 100 lines. From there the bands are judged
  against their pooled rate; below, unchanged. The convention bar and band
  edges were kept — the 25-99 knee straddles the bar on five histories, which
  is what a bar at the knee looks like. Still `draft`: the pooling boundary was
  read off five histories, not calibrated against any that had no hand in it.
