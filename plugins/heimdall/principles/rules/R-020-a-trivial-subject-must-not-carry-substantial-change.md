---
id: R-020
title: A subject naming a trivial change must not carry a substantial one
principle: P-12
severity: warning
status: draft
introduced: 0.9.1   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

A landing whose subject makes a trivial claim — typo, spelling, whitespace,
formatting, lint, rename, bump, cleanup, comments — must not carry a hundred
or more lines of source change that are not that class of change.

The claim is the mismatch between the label and the size. A "cleanup" of
1,800 lines may be a fine change; it is not a cleanup, and a reader who
skipped it because it said so skipped 1,800 lines.

**No convention needed.** Every repository has a "fix typo" commit.

**The trivial word must be the subject's head claim** — a short subject of
six words or fewer, or one that opens with the word. Not a word inside a
long subject, not the feature's own domain ("…for list formatting"), not a
backticked identifier (`Rename` events).

**Each trivial class has a shape that is that class, and a landing in that
shape is what it says, however large:** a rename that is eight in ten files
renamed; a bump that touches only manifests, lockfiles and tooling; a
formatting or lint landing whose lines survive whitespace removal unchanged;
a lint or formatting sweep of twenty or more files at a few lines each.
Tooling and configuration paths never count as source.

**Floor: one hundred source lines**, chosen.

## Rationale

P-12 holds that the record must describe the change it carries. A trivial
label is the strongest signal a subject can send that nothing needs reading,
and it is the one most often wrong in the direction that matters: the
"cleanup" that was a rewrite, the "lint fix" that changed logic to satisfy
the linter, the "bump" whose new version required the source to change
around it. The rule does not say those changes were bad. It says the label
told the reader not to look.

## How to check

```sh
bin/subject-content --since "6 months ago"
```

The script reports how many landings made a trivial claim, how many of them
carry the floor in source outside their class's shape, and lists those with
the claim, the line count and the subject.

Limitations to state in a case file:

- **The word list is English and finite.** A repository whose trivial
  subjects use other words reads as making no trivial claims.
- **Source is what the shared classifier calls code**, less tooling paths.
  A repository whose source lives under a path it calls something else will
  read differently, and R-019's home learning does not apply here.

## Evidence to cite

- The subject, the claim word, and the source line count outside the
  class's shape.
- What the change actually was, from reading it, and what the subject should
  have said.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A dependency or toolchain bump whose new version required source
  changes** — the bump is honest about the cause; the source edits are its
  cost. Two of six survivors on one history, at 211 and 268 lines. A reader
  should still see them, which is why they are listed.
- **A lint fix that changed logic** to satisfy a linter that was right —
  the label undersells it, and the change was correct. The finding is the
  label.
- **A rename that also moved or split** what it renamed, where the moves
  defeat rename detection.
- **A cleanup that the repository's own convention uses for refactors**,
  where the word means more than it says elsewhere.

## History

- **Draft, on derivation.** The third rule under P-12, built in the house
  order on three histories. The first run matched any trivial word anywhere
  in a subject and listed thirteen on one history; six were the word as a
  feature's domain, a backticked identifier, or one clause of a twelve-word
  subject, and one was a 581-file lint sweep. Head-claim matching and the
  sweep shape removed those. What remained: a "types cleanup" of 1,822
  lines, a "clean up … a bit" of 1,116, a "parser clean up" of 344, a
  cleanup of 108, and two bumps at 268 and 211 that forced source edits —
  every one the shape the rule describes, and the first rule in the frame
  whose survivors on first contact were not exemptions.

  Held at `draft`: the floor is chosen and the word list is a first draft.
