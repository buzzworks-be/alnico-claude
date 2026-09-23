---
name: matrix
description: >-
  Give every tracked vector a disposition — mitigated, accepted or deferred —
  and record the mitigation, owner or expiry that makes it a decision, with
  each mitigation written into the specification the work is built from, and
  a likelihood, impact and risk level the person rates. Use
  when a .vectors.yaml is complete and someone asks what is being done about
  the threats, for "the threat matrix", "disposition these", "who owns this
  risk", "we need the mitigations written down", "how bad is this", "rate the
  risks", "likelihood and impact" — or when the register has
  changed and new vectors sit undispositioned or a deferral has expired. The
  output is the same ctm/<slug>.vectors.yaml, with dispositions and mitigations
  added, and its rendered ctm/<slug>.matrix.md.
---

# The matrix: from a threat model to decisions

A threat model says what could go wrong. A matrix says what somebody decided
to do about each thing, and who. This skill is where those decisions are made
and written down — and, for anything not yet built, where the mitigation is
written into the specification an implementer will read, so the control is
built into the product rather than looked for afterwards.

It is a skill rather than an agent for the reason `/vector:promote` is: every
disposition needs a person. An owner, an acceptance, a date, a likelihood and
an impact — none of these can be invented, and the person in the session is
the one who can give them.

"Done" is a script's decision. `scripts/check_matrix.py` reads the register
and reports every vector without a disposition or a rating, every disposition
missing the field that makes it a claim, and every mitigation that is written
nowhere the work will meet it. You are finished when it exits 0.

## Before anything else

**Refuse an unfinished register.** Run the promotion check first. Undecided
findings, or a register stale against its enumeration, mean the set of vectors
is still moving, and dispositioning a moving set produces decisions about the
wrong things. Say so and stop; finishing it is `/vector:promote`'s job.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_vectors.py ctm/<slug>.vectors.yaml
```

**Find out who is deciding, and who owns what.** The person in the session
carries the session's decisions, but an acceptance is owned by whoever is
accountable for the risk, and that may be somebody else. Ask. Never write a
team as an owner: a team accepts nothing, a person does.

**Settle the scale, once.** Ask whether the organisation has a risk matrix of
its own. If it does, declare it in full as `risk_scale` — five likelihood
levels, five impact levels each defined for the organisation and for the
people the data is about, the bands, and all twenty-five cells — and the check
will refuse a partial one. If not, the register gets `risk_scale:
vector-5x5-v1`. Either way it is named: a rating means nothing without the
scale it was given on. Show the person what they will be rating against:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_matrix.py ctm/<slug>.vectors.yaml --scale
```

## The loop

1. **Run the matrix check immediately.** It reports every vector as
   undispositioned, grouped by element, which makes the remaining work a
   number from the first turn.

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_matrix.py ctm/<slug>.vectors.yaml --json
   ```

2. **Look for the control before proposing one.** For each vector, before
   asking anything, search the code and the project's documents for something
   that already addresses it — a rate limit in the gateway config, a
   validation middleware, a review procedure. A mitigation that already exists
   is `mitigated` with `implemented_in` pointing at real code, and that beats
   a specification for work that is already done. Say what you found; let the
   person confirm it is the control they mean.

3. **Ask the one question, and let the answer pick the state.** *What is being
   done about this?* Three answers exist:
   - **A control addresses it** → `mitigated`, naming the mitigation. If the
     control does not exist yet, this is not the answer — see the next.
   - **It is designed and not built, or not yet decided** → `deferred`, with
     an owner, a reason and a date. Push back on "when we get to it": a
     deferral with no date is an acceptance with nobody accountable, and the
     check will not take one.
   - **The exposure is knowingly carried** → `accepted`, with an owner and a
     reason a reader can disagree with. "Low risk" is not a reason; "the
     address is the one the shopper just typed, sent to the address they just
     gave" is.

4. **Rate it.** Every vector gets a likelihood and an impact from the person,
   each with a sentence saying why that level and not the one beside it.
   - Show the definitions from `--scale` — the check's words, not a summary
     of them — and the vector's own `attack`, `impact` and `context`.
   - Ask for the likelihood, and why.
   - Ask who is harmed — the organisation, the people the data is about, or
     both — then for the impact at the worse of the two, and why. That
     question is what keeps the privacy half from rating low by default.
   - For a `mitigated` vector, ask both again with the control in place: the
     `residual`. An `accepted` or `deferred` vector has only the `inherent`
     rating, because nothing is in place for a second one to describe.
   - Write `level` from the `ratings` in `--json`. Never choose it.

   **Do not propose a level** — not as a number, not as a range, not as
   *that sounds like a 3*. A suggested level is an anchor, and a person
   agreeing to it is an invented score with a signature on it. If they ask
   what you think, say that the choice is theirs, and point at the two
   definitions they are between.

5. **Write the requirement where the work is specified.** For every
   mitigation that is not yet built, the control goes into the document the
   implementer will build from — an SDD, a design doc, an RFC, a README
   section; whatever this project uses — and `specified_in` points at it,
   with an anchor. Write it there *in this sitting*, in the project's own
   voice, as a requirement: what the control is, what it must do, how it will
   be verified. A mitigation that exists only in the register is the failure
   this skill exists to prevent, and the check refuses a `deferred` vector
   whose mitigation names no specification.

   A project with nowhere to write a requirement has found a real problem.
   Say so; do not invent a document to satisfy the check.

6. **Say how each mitigation will be verified.** `code` means a check in CI
   will later look for an annotation naming the mitigation's id where the
   control lives, and `implemented_in` says where that is. `manual` means a
   person does something and there is evidence they did — name where the
   evidence lives. A manual control nobody can show is a claim.

7. **Assign the next id from the check, never by counting.** `--json` reports
   `next_id`, computed over live and retired mitigations, so a retired number
   is never handed out again.

8. **Record a change as a change.** When a disposition changes state, a
   rating changes, or a deferral's date moves, the previous state goes into `history` with its own
   reason and date. The reason a decision was reversed is often the most
   useful thing in the document, and a date pushed twice is reported so a
   reader sees the pattern.

9. **Re-run the check after every element.** Finish only when it exits 0.

10. **Render, and hand back the limits with the document.**

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_matrix.py ctm/<slug>.vectors.yaml
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/render_matrix.py ctm/<slug>.vectors.yaml -o ctm/<slug>.matrix.md
```

Both take `--as-of YYYY-MM-DD` to judge deferrals against a date other than
today, which is what a test or a fixture needs. `uv run --script` in place of
`python3` works too — each script carries inline dependency metadata and a
lockfile.

The rendered matrix opens with where the risk sits — two five-by-five grids,
*now* and *with nothing done*, whose difference is what the controls moved —
lists vectors worst first, and states the scale it was rated on. It links
every id and every reference it can reach: a
mitigation id to its own section, a `specified_in` to the requirement that
carries the control, and a vector id to that vector's own entry in
`ctm/<slug>.vectors.md`. It links only what resolves, so render the threat model
view first — [`/vector:promote`](../promote/SKILL.md)'s last step — or the
vector ids come out as plain text. Everything is relative to `-o`, so write the
document beside the register.

## What the fields look like

```yaml
- id: VEC-0001
  # … the vector, as /vector:promote wrote it …
  disposition:
    state: deferred                       # mitigated | accepted | deferred
    owner: Ines Verhaeghe, privacy lead   # a person; accepted and deferred need one
    reason: >-
      The control is designed and written into the specification, and it is
      not built: it lands with the guest-path rework rather than ahead of it.
    until: 2027-03-31                     # a date; deferred needs one
    until_label: 2027.1 — guest path rework   # the milestone, beside the date
    decided: 2026-09-13
    mitigations: [MIT-0001]
    risk:
      inherent:                           # every vector
        likelihood: 3                     # 1 to 5, on the register's scale
        likelihood_reason: >-
          A motivated outsider who knows a guest's email and can produce a
          document nobody has anything to compare against.
        impact: 4
        impact_on: both                   # organisation | data_subjects | both
        impact_reason: >-
          A complete export delivered to a stranger — a notifiable breach, and
          serious for the person it is about.
        level: high                       # from --json; never chosen
      # residual: the same five fields and a level, on a mitigated vector only
    history:                              # only once something has changed
      - state: deferred
        until: 2026-12-31
        reason: Original estimate, moved when the rework slipped.
        decided: 2026-06-01

mitigations:
  - id: MIT-0001
    title: Bind the guest email before an order or a data request is accepted
    control: >-
      A six-digit code is sent to the address and must be returned within
      fifteen minutes; five attempts per address and twenty per source per hour.
    specified_in: docs/specifications/SDD-0014.md#guest-email-verification
    implemented_in: src/checkout/verify.ts      # once it exists
    verification: code                          # code | manual
    vectors: [VEC-0001]
```

The two fields the matrix owns are `disposition` on each vector and the
`mitigations` list; `retired` is shared with `/vector:promote`, and a retired
mitigation goes there with a reason. Nothing else in the file is this skill's
to change. The worked register at `assets/example.vectors.yaml` dispositions
fourteen vectors, with `assets/example.spec.md` standing in for the
specification its mitigations were written into, and `assets/example.matrix.md`
is what the result reads like.

## What the check reports, and why each is worth satisfying

- **`NO_DISPOSITION`** — the terminating condition itself. Nothing is finished
  while one remains.
- **`MISSING_OWNER` / `MISSING_REASON` / `MISSING_UNTIL`** — the field that
  makes the state a claim. An acceptance without an owner is a shrug; a
  deferral without a date cannot expire, and so cannot be caught going stale.
- **`BAD_UNTIL`** — a milestone where a date should be. Put the milestone in
  `until_label` beside a date the team believes in; if the milestone moves,
  the date moves and `history` records that it did.
- **`EXPIRED`** — a deferral past its date. Decide it, or move the date with a
  reason in `history`. Never quietly extend it.
- **`NO_PLACE`** — a mitigation with neither `specified_in` nor
  `implemented_in`. It exists only in this file, which is exactly the state
  the capability exists to prevent.
- **`SPEC_REQUIRED`** — a deferred vector's mitigation with no specification.
  The work is ahead; the requirement has to be where the implementer reads.
- **`IMPL_REQUIRED`** — a mitigated vector's code-verified mitigation with no
  `implemented_in`. Mitigated means the control exists; say where.
- **`UNRESOLVED_SPEC`** — a `specified_in` path that does not exist. The
  requirement is claimed to be written somewhere it is not. Paths resolve
  from the register's directory or the repository root; a URL is accepted as
  written.
- **`MISSING_EVIDENCE`** — a manual control with nowhere its evidence lives.
- **`DISAGREEING_LINK`** — a mitigation and a vector that do not name each
  other. Both sides list the relation so that either file section reads
  alone; keep them agreeing.
- **`ORPHAN_MITIGATION`** — a mitigation serving no live vector, because the
  vector was retired upstream. It stays, blocking, until the person retires
  it too, with a reason: it may be real code that now protects nothing anyone
  tracks, and that is a decision, not a tidy-up. Never delete it.
- **`PUSHED_UNTIL`** — advisory. A date moved twice or more. Sometimes the
  work really did slip twice; always worth asking whether this is `accepted`
  wearing a date.
- **`ALL_ACCEPTED`** — advisory. An element every one of whose vectors is
  accepted. Sometimes right; always worth a second look.
- **`NO_SCALE` / `UNKNOWN_SCALE` / `BAD_SCALE` / `NON_MONOTONIC_SCALE`** — the
  scale is missing, not one this check ships, incomplete, or says more
  likelihood can mean less risk. Nothing can be rated until it is fixed.
- **`UNRATED` / `NO_RESIDUAL`** — a vector with no rating, or a mitigated one
  with nothing saying what its control bought.
- **`STRAY_RESIDUAL`** — a residual on an accepted or deferred vector. Nothing
  is in place for it to describe; remove it.
- **`BAD_RATING`** — a level that is not a whole number from 1 to 5, or an
  `impact_on` outside its three words.
- **`RISK_MISMATCH`** — a `level` that is not the scale's cell for the two
  levels beside it. Take it from `--json`.
- **`RESIDUAL_ABOVE_INHERENT`** — a control rated as making things worse. That
  is a data error, not a finding.
- **`NO_REDUCTION`** — advisory. A control that leaves the risk in the same
  band. Sometimes true; always worth asking whether it is the right control.

## After the register changes

`/vector:promote` reconciled the register against a re-run enumeration: new
vectors arrive without dispositions and go through the loop; a vector it
retired leaves its mitigation orphaned, to be retired here with a reason or
re-pointed at a vector it still serves. A deferral passes its date: the check
goes red until somebody decides. Nothing here is edited without the check
being run again.

## What you cannot do

**A disposition is a claim, not a fact.** "Mitigated" means somebody said so
and named a control, and the check requires the control to have a place and
stops there. Whether the code honours the requirement is a code review;
whether the annotation is on the right function is one too. Say so when you
hand the document back, and let the rendered limits say it again.

**Do not propose a rating.** The scale in force is the model and the person
is the one using it. Levels are positions on two scales, not quantities: never
multiply them, add them, or offer a score for the system. The rendered matrix
orders by band and shows the levels beside it, and that is all the arithmetic
there is.

**A rating is a judgement, and the check cannot see a bad one.** It requires a
reason for every level and cannot tell whether the reason is true. Say so when
you hand the document back.
