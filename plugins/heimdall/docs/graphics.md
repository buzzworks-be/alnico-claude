# Graphics in a case file

What a chart may show, which five earn a place, what is refused, and how
they would be produced. Built: `bin/case-charts` draws all five. Nothing is ever rendered
unasked.

## Preview

What `/profile` would hand over, on invented figures
under the codename TALLOW: the strip row, the offer as spoken, the two
charts drawn on that reading, and the two other drawable shapes shown once
each. Rendered from the same `mermaid` blocks the skill would write, with a
palette added and nothing else.

https://claude.ai/code/artifact/64f3d66f-dd49-4aaf-b710-a76141da0349

## The test a chart must pass

A case file is tables, prose and the strip. A chart is added only where it
shows a **shape** the tables state but a reader cannot see at a glance — a
burst, a gap, a trend, a cloud, an accumulation. Anything a table already
shows stays a table; anything that reduces a reading to one figure is
refused outright (see below). The strip remains the canonical record. A
chart is an aid beside it, never the finding, and a case file with the
charts removed must still say everything the case file says.

Every chart carries the same three things a table does: the window, the
landing count behind it, and the thin-sample marking wherever a rule would
have declined to judge. Its caption names the rule and the principle with
their titles, and the principle's signature and what it reads, from the
table at the top of `principles/README.md`, so a reader without the frame
open knows what kind of concern the picture serves. And every chart carries the **denominator**: what
adhered is drawn beside what did not, never a rate alone. A finding is a
sliver on a bar whose height is everything that satisfied the rule, so a
reader sees the two untested landings against the thirty-eight tested ones
and not as a count on its own. This is the chart form of the rule-writing
requirement in `principles/README.md`: a finding is read against what
adhered.

## The five

### 1. Landing timeline — P-1

Each landing as a mark on a time axis: height by code lines, colour by
route (merge, direct, forge-committed), and for a merge the review interval
drawn as a bar from branch tip to landing. Gaps in the history are left as
gaps, not compressed.

What it shows: a burst of tall direct marks with no interval, which is the
P-1 concern in one picture; and a gap under a baseline window, which is why
a comparison could not be formed. Serves R-001, R-004, R-006 and R-007.

Data: `bin/reviewability` (route and interval), `bin/digest-rate` (pace),
landing unit as in `bin/tests-with-code`.

### 2. Care by size band — P-2, P-8

Per line band (1-24, 25-99, 100-299, 300-999, 1000+), one bar of every
landing in the band with the part that carried a test drawn over it: what
adhered in one tone, the remainder in another, the count in the label. A
second panel does the same by net decision band, and a third for reasoning
under R-003. The rates the rule tested and the convention bar go in the
caption, because a counts axis cannot hold a 50% line and the counts are
what a reader needs to weigh the finding.

What it shows: what adhered beside what did not, at every size; a thin band
is visibly thin, and a finding is a sliver against the bar it sits in.
Serves R-003, R-011 and R-027. The pooled regime from 100 lines up is drawn
as one bar spanning three bands, so the pooling is visible rather than
stated.

Data: `bin/reasoning-with-code`, `bin/tests-with-code`, `bin/care-by-size`,
`bin/decision-points`.

### 3. Care over time with risk windows shaded — P-14, P-15

A step line per calendar window for test rate and reasoning rate. Declared
risk moments shaded behind it: release run-ups scaled to the tag cadence,
major versions, reverts, breaking markers, each kind in its own tone. A
declaration of stakes as a vertical line with ninety days marked either
side. Windows under the sample floor drawn hollow.

What it shows: the trend, which is the one thing a table cannot show, and
whether care rises into the shaded windows or ignores them. Serves R-021 to
R-025.

Data: `bin/care-over-time`.

### 4. Size against interval — P-14

A log-log scatter of code lines against review interval, one point per
merge, per window or for the whole span, with the rank correlation in the
corner.

What it shows: a flat cloud is R-023's observation; a rising one is a
process whose reading time grows with what there is to read. One glance
settles what the coefficient only asserts.

Data: `bin/care-over-time` (size and interval per landing).

### 5. Stocks of what did not finish — P-10

For open-ended branches, one reading sees only the survivors, so the axis
is **readings of the case**, not windows: a bar of the stale stock at each
reading, a line for what was resolved since the previous one (landed or
deleted, git cannot say which) and a line for what was begun since. Resolved
is what adhered. With a single reading the chart falls back to survivors by
start window and says so in its caption. For recorded obligations the axis
is windows: added, discharged, surviving, as the extractor already counts
them.

What it shows: accumulation, which is an area under a curve and invisible
in a count; and whether a growing stock is inflow outrunning outflow or a
repository that finishes what it starts. Serves R-014 and R-015.

Data: `bin/open-ended-work`, `bin/marker-debt`.

## Refused

- **No gauge, score, traffic light or composite index.** A single number is
  a verdict, and Heimdall does not give one. The severity field is a routing
  label for whoever receives the file, not a figure to plot.
- **No per-person chart of any kind.** P-6 forbids comparing contributors,
  and a chart would do it faster than a table. No author axis, no author
  colour, no author legend, ever.
- **No chart that names the target.** Titles, axis labels and legends use
  the codename and the rule ids; a path may appear only where the case file
  would already cite it, and never in a chart that leaves the case
  directory.
- **No chart from a draft rule presented as a finding.** A draft rule's
  observation is drawn in the same muted style as a signal with no rule.

## When a chart is offered

Never by default. A chart is drawn only when a reading gives it something to
show, and only when the reader asks for it. After a reading, `/profile`
looks at the strip row it has just written and offers the charts the row
makes relevant — by name, one line each, with what the chart would show on
this reading — and draws the ones the reader picks. A row of passes and
not-applicables offers nothing.

| Outcome on the row | Chart offered |
|---|---|
| R-001, R-004, R-006 or R-007 as violation, or R-006/R-007 as cannot tell on a bursty window | 1. Landing timeline |
| R-003, R-011 or R-027 as violation or observation, or stood down against a band the reader may want to see | 2. Care by size band |
| Any of R-021 to R-025 engaged, or `bin/care-over-time` reporting a drift in either direction | 3. Care over time |
| R-023 as observation, or a size–interval correlation reported near zero | 4. Size against interval |
| R-014 or R-015 as observation, or a rising stock in S-9/S-10 | 5. Stocks of what did not finish |

Two consequences. A conducted run — one driven by its tasking rather than by
a person at the terminal — has nobody to ask, so it draws nothing unless its
tasking names a chart, and the tasking is recorded verbatim in the case file
as always. And the offer is itself
evidence of what the reading found: a case file that carries chart 3 and
not chart 1 says, without a word, where the shape was.

## Mechanics

- `bin/case-charts <n> --since … [--until …] --id <reading>` draws chart *n*
  as one SVG into the case directory (or `--out`), and the SVG is the whole
  deliverable: the frame drawn above the chart (each rule and its title,
  each principle and its title, the signature and what it reads), the
  chart, and the figures it is read against below. Drawing the same chart
  again for the same reading overwrites it. Nothing else is written; what
  the script prints is the same frame and caption in text, for the
  conversation. There is no companion file — an earlier version wrote one,
  and before that left the frame to be pasted by hand, which is where the
  first field runs lost it.
- No library, no `--json`. The script imports the extractors' own functions
  by path — the landing series from `care-over-time`, the decision reader
  from `decision-points`, the marker counters from `marker-debt` — so a
  chart and the table beside it are computed the same way; the branch stock
  chart reads the sidecars `open-ended-work --record` leaves in the case
  directory. The one addition an extractor needed was the landing's route
  (merge, forge, direct) on the series record, for the timeline's colour.
- The case file references the SVGs by relative path; a reader without them
  loses nothing but the pictures. The files are gitignored with the case.
- Colour carries route and kind only, never judgement: no red for a
  violation, no green for a pass. The strip's glyphs already say which is
  which. Thin bands are hatched; a window under the floor is a hollow bar.
- Chart 4 on a squash history, and chart 5's branch panel with a single
  reading, draw their own limitation in place of a picture and say so in the
  caption, rather than drawing something that would read as data.
