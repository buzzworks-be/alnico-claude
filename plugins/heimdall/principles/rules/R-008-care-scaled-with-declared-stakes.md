---
id: R-008
title: Care must follow the gradient a repository declares in its own ownership file
principle: P-5
severity: warning
status: draft
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository declares, in-tree and path-scoped, that some paths need
**more** named owners than others, merged work touching the more heavily owned
paths must receive **at least** as much review window per line as merged work
touching the less heavily owned ones, measured over the same window in the same
repository.

The comparison is entirely internal, and the ordering being tested is the
repository's own. There is no threshold for "enough care": this rule cannot say
a window was too short — that is R-001 — only that the repository gave *less* of
whatever it normally gives to the paths it had itself marked most heavily.

**Scope: a declaration with a gradient.** `CODEOWNERS` is the declaration that
is both path-scoped and readable from git, and the **number of owners per
pattern** is the ordering. Where there is none, or where every pattern names the
same number of owners, the outcome is **not applicable** — a flat declaration
expresses no relative priority. Report the declaration's shape as an
observation.

**Coverage is not the test.** A declaration covering nearly every changed file
used to disqualify a repository outright. Under this statement it does not
matter: the comparison is between *levels of the declaration*, not between
declared and undeclared paths, so a repository that owns everything is still
measurable as long as it owns some things more heavily than others.

**Scope: merges only.** A CODEOWNERS entry is a review-routing declaration and
bears on the review window. Work landing directly on the trunk has no review
window by construction, which is R-004's business and a different claim, and
neither a forge-mediated landing nor an applied patch carries a measurable one.

**Scope: at least three merges on each side of the median owner count.** Below
that the medians are an accident, not a pattern. Merges at the median exactly,
and merges touching no declared path, are excluded from the comparison and
reported separately.

**A merge's weight is the highest owner count among the paths it touches.**
Highest, not average: a change reaching into the most heavily owned path in the
repository is a change to that path, whatever rode along with it.

**Equal treatment is not a violation.** A repository that gives every path the
same window is not failing P-5; it is not differentiating, which may be right
for it. The rule reports only where the more heavily owned paths fall materially
*below* the less heavily owned ones.

## Why this was revised

The first statement compared **declared paths against undeclared ones**. That
needs an undeclared remainder, and a declaration worth comparing against tends
to cover everything worth owning. Measured: across seven repositories, six
declared nothing at all, and the seventh — with an exemplary declaration, seven
patterns and no catch-all — partitioned 6 merges against 0, or 7 against 1 over
its whole life. The rule could not run at any range, and briefly it was retired
for that.

Retiring it was the wrong call, for a reason worth recording: **"often not
applicable" is not a retirement criterion**, and no other rule in this frame is
held to it. On the same reading that retired R-008, four of seven active rules
returned not-applicable. The evidence said the *partition* was wrong, not that
the question was.

The declaration carries its own gradient. A repository asking for two named
owners on one path and eight on another has stated an ordering — in tree,
path-scoped, and without Heimdall inferring anything about someone else's
architecture, which is P-5's hard constraint. That gradient survives total
coverage, which is precisely the case that defeated the first design.

**Still uncalibrated, and honest about it.** On the repository that motivated
the revision the gradient runs 2, 3, 4, 6, 8 across seven crates — steep and
real — and the rule *still* returns not-applicable, because only 2 measurable
merges touch the two most heavily owned paths against a minimum of 3. Every
alternative tie-break was checked and none reaches three either, so the split
was chosen on principle rather than tuned until the data passed. What this
repository demonstrates is that the comparison can now be *formed*; that it can
be *populated* awaits a target with more merge traffic.

## Rationale

P-5 holds that care should be proportional to what is at stake, and that stakes
must be read from what the repository declares rather than inferred by Heimdall
from the code — inferring would be an opinion about someone else's
architecture, which this instrument does not hold.

That constraint is what makes the rule checkable at all, and it also makes it
unusually well-founded for a process rule: the standard being applied is not
Heimdall's. The repository wrote down that these paths need a particular
person's eyes. The rule only asks whether its own declaration is reflected in
how the work landed.

It is also a correction to the rules above it. R-001, R-002 and R-006 apply one
threshold to every path, so a repository that is careful where it counts and
quick elsewhere scores no better than one that is uniformly quick — and the
first is better practice. R-008 is the only rule in the frame that can see the
difference.

The finding it produces is narrow and should be read narrowly: *the declared
paths got less reading time than everything else*. That is an inversion worth a
person's attention, and it is not a claim that anything was unreviewed,
unsafe, or wrong.

## How to check

```sh
bin/stakes-proportionality --since "2 weeks ago"
bin/stakes-proportionality --since 2026-01-01 --until 2026-02-01
```

The script locates `CODEOWNERS` (`.github/`, root, or `docs/`) at the ref,
parses its patterns — owners are deliberately never read — classifies each merge
in the window by whether it touches a declared path, and compares the median
review window per line of the two groups. Review window is branch lifetime, as
in R-001: earliest author date on the merged side to the merge's commit date.

It reports `NOT APPLICABLE` for every scope condition above rather than a pass,
and prints the ratio it used so the reading can be argued with.

Two limitations to state in any case file citing this rule:

- **CODEOWNERS matching is a documented subset.** Gitignore-shaped patterns are
  supported; negation and some corner cases are not. A pattern the parser
  cannot express is left unmatched rather than guessed at, which biases towards
  under-reporting.
- **`--margin` and `--min-side` are not calibrated.** They were chosen, not
  swept against real history. This is why the rule is `draft`.

## Evidence to cite

- The declaration: the `CODEOWNERS` path and the patterns that matched, at a
  specific ref. Quote the lines.
- The coverage fraction, so a reader can judge whether the declaration
  discriminates.
- Both medians and the ratio, not the ratio alone.
- The merges themselves: sha, lines, window, and merge time — the ones with the
  least window per line, which are what a reader will want to look at first.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **An owner count that tracks something other than risk.** This is the
  revision's main confound and it is not visible from the file. A crate may
  carry eight owners because it is old, because two teams merged, or because
  nobody prunes the list; another may carry two because it is new and well
  understood. The count states an ordering the repository wrote down — it does
  not certify that the ordering is about stakes. Check whether the counts move
  when maintainership does before treating a finding as meaningful.
- **A declaration nobody maintains.** An owner set naming people who left reads
  identically to a live one. One observed repository had a commit removing an
  inactive CODEOWNERS entry, which is evidence of curation; absence of such
  commits is evidence of nothing either way.

- **CODEOWNERS used for notification, not gating.** Many repositories use it
  only to auto-request reviewers or route mail, with no expectation of extra
  care. It then declares *interest*, not *stakes*, and this rule's premise
  fails. Look for whether the repository says anywhere what it uses the file
  for; if it does not, the finding is at most advisory.
- **The declared owner is the author.** Nothing needs waiting for a person to
  read work they wrote. Common wherever ownership tracks who maintains an area,
  and it produces this shape while meaning the opposite.
- **Generated or mechanical content under an owned path.** A lockfile, vendored
  code, a formatter pass or a mass rename inside an owned directory needs no
  reading time, and a repository that merges it quickly is right to.
- **Incident work.** A revert, a hotfix or a rollback touching a critical path
  legitimately lands fast — speed *is* the care. Check whether the merge is a
  revert, references an incident, or is followed shortly by a fix-forward.
- **Review happened off-platform or before the push.** Approvals, pairing and
  pre-push review are invisible in git (forge blindness, as in R-001). A short
  window is not evidence that nobody read it.
- **The baseline is inflated by long-lived branches.** A handful of
  months-open, low-traffic branches on undeclared paths can lift the comparison
  side's median without anyone having reviewed anything. Look at the
  distribution, not only the median.
- **The declaration was added mid-window.** Merges predating the CODEOWNERS
  commit were made under no declaration at all. Check when the file landed.
- **Size skew between the two groups.** Window per line partly controls for
  this, but very small declared-path changes and very large undeclared ones can
  still distort the ratio. Compare the line counts before believing it.

## History

- **Draft, on derivation.** The first rule under P-5, and the first in the frame
  to use a target's own declarations as the standard. Held at `draft`
  deliberately: the extractor was verified against synthetic repositories
  covering each branch — inversion, healthy shape, blanket declaration, no
  declaration — but its two thresholds have never been swept against real
  history, and a rule whose numbers were chosen rather than calibrated may be
  raised as an observation and must not be reported as a violation. Promotion
  to `active` needs a sweep on repositories that did not shape it.
