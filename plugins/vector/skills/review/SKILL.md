---
name: review
description: >-
  Read the design documents that have landed in a repository against a data
  flow diagram, decide what each one means for the model, and record it — a
  path, a digest, a date, an impact and a reason. Use when a .dfd.yaml exists
  and an architecture decision, specification or use case has been written
  since, for "is the threat model still current", "we just merged an ADR",
  "review the model", "the build says a document is unreviewed" — or when
  adopting the currency check for the first time. The output is the same
  ctm/<slug>.dfd.yaml, with system.design_sources and system.reviewed filled in,
  and its regenerated ctm/<slug>.dfd.md.
---

# The review: keeping the model current with the design

A threat model is accurate on the day it is written and decays from then on.
The decay does not begin when code ships — it begins when the design changes,
and by the time the code exists the model has been wrong for weeks and nobody
was told. This skill is the moment somebody is told.

It reads the project's own design documents, and for each one asks a question
only a person can answer: **does this change the modelled system?** A new
component, a moved trust boundary, a new data item, a removed flow — or
nothing at all, which is the common answer and still needs a sentence.

It is a skill rather than an agent for the reason `/vector:promote` is: the
judgement is the point. Enumeration was made mechanical so that this could be
deliberate.

"Done" is a script's decision. `scripts/check_reviews.py` reads the model and
the repository and reports every document nobody has accounted for. You are
finished when it exits 0 — never because the documents felt unimportant.

## The one rule

**Never record a review of a document you have not read.** Every other rule
here is enforced by a script; this one cannot be, and it is the one the whole
capability rests on. A `reviewed` entry is a person's claim that somebody
looked. Writing one from a filename, a commit message or a title makes the
model's own record of its currency a lie, and a lie in exactly the place
somebody would go to check.

## Before anything else

**Validate the model.** A model with blocking gaps is not one to reconcile
against anything.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/validate_dfd.py ctm/<slug>.dfd.yaml
```

**Find out whether this project has opted in.** If the model has no
`system.design_sources`, the capability is off and this is an adoption, which
runs differently — see below. If it has them, run the check and work the list.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/check_reviews.py ctm/<slug>.dfd.yaml --json
```

## Adopting, on a model that has never been reviewed

1. **Ask where this project writes its design down.** Not where its
   documentation lives — where *decisions* live. Architecture decisions,
   specifications, use cases, RFCs. Whatever the layout is, it is the
   project's, and any of `docs/architecture/`, `rfcs/`, `DECISIONS.md` or
   `docs/**/*.md` is a legitimate answer. `$ARGUMENTS` may already name them.

2. **Warn about what the glob sweeps in.** Every tracked file under a source
   becomes something somebody must answer for, meeting notes and drafts
   included. Narrowing it is the project's to do, not yours to guess.

3. **Work through the documents before declaring anything**, by the loop
   below. A document whose status says superseded, deprecated, withdrawn or
   obsolete needs no reading — it has retired itself, and the check skips it.

4. **Write `design_sources` last**, once the list is clean. Declaring it first
   turns the project's build red before anybody has had a chance to do the
   work, which is how this check gets disabled in a fortnight.

5. **Offer `review_cycle`, as a question about obligations rather than a
   suggestion.** *Does anything require this model to be re-read on a
   schedule — an audit, a certification, a customer commitment?* If the answer
   is no, say plainly that the project does not want one: where a document has
   not changed, re-reading it produces the same sentence, and the repair is
   re-stamping a date. The pulse — how old the oldest reading is — is reported
   without it.

## The loop

1. **Read the document. All of it.** See the one rule.

2. **Say what it means for the model, in terms of the model.** Not a summary
   of the document — an answer about elements, flows, trust zones and data:

   - a component that is not in the diagram, or one that has gone;
   - a flow that is new, removed, or now crossing a different boundary;
   - a data item, or a change to how one is classified;
   - a trust zone whose controller or assumptions have moved;
   - an assumption in `system.assumptions` the document contradicts.

   Where you are unsure, say which way you are unsure and let the person
   decide. An impact recorded on your guess is worth less than a question.

3. **Edit the model surgically where it is warranted.** The smallest change
   that makes the model true again — not a rewrite, and not an opportunity to
   tidy. Then validate it, because a currency review that leaves new blocking
   gaps has traded one kind of wrong for another.

4. **Record the review**, with the digest of the file you just read:

   ```sh
   python3 -c "import hashlib,sys;print('sha256:'+hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <path>
   ```

   ```yaml
   system:
     reviewed:
       - path: docs/architecture/ADR-0014.md
         digest: sha256:4f21c9…
         reviewed: 2026-09-15
         impact: none
         reason: >-
           Changes how the export job is scheduled, not what it reads or where
           it sends it. No element, flow or data item moves.
   ```

   `impact` is `none` or `modelled`, and **both need a reason** — a sentence a
   later reader could disagree with. "No impact" on its own says only that
   somebody clicked past, and a reviewer who writes that on every document has
   a model that reports clean and is stale.

5. **For a changed document, say it is a re-read.** The check separates
   *unreviewed* from *changed* because they ask for different things: the
   first is a first reading, the second is reading a diff. Show what moved
   where you can, then either revise the model or record the new digest — the
   one-line diff that says *I read the change*.

## When the model changes

**Recording a reading changes nothing downstream.** `system.reviewed`,
`system.design_sources` and `system.review_cycle` are left out of the model's
digest, so a review whose every entry is `impact: none` leaves the enumeration,
the register and the matrix exactly as current as they were. Recording a
review is never the thing that turns a build red.

A review that is `modelled` is different, because it edited what the model
describes. Say what went stale, and to whom. That edit breaks `model_digest`,
which makes the enumeration stale, which makes the register stale, which makes
the matrix stale. Nothing here repairs that, and nothing should: each step has
its own judgement in it.

```
/vector:enumerate → the enumeration     (a new element has threats nobody has judged)
/vector:promote   → the register        (new findings, or old ones that have moved)
/vector:matrix    → the dispositions    (new vectors nobody has decided about)
```

Name them in that order and stop. Running them unasked would bury a person's
design decision under three artefacts they did not ask you to regenerate.

## Finishing

Regenerate the rendered view, so the model's age is legible to somebody who
reads Markdown rather than YAML:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/render_dfd.py ctm/<slug>.dfd.yaml -o ctm/<slug>.dfd.md
```

Then run the check once more and report what it says, advisories included,
ending with the pulse — how many documents, how many readings, and how old the
oldest is.

And say the limit out loud, because a clean run is the moment it is most
likely to be forgotten: **this is a claim about documents, never about the
system.** A team that changes its architecture in a meeting and writes nothing
down gets a model that reports clean and is wrong, and that is the one failure
this capability cannot see.
