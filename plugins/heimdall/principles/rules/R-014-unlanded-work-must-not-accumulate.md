---
id: R-014
title: Unlanded work must not accumulate across consecutive windows
principle: P-10
severity: warning
status: draft
introduced: 0.8.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository removes branch refs when work lands, the branches that
survive are work that did not. Such work must not be begun and left, window
after window: stale outstanding branches — last commit older than one window —
must not have been started in three or more consecutive windows.

The claim is about the repository's habit, not about any branch. A single
abandoned branch is a decision; a stream of them is a process property, and
the process is what this frame reads.

**Scope: conditional on the ref-retention convention**, established from the
history in the way R-003 and R-011 establish theirs. `bin/open-ended-work`
counts the branches that visibly landed in the span and what share still hold
a ref. Above a fifth, the repository keeps refs after landing, survivors are
done-and-kept mixed with abandoned, nothing in git separates them, and the
outcome is **not applicable** — report the stock as an observation. Below,
the survivors are outstanding work and the rule can run. Fewer than five
visible landings and the convention cannot be read at all.

**Scope: work, not structure.** Release lines, integration branches, bot
branches and the platform's own are excluded by name pattern.

**Scope: stale only.** The most recent window is full of pull requests awaiting
review, which look identical from git. Only a ref whose last commit is older
than one window is past that explanation.

**A surviving ref did not land here. That is not the same as unfinished.**
Work continues on forks, in successor branches after a rebase, and in places
git does not see; silence in the clone is not idleness. The rule's claim is
about branches that did not land in this repository, and a case file must
say it that way.

**One reading sees only inflow; the delta is read across readings.** On a
repository that removes refs when work lands, everything that resolved has
vanished, so "begun per window" counts the survivors by their start date and
cannot say whether the stock is growing — a repository that begins and
resolves five branches a window has a flat stock and the same shape. Where a
previous reading of the same case left its sidecar (`--record`), the
extractor reports begun, resolved and still outstanding since, and the
finding rests on the stale stock having grown. With one reading only, the
condition below is held to an **observation**, whatever the run length.

**What landed is decided by three tests, not one.** On a squash-landing
repository every surviving branch is unreachable from the trunk whether it
landed or not. A branch is called landed if its tip is reachable, or it has no
commits of its own, or its cumulative diff fingerprints to a trunk commit.

## Rationale

P-10 holds that work begun is work owed, and that everything else in the frame
looks only at what landed. This is the branch half of it. Its confound is
severe enough that the rule's most important behaviour is declining to run:
where refs are kept, the count means nothing, and a rule that reported it
anyway would be worse than none.

## How to check

```sh
bin/open-ended-work
bin/open-ended-work --window 30 --windows 6
```

The script reports every non-structural ref as outstanding or landed (and how
it landed), the retention convention with its sample size, the trunk's landing
rate per window, the outstanding stock by age, the stale stock, and in how many
consecutive windows stale work was begun.

Limitations to state in a case file:

- **The stock is a floor.** Work begun, abandoned and deleted is invisible.
- **The bare clone carries what the remote kept.** A remote that prunes
  aggressively reads as clean.
- **Structural refs are matched by name.** A release line under an unusual name
  counts as outstanding; a feature branch named `next` does not.
- **Branch names carry identity.** They frequently include a contributor's
  handle. The script prints them so a reader can look. **A case file must not
  quote them** — P-6 forbids resolving any finding to an identifiable person,
  and a branch name does exactly that.

## Evidence to cite

- The retention figure and its sample size, always — a finding without the
  convention that licenses it is meaningless.
- The stale count, its age distribution, and the run of windows.
- The stale stock in windows of the trunk's own throughput, which is what
  makes the number comparable across repositories of different pace.
- Never a branch name. Cite ages, sizes and counts.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Work that continued where git cannot see it** — a fork, a successor
  branch after a rebase, a design thread — or was deliberately parked. The
  ref did not land here; the rule cannot say the work stopped.
- **Open pull requests under review**, which is why the most recent window is
  excluded and why a reader should check the youngest stale refs before
  believing the count.
- **A stacked series in flight** — several refs from one effort, each a step,
  all young. Seen on one history: eight outstanding refs, all two days old,
  one series.
- **Long-lived experiment or spike branches the repository keeps by policy**, a
  documented convention that says so being the evidence.
- **Branches held for a release that has not happened** — backports, staged
  features — where the repository's release process explains the hold.
- **A remote whose refs were imported from elsewhere** — a migration, a
  mirror — where the stock predates the repository's current practice.
- **A convention change inside the span.** A repository that started deleting
  on landing partway through has an old stock from before and nothing since;
  read each side separately.

## History

- **Draft, on derivation.** Built in the house order on three histories, and
  the runs were mostly about the extractor. The first version established
  retention from merges whose second parent still had a ref — on a squash
  repository that is a sample of one, and it read "refs kept" on a history
  whose 147 squash landings with no surviving ref were the evidence that refs
  are removed. The second counted begun-per-window over all outstanding refs
  and was dominated by the in-flight pull requests of the most recent window.
  What survived: retention from every visible landing with a sample floor,
  begun-per-window over stale refs only, and a run of three windows.

  On the three histories: one read 25 stale refs — a window of its own
  throughput — with stale work begun in three consecutive windows on a
  repository that removes refs on landing (1 of 148 landed branches kept its
  ref) — the
  shape the rule describes, held as an observation because the rule is draft;
  one read a single stale ref under the floor; one read eight refs all two days
  old, a stacked series, and zero stale. The conditional stood down nowhere
  and the floor stood it down twice, which is the behaviour that matters.

  Held at `draft`: the run length and floor were chosen, and the rule has one
  history on which it engaged.

- **Amended on 2026-09-04, on two readings of its own text.** The extractor's
  summary said "what survives was not finished", which git does not support:
  a surviving ref did not land here, and work continues in places the clone
  cannot see. Reworded, and an exemption added for it. The second reading
  was the deeper one: the condition counts survivors by start date, which is
  inflow with the outflow deleted, so a steady-state repository shows the
  same shape as an accumulating one. The extractor now leaves a hashed
  sidecar per reading and reports begun, resolved and still outstanding
  against the previous one; the finding rests on the stale stock growing,
  and with one reading only it is held to an observation.
