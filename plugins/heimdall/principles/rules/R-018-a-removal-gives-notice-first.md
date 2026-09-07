---
id: R-018
title: A removal gives notice first, and the notice stands long enough to be read
principle: P-13
severity: advisory
status: draft
introduced: 0.9.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where a repository marks things deprecated before removing them, a marker
must stand for at least thirty days before the thing it marks is removed.

The claim is an interval, in the shape of R-002: the notice was opened at one
commit and closed at a later one, and the time between is what a downstream
reader had. It says nothing about whether the removal was right, whether
anyone was affected, or whether the thing was public — the last of those is a
claim about consumers that git does not show, and this rule reads only what
the repository itself marked.

**Scope: conditional on the repository giving notice this way.** The script
counts deprecation markers opened in the window; below five, the repository
does not evidently use them, there is no interval to read, and the outcome is
**not applicable**. A removal that was never announced with a marker is
invisible here — the larger half of P-13's concern — and stays in the case
file as an observation.

**Scope: markers in code the repository ships.** Configuration files
mentioning a warning class, documentation noting a deprecation, tests
exercising one, vendored trees, and anything under an `internal/` directory
give notice to nobody downstream and are excluded.

**Moving, rewording and withdrawing are not closing.** A marker removed and
re-added in the same commit moved; one removed from a file that gained a
marker in the same commit was reworded; one removed by a commit that is a
revert was withdrawn — the deprecation was undone, not the thing. None
closes a notice. A marker added to a file already carrying open notices
inherits the earliest of them as its start, which over-credits a second
distinct deprecation in the same file and is the lenient direction.

## Rationale

P-13 holds that removal must give a reader time to leave. P-3 measures the
interval between deciding and building; this is the symmetric interval,
between announcing that something will go and its going, and it is the
interval a consumer lives in. A notice closed the same week it opened gave
nobody one.

Advisory, because the rule cannot tell an application from a library. An
application's own symbols have no downstream importer, a notice there serves
callers inside the repository, and a short interval costs nobody outside.
The rule reports the interval; the reader decides whether anyone was
downstream.

## How to check

```sh
bin/removal-notice --since "24 months ago"
bin/removal-notice --since "6 years ago" --bar 30 --markers '@deprecated|#\[deprecated'
```

One pass over the first-parent diffs, oldest first, keying each marker line
by file and normalised text. The script reports notices opened, closed,
withdrawn and still open; the distribution of notice length when closed; and
every closure under the bar with both shas and the marker text.

Limitations to state in a case file:

- **Markers are recognised by text.** The defaults cover the common languages'
  conventions; a repository with its own deprecation mechanism — a registry,
  a struct, an attribute the pattern does not know — reads as giving no
  notice, or as closing one when it migrates a text marker to that mechanism.
  Three of five short closures on one workspace were that migration. Set
  `--markers` to the repository's own vocabulary before believing a finding.
- **A commented-out marker matches.** The pattern cannot tell an attribute
  from a comment quoting one.
- **The bar is chosen.** Thirty days is one release cycle for many tools and
  far less for some libraries; a repository that states its own deprecation
  policy sets the bar, and the case file should say which was used.

## Evidence to cite

- The convention count and the bar.
- For each short closure: the marker text, both shas with their dates, and
  the interval.
- What was removed, from reading the closing commit: a flag, a function, a
  module — and whether the repository documents a policy the interval
  breaks.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **The deprecation itself was reverted** — detected mechanically where the
  closing commit is a revert, and to be checked by hand where it is a revert
  under another name.
- **A rewording or migration of the notice** into a form the pattern does not
  recognise. The notice continued; the pattern lost it.
- **A symbol internal to an application**, with no consumer outside the
  repository. The `internal/` convention is excluded mechanically; other
  layouts need a reader.
- **A notice on something never released** — deprecated and removed between
  two releases, so no consumer ever saw the deprecated form.
- **A repository whose stated policy is shorter than the bar**, where the
  policy is the standard and the bar should be set to it.
- **A marker whose text happens to match** — a comment quoting an attribute,
  a string that mentions the word.

## History

- **Draft, on derivation.** The first rule under P-13. Built in the house
  order on four histories, and the first run on each put something at the top
  of its list that became an exclusion: a test runner's `filterwarnings` line
  in a configuration file (closed in twenty days, deprecated nothing);
  twenty-six markers under a vendored `third-party/` tree the shared classifier
  did not recognise with a hyphen; two symbols under `internal/`; three
  two-day closures that were one reverted pull request; a rewording in a
  separate commit of a notice the file had carried for months; and help
  strings migrated into a struct-based mechanism the pattern does not know.
  What survived: on a library with a deprecation culture, seventeen closures
  with a median of 225 days and none under the bar; on a command-line
  application, seven with a median of a year and one at five days in its own
  command package; on a large workspace, twenty-one with a median of 44 days
  and five under the bar, most of them the migration above.

  Held at `draft`, and `advisory`: the bar is chosen, the pattern is
  convention-bound, and the rule cannot see whether anyone was downstream.
