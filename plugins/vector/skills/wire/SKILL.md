---
name: wire
description: >-
  Put the traceability check into this repository so CI fails the build when
  the threat model stops describing the product: copy the check beside the
  code, write a workflow that runs it, and record a digest against every
  requirement the register references. Use when a .vectors.yaml exists with
  dispositions and someone asks to wire the check into CI, to make the threat
  model checked on every push, for "continuous threat modelling" or "fail the
  build when the model goes stale" — and when a repository already has the
  check and the plugin has moved on since it was copied.
---

# Wiring the check into a repository

Everything else in this toolkit runs when somebody runs it. This one runs on
every push, where no session exists, and it is the only part of the toolkit
that can make a build fail. Setting it up is the one piece that needs a
session, and it is what you are doing here.

The check is **copied into the repository, not referenced**. One committed
file, one pinned dependency, one command. A project can read every line of what
gates its merges, nothing is fetched at build time, and any runner at all can
run it — which is the whole argument in
`docs/architecture/ADR-0007.md` if somebody asks why there is no Action to add
in three lines.

## Before anything else

**Refuse a register that is not finished.** Run the matrix check first.
Undispositioned vectors mean the register is still being decided, and wiring a
build to fail on an unfinished document teaches people to ignore the build.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_matrix.py <slug>.vectors.yaml
```

**Ask where the files should go.** `.vector/` is the default and nothing more
than that; a project with a `tools/` or `ci/` convention should keep it. The
path appears in exactly one line of the workflow.

## The loop

1. **Copy the check and its lock.**

   ```sh
   mkdir -p .vector
   cp "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_traceability.py .vector/
   cp "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_traceability.py.lock .vector/
   ```

   Then rewrite one line in the copy so a build log says which version made the
   claim, taking the version from the plugin's own `plugin.json`:

   ```
   VENDORED_FROM = "0.9.0"
   ```

2. **Write a workflow, if the project uses GitHub.** One job, one command, and
   nothing clever:

   ```yaml
   name: threat model
   on: [push, pull_request]
   permissions:
     contents: read
   jobs:
     traceability:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with:
             persist-credentials: false
         - uses: astral-sh/setup-uv@v10
         - run: uv run --locked --script .vector/check_traceability.py
   ```

   Say plainly that this file is the project's, not the toolkit's: it can be
   replaced, merged into an existing workflow, or skipped entirely. `python3`
   against a system PyYAML works the same way, and so does a Makefile target, a
   pre-commit hook, or GitLab CI. **Pin the actions the way the project pins
   actions** — if it pins to commit hashes, match that, and do not quietly
   introduce a looser convention than the repository already keeps.

3. **Seed the digests, showing each document first.** Every mitigation that
   names a `specified_in` needs a `specified_digest` beside it, and this is the
   step to slow down on. **Show the person the requirement before recording
   anything.** A digest is a claim that somebody read the document and agrees
   the mitigation still answers it; recorded without reading, it is the rubber
   stamp the whole chain cannot prevent, applied at the very first opportunity.

   ```sh
   sha256sum docs/specifications/SDD-0014.md
   ```

   If a document plainly does not say what the mitigation claims, that is a
   finding, not a formatting problem. Record it as a disposition to revisit
   rather than digesting it and moving on.

4. **Check whether the referenced documents carry a status.** The check reads
   YAML frontmatter, or the first word of a `Status` row in a header table. If
   a project's documents have neither, everything still works except
   supersession detection, and the check says so as an advisory. Offer to add a
   status row; never add one unasked, because a status is a claim about the
   document and it belongs to whoever owns it.

5. **Run the check and read the result together.**

   ```sh
   python3 .vector/check_traceability.py --as-of 2026-09-14
   python3 .vector/check_traceability.py --json
   ```

   Advisories are not failures and should not be tidied away reflexively. A
   mitigation with no specification is sometimes a control that existed before
   anybody wrote a requirement for it, which the register allows on purpose.

6. **Exclude what should not be scanned.** Documentation quoting the annotation
   format registers as an annotation, and so does a test fixture containing a
   deliberately broken one — the format is a literal string and the scanner does
   not know what a comment is. Add `--exclude 'docs/*'` and `--exclude 'tests/*'`
   to the workflow's command where that happens, and the same for generated
   files that are committed. Keep the list in the workflow, where the diff shows
   it. This toolkit's own repository needs both, which is the clearest evidence
   that a project will.

7. **Hand back what the build will now do**, including that it reports coverage
   rather than proof, and that a green build means the paperwork is consistent
   and current — never that any control works.

## Updating a vendored copy

The cost of copying rather than referencing is that no fix reaches a repository
on its own. **When this skill runs in a repository that already has the check,
compare versions first**: the `VENDORED_FROM` line in `.vector/` against the
plugin's current `version`. If the plugin is newer, say so and offer to rewrite
the file, then show the diff. That is the whole update mechanism, and it works
only because somebody is present — which is why the skill does it before
anything else.

## What the check reports

- **Stale** — a referenced requirement has changed since the mitigation was
  decided against it. Read the change, then either revise the mitigation or
  record the new digest to say you have read it.
- **Superseded** — the requirement's status says it has been retired. The
  mitigation answers a decision nobody holds any more, and needs re-deciding
  rather than re-digesting.
- **Expired** — a deferral is past its date, which is staleness of the same
  kind measured against the clock.
- **Stale model or enumeration** — something upstream moved and the chain below
  it has not been re-run. `/vector:dfd`, `vector:enumerate` and
  `/vector:promote` are the repairs, in that order.
- **Unknown annotation** — a line in the source names a mitigation no register
  has. A claim in code about a document that does not support it.
- **Partial coverage** — a mitigation declaring several locations, annotated in
  some. Shipped on one platform, missing on another.

## What you cannot do

**Nothing here proves a control works.** The check reads documents and compares
them with each other, so a green build means a set of internally consistent
claims is current. Whether the code does what the requirement says is a code
review, and the one mechanical way to contradict a claim is a vulnerability
scanner reporting something the matrix says is handled.

Do not add the check to a repository whose register is unfinished, and do not
soften it to get a green build. A check people disable is worse than no check,
because the reassurance outlives the enforcement.
