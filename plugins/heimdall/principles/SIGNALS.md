# Signals

What can actually be measured from a repository's history, what each measurement
suggests, and — the part that matters — how each one lies.

A signal is not a rule. Nothing here is a violation. These feed the rules in
`rules/` once best practices are defined; until then they are readings, and a
reading is reported as shape, never as deviation.

Every signal below must remain stated so that it would make sense pointed at any
repository.

---

## S-1. Review latency — merge lag against branch tip

**Measure:** the interval between the newest commit on a branch and the merge
commit that lands it.

**Suggests:** whether a merge could have been preceded by a read. A branch
merged within a minute of its last commit was not reviewed in that minute; the
physical time did not exist. This is the sharpest available evidence for the
difference between a human in the loop and a human on the merge button.

**How it lies — two ways, both real:**

1. **The branch may have been reviewed hours earlier.** A pull request sits
   open, gets read, receives one final fixup commit, and merges immediately
   after. Lag reads near zero; review happened. Measuring lag alone will
   systematically accuse a healthy workflow.
2. **Lag is not review.** A long gap means only that time passed. Nobody was
   necessarily reading during it.

**Read it with:** the branch's full lifetime (first commit to merge) and its
size. Short lifetime plus large size plus near-zero lag is the combination that
carries signal; lag alone is close to worthless.

---

## S-2. Digest rate — volume against elapsed time

**Measure:** lines changed per minute across runs of closely spaced commits, and
the share of a window's churn arriving inside such runs.

**Suggests:** whether production outran absorption. Careful reading of unfamiliar
code runs at a low, human, roughly knowable rate. Sustained output far above it
means the output was not read as it was produced — arithmetic, not judgement.

**How it lies:** it conflates production with the *opportunity* to absorb. A
person may read attentively while a machine writes. The measure bounds
absorption from above; it never demonstrates that nobody read.

**Read it as:** a ceiling on what could have been digested, not a claim about
what was.

**Derived rule:** R-006, which binds the ceiling over sustained runs of
commits — including in solo work, where R-001 and R-004 cannot reach.

---

## S-3. Machine attribution

**Measure:** commit trailers naming an AI co-author, committer identities that
differ from author identities, bot accounts, generation markers in commit
bodies.

**Suggests:** which share of the work was machine-produced.

**How it lies — badly, and this is the important one.** Attribution is opt-in
and trivially removed. A tool can be configured not to write the trailer, and
then entirely machine-generated history is indistinguishable from hand-written.
**Presence is strong evidence; absence is no evidence at all.** A signal that
can be switched off by the thing it measures must never carry a rule on its own.

**Read it as:** a floor on machine involvement. Never infer human authorship
from a missing trailer. Where attribution matters to a finding, corroborate with
signals that cannot be opted out of — S-2 rate, S-4 shape.

**Derived rule:** R-007 — which fires only on the conjunction of machine pace
and absent declaration, exactly because pace cannot be switched off and
attribution can. The warning above still governs: absence alone is never a
finding, and R-007's text repeats it.

---

## S-4. Dumping — concentration of a window's output

**Measure:** churn per document file; the largest single commit's share of a
window; whether specification and implementation changed in the same increment.

**Suggests:** whether the work arrived as a sequence of decisions or as one act.
A large specification and broad code change landing together indicates no point
at which the specification could have been reviewed before being built on.

**How it lies:** a genuine one-off — an initial import, a vendored dependency, a
generated client — looks identical. Establish what the increment contains before
reading its shape.

---

## S-5. Documentation drift

**Measure:** documentation churn against code churn; and documents left
untouched while the code they describe keeps moving.

**Suggests:** rot. Documentation produced faster than it can be read is
documentation that will not be read, and then not maintained. Both the growth
rate and the staleness are visible; the reading is not.

**How it lies:** the relationship between a document and the code it describes
is inferred from paths and timing, not from content. A document may legitimately
outlive the churn beneath it.

**Derived rule:** R-005, which narrows the inference to the checkable core — a
document that names a path is claiming it exists and is current.

---

## S-6. Reading weight — where the cost of reading sits

**Measure:** for code files, lines split into code, comment and blank, and the
comment share per file, against the repository's own median. For documents,
total length and — the figure that matters — the **longest unbroken span between
headings**, which is what a reader must cross to reach one answer. Both are
quoted in reading time at the same generous rate R-001 uses.
`bin/reading-weight` computes it.

It also separates the documents written for a **model** — `CLAUDE.md`,
`AGENTS.md`, agent, skill and rule files — and reports those in tokens rather
than spans, split by whether they load on every turn or on demand.

**Suggests:** where a repository's reading cost actually lives, and what is out
of line with its own norm. For agent files it suggests something different
again: a standing charge against the context budget that the work itself has to
share. Observed on real history — a 597-line file with thirty headings, ideal by
the human measure, was simultaneously the most expensive file in that repository
for a model. A file that is 80% comment is mostly prose and costs
prose to read; a 600-line document with four headings costs more to use than a
5,000-line one sectioned every eighty lines, and ranking by length gets that
backwards.

**How it lies:** in more ways than most of these, and none of them subtle.

*The comment share is not a quality score and must never be reported as one.*
It cannot distinguish careful explanation from commented-out code, a licence
header, or generated narration — a short file with a licence banner scores like
a well-documented one, which is why the outlier list has a length floor. Read it
as weight, never as merit; used as a score it is the most trivially gameable
number in this catalogue.

*The lexing is approximate.* Comment syntax is a vendored table for common
languages, not a lexer: markers inside string literals, nested block comments,
heredocs and regex literals are not modelled. Python docstrings count as
comments, which is right for reading weight and wrong if you wanted comments
strictly. Trailing comments on code lines count as code, deliberately — the line
must be read for its logic either way. Never quote one file's ratio as exact.

*Structure detection is convention-bound.* Headings are recognised in the
markdown and rst styles; a document organised some other way reads as
unstructured when it is not. And any heading counts as an entry point, which
over-credits a document with many shallow headings that do not actually
partition meaning.

*The token count is an estimate and the audience is a guess.* Tokens are
approximated at four characters each — the standard rough heuristic, wrong by a
noticeable margin for code, tables and non-English text, and wrong in a
model-specific way regardless. And whether a file is written for a model is
decided by path convention (`CLAUDE.md`, `.claude/`, `.cursor/`, `SKILL.md` and
friends); a repository with its own convention will have its instruction files
counted as prose, and a human-read document living under one of those paths
counted as machine-read. Which files load *every turn* is convention too, and
harness-specific.

*The distribution excludes what it could not read.* Generated, vendored and
unknown-syntax files are skipped, so a repository whose weight lives in a
language the table does not carry reads as lighter than it is. The count of
skipped files is printed for that reason.

**Derived rule:** R-010, from the document half only — the longest prose span
between headings, exempting spans that are mostly table or fenced code. The
comment-share half has no rule and should not acquire one, for the reason above:
it is weight, not merit.

---

## Method notes

**Absolute figures mean little.** Every signal is read against the same window
one period earlier — the repository's own history is the only honest yardstick.
`bin/window-facts --baseline` does that comparison.

**A dated, stated convention change is a window boundary.** Where the repository
records the moment its practice changed — an accepted decision record adopting a
branching model, a documented policy shift — its history has regimes, and a
window that straddles the boundary averages across them, producing a reading of
neither. Split at the boundary and read each side against its own kind. The same
caution applies to trends across the boundary: a change in the numbers may be
the convention taking effect, or the work changing character at the same moment
(a project winding down produces small careful increments because the increments
are small), and the split alone cannot say which.

**Window edges cut act-grouping.** Signals that group consecutive commits into
increments by time gap (`--act-gap`) will split a run that straddles a window
edge into two, so a windowed reading and a full-history reading can disagree by
an increment or two at the margins. Neither is wrong; compare like with like.

**The script counts; the agent interprets.** A process reading is mostly
numbers, and one wrong figure discredits the document.

**Retired: rework commit ratio.** The fraction of commits touching a
previously-touched file was measured at 84–98% across every real window tried.
At any scale most commits touch something an earlier commit touched, so it
reported that iteration exists rather than what it cost. Gross churn against net
churn carries the same concern honestly.

**Tested once, not established: fast work predicting later rework.** The
hypothesis that burst-produced files are rewritten more afterwards was tested on
one repository over one period. Naively it appeared to hold; the apparent effect
was largely a confound, because bursts are disproportionately where
documentation is produced, and documentation and source have different natural
rework rates. Stratified by file kind, the effect survived weakly for source
files and vanished for documentation, on a small sample. **Not strong enough to
treat as a leading indicator.** Worth re-testing on more history before any rule
depends on it — and worth remembering as the shape such a test takes: a
correlation that dissolves once you ask what kind of files it is made of.

---

## S-7. Declared stakes — which paths a repository singles out

**Measure:** whether the repository declares, in-tree and path-scoped, that
some paths need particular people — `CODEOWNERS` at any of its three valid
locations, or `OWNERS` files by placement — and if so, how many patterns it
carries, whether any is a catch-all, and what share of the files changed in a
window those patterns cover. `bin/stakes-proportionality` computes it.

**Suggests:** where a project believes its own risk sits, stated by the project
rather than inferred by this instrument. That distinction is the whole value: a
declaration is the target's own standard, and reading stakes off the code
instead would be an opinion about someone else's architecture. Coverage is the
informative half — seven patterns naming seven distinct owner sets says
something quite different from one line reading `* @org/team`, and a
declaration covering 87% of changed files says the project treats nearly
everything as owned.

**How it lies:**

*Absence is not indifference.* Six of seven repositories measured had no
declaration of any kind, including a mature workspace with careful review
practice. `CODEOWNERS` is a review-routing feature of one hosting platform;
not using it says the team does not route reviews that way, not that nobody
cares where it counts.

*Presence is not enforcement.* The file declares an intent. Whether the named
owners actually reviewed anything is on the hosting platform, outside git and
outside this instrument entirely.

*Currency is unverifiable.* An owner set can name people who left years ago,
and the file reads identically either way.

**Signal and rule, not signal instead of rule.** R-008 derives from the same
measurement and asks a narrower question: whether the paths a repository marks
most heavily get at least the review window of the paths it marks least. That
rule needs a populated gradient and often has none. This signal has no such
requirement — it reports the declaration and its coverage on any repository that
has one, including every repository where the rule returns not-applicable, which
so far is all of them. Report the shape; leave the scoring to R-008.

---

## S-8. Reversal — change that undid recent change

**Measure:** the commits in a window that revert (by subject, by git's own
"This reverts commit" trailer, or by quoting the subject of an earlier commit,
which is all a squash landing keeps); commits that announce themselves as a
re-land; the share of commits that name what they fix; and, for each revert,
whether the reverted content returned later in the window and whether it
returned byte-identical (patch-id equality). `bin/reversal` computes it,
together with the file-level rewrite reading behind R-013.

**Suggests:** whether the repository has a working correction path at all, and
whether what it corrects stays corrected.

**How it lies — and it lies in the flattering direction.** A high reversal rate
is at least as consistent with a healthy safety net as with poor work: a team
that detects and backs out within the hour reads worse by this count than one
that ships the same defect and never notices. And a revert is only one shape
of correction — fix-forward work that names nothing is indistinguishable from
any other change, so a repository that never reverts on principle reads as one
that never corrects. Read it as evidence that correction *happens*, never as a
defect rate, and read the fix-reference share as a habit of the history, not a
measure of anything about the code.

**Derived rules:** R-012, from the re-land half; R-013, from the file-rewrite
reading in the same script.

---

## S-9. Open-ended work — branches that never landed

**Measure:** branch refs that did not land, by three tests rather than one:
the tip is not reachable from the trunk, the branch has commits of its own,
and its cumulative diff does not fingerprint (patch-id) to any trunk commit.
For each: age of the last commit, when the work was begun, commits held. Plus
the repository's **ref-retention convention** — what share of branches that
visibly landed still hold a ref — and the trunk's landing rate per window, so
the stale stock can be stated in windows of throughput. `bin/open-ended-work`
computes it.

**Suggests:** how much begun work is outstanding, how old it is, and whether it
keeps being left.

**How it lies — badly enough to nearly disqualify it.** *On a squash-landing
repository every surviving branch is unreachable from the trunk whether it
landed or not*; the naive measure calls the whole ref list abandoned. The
patch-id test is what makes the signal readable there at all. Then the
retention convention decides everything: where refs are removed on landing the
survivors are outstanding work, and where they are kept the survivors are done
mixed with abandoned and nothing in git separates them. The convention has to
be established from the history — it is the measurement, not a preliminary —
and on a sample of one merge it was established wrong. Also inflated by release
and integration lines, forks and bot branches (excluded by name pattern, which
is convention-bound); a bare clone carries only what the remote kept; and the
most recent window is full of pull requests awaiting review, which look
identical from git, so only refs older than a window are called stale. What it
cannot see at all: work begun, abandoned and deleted. The stock is a floor.
And one reading sees only inflow: where refs are removed on landing,
everything that resolved has vanished, so begun-per-window is survivors by
start date and says nothing about growth. The delta is a cross-reading
quantity — with `--record` the reading leaves a sidecar of hashed tips in the
case directory, and the next reading reports begun, resolved and still
outstanding since. A surviving ref did not land here, which is not the same
as unfinished.

**A constraint from P-6.** Branch names frequently carry a contributor's
handle. The script prints them so a reader can look; a case file must not
quote them.

**Derived rule:** R-014, conditional on the retention convention.

---

## S-10. Marker debt — recorded obligations that accrete

**Measure:** over consecutive windows, markers added and removed (from the
diffs), the stock at each window boundary (from the tree), and the age of what
survives (from blame on the files holding them, capped). Word-bounded and
case-sensitive — `TODO`, `FIXME`, `HACK`, `XXX`, `BUG` by default, configurable
to whatever the repository actually writes. Vendored, generated and fixture
paths excluded. `bin/marker-debt` computes it.

**Suggests:** obligations the repository recorded for itself and has not
discharged, and whether the pile is growing.

**How it lies:** the level is meaningless. A repository that writes no markers
is not cleaner, it is silent — measured: one mature history carried zero
markers over two years, another 337 — so cross-repository comparison says
nothing and only the repository's own trend carries anything. The trend is
also noisy at short windows: on a small repository the stock sat flat for four
windows and moved in two. And a marker is a *good* practice being counted
against: the honest reading is the derivative, never the stock, and a
repository that writes markers and works them off is doing exactly what the
markers are for.

**Derived rule:** R-015, conditional on the repository evidently using markers.

---

## S-11. Increment spread — declared areas per landing

**Measure:** per landing, the number of distinct areas touched under the
repository's **own** partition — its ownership file's patterns, else its
workspace manifest, else its top-level directories, descending into a lone
code directory until at least two code areas exist. Reported by size band
against the repository's own distribution. Hub areas (touched by most
landings) and accompaniment areas (tests, docs, examples, tooling) are
excluded; landings that are renames, lockfiles, manifests, changelogs, a
sweep (many files at a line or two each) or one edit applied everywhere are
reported as mechanical. `bin/increment-spread` computes it.

**Suggests:** whether a landing could have been reviewed as a single decision.

**How it lies:** the partition is the whole measurement, and each source of it
misleads differently. Ownership patterns declare stakes, not modules. A
workspace manifest declares packages, which inflates spread on a fine-grained
workspace and deflates it on a coarse one. Top-level directories on a
single-package repository are `src`, `tests`, `docs` — accompaniment, not
width, which the first run reported as a finding before that exclusion
existed. The mechanical exemptions are heuristics: a dependency migration
that touches every crate for real reasons is not a sweep and is not uniform,
and it will be listed. And the landing unit matters more here than anywhere:
grouping squash landings by time welded independent pull requests together,
and a one-file dependency bump read as 586 files across 18 areas until the
unit was fixed.

**Derived rule:** R-016.

---

## S-12. Enforcement surface — what the repository makes mandatory by machinery

**Measure:** an inventory at the ref of pipelines, hooks, lint and format
configuration, test-runner configuration, build and type configuration,
ownership, change templates, release and dependency automation, and written
conventions; per category, how often it was touched in the window and ever,
and when last; and whether file types or top-level areas that first appeared
in the window are named anywhere in the pipeline, hook or lint configuration.
`bin/enforcement-surface` computes it.

**Suggests:** how much of the repository's discipline is written down as
machinery rather than carried by habit — P-6's question, asked of
configuration, which is the only way P-6 permits it to be asked — and whether
that machinery moved while the work did.

**How it lies:** presence is not execution. A workflow can be disabled at the
platform and reads identically in git. Required checks, approval rules and
branch protection live on the forge, invisible here. A repository may enforce
from a shared external system and carry nothing in-tree. Hooks in `.githooks/`
run only where each clone has been told to use them. And "touched in the
window" measures churn in the configuration, not enforcement: on one history
71% of landings touched the surface because an automated updater bumped hook
versions weekly.

**No rule, and none proposed.** This narrows the frame's *verification
blindness* gap — the gate chain is at least visible — without closing it, and
the residue is the same forge boundary R-001 lives with.

---

## S-13. Merge provenance — what a merge landed beyond its branches

**Measure:** for each two-parent merge with a merge-base, the automatic
merge of the parents is recomputed (`git merge-tree --write-tree`) and the
merge's actual tree is diffed against it. Reported in two parts: the size of
any hand-written resolution inside conflicted files, and every change in a
file no conflict touched. `bin/merge-provenance` computes it.

**Suggests:** how much of a repository's landed content exists on no branch.
A merge identical to the automatic merge carried only what was reviewed; one
that differs carried something that was not.

**How it lies:** the automatic merge is git's, with the default strategy. A
repository that merges through a queue, a bot or a custom driver will differ
from it systematically, and every merge will read as carrying extra content
— which is the tell, and the first run makes it obvious. A conflict
resolution is content from neither branch and is expected; only its size
is informative. Not applicable at all on squash and applied-patch histories,
which is most of them. Measured: on a merge-commit library, 45 of 57 merges
identical, 15 with resolutions of median 15 lines and one of 428, one
changing four lines outside any conflict; on a button-merge application, 441
of 441 identical.

**Derived rule:** R-017, from the outside-any-conflict half only.

---

## S-14. Removal notice — how long a deprecation stands before its thing goes

**Measure:** over first-parent diffs, every deprecation marker added and
later deleted, keyed by file and normalised text, giving notices opened,
closed, withdrawn (the closing commit is a revert) and still open; the
distribution of notice length when closed; and the age of what is still
open. Markers are recognised by the common languages' conventions and are
configurable. Only code paths count — not configuration, documentation,
tests, vendored trees, or anything under `internal/`. `bin/removal-notice`
computes it.

**Suggests:** how much time a repository gives between announcing a removal
and making it.

**How it lies:** in a stack of ways the first runs enumerated one by one. A
test runner's `filterwarnings` line in a config file matched (twenty days,
deprecated nothing). A vendored tree under `third-party/` matched twenty-six
times. Two symbols under `internal/` had no downstream reader. Three two-day
closures were one reverted pull request — a notice withdrawn, not a thing
removed. A rewording in a separate commit read as a fresh notice. And a
repository migrating text markers to a struct-based mechanism the pattern
does not know reads as closing every notice at once. What remains after all
of that: the pattern is convention-bound, a commented-out marker matches, and
whether anything downstream existed is not in git at all.

**Derived rule:** R-018, conditional on the repository using markers.

---

## S-15. Subject against content — what a landing said against what it did

**Measure:** per landing on the first-parent line, the subject (for a merge,
the first line of its body where a platform puts the pull-request title, else
the branch tip's subject) against the classified churn: whether the subject
is typed and with what type, whether it makes a trivial claim, and how many
source lines it carries in the repository's source home and outside its test
home — both homes learned from which typed landings touch which directories.
`bin/subject-content` computes it.

**Suggests:** how far a reader can trust this repository's labels, which is
how far a reader filtering by label can skip.

**How it lies:** the typed convention is recognised in its common form only,
and a repository with its own vocabulary reads as untyped. The homes need
ten typed landings of each kind to learn and are learned at two path levels;
churn share cannot learn them at all, because good `fix:` commits carry tests
into the test directories. Doc comments inside source are source. The
trivial-word list is English and finite, and matching it anywhere in a
subject was wrong half the time — the feature's own domain, a backticked
identifier, one clause of a long subject — until only the head claim
counted. Measured: on a fully typed history, 348 restrictive-type landings
yielded six candidates after the layout was learned; on a partly typed one
the typed half stood down and 227 trivial claims yielded six, all the shape
the rule describes.

**Derived rules:** R-019, from the typed half, conditional; R-020, from the
trivial-claim half.

---

## S-16. Care over time — the repository's own rigor as a series

**Measure:** the landing unit over N consecutive windows, each landing with
its size, test and reasoning accompaniment, review interval where it is a
merge, and paths. From that one series: care per window and per window
ranked by throughput; the rank correlation of size and review interval per
window; care inside and outside the windows around each kind of declared
risk moment — release tags with a run-up scaled to the tag cadence, major
versions, reverts, breaking markers; care per area of the repository's
partition in each half of the span; and, from the whole history rather than
the span, care on the paths an ownership declaration named, ninety days on
each side of it. `bin/care-over-time` computes it.

**Suggests:** whether the repository's rigor tracks its risk and resists its
pace, in its own terms and over its own time.

**How it lies:** it needs history. Below eight windows with ten substantial
landings each, nothing here is a trend; two of four calibration histories
were too quiet, and a young repository will always be. Windows are calendar
slices, and a documented convention change inside the span turns a trend
into two processes. Risk is only what was declared, and a declaration can
be the normal state — a fixed fourteen-day release window covered 84% of
one history's landings, and 282 breaking labels in two years made
"breaking" ordinary on another — so each kind is compared separately and a
saturated kind is set aside. The review interval exists only on merge
commits. And the ownership experiment needs a declaration broad enough that
ten landings touched its paths on each side, which four narrow declarations
on one history did not give it. Measured, on a busy application over two
years: tests 95% in the first quarter and 53% in the last, fastest windows
twelve points under the slowest, review interval uncorrelated with size in
every window.

**Derived rules:** R-021, R-022, R-023 (P-14); R-024, R-025 (P-15).

---

## S-17. Decision points — how much branching a landing added

**Measure:** per landing, the number of decision points in the code lines it
added less those in the lines it removed — `if`, loops, `case`, `catch`,
boolean operators, the ternary, a `match` arm — counted by token on the diff
of code files, per extension family, skipping comment lines and counting
nothing in configuration. That is McCabe's cyclomatic number computed the
only way a bare clone allows: on the change, with no parser, as a count of
how many new ways through the code the landing opened. Reported by line band
(the spread of decisions at each size, and the rank correlation between the
two axes), by decision band (whether a test arrived, beside the same rate by
line band), as the landings small in lines and large in decisions, and per
top-level area (share of decisions added against share of lines, and the
care in each). `bin/decision-points` computes it.

**Suggests:** whether the repository's care follows how much a change could
go wrong, where line count cannot see it; and where the repository's
branching concentrates, which is a gradient of stakes it never declared.

**How it lies:** it is a token count, not a graph. A decision keyword inside
a string counts; a generated switch counts unless the classifier knows the
file is generated; a language the family table does not know is counted by
a generic pattern that misses its own keywords and matches English. Net of
removals is the measure because gross count listed exactly the wrong things
first — a substitution of one atomic API for another, a lint fix, a
linter enabled across ten files — but net also hides a rewrite that replaces
thirty decisions with thirty different ones, which is R-013's shape and not
this one's. And the number is a proxy for lines for most software (Shepperd
1988) with high variance at the level of one change (Landman et al. 2016);
measured here on four histories, the rank correlation between lines and net
decisions per landing ran from +0.31 to +0.60, which is the second axis
carrying something and not everything. What it cannot say is anything about
whether the branching was warranted, well-shaped or understood: that is a
judgement about code, and outside this instrument.

**Derived rule:** R-027.
