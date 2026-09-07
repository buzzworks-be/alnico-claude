---
id: R-001
title: A merged branch must have had time to be read
principle: P-1
severity: warning
status: active
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

A merged branch must have been physically possible to review: it must have
existed for at least as long as a reader would need to cover the change it
carries, at a generous reading rate.

This is a **necessary-condition** test. It identifies merges that *could not*
have been reviewed, because the time did not exist. It never claims a merge was
not reviewed — only that reviewing it was impossible.

**Scope: repositories with more than one active contributor in the window.**
This rule measures a *second party's* reading window. Where the window's work
has a single contributor, no second party exists, and the outcome is **not
applicable** — not pass, not violation. Report the intervals as observations
(they still describe the workflow: a merge step that is packaging plus a gate,
not a reading window), but the rule has nothing to bind on. Establish the
contributor count before applying the rule: `bin/target-git shortlog -sn
--since=<start> --until=<end> <ref>`, discounting bots.

**Scope: landings whose branch is still in the history.** A pull request
accepted by squash or rebase leaves one ordinary commit on the trunk: the
branch, its commits and their timestamps are gone, and no merge commit exists.
Such a landing was reviewed — on the hosting platform, where this instrument
cannot see — but the interval that would prove it is not in git. It is
therefore **not measurable** by this rule, and is reported as such rather than
tested. `bin/reviewability` classifies it from the commit's committer identity
(`FORGE_COMMITTERS`), which is in git and needs no forge access.

On a repository that squash-merges everything, this rule examines **nothing**.
An `examined: 0` here is **not applicable, and emphatically not a pass** — it
means the entire review history is out of reach. A case file must say so.

**Scope: merges that share an ancestor with the trunk.** A repository can
absorb an independent project wholesale — a vendored crate, a subtree import, a
codebase moved in under a subdirectory. Such a merge has no common ancestor, so
its "branch lifetime" spans the whole existence of that other project and its
commit count is that project's work, not a branch's. A reading window computed
from it is meaningless: observed at 161, 149, 116, 301 and 467 commits per
"branch" on one workspace. These are counted and reported as **absorbed
history**, never judged.

Before this was handled, `git merge-base` exiting 1 on unrelated histories was
treated as a fatal error by the extractor, which exited 1 printing nothing at
all — so on any repository containing such a merge, this rule and R-003 were
silently unavailable and a case file could not tell that they had not run.

**Scope: merged branches only.** Work landing directly on the trunk is governed
by R-004, which makes a different and weaker claim — a branch has a review
window and a trunk commit does not. The same check produces both, but the two
must not be cited as one finding.

## Rationale

P-1 holds that work outrunning digestion is not done. The difficulty is proving
anything was digested: reading leaves no trace in a repository. What *is* visible
is when reading was impossible, and impossibility suffices — a change nobody
could have read is a change nobody did read.

For branches, the obvious measure is the gap between the last commit and the
merge, and it is the wrong one. A branch may sit open and reviewed for hours,
take a final fixup commit, and merge seconds later; the gap reads near zero and
the review happened. Measured on real history that naive test both accused
healthy merges and missed most of the unreadable ones. Lifetime against size
does not have that failure.

This rule alone is not coverage. On a trunk-based repository the majority of code
can arrive without ever passing through a branch, and reading only this rule's
result gives a clean, precise-looking number drawn from a minority of the work.
R-004 covers the remainder; a case file citing one without the other is reporting
half a picture. `bin/reviewability` prints the coverage split for that reason.

## How to check

```sh
bin/reviewability --since "<window start>" --until "<window end>"
```

For each merged branch it computes:

- **reviewable churn** — lines changed, excluding lockfiles and other generated
  artefacts whose size says nothing about reading effort
- **elapsed time** — first commit on the branch to the merge, using *author*
  dates so that a rebase rewriting committer dates cannot manufacture a finding
- **reading time needed** — churn ÷ rate

A branch fails when `elapsed < needed` and churn is at or above the floor.
Findings are tagged `R-001`; those tagged `R-004` belong to that rule.

The tool also reports **coverage**: how much churn arrived by each route. Read it
before reading the findings. A rule is only as good as what it looked at, and
this one silently examined a minority of the work until it was extended.

The default rate is deliberately several times more permissive than any review
guidance — studies of review effectiveness put the useful ceiling in the low
hundreds of lines per hour. Set high on purpose: a finding should be unarguable,
not merely suboptimal. Sensitivity is smooth rather than cliff-edged.

## Evidence to cite

The increment and **its kind**, its reviewable churn (and generated churn,
excluded), the elapsed time, the reading time needed, and the rate and floor
used. Quote the parameters: a finding is only as strong as the rate it assumed,
and a reader of the case file must be able to disagree with that assumption.

Cite the coverage split too. "9 of 34 merges" means something different when
those merges carried all the work than when they carried a third of it.

**And state what this rule cannot see: forge metadata.** Review approvals, PR
comments, and requested changes live on the hosting platform, outside the git
history that `bin/target-git` reads. A finding here means the *interval* was too
short — it can never mean no review happened on the platform. Where platform
review records are available through the evidence given to the assessment, check
them before citing; where they are not, say the case file is blind to them.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Small changes.** Below the floor, reading time is not measurable.
- **Mechanical change.** A mass rename, a formatting pass, a codegen output or a
  dependency bump can carry enormous churn at near-zero reading cost. Generated
  files are excluded by path, but a mechanical change to hand-written files is
  not detectable this way. Check what the diff contains before citing.
- **A revert** of a change that was itself read.
- **Initial import or vendored code** entering the repository. Note that a first
  commit will usually be large and will usually fail; that is an artefact of
  where history starts, not a finding about anyone's process.
- **The reader saw the work before it was committed** — pairing, or a design
  review conducted with a second contributor before the branch landed. This
  covers multi-contributor work where the reading happened outside the branch's
  lifetime. (Solo and agent-directed work is not an exemption but a scope
  question — see the Statement: with one contributor the rule is not applicable
  at all.)
- **Rewritten history.** A force-push, squash, or cherry-picked branch can
  compress apparent elapsed time. Author dates mitigate this; they do not
  eliminate it.

Because several of these are common and legitimate, this rule is a **warning**
rather than blocking: it is a strong prompt to look, not a conclusion. A case file
citing it should say what the change contained, not only how fast it landed.

## History

- Originally titled "A merge must have had time to be read", scoped to merged
  branches.
- Briefly extended to cover work landing directly on the trunk, after an
  assessment found the rule reporting a clean result on a repository where most
  churn never passed through a branch.
- Narrowed back to merged branches, with trunk work moved to **R-004**. The
  extension was right about the coverage gap and wrong about the packaging: a
  branch lifetime is a review window and a trunk commit has none, so the two were
  making different claims under one id and a case file citing "R-001" could not say
  which. The coverage the extension added is retained — `bin/reviewability` still
  examines both and prints the split.

- The solo-work case was moved from an exemption to a scope condition (outcome:
  not applicable) after two independent assessments of the same range, under the
  same pinned principles, returned different headline severities — clean and
  warning — split solely on whether the solo-work clause exempted the findings
  or merely caveated them. Both readings were defensible from the text as then
  written, which made the divergence the rule's defect, not either assessor's.
  Defining the outcome removes the ambiguity: with no second party the rule
  measures nothing, and "not applicable" says so where "exempt" and "violation
  with caveat" each smuggled in a claim the rule cannot support.

Case files stamped with an earlier `principles_sha` were produced under whichever
scope was current then; the sha in the case file says which.
