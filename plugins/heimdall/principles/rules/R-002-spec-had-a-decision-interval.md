---
id: R-002
title: A specification must have had an interval in which to be decided on
principle: P-3
severity: warning
status: active
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

When a substantial specification enters the repository, implementation built on
it must not begin before the specification could have been read. The interval
between the two is where a person decides whether the specification is right;
if implementation starts sooner than the document could have been taken in, that
decision did not happen.

Two failing shapes:

- **same act** — one increment carries both a substantial specification and a
  substantial implementation. The interval is zero by construction.
- **no interval** — the specification lands on its own, but implementation
  follows before it could have been read.

Like R-001 this is a **necessary-condition** test: it finds where a decision was
not possible, never that none was made.

## Rationale

P-3 holds that a specification and its implementation arriving together means no
decision happened between them. Writing a specification and building against it
are two acts, and the gap is not dead time — it is when someone works out
whether the plan is any good, while changing it is still cheap.

Machine-generated work removes that gap by default, because it can produce both
at a speed that leaves no room for a decision in between. The finding is not the
volume. It is the missing step the volume implies was skipped.

The second shape exists because the first alone is trivial to evade: split the
same act across two commits a minute apart and a single-commit test sees
nothing. Measuring the interval, not the packaging, closes that.

## How to check

```sh
bin/spec-decision-gap --since "<window start>" --until "<window end>"
```

For every commit changing at least `--spec-min` lines of documentation:

- if the same commit also carries at least `--code-min` lines of code, the
  interval is zero — **same act**
- otherwise, find the next commit carrying that much code, and compare the gap
  against the time needed to read the specification at `--rate` — **no interval**
  when the gap is shorter

The rate matches R-001 on purpose: the two rules make the same claim about
reading, and should not disagree about how fast a person reads.

The result is largely insensitive to its own thresholds, because the dominant
failure is structural rather than marginal — a zero interval stays zero at any
reading rate. Treat a finding that only appears at an aggressive threshold with
more suspicion than one that survives a permissive one.

## Evidence to cite

The specification commit, its documentation churn and file count, the
implementation it was built on by (the same commit, or the one that followed),
the interval, the reading time needed, and the thresholds used. Say which shape
it is: "same act" and "no interval" mean different things to whoever fixes it.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **The check matches by adjacency, not by subject.** It has no way to know the
  documentation and the code that follows describe the same thing. Documentation
  written *after* an implementation, followed shortly by unrelated code work,
  will be flagged. Read the diff before citing this rule — this is its most
  likely false positive, and the only defence is a human looking.
- **Documentation that is not a specification.** A README rewrite, a changelog,
  generated API reference or a large moved document all clear the size
  threshold. Size does not distinguish a plan from prose.
- **Squashed history — and the check is per branch, not per repository.** A
  workflow that squashes each branch to a single commit will produce "same act"
  findings even where the branch separated specification from implementation by
  days. But "is this repository squashed" is the wrong question: in an
  unsquashed history a large share of branches can still carry exactly one
  commit, and for those the same-act shape is indistinguishable from a squash —
  the one commit may itself be the collapse of separated work, or may not, and
  the shape cannot tell. So establish it per finding: a same-act finding on a
  single-commit branch carries no information, whatever the repository's overall
  convention; on a multi-commit branch it does. Only the interval shape survives
  the single-commit case.
- **A specification published rather than authored.** Where the plan was written
  and agreed elsewhere and the commit merely records it, the decision happened
  outside the repository and this rule cannot see it.
- **Deliberate spike-then-document.** Building a prototype to find out what the
  specification should say inverts the order on purpose. The document follows
  the code because that was the method.
- **The document is the deliverable, not a plan for one.** This rule assumes the
  documentation describes work to be done, so that an interval exists in which
  someone could decide whether to do it. Some documents are not plans: an
  inventory, a matrix, a register, a generated reference. Where such a document
  ships together with the code that produces, checks or gates it, the two are one
  artefact — neither is meaningful alone, and splitting them across increments
  would leave one of them broken or stale on arrival. There is no decision
  interval to demand, because there is nothing to decide between.

  The tell is whether the code *implements* the document or *maintains* it. A
  specification and its implementation are two things and belong apart; an
  inventory and the gate asserting the inventory still matches reality are one
  thing and belong together. This check cannot distinguish them — only reading
  the diff can, and that reading is required before citing this rule.
- **The decision was recorded as an open question and answered later.** This
  rule assumes deliberation looks like *specification → interval → code*. It is
  not the only shape a repository can use, and it is not the best one. A change
  can raise a numbered, identified open question in one commit and resolve it in
  a later one, so that the record carries the question, the interval, the answer
  and the reasoning that closed it — which is a *stronger* record of
  deliberation than two files landing a day apart, and R-002 cannot see it at
  all. The document and the code then land together *because the deciding
  already happened*, in the open, earlier.

  The tell is specific and checkable: an identified question — numbered,
  titled, or otherwise addressable — raised in an earlier commit, and a later
  commit that resolves that same question. Cite both commits and the interval
  between them. A vague "we discussed this" is not the exemption; a question the
  record can be pointed at is.

- **The code maintains the document rather than implementing it.** The rule
  assumes the arrow points document → code: something was specified and then
  built on. Where it points the other way — a heading is renamed and an enum is
  reordered to match, a document is restructured and a constant follows — the
  code is downstream of the prose, not built on it. Nothing was decided and
  immediately acted upon, because nothing was decided at all.

  The tell is proportion and direction together: a large document change against
  a small code change that only re-aligns names, ordering or references to it.
  Observed in the field at 513 lines of concept and decision-record prose
  against 23 lines of enum reorder and heading changes to match. Read the code
  side and ask what would break if it were reverted; if the answer is "the
  document and the code would disagree" rather than "a behaviour would be
  missing", this is the exemption.

- **Mechanical documentation change** — reformatting, link fixes, a bulk move.

This is a **warning** rather than blocking. The adjacency limitation alone means
a finding must be looked at before it is believed, and several legitimate
workflows produce the pattern honestly.

## History

- **Exemption added: the code maintains the document.** Raised by a field run
  that flagged 3 of 3 specifications in a tight range — the strongest rate this
  check can emit — where all three dissolved on reading, each on different
  grounds. One of the three was a large document change against a small code
  change that only re-aligned an enum and some headings to match it: the arrow
  pointing document ← code rather than document → code, which the rule had no
  language for. The same run also exercised the open-question exemption below
  in the field, with both endpoints inside the range (a question raised at
  12:37 with three options enumerated, resolved 96 minutes later by taking one
  of them), and found the limit of it: a commit that *raises* an open question
  is not covered by the exemption that clears the commit resolving it, and
  needs its own ground.

  `bin/spec-decision-gap` now reports each finding's interval as a share of the
  interval needed, and flags those at or above 60% as near-boundary. The same
  run dismissed a candidate partly at 23 minutes against 30.8 needed, having
  divided by hand — the identical situation that made R-006's boundary artefact
  mechanical.

- **Exemption added: decisions recorded as open questions.** Reported by an
  independent session assessing a different history, which dismissed a
  doc-and-code act (248 doc against 640 code lines) on evidence rather than
  technicality: the decision it implemented had been raised as a numbered open
  question in the previous commit and resolved 96 minutes later. The instance is
  not verifiable from this checkout and is recorded as reported; the gap is not
  in question, being visible by reading the rule — no prior exemption covered
  deliberation that happens *before* the specification is written down.

  It is the reason to prefer the exemption over widening the check: the shape it
  describes is better practice than the one the rule tests for, so a rule that
  flagged it would be penalising the stronger record.

- The "document is the deliverable" exemption was added after an assessment
  raised a finding against an increment where the documentation was an inventory
  and the code was the gate keeping that inventory true. The rule as first
  written had no way to say that was fine. Case files stamped with an earlier
  `principles_sha` were produced without this exemption.
- Squash landings are now excluded mechanically, not just cautioned about.
  `bin/spec-decision-gap` drops any commit whose committer is a hosting
  platform and reports how many it dropped; where most of a window is dropped
  the outcome is not applicable. Before this, a repository landing everything
  by squash merge reported 18 of 20 specifications built on with a zero-minute
  interval — every one of them the squash, not a decision that never happened.
- The squash caveat was narrowed from per-repository to per-branch after an
  independent observation found a history that was not squashed overall yet
  carried a majority of single-commit branches — for which the same-act shape is
  equally uninformative. The repo-wide question gave the wrong answer for most
  of that history's branches.
