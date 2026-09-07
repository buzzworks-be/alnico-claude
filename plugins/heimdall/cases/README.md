# Cases

One directory per case, named by **codename**; one case file per reading inside
it:

```
cases/<codename>/<YYYY-MM-DD>-<short head sha>-<short principles sha>.md
cases/<codename>/case.json
```

A **codename** is a pseudonym for the case, drawn at random from
`bin/codenames.txt` at attach time and stable for the life of the case. It is
never derived from the target — a name computed from a URL could be reversed by
anyone holding the wordlist, which would put the repository's identity in a
directory name with every content rule satisfied.

Being target-agnostic buys more than safety. A codename lets a case be
discussed, filed and compared without naming what it is about: *"the finding in
ORCHARD"* is sayable in a room where the repository's name is not.

**Detaching closes a case. Re-attaching the same target opens a new one**, with
a new codename — a second investigation of the same repository is a second
investigation, and case files already carry the old name. `case.json` records
the codename, when the case opened and closed, and how many readings it holds;
it records nothing about the target, which stays in the gitignored
`.heimdall/`.

**Purging is per case.** `bin/detach-target.sh --purge-case-files` removes the
files of the case being closed and no others, and reports which other codenames
still hold files, so an operator cannot purge one case and believe the machine
is clean.

All three parts earn their place. The date orders the records, the head sha says
what was read, and the principles sha says which frame of reference it was read
*against* — so a range re-examined under amended rules stands beside the earlier
record instead of replacing it. Rules change as they are found wanting; the record of what they
used to say, and what they used to find, is worth keeping.

## A case file is a handoff artifact, not a repository file

Heimdall writes the case file here as `<id>.md`, following `_TEMPLATE.md`, and
hands it over — to a human, or to another agent. It is **gitignored**: it cites
files, lines and code in the observed target, and **nothing about the target
may enter Heimdall's own history** — not its name, not its owner, not a path or
a line of its code, in a tracked file or a commit message. Only this README and
the template are tracked.

Retention is the recipient's problem, deliberately. Heimdall keeps no memory of
its own readings, which means it cannot answer "is this getting better or
worse" — that question belongs to whoever collects the artifacts.

## Written for two readers

The frontmatter is for a machine: target, range, principles sha, an overall
`severity` field, and counts by severity. An agent can route on it without
parsing prose.

The body is for a person. One rule it must follow: **quote what the rule
requires, do not just cite its id.** The recipient may not have Heimdall's
checkout, and `R-007` on its own is not actionable. Rules are target-agnostic,
so quoting them into a case file leaks nothing.

One consequence worth being deliberate about: handing a case file to an agent that
then fixes the findings closes the loop, and a closed loop means the worker is
optimising against the rules. That may be exactly what you want. It does mean
the rules stop being a measurement and become a target — so it is a choice to
make per use, not a default to drift into.

The human form of the same loop is easier to walk into and harder to notice:
taking a case file into the team's own sprint or project retrospective. It
feels like the responsible thing to do with a finding, and it is the fastest
way to lose the instrument. From the next sprint the history is written by
people who know what is counted, and nothing about that adjustment is visible
in the record. Same rule applies — a deliberate choice, spent once, and every
later case file on that repository must carry it as a limitation.

## The trigger is not yet defined

Two questions are open, and they are coupled:

**What is an increment?** A single commit; a merged PR; the diff of a branch
against its base; or a session's worth of work however many commits it took.
This decides what `<base>..<head>` means, and whether increments can overlap or
be reassessed.

**What starts an assessment?** On demand in a session; a schedule that polls
the target for new commits; or a webhook on the target. Note that Heimdall
observes read-only — it can *watch* the target without any write access, but
anything that reports back into the target (a PR comment, a status check) would
need write access there and would break the read-only property. If case files stay
in this repo, the boundary holds.

Until both are settled, `/profile` takes its range from the user and states it
explicitly in the record.

## What a case file must contain

Enough that someone can re-derive the conclusion without rerunning the
assessor:

- **Target** — URL, and the `<base>..<head>` range assessed
- **Principles version** — the sha from `bin/principles-ref`, so a case file stays
  interpretable after the rules change. That command also refuses to produce one
  while `principles/` has uncommitted changes: a standard that moved during the
  assessment cannot be cited by it
- **Per-rule outcome** — pass / violation / not applicable, by rule id
- **Findings** — each with file, line, and ref in the target
- **Observations** — anything worth saying that no rule covers
- **Severity** — the overall level, plus what was *not* checked
- **`outcomes:`** — one entry per rule that existed at `principles_sha`,
  including rules that were not run, marked `not-reported`. `bin/case-strip`
  renders a cell for every rule in the frame and marks a missing entry `!`,
  so leaving a rule out makes the gap louder rather than quieter

**Never a rate without its adjudicated outcome.** A check's candidate count is
not a result, and separating the two is how a case file misleads without saying
anything false. A field run produced *3 of 3 specifications flagged* — the
strongest signal R-002 can emit — and all three dissolved on reading: one under
the open-question exemption, one a mechanical rename, one where the code
maintained the document rather than implementing it. Written as a rate, that
increment reads as damning; written as a rate *with what adjudication did to
it*, it reads as three different innocent shapes and a check doing its job. The
first version is the one a hurried reader remembers, so the two figures travel
together or the rate does not appear.

