---
id: R-019
title: A typed subject must be able to hold its content
principle: P-12
severity: warning
status: draft
introduced: 0.9.1   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository types its subjects — `feat:`, `fix:`, `docs:`, `test:`,
`ci:`, `build:`, `style:` and kin — a landing under a **restrictive** type
must not carry substantial content the type cannot hold: a `docs:` landing
that changes the repository's source, a `test:` landing that changes the
thing under test, a `ci:` or `build:` landing that changes source outside
tooling paths, a `style:` landing whose lines do not survive whitespace
removal unchanged.

The claim is about the label. Not that the content was wrong, not that it
should have been split — only that a reader who trusted the type never
looked, and the type gave them no reason to.

**Scope: conditional on the convention.** Below half of the window's
landings typed, or fewer than ten, typed subjects are not this repository's
practice and the outcome is **not applicable**.

**Scope: restrictive types only.** `feat`, `fix`, `refactor`, `perf` and
`chore` may carry anything by their own meaning and are never candidates.

**Where source and tests live is the repository's own statement**, read from
where its typed landings go. A directory reached by test-typed landings at
least twice as often as by feat/fix landings is a test home; the reverse is a
source home. A restrictive type is a candidate only for what it changes
inside a source home and outside a test home. Where no source home can be
learned, the rule **cannot tell** and says so.

**Floor: twenty-five source lines**, chosen.

## Rationale

P-12 holds that the record must describe the change it carries, and a typed
subject is the most explicit description a commit can give: it says which
kind of thing this is. A convention that types subjects is a convention that
invites readers to filter by type — to skip `docs:` and `test:` in a review
of behaviour, to trust `style:` without opening it — and that trust is only
as good as the typing.

The source-home mechanism exists because of the first run. Twelve `test:`
landings were reported for carrying source that was the repository's
end-to-end suite, under a directory name the shared classifier had no reason
to know. Learning the layout from churn share failed — good `fix:` commits
carry tests into the same directories — and learning it from which typed
landings *touch* which directories worked: 80% of `test:` landings against
35% of `fix:` for the suite, 26% against 99% for the package tree.

## How to check

```sh
bin/subject-content --since "6 months ago"
```

The script reports the typed share and the types in use, the source and test
homes it learned and from what, the restrictive-type landings examined, and
every candidate with the type, the straying line count and the subject.

Limitations to state in a case file:

- **The convention is recognised by its common form** — `type(scope)!: subject`
  with a known type word. A repository with its own vocabulary reads as
  untyped.
- **Homes are learned at two path levels** and need ten typed landings of
  each kind. A small window learns nothing and the rule cannot tell.
- **Doc comments inside source are source to the classifier.** A `docs:`
  landing that edits them will be listed; on the first history two of six
  survivors were exactly that.

## Evidence to cite

- The typed share, the homes learned, and the floor.
- The landing: its type, its subject, and what it changed in the source home
  — file and line count, and what kind of change it was on reading.
- What the subject should have said. A finding under this rule that cannot
  propose the honest label has not been adjudicated.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Doc comments in source** under a `docs:` subject. The classifier cannot
  tell a comment from code; a reader can in a second.
- **A `test:` landing that exported or exposed something so it could be
  tested** — a small change to the subject in service of the test.
- **A `build:` or `ci:` change whose consequence propagates into source** —
  a stricter compiler setting that forces annotations everywhere, a bundler
  change that alters import forms. The label is honest about the cause; the
  content is its effect. Listed on the first history at 310 lines, and a
  reader should still see it.
- **A type used loosely by the repository's own convention** — `docs:` for
  anything user-facing, `test:` for anything under a test directory the
  home learning did not reach. Read the convention document before citing.
- **A `style:` landing that is a formatter run with a formatter that reorders**
  — imports sorted, keys reordered — which whitespace removal does not undo.
- **Documentation that lives in source files.** API annotation files, doc
  comments, a source file the repository keeps as a ledger of ported changes:
  `docs:` landings that edit them carry hundreds of lines in the source home
  by directory and are documentation by content. The held-out editor history
  put fourteen of these at the top of its list.
- **A vendored dependency under a build type.** `build(deps): vendor …` lands
  thousands of source lines that are someone else's, mechanically.

## History

- **Draft, on derivation.** The second rule under P-12, built in the house
  order on three histories: one typed throughout (1,135 landings, 100%),
  one partly typed (37%), one a hair under the bar (49.7%). The conditional
  stood down on the last two, the third by a rounding's width — which is
  what a bar at the knee looks like, and why the share is printed to a
  decimal. On the first, twenty candidates became six once the repository's
  own layout was learned from its own landings, and the six that remained
  were read and are the exemptions above plus one genuine build-setting
  cascade.

  Held at `draft`: the floor is chosen, the home learning has run on one
  history that has a convention, and every survivor so far was innocent on
  reading.

- **Held-out sweep, 2026-09-07.** Three public histories none of the rules had
  run on, each chosen for a shape and used only to confirm: K, a web framework
  with a formal deprecation policy (about a thousand landings a year, all
  applied patches); L, a continuous-delivery tool with per-path code owners
  (about two thousand, squash); M, an editor that reverts often (about four
  thousand, merges and squash).
  Not applicable on K (no typed subjects); no finding on L at 97% typed, where
  every restrictive type held its content; 124 candidates on M at 69% typed,
  the top fourteen all `docs:` landings editing documentation kept in source
  files, and `build:` landings vendoring dependencies — the two exemptions
  above. Still `draft`: engaged, and what it listed was innocent.

- **Second held-out sweep, 2026-09-07.** Five public histories chosen for the
  shapes the drafts still needed, and used only to confirm: O, an
  infrastructure tool landing by merge commit, applied patch and squash, with
  a catch-all ownership file (about nine hundred trunk commits a year); P, a
  numerical library landing by merge commit with a formal deprecation policy
  (about fourteen hundred); Q, a UI library that reverts and re-lands, landing
  by squash, with a fixture-driven suite (about eight hundred and fifty); R,
  an inference engine whose pace tripled in the year, landing by squash (about
  eleven and a half thousand); S, a framework typing every subject, landing by
  rebase (about four thousand).
  Formed twice. On S, typing 98% of its subjects in the conventional
  vocabulary, every restrictive type held its content. On P it read as 15%
  typed until the signal learned the history's own vocabulary — MAINT,
  BUG, ENH, DOC, TST, TYP, on 93% of landings — and then every restrictive
  type held its content there too. Stood down on O, Q and R; R tags every
  subject in brackets rather than with a type and a colon, a convention the
  pattern does not yet read. Still `draft`: formed on two real histories,
  both passes.
