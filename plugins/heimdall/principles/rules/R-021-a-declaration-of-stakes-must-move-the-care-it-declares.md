---
id: R-021
title: A declaration of stakes must move the care it declares
principle: P-14
severity: warning
status: draft
introduced: 0.10.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

When a repository adds or extends its ownership declaration — new patterns in
`CODEOWNERS` naming paths that need particular people — the care shown on
those paths afterwards must be at least what it was before. If neither the
test-accompaniment rate nor the review interval per line on the newly
declared paths rose, the declaration changed nothing the history can see.

This is a natural experiment the repository hands over for free: the
declaring commit is a date, the patterns say which paths, and the same
measures the frame already uses can be read on both sides of it.

**Scope: declarations that add path patterns**, not a catch-all (`*`) and
not edits that only change owners. Every declaring commit in the whole
history is examined, not only the span — a declaration is a one-off event
and the last one may be years old — with its own series of ninety days on
each side.

**Scope: ten landings on the declared paths on each side**, above the
twenty-five-line floor. Below that the outcome is **cannot tell**, which on
a narrow declaration — one file, one directory nobody touches — is the
usual outcome.

**The bar is any movement.** The claim is not that care rose by a margin; it
is that a declaration is not decoration, and the weakest evidence that
suffices is that something moved in the right direction.

## Rationale

P-14 holds that care must rise where the repository says risk rose, and an
ownership declaration is the plainest way a repository says it. R-009 asks
whether a practice has a carrier; this asks the reverse — whether a carrier
carries a practice. A declaration that changed no measurable behaviour is a
practice claimed with nothing in the numbers behind it, and the reader
deciding what the declaration means deserves to know that.

## How to check

```sh
bin/care-over-time
```

The script lists every declaring commit with the patterns it added, the
landings on those paths ninety days before and after, and the two measures
on each side. On a history with no declaration, or only catch-alls, it
reports not applicable.

Limitations to state in a case file:

- **Ninety days is chosen.** A declaration whose effect took a quarter to
  show reads as decoration; one whose paths were quiet reads as cannot tell.
- **The review interval is measurable on merge-commit landings only.** On a
  squash history the test rate carries the whole comparison.
- **The patterns are matched as the ownership file matches them**, and a
  pattern the matcher misreads declares nothing here.

## Evidence to cite

- The declaring commit and date, the patterns, and the two sides: landings,
  test rate, and where measurable the median review interval per line.
- Whether anything else changed at the same date — a convention document, a
  pipeline — that would explain a movement the declaration did not cause.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A declaration made for routing, not rigor.** Some repositories use the
  ownership file to route notifications, and say so; care was never the
  point and the reader should look for that statement.
- **Care that was already at its ceiling.** Paths tested on every landing
  before the declaration cannot rise afterwards. The script says so where
  the before-rate is at or above ninety percent.
- **A declaration whose effect is enforced on the platform** — required
  reviews — which git cannot see and which may have changed everything.
- **Declared paths that went quiet**, where the after-side is thin.

## History

- **Draft, on derivation.** The first rule under P-14. Four real histories
  yielded no populated case: one had no declaration, one a catch-all, one
  four narrow declarations with under ten landings a side, one none. It
  engaged on two synthetic fixtures built for it — a declaration followed
  by unchanged care, and one followed by care rising — and reported the
  first and passed the second.

  Held at `draft`: it has never engaged on a real history.
