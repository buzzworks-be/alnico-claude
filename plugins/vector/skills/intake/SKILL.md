---
name: intake
description: >-
  Put every scanner finding to the threat model — where was this in the matrix,
  and did we evaluate it incorrectly, or should we adapt? — and record the
  answer in the register. Use when a SARIF file exists beside a dispositioned
  .vectors.yaml, for "triage these findings", "what does the threat model say
  about this CVE", "we have a scan and a threat model and nobody has compared
  them", "the build produced a SARIF file" — or when a finding lands on
  something the matrix already called mitigated. The output is the same
  ctm/<slug>.vectors.yaml, with an `answers` section, and its rendered
  ctm/<slug>.matrix.md.
---

# The intake: findings put to the threat model

Everything else in this toolkit is attestation. The model is what somebody said
the system is, the enumeration is what somebody judged about it, the register is
what somebody decided — all written by the same people, and none of it able to
be contradicted from outside.

**A scanner can.** It observes the system as built and knows nothing about what
anybody claimed, so a finding where a vector says `mitigated` is evidence the
attestation is false, and a finding with no home in the model at all is evidence
the model is incomplete — which the enumeration can never see, because it works
from the system as described rather than as built.

So there is exactly one question here, asked of every finding:

> Where was this in the threat matrix, and did we evaluate it incorrectly, or
> should we adapt?

"Done" is a script's decision. `scripts/check_answers.py` reads the scan and the
register and reports every finding nobody has answered. You are finished when it
exits 0 — never because the remaining findings looked unimportant.

## The asymmetry, which must survive this whole session

**A finding can lower confidence in a claim and can never raise it.** A scan
that reports nothing means the scanner found nothing it knows how to look for,
and nothing more. Say that in those words whenever a scan comes back quiet. The
moment a clean scan reads as confirmation, this capability has manufactured
exactly the false comfort the rest of the toolkit is written to remove.

## Before anything else

**Refuse an undispositioned register.** A finding argued against a matrix that
is still moving is argued against the wrong thing.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_matrix.py ctm/<slug>.vectors.yaml
```

If that does not exit 0, say so and stop. Finishing it is `/vector:matrix`'s job.

**Then read the scan.** `$ARGUMENTS` may name it; otherwise ask where the build
puts it. SARIF 2.1.0 is the only format read, and it is read from a file — never
fetched from a vendor's API, because the repository is the source of truth.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_answers.py <scan>.sarif ctm/<slug>.vectors.yaml --json
```

## The loop

1. **Group before asking.** Twenty findings of one rule in one directory are one
   question, and asking twenty times is how an intake gets abandoned. The check
   groups unanswered findings by rule for exactly this; propose the group and
   the scope that covers it.

2. **Put the model in front of the person, not just the finding.** This is the
   whole value of the capability, and skipping it turns the session into a
   worse version of the scanner's own dashboard. For each group, say what the
   model knows about where it landed:

   - which element the location belongs to, if that is knowable — say *if*,
     because the model does not record where code lives and guessing is worse
     than asking;
   - which trust zone that element sits in, and who controls it;
   - what data flows through it, and how it is classified;
   - what the register already says: vectors on that element, their
     dispositions, the mitigations behind them.

3. **Ask the one question, and let the answer pick the record.** Three answers
   exist, and they are not a severity scale:

   - **`vector`** — it is this threat, named by id. Use it whether the vector
     already existed or you have just promoted one for it, and whether the
     disposition survives the finding or has to change. What happens to that
     vector is the matrix's business; the answer records that the question was
     answered and where it went.
   - **`not_a_threat`** — dismissed, with a reason, and the reason is usually
     the model: a vulnerability in a component no flow reaches, outside every
     boundary that matters, is not the same risk as the same vulnerability on
     the front door.
   - **`model_gap`** — the finding is in a part of the system the diagram does
     not contain. The most serious of the three; see below.

4. **Never propose the link as settled.** An agent proposes, a person confirms.
   Inferring which vector a finding belongs to would produce false
   contradictions, and an intake people learn to click through is worse than no
   intake at all.

5. **Say what a scope costs, at the moment it is drawn.** A `where` covers
   everything under it, now and later, so a wide one dismisses findings nobody
   has seen yet. That is the single silent failure in this design — every other
   way it fails asks the question again — and the person choosing the scope is
   the only one who can bound it. Offer the narrowest scope that covers the
   group, and name what a wider one would swallow.

6. **Record the answer** in the register's `answers` section:

   ```yaml
   answers:
     - id: ANS-0001
       scanner: codeql
       rule: js/missing-rate-limiting
       where: src/checkout-api/
       answer: vector
       vector: VEC-0003
       contradiction: false_positive
       reason: >-
         The throttle runs at the edge proxy in front of the API, outside the
         tree this scan covers. The scanner is right that the handler has no
         limit and wrong that nothing limits it.
       seen_as:
         partialFingerprints: {primaryLocationLineHash: "1f3c9a0d4e2b:1"}
       answered: 2026-09-20
   ```

   Ids are `ANS-NNNN` and never reused. `seen_as` is whatever identity the
   finding carried — copy it so a later reader can find the original, and know
   that nothing matches on it. A dismissal and a model gap record
   `model_digest`, because the argument was made against a model and lapses when
   that model moves.

## When a finding lands on something called `mitigated`

**The case this capability is worth the most for**, and the only place in the
toolkit where evidence argues with an attestation. Two things are true and the
answer has to say which:

- **`contradiction: disposition_revised`** — the control does not do what it
  claimed. Change the disposition, with the finding cited as the reason and the
  previous state kept in `history`, then say so here.
- **`contradiction: false_positive`** — the finding is wrong, and *why* it is
  wrong is the part worth writing. "The control lives somewhere the scan cannot
  see" is a reason. "We looked at it" is not.

The check will not let this close without one of those two words. That is
deliberate: a contradiction closed by silence is the failure mode this exists
to prevent, and neither answer is the safe one.

## When a finding has no home in the model

`model_gap` is the most serious answer and the easiest to record and forget. It
says a scanner found something in a part of the running system the diagram does
not describe — so nothing was ever enumerated against it, and no amount of work
in this register fixes that.

Say it plainly, name what is missing, and point at `/vector:dfd`. Then stop
treating it as a triage item: it is a defect in the model, and the register is
only holding the note.

## Finishing

Regenerate the rendered view, so the answers are legible beside the dispositions
they argue with:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/render_matrix.py ctm/<slug>.vectors.yaml -o ctm/<slug>.matrix.md
```

Then re-run the check and report what it says, advisories included — the
suppressed findings among them, because a suppression in the scanner says *do
not show me this* and never says what the threat model decided.

And end where this started: **what a clean run does not mean.** Every finding
has an answer; none of that is evidence that any control works.
