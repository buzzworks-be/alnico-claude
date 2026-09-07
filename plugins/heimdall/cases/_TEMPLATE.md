---
# Machine-readable header. A receiving agent routes on this; a human skims it.
#
# Filename: <YYYY-MM-DD>-<short head sha>-<short principles sha>.md
#
# The principles sha belongs in the name, not only in the header. The same range
# assessed twice under amended rules is two different case files, and naming them
# by range alone makes the second silently overwrite the first — losing the
# record of what the rules used to say and what they used to find.
target: owner/repo
range: <base>..<head>
assessed_at: 2026-01-01T00:00:00Z
principles_sha: <from bin/principles-ref>
supersedes:             # earlier case file on this range, if any; omit when none
tasking: |              # conducted runs only: the invoking prompt, verbatim.
                        # Steering the instrument must be visible in the artifact.
                        # Omit for interactive runs.
severity: clean         # clean | advisory | warning | blocking — the highest severity found
findings:
  blocking: 0
  warning: 0
  advisory: 0
outcomes:               # every rule that existed at principles_sha, no exceptions.
  R-001: not-applicable # pass | violation | not-applicable | cannot-tell | observation
  R-002: pass           # A rule you did not run is still listed, as: not-reported.
  R-003: pass           # Omitting it does not make it disappear — bin/case-strip
  R-004: not-applicable # renders a cell for every rule and marks a missing one "!",
  R-005: violation      # because silence about a rule reads as coverage of it.
  R-006: cannot-tell    # Draft rules are observation at most, never violation.
  R-007: pass
  R-008: not-applicable
  R-009: observation
  R-010: not-reported
  R-011: observation
  R-012: not-reported
  R-013: not-reported
  R-014: not-applicable
  R-015: not-applicable
  R-016: not-reported
  R-017: not-applicable
  R-018: not-applicable
  R-019: not-applicable
  R-020: not-reported
  R-021: cannot-tell
  R-022: cannot-tell
  R-023: cannot-tell
  R-024: cannot-tell
  R-025: cannot-tell
  R-026: cannot-tell
  R-027: not-applicable
---

# Case file — <range>

> **This file is a handoff artifact, not a repository file.** It cites paths and
> code in the observed target, so it must never be committed into Heimdall. It
> is gitignored here; hand it over and let the recipient own its retention.

## Notes

<!-- What Heimdall scribbles at the whiteboard: the gist, in plain English, as
     you would say it aloud. Reproduced verbatim in the conversation inside a
     fence, so it must read on its own.

     NO rule ids, no symbols, no strip, no frame words (violation, pass,
     severity, not applicable). Those are the case file's and the strip's job.
     One screen, about five paragraphs, no headings.

     Cover this ground in this order, as prose: what stands · what dissolved on
     reading and why · what we could not look at and why · what we could not
     tell and what would settle it · the one question worth asking. The style
     rules are in the profile skill: spoken register, nothing that grades, no
     frame words, no names, "the record does not show" rather than "there is
     no". -->

```
CODENAME — <the period, in words>

<what stands, in plain terms>

<what looked bad and was not, and why>

<what we could not look at here, and why — never omitted>

<what the record cannot settle, and what would settle it>

<the question worth putting to the work>
```

## Coverage at a glance

<!-- Technical output, beside the technical record. Not in the notes. The
     script's output whole: every block and the legend under them, verbatim.
     A strip without its legend is a row of glyphs nobody can read. -->

```
<bin/case-strip output for this reading, blocks and legend, unedited>
```

## Scope

<What was assessed: how many commits, which files, and anything about the range
that affects how the rest should be read. If the range was given rather than
derived, say so — a reader cannot otherwise tell.>

## Rules applied

| Rule | Title | Severity | Outcome |
|---|---|---|---|
| R-00N | <title> | blocking | violation |
| R-00N | <title> | warning | pass |
| R-00N | <title> | advisory | not applicable |

Outcomes are `pass`, `violation`, or `not applicable`. **Not applicable is not a
pass** — it means the increment does not touch what the rule governs.

## Findings

### R-00N — <rule title>

**Severity:** blocking
**Where:** `path/to/file.ext:42` at `<ref>`

**The rule requires:** <quote or paraphrase the rule's statement — the recipient
may not have Heimdall's checkout, and a bare rule id is not actionable.>

**What is there:**

```
<the offending code, quoted>
```

**Why this violates it:** <one or two sentences. Not a fix — a fix is the
recipient's to decide.>

**Beside it:** <what adhered — how many comparable units in the window
satisfied the rule, next to how many did not. Never omitted: a count without
its denominator invites a pattern the record may not hold.>

<!-- Repeat per finding, most severe first. -->

## Observations

<Things worth saying that no active rule covers. Label them as unruled. If an
observation recurs across increments, that is a signal a rule may be missing —
say so, but do not treat it as a violation.>

## Not checked

<What this assessment did not cover, and why: rules that are draft, parts of the
diff not read, things not visible from the evidence available. Silence here
reads as coverage, so an empty section must be an explicit "nothing".>
