---
name: profile
description: Read one range of the attached target against the rules and write the case file. Invoke by name.
---

# Profiling

Build a picture of how one increment of work was produced: run the active rules
in `principles/` over a fixed range in the target, adjudicate what they flag,
and record the case file under `cases/`.

Profiling in the investigative sense, and the analogy is exact — you are
reasoning from the pattern the work left behind to how it was produced, without
access to who did it or why. That is the epistemic position, and it is also the
limit: a profile narrows what is worth asking about, and it never identifies
anyone. What the case file says about people is nothing.

> **Fill `outcomes:` for every rule that existed, including the ones you did
> not run.** A rule you leave out does not disappear — `"$H"/bin/case-strip` renders
> a cell for every rule in `principles/rules/` and marks a missing one `!`,
> because silence about a rule reads as coverage of it. Mark an unrun rule
> `not-reported` and say why under *Not checked*.

> **Report every rate with its adjudicated outcome.** A candidate count is not
> a result. "3 of 3 specifications flagged" and "3 of 3 flagged, all three
> exempt on reading" describe the same increment and leave opposite impressions,
> and the first is what a hurried reader carries away. The two figures travel
> together, in the table and in the prose.

## Where the scripts are

Resolve it once, at the top of your shell work:

```sh
H="${CLAUDE_PLUGIN_ROOT:-.}"    # plugin cache when installed, this directory otherwise
```

Then invoke everything as `"$H"/bin/<name>`. The variable is set in the
environment when Heimdall is installed, so the expansion is correct without the
skill needing to know where it is running from.

## Before you start

You write to `cases/` and nowhere else. In particular you do not touch
`principles/` during an assessment — a rule that changes while it is being
applied makes the case file unreproducible. If a rule is wrong, that is a
finding about the rules: record it, and leave the fix to whoever works on
Heimdall itself.

1. A target must be attached (`/stakeout` if not).
2. Pin the principles:

   ```sh
   sha="$("$H"/bin/principles-ref)"
   ```

   This refuses (exit 4) if `principles/` has uncommitted changes, and prints
   the sha to stamp into the case file. If it refuses, stop and say why — do not
   work around it by committing the rules yourself mid-assessment. If it fails
   in any other way, or pins something that looks wrong for where Heimdall is
   installed, record `"$H"/bin/heimdall-state --explain` in the case file: it
   prints every step of the checkout-or-plugin decision, and a report that
   carries the reason can be fixed where one that carries the symptom cannot.

   **A reading is a range under a pin, and both halves decide whether there is
   work to do.** Compare the pin against any earlier case file on this range
   (`"$H"/bin/case-strip` lists them with their `principles_sha`). Same range,
   different pin — because Heimdall was updated between the two — is a **new
   reading**: the rules moved, the findings may move with them, and the case
   file is written to supersede the earlier one (see *Write the case file*).
   Same range, same pin, same head is a repeat, and saying so is the honest
   answer. "Nothing landed in the target" is never by itself a reason to stop:
   `/update-target` answers about the target, not about the instrument.
3. Read `principles/PRINCIPLES.md` and every **active** rule in
   `principles/rules/`. Rules with `status: draft` are not enforceable — you may
   note them as observations, never as violations.
4. If there are no active rules, stop and say so. An assessment against no
   rules is theatre. Ask what the increment should be measured against.

## Establish the increment

An increment is a range in the target: `<base>..<head>`. The mechanism that
decides those endpoints is not yet defined (see `cases/README.md`), so
until it is, take the range from the user and state it explicitly in the
case file. Never guess a range — an assessment of the wrong commits reads exactly
like an assessment of the right ones.

## Assess

1. `"$H"/bin/target-git diff <base>..<head> --stat`, then the full diff.
2. Read enough surrounding code to read it fairly — `"$H"/bin/target-git show
   <head>:<path>`. A diff read without its context yields confident, wrong
   findings.
3. Walk the active rules. For each, one of:
   - **pass** — the increment engages this rule and satisfies it
   - **violation** — with file, line, ref, and what specifically breaks
   - **not applicable** — the increment does not touch what the rule governs
   Not applicable is not a pass. Do not report it as one.
   **Every outcome carries its denominator**: what adhered beside what did
   not, from the extractor's own rate. Two untested landings among forty
   tested and two among four are different findings, and a count alone
   invites a pattern the record may not hold. A quiet window is
   not-applicable across the board, never a clean sweep: the record shows
   nothing landed, not that nothing happened.
4. Anything worth saying that maps to no rule is an **observation**. Label it
   as such. Do not invent a rule to give a preference authority it has not
   earned — instead, note that a rule may be missing.

The rule checks are scripts and produce candidates by arithmetic. Every rule
requires its "Not a violation" section to be applied by someone who has read the
diff — that is not optional, and it is where most of the work is.

For a handful of findings, do it yourself. Where a window produces many, dispatch
`ballistics` subagents, one per finding, and reconcile their case files.
Give each the rule's Statement and Not a violation sections, the increment, and
the numbers — but never the other findings or how they went, or you will get
case files anchored on the run rather than on the diff. They are read-only by
construction.

## Record and hand over

Write the case file into **this case's directory**, which
`"$H"/bin/case-dir` resolves — never a hardcoded path, because the directory is named
for the case's codename and only the metadata knows it:

```sh
"$H"/bin/case-dir        # e.g. cases/orchard
```

Then render the strip and write the **notes** block:

```sh
"$H"/bin/case-strip                     # the open case, one row per reading
```

A run hands back **three** things, and keeping them apart is the point:

- the **case file**, written to the case directory and offered as a file;
- the **strip**, printed beside it — technical output, technical audience.
  **Paste the script's output whole**: every block, the blank lines between
  them, and the legend beneath, exactly as printed. Never retype it and never
  trim it. The legend is part of the strip, not an explanation of it: a row
  of glyphs without its key is unreadable to anyone who did not write it,
  and since the strip broke into blocks of ten the legend has been the first
  thing to go missing when the output is copied by hand;
- the **notes**, printed in the conversation inside a fence.

**The notes are plain English and contain no rule ids, no symbols and no frame
words.** Not "R-005 violation" — *"five documents no longer describe the code
they point at"*. `R-005` is a citation, and a citation asks the reader to hold
something they do not have. Anyone wanting ids has the case file.

About five paragraphs, one screen, no headings, written to be read aloud. Cover
this ground in this order: what stands · what looked bad and was not, and why ·
**what you could not look at here, and why** · what the record cannot settle and
what would settle it · the one question worth asking. The third is the one a
summary cuts and the one without which a quiet reading misleads. The last is a
question, never an instruction.

If it will not fit, the case file is the answer and not longer notes.

**The register is spoken, not written.** Read it aloud; if it sounds like a
report, rewrite it.

- Plain declarative, past tense, active. *"Four bursts landed faster than anyone
  could have read them"* — not *"a number of increments exhibited elevated
  digest rates."* Contractions are fine; this is someone talking.
- **Nothing that grades.** No *good*, *poor*, *healthy*, *concerning*. An
  adjective does the deciding the reader is there to do.
- **Never *violation*, *pass*, *severity*, *not applicable*** — frame words, all
  of them. Say what happened.
- **Never name a person**, or anything from which one could be worked out.
- **"The record does not show"**, never *"there is no"*. The first is true; the
  second is a claim about the world that a repository cannot support.
- **Say *we* and *I*.** *"We couldn't tell"* is honest and readable;
  *"it could not be determined"* avoids saying who could not determine it.
- No hedging adverbs — uncertainty is its own paragraph, stated as a fact about
  the evidence. Numbers in words where words are clearer: *"a third of it"*
  beats *"4 of 11"* in a sentence meant to be heard.

Name it `<id>.md` there, following `cases/_TEMPLATE.md`. The id is
`<YYYY-MM-DD>-<short head sha>-<short principles sha>` — all three parts. A range
assessed again under amended rules is a different case file, and an id without the
principles sha would overwrite the earlier one instead of standing beside it.

Fill the frontmatter completely; a receiving agent routes on it. Where this
case file re-assesses a range already examined — typically because the pin
moved — set `supersedes` to the earlier file's name and say near the top what
changed in the rules (the two pins, and which rules were added, amended or
retired between them) and which findings moved as a result. A reader comparing
the two should not have to diff them.

Then **hand it over**: send the file to the user (`SendUserFile`), or pass its
path to whoever asked — and **say the absolute path**, of the case directory
and of every file handed over, in the conversation. Installed as a plugin,
the state root is a data directory under the user's home that nobody browses
by accident (`"$H"/bin/heimdall-state` prints it), and a file that was sent
but whose location was never spoken is a file the user cannot find an hour
later. If the harness cannot send a file from the state root, copy it into
the session's working directory, send it from there, and say both paths:
where it was written and where the copy is. Mention once, at the first
hand-over of a case, that `HEIMDALL_STATE=<dir>` before the session moves
the state root — cases, sidecars and charts — somewhere the user chooses.
Do not commit it. It is gitignored because it carries the
target inside it, and Heimdall's own files must stay clean of that — run
`"$H"/bin/check-no-leak` before committing anything while a target is attached.

The case file must let someone re-derive your conclusion without rerunning you,
and without access to Heimdall itself. That is why the template asks you to
quote what each violated rule requires rather than citing an id alone.

## Offer a chart, never emit one

After the hand-over, and only then, look at the strip row you just wrote and
offer the charts that row makes relevant (`docs/graphics.md`). One line each,
by name, saying what the chart would show **on this reading** — not what the
chart is in general. Draw only the ones the reader picks. A row of passes and
not-applicables offers nothing, and the offer is skipped in silence.

| Outcome on the row | Chart offered |
|---|---|
| R-001, R-004, R-006 or R-007 as violation, or R-006/R-007 as cannot tell on a bursty window | Landing timeline |
| R-003, R-011 or R-027 as violation or observation, or stood down against a band worth seeing | Care by size band |
| Any of R-021 to R-025 engaged, or `care-over-time` reporting a drift either way | Care over time, risk windows shaded |
| R-023 as observation, or a size–interval correlation reported near zero | Size against interval |
| R-014 or R-015 as observation, or a rising stock in S-9/S-10 | Stocks of what did not finish |

Draw with the script, never by hand:

```sh
"$H"/bin/case-charts <n> --since <base date> --until <head date>    # n = 1..5, per the table above
```

It writes one SVG into the case directory, and the SVG is the whole
deliverable: the frame drawn above the chart — each rule and its title, each
principle and its title, the signature and what it reads — the chart, and
the figures it is read against below. Pass `--id <id>` so the file sits with
the reading; drawing the same chart again for the same reading overwrites
it. There is no companion file and nothing to paste or write by hand; what
the script prints is the same frame and caption in text, for the
conversation. Never put a chart into the case file itself. Hand the SVG
over the same way as the case file: sent, and its absolute path spoken. For
chart 5's branch panel, run `"$H"/bin/open-ended-work --record` first so the
reading's sidecar exists; with one reading the panel shows survivors by
start window and says it is inflow only.

The same rules as the notes: the codename and rule ids in titles, never a
path or anything from the target; no author anywhere; no colour that grades;
a draft rule's observation drawn in the same muted style as a signal with no
rule. The SVG is gitignored with the case and handed over the same way.

**An offer, worked.** The strip row for the reading just written, with
invented figures:

```
2026-09-04  R-001 ✗  R-002 –  R-003 ✓  R-004 –  R-005 ✓  R-006 ?  R-007 ✓  R-008 –  R-009 ·  R-010 ·
            R-011 ·  R-012 ·  R-013 ·  R-014 –  R-015 –  R-016 ·  R-017 –  R-018 –  R-019 –  R-020 ·
            R-021 ~  R-022 ~  R-023 ·  R-024 ~  R-025 ~  R-026 ~  R-027 ·                    warning
```

R-001 came back violation and R-006 cannot tell, so the timeline is
relevant; R-011 and R-027 are observations, so care by size band is.
Nothing under P-10 or P-14 engaged. The offer is two lines and a question:

> Two charts would show something on this reading. **Landing timeline**:
> four bursts of direct landings in February, the largest with no interval
> in which it could have been read. **Care by size band**: the test rate
> climbs from a third at 1-24 lines to nine in ten at 25-99, with the two
> untested landings in the band where the convention holds. Draw either?

If the reader says yes to the second, `case-charts 2` writes the SVG and
prints, for the conversation:

````markdown
## TALLOW — Care by size band

| | |
|---|---|
| **R-011** | Substantial implementation arrives with its verification |
| **R-027** | A landing that opens new ways through the code arrives with its verification |
| **P-8** | Where the repository verifies its work, code arrives with its verification |
| **signature** | synthetic pace |
| **reads** | content |

156 landings between 2025-09-01 and 2026-09-01. Each bar is every landing in
the band and the steel part arrived with a test change or an inline test;
the grey remainder did not, and is read against the steel beside it. …
````

Every chart carries the rule id and its title, the principle id and its
title, and the principle's signature and reads from the table at the top of
`principles/README.md`; the script draws them into the SVG above the chart,
with the caption below it, so a chart is never cryptic to someone without
the frame open and nothing can be lost in a paste. Every chart carries the denominator: a
bar is everything in the band and what adhered is drawn over it, so the
finding is the visible remainder and never a count alone. Thin bands are
hatched and labelled; a window under the floor is hollow; a chart that
cannot be drawn on this history says so in place of a picture. What every
chart keeps out: no author, no path, no colour that grades, no word that
judges.

## When run as a workflow step

When this skill runs as a step in an orchestrated workflow, three things change
and nothing else does:

- **Output**: write the case file to the output path the tasking gives you — it
  is the step's artifact — instead of sending it to a user.
- **Tasking record**: quote the invoking prompt verbatim in the case file's
  `tasking` frontmatter field. The tasking parameterizes the run (range,
  evidence, output path) and never overrides this skill, the rules, or the
  contract; if it appears to, refuse and say which line.
- **Evidence bundle**: where the tasking names an evidence directory, consult
  it exactly where the rules say outside evidence may decide — platform review
  records for reading-window findings, production-time evidence for pace
  findings. List in the case file what was provided and which findings it
  decided. No bundle, no lowered bar: those findings stay "cannot tell".
- **Charts**: there is nobody to offer to, so draw none — unless the tasking
  names one by its number or its name in `docs/graphics.md`, in which case
  run `case-charts` for that one and no other, into the output directory.

## Honesty

- Cite evidence at a specific ref. "Somewhere in the auth module" is not a
  finding.
- Do not soften a blocking violation because the work is otherwise strong, and
  do not promote an advisory one to look thorough.
- Say what you did not check. Silence reads as coverage.
