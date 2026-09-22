---
name: promote
description: >-
  Turn a finished threat enumeration into a threat model: walk every finding
  with the person whose judgement decides what is tracked, promote the real
  ones to vectors with stable ids, chain the ones that are one concern seen
  from several elements, and record why the rest are not tracked. Use when a
  .threats.yaml is complete and someone asks which threats matter, what to
  track, how to get from findings to a threat model, or for "the vectors" —
  and when an enumeration has been re-run and the register beside it needs
  reconciling. The output is ctm/<slug>.vectors.yaml and its rendered
  ctm/<slug>.vectors.md.
---

# Promotion: from findings to a threat model

An enumeration is an inventory. A threat model is a set of decisions. This
skill is where a person makes them — which findings are real enough to track,
which are one concern wearing several elements' clothes, and why the rest are
not worth an id — and it is a skill rather than an agent on purpose: the
enumeration was made mechanical so that *this* step could be deliberate.

"Done" is still not a feeling. `scripts/check_vectors.py` reads the register
and reports every finding nobody has decided about, and you are finished when
it exits 0. Every `threat` verdict in the enumeration, and every open question
the model carried forward, ends up in exactly one of three places: as a
vector's source, in an authored vector's chain, or dismissed with a reason.

## Before anything else

**Refuse an unfinished enumeration.** Run the coverage check on the
`.threats.yaml` first. Uncovered pairings or a stale digest mean the input is
still moving, and promoting from a moving set produces decisions about the
wrong things. Say so and stop; the enumeration is `vector:enumerate`'s to
finish.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_coverage.py ctm/<slug>.threats.yaml
```

**Find out who is deciding.** The person in the session is the threat model's
owner for the duration — a security or privacy reviewer, or the engineer
acting as one. Their judgement is the point. Do not promote or dismiss
anything on your own; present, ask, record.

## The loop

1. **Write the skeleton immediately and run the check.** `threats`,
   `threats_digest`, `vectors: []`, `dismissed: []`, `retired: []`. Compute the
   digest from the enumeration's bytes:
   `sha256:$(sha256sum ctm/<slug>.threats.yaml | cut -d' ' -f1)`. The check then
   reports every finding as undecided, which makes the remaining work a number
   from the first turn rather than an estimate.

2. **Surface candidate chains first.** Run the check with `--json` and read
   `shared_nodes`: undecided findings on different elements citing the same
   catalogue pattern. Three findings citing `AA01` on three elements are
   usually one concern — the same missing control, seen from each place it is
   missing — and a chain authored *after* its parts were promoted separately
   leaves three ids where one was meant. Show these together, before anything
   is promoted singly, and ask whether they are one thing.

3. **Then one element at a time.** `undecided_by_element` groups the rest.
   For each finding put the verdict's `summary`, `detail` and cited nodes in
   front of the person, and ask what it means for *this* system. Never re-read
   them the verdict; they can read. Ask the question the verdict cannot answer:
   is this real here, and is it worth an id?

4. **Promotion asks three questions**, and records the answers as `attack`,
   `impact` and `context`:
   - what would an attacker actually do — or, for a privacy finding, what
     happens without anyone attacking;
   - what does it cost if it works;
   - what is already true about the system that makes it more or less likely.

   All three are required. A vector without them is a verdict with a number on
   it. "Nothing more is known" is an answer and should be written down as one;
   an empty field is not.

5. **Dismissal asks for the reason, and pushes back on a thin one.** "Not a
   priority" is not a reason. "The login already reveals account existence by
   design, so closing this timing channel changes little" is. The reason is
   the whole value of a dismissal — it is what the next reviewer disagrees
   with — and a register full of "not applicable here" has not been reviewed.

6. **Assign the next id from the check, never by counting.** `--json` reports
   `next_id`, computed over live *and* retired vectors, so a retired number is
   never handed out again. `VEC-0007` in a pull request description has to
   mean one thing forever.

7. **Review the open questions** the enumeration carried forward, with the
   same two options. "Nobody knows the retention period" is a non-compliance
   vector waiting to be promoted, and promoting it from the question rather
   than from a finding on the same concern keeps the origin visible — the
   vector's first job is to get the question answered.

8. **Re-run the check after every element.** Finish only when it exits 0.

9. **Render, and hand back the limits with the document.**

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_vectors.py ctm/<slug>.vectors.yaml
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_vectors.py ctm/<slug>.vectors.yaml --json
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/render_vectors.py ctm/<slug>.vectors.yaml -o ctm/<slug>.vectors.md
```

`uv run --script` in place of `python3` works too — each script carries
inline dependency metadata and a lockfile — and installs the pinned PyYAML
with no setup.

## What a vector looks like

```yaml
- id: VEC-0003
  title: The order path has no throttle anywhere in the model
  element: checkout-api                 # the primary anchor; where a control would land
  category: stride/denial_of_service
  source: authored                      # verdict | authored | question
  verdicts:                             # only on authored: the findings it chains
    - {element: checkout-api, category: stride/denial_of_service}
    - {element: submit-order, category: stride/denial_of_service}
  promoted: 2026-09-13
  attack: >-
    Flood submit-order. It needs no account, and every request costs a
    database write and a synchronous call to Stripe.
  impact: >-
    Database and third-party quota consumed by an unauthenticated caller, and
    checkout unavailable to paying shoppers while it lasts.
  context: >-
    No field in the model records a rate limit anywhere. This may be a control
    nobody was asked about; until it is recorded, the model says there is none.
```

A dismissal is a pairing and a reason; a dismissed open question is the
question's text, verbatim, and a reason. The worked register at
`assets/example.vectors.yaml` decides twenty-one findings and one question, and
is the reference for what a finished one reads like.

## What the check reports, and why each is worth satisfying

- **`UNDECIDED_VERDICT` / `UNDECIDED_QUESTION`** — the terminating condition
  itself. Nothing is finished while one remains.
- **`DECIDED_TWICE`** — a finding both promoted and dismissed, or chained by
  two vectors. Usually a chain authored after one of its parts was already
  promoted; resolve by retiring the single, never by keeping both.
- **`THIN_CHAIN`** — an authored vector chaining one finding, or one whose
  primary pairing is not among what it chains. A chain of one is a promoted
  verdict and should say so.
- **`ORPHAN_VECTOR`** — the enumeration was re-run and this vector's source is
  no longer a finding. It stays, blocking, until the person retires it with a
  reason: it may already carry a mitigation and a code annotation, and an
  exposure that was designed out is a decision worth a sentence. Never delete
  it. The retired entry keeps the id, so the number is never reused.
- **`UNRESOLVED_PAIRING` / `UNRESOLVED_QUESTION`** — a dismissal of something
  the enumeration no longer has. Stale; drop it. Nothing downstream references
  a dismissal, which is the difference from an orphan.
- **`EMPTY_UNEXPLAINED`** — nothing promoted and no `empty_because`. A threat
  model with no vectors is a legitimate outcome only when it says why.
- **`ALL_DISMISSED`** — advisory. Every finding dismissed, the vectors coming
  only from questions or chains that resolve to nothing. Sometimes right;
  always worth a second look.

## Reconciling after the enumeration changes

The model changed, `vector:enumerate` re-ran, and the digest no longer
matches. Run the check: new findings appear as undecided and go through the
loop; vectors whose source disappeared appear as orphans and are shown to the
person with what they used to come from. Update `threats_digest` only once
everything is decided again — it is the statement that the register was
reconciled against *this* enumeration, and it should not be made early.

## What you cannot do

**The script proves every finding was decided; nothing proves the right ones
were promoted.** That is the trade the toolkit makes on purpose — mechanical
everywhere it can be, so that human attention lands here rather than on
walking a grid — and it means a register can be complete and wrong. Say so
when you hand the document back, and let the rendered limits say it again.

Do not score, rank or rate. Promotion says *this is real and we are tracking
it*; what to do about it, and in what order, is the matrix's question, where
the cost of acting is also known.
