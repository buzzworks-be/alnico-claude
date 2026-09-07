---
id: R-009
title: A practice the repository relies on must be carried by something in the repository
principle: P-6
severity: advisory
status: draft
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository observably relies on a practice — it holds on the large
majority of changes in the window — something **in the tree** should require,
prompt or produce it: a pipeline, a hook, a change template, a decision-record
template, a written convention, an ownership file.

Where the practice holds and no such carrier exists, the practice is being
carried by the people currently doing the work. That is a finding about
**durability**, not about quality: the work in the window is fine, and nothing
in the repository would keep it that way if the people changed.

**Scope: practices the repository evidently relies on.** Below the reliance bar
the outcome is **not applicable** — a practice followed a third of the time is
not something the repository depends on, and its missing carrier says nothing.

**Scope: enough changes to establish a rate.** Below the minimum, not
applicable.

**This rule computes nothing per contributor.** P-6 forbids resolving
consistency into a comparison of identifiable people, and this rule satisfies
that by construction rather than by restraint: it reads paths and configuration,
never authorship. There is no contributor floor because there is no contributor
axis. Any future rule under P-6 that *does* look at people inherits the
constraints recorded with the project's roadmap, and this one does not
need them.

## Rationale

P-6 holds that discipline belonging to the system survives turnover and
discipline belonging to individuals leaves with them, and that no single
increment shows which of the two a repository has.

The direct approach — compare how different contributors work — is closed off,
and rightly: it produces a league table, its confounds are severe (people work
on different things for reasons that have nothing to do with care), and it
cannot be reported without re-identifying someone.

So the rule attacks the other half of the principle. A **carrier** is a fact
about the tree, and its absence is checkable. The inference runs backwards, in
the frame's usual shape: the check cannot show that a practice lives in habit,
only that nothing in the repository would keep it going. That is a narrower
claim and a defensible one.

It is the first rule in the frame whose finding is about the *future* rather
than the window. Every other rule says something did or could not have happened.
This one says a currently-healthy practice has nothing holding it up — which is
why its severity is advisory: nothing is wrong yet, and the remedy is cheap
while it is still true.

## How to check

```sh
bin/unenforced-practice --since "2 weeks ago"
bin/unenforced-practice --since 2026-01-01 --until 2026-02-01
```

The unit is a **landing**, not a commit: each merge counts once, measured by
what it brought to the trunk, and runs of consecutive direct commits are grouped
by the act gap. "Did this change arrive with tests" is a question about the
change as it landed — a branch that puts code in one commit and its tests in the
next arrived with tests, and counting the commits separately would score it 50%.

The script classifies each changed path in a landing as code, test,
documentation or noise (vendored, generated, lockfiles), measures how often
code-bearing landings arrive with tests and with documentation, and looks in the
tree for carriers: CI configuration whose content names a test runner, commit
hooks, change and document templates, and written conventions
(`CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md`) whose content names tests or
documentation.

Two practices only, in this version: tests alongside code, and reasoning
alongside code. Both are cleanly detectable from paths and both have
identifiable in-tree carriers.

Three limitations to state in any case file citing this rule:

- **Carrier detection is a documented subset, and it errs in both
  directions.** Standard locations and common runner names are recognised; a
  Makefile target, a bespoke script or an unusual CI path is not — undetected
  means *not found*, never *not present*, which over-reports. It can also
  *under*-report: a file matching a carrier pattern suppresses a finding whether
  or not it genuinely carries the practice, and detection tests presence, never
  strength. A `CLAUDE.md` that mentions documentation in passing counts the same
  as one that requires it. Check the named carrier before accepting a clean
  result, exactly as you would check for a missing one before accepting a
  finding.
- **The reliance bar and the minimum change count were chosen, not calibrated.**
  This is why the rule is `draft`.
- **The inverse case is out of scope.** A carrier that exists while the practice
  does not hold — decorative machinery — is a different finding and this rule
  does not report it.

## Evidence to cite

- The practice rate: how many code-bearing changes carried the practice, out of
  how many, over what window.
- The carriers actually searched for and not found — naming the search, so a
  reader can tell a genuine absence from a gap in detection.
- Where a carrier *was* found for one practice and not another, say so: it is
  the strongest form of this finding, because the repository has demonstrated it
  knows how to institutionalise a practice and did not do it for this one.
- Never a contributor, a name, a handle, or a count from which either could be
  worked out.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Enforcement lives on the forge.** Branch protection, required reviewers,
  required status checks and organisation-level workflows are invisible from
  git. This is the largest exemption and the most common: a rigorously governed
  repository can have no in-tree carrier at all. A finding means "no carrier in
  the tree" and never "not enforced" — say it that way in the case file.
- **Organisation-level tooling.** Shared CI templates, a platform that injects
  checks, a monorepo parent that owns the pipeline. Same shape as above, and
  equally invisible.
- **The toolchain enforces it structurally.** Some practices need no carrier: a
  build that will not pass without tests, a typed language, a generated-code
  gate. The practice is held by physics rather than by policy.
- **The practice is younger than the window.** A convention adopted recently may
  have its carrier still in flight. Check when the practice started; direction
  of travel matters and this rule cannot see it.
- **The practice is intrinsic to the repository's content.** A documentation
  repository will show "reasoning alongside code" on every change for reasons
  having nothing to do with discipline.
- **A carrier exists that the parser did not recognise.** Given the detection
  subset, this is the first thing to check and the most likely innocent
  explanation for a surprising finding.
- **A deliberate decision not to automate.** A small team may have decided that
  a convention is cheaper than a gate, and recorded that decision. That is a
  legitimate position — the finding still stands as an observation about
  durability, and the recorded decision is what makes it advisory rather than
  anything more.

## History

- **Amended, on first contact with real history.** Two defects, both found by
  running the rule rather than by reading it.

  **Commit selection.** The check took work with `--no-merges --first-parent`,
  which on a repository that lands everything through pull requests selects
  *nothing* — every first-parent commit is a merge. It reported zero
  code-bearing changes over an 84-commit window: blind on the most common
  workflow there is. It failed safe (not applicable rather than a false clean)
  only because the minimum-count floor caught it; a handful of stray direct
  commits would have produced a rate computed from an unrepresentative sample.
  Replaced with the landing unit above, which also fixes a distortion nobody had
  noticed: a branch splitting code, tests and documentation across three commits
  used to score 33% on a trunk-based repository and now scores 100%, correctly.

  **Carrier over-matching.** The decision-record template pattern matched any
  file under a decisions directory whose *name contained* "template", so a
  record titled "template execution remodel" registered as a template and
  suppressed a finding. Tightened to require `template` to be the file rather
  than a word in its title, and the limitation above now states the
  under-reporting direction, which the first version claimed did not exist.

- **Draft, on derivation.** The first rule under P-6, and the first in the frame
  whose finding concerns durability rather than what happened in the window. It
  is also the first written specifically to avoid a measurement: the direct
  reading of P-6 — comparing contributors — is what the principle forbids, so
  the rule was built to answer the same question from configuration instead.
  Verified against synthetic repositories covering each branch: practice with no
  carrier, practice with carriers, practice below the reliance bar, and too few
  changes. Held at `draft` because the reliance bar and minimum count were
  chosen rather than swept, and because its detection subset biases towards
  over-reporting, which needs measuring on real repositories before it can be
  active.
