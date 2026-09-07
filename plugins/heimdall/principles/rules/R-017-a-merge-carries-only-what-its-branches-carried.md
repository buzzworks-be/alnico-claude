---
id: R-017
title: A merge carries only what its branches carried
principle: P-12
severity: warning
status: draft
introduced: 0.9.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

A merge commit must not change a file that no conflict required it to
change. What the automatic merge of its two parents would have produced is
recomputed; whatever the merge actually landed beyond that, in a file the
merge did not have to decide about, is content from neither branch.

The claim is provenance, and nothing else. Not that the extra content was
wrong, not that it was hidden on purpose — only that it existed on neither
branch and was therefore reviewed on neither, and that the commit carrying
it says "merge".

**Scope: repositories that land by merge commit.** A squash or applied-patch
landing has no second parent and no automatic merge to recompute; on such a
history the outcome is **not applicable**. Merges that absorbed an unrelated
history (no merge-base) and octopus merges are skipped and counted.

**A conflict resolution is not this rule's concern.** In a file the automatic
merge could not decide, a hand-written resolution is expected; it is also
content from neither branch, and `bin/merge-provenance` reports its size so a
reader can look at a large one, but it is never a finding by itself. Only
changes **outside** any conflicted file are candidates.

**Noise paths are excluded** — lockfiles, vendored and generated trees — by
the shared classifier.

## Rationale

P-12 holds that the record must describe the change it carries. A merge
commit is the one place in a history where a change can land under a label
that says nothing about it: the reviewer of either branch never saw it, the
reader of the trunk sees "Merge branch", and the diff that would show it is
the one diff nobody reads — a merge against its first parent, which is
dominated by the branch's own work.

Most of what this finds will be small and innocent, and the *Not a
violation* section says so. The rule exists for the case that is not: work
slipped into a merge, deliberately or not, that no branch and no review ever
held.

## How to check

```sh
bin/merge-provenance --since "6 months ago"
```

For each two-parent merge with a merge-base, the script recomputes the
automatic merge (`git merge-tree --write-tree`, git 2.38 or later), records
which files conflicted, and diffs the merge's tree against the automatic one.
Changes in conflicted files are reported as resolution size; changes in any
other file are candidates, listed with lines, files and subject.

Limitations to state in a case file:

- **The automatic merge is git's, with default strategy.** A repository that
  merges with a different strategy or custom drivers will show small,
  systematic differences everywhere; the first run on such a history will
  make that obvious, and every merge reading as a candidate is the sign.
- **Requires git 2.38+.** Older git reports not applicable.

## Evidence to cite

- The merge sha, its two parents, the files changed outside any conflict,
  and the line count.
- The diff of those files against the automatic merge — the actual content
  from nowhere, quoted. A finding that cites a line count and not the lines
  has not been adjudicated.
- Whether the merge's message says anything about it.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A fix-up needed for the two lines of work to coexist** — a type-checker
  directive removed because it was needed on one branch and not the other, an
  import reconciled, a call updated to a signature the other branch changed.
  The one candidate on the first merge-commit history tried was exactly this:
  four lines in two files, two comments deleted. Semantic conflicts are
  conflicts git cannot see, and resolving them is what a merger is for.
- **A regenerated lockfile or generated file**, where the path classifier did
  not recognise it as such.
- **A formatter or lint pass run on the merge result.**
- **A version bump, changelog entry or release note written at merge time**,
  by convention, in a repository that does that.
- **A merge produced by tooling with its own strategy** — a merge queue, a
  bot — whose result differs from git's default systematically. Every merge
  will show it, which is the tell.

## History

- **Draft, on derivation.** The first rule under P-12. Built in the house
  order on three histories: one landing by merge commit with real conflicts
  (57 merges, 15 with a resolution, median 15 lines, one of 428; one merge
  changing files outside any conflict — a four-line type-directive fix-up),
  one landing by platform button (441 merges, every one identical to the
  automatic merge), and one landing by squash, where the conditional stood
  down. The exemption that leads the list above came from the single
  candidate the runs produced.

  Held at `draft`: it has engaged once, on a change that was innocent, and
  the line floor is chosen.
