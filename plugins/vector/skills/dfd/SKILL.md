---
name: dfd
description: >-
  Interview the user until a data flow diagram of a system, service, or product
  is genuinely complete — captured as a structured YAML model and rendered as a
  Mermaid diagram, scoped for STRIDE security and LINDDUN privacy threat
  modeling. Use this whenever someone wants a DFD, data flow diagram, threat
  model, data map, or trust boundary analysis; when they ask "where does our
  data go", "what are our trust boundaries", "map the flows through X", or want
  to prepare for a security, privacy, or GDPR review; and when they want to
  resume, extend, or re-render an existing .dfd.yaml model. Reach for it even
  when the words "DFD" or "threat model" are never spoken — a request to map or
  document how data moves through a system is this skill's job.
---

# Data flow diagram interview

Build a DFD by interviewing the person who knows the system, and keep going
until it is complete. "Complete" is not a feeling: it is defined by
`scripts/validate_dfd.py`, which reads the model and reports every gap. The
interview ends when that script reports no blocking gaps and the user has seen
the rendered diagram.

The output is two files, in `ctm/` at the root of the project:

- `ctm/<slug>.dfd.yaml` — the model. This is the source of truth.
- `ctm/<slug>.dfd.md` — the rendered Mermaid diagram plus element tables,
  generated from the YAML. Never hand-edit it; regenerate it.

**Everything this toolkit writes goes in that one directory** — the model, the
enumeration, the register and every rendered view, for this and every later
step. Create it if it is not there. A project that already keeps them
elsewhere should keep doing so: nothing resolves by convention, every script
is given the path it is to read, and `check_traceability.py` finds a model
wherever in the tree it sits. The directory is where they go by default, not
where they are required to be.

## Why the model is structured rather than drawn

A picture is the deliverable people ask for, but it is a bad place to keep the
answers. STRIDE needs to know which trust zone each element sits in and what
authenticates each flow; LINDDUN needs to know which data is personal, whose it
is, and how long it is kept. None of that fits on a diagram, and all of it is
what makes the DFD worth building. So capture answers in YAML, and treat the
diagram as a view.

Read `references/model-schema.md` before writing any YAML. It is the field-by-
field contract the validator enforces. `assets/example.dfd.yaml` is a complete
worked model of a small checkout system — read it when you want to see the
finished shape, particularly how the parts people skip (support tooling, audit
logs, the data subject access path) get represented.

## The loop

**1. Look for an existing model before asking anything.**

Glob the working directory for `*.dfd.yaml` first. Do not assume there isn't
one — these interviews span sessions, and opening a fresh interrogation on top
of a model someone already filled in throws away their earlier work and their
patience with it. If you find one, skip the scoping batch entirely and go to
"Resuming an existing model" at the end of this file.

**2. Scope it, in one batch.**

Open with a small batch of questions — four or five — that sketch the system.
Batching here is deliberate: at the start the user has the whole system in
their head and answering in bulk is fast, whereas one-at-a-time feels like an
interrogation. Ask for:

- What the system is, in a sentence, and what it does for whom.
- Who uses it and who else it talks to (other systems, vendors, partners).
- What is in scope and, importantly, what is not.
- Whether this is for a security review, a privacy review, or both — it changes
  which gaps are worth pushing on.
- Whether personal data is involved at all. If the answer is no, say plainly
  that the LINDDUN half will be thin, and confirm they still want it.

If `$ARGUMENTS` names a system, use it as the subject and skip asking what the
system is.

**3. Write a first model immediately, as a level 0.**

Do not interview to completion before writing anything. Write the YAML from the
opening batch — sparse, with `null` wherever you do not yet know — and run the
validator. A visible skeleton changes the conversation: the user starts
correcting a concrete artifact instead of answering questions in the abstract,
which surfaces the things they would never have thought to mention.

Write that first model at the boundary: the external actors, a handful of
processes standing for the system's large parts, and the flows that cross
between them. Three or four inside processes, not thirty — this is the picture
somebody would draw on a whiteboard to explain what the system is, and it is
what makes the first render worth showing. A model built the other way round,
by writing down every component as it comes up in conversation, ends as a flat
list with no shape, and there is no later step that recovers one.

Prefer explicit `null` over an omitted field. Omission is ambiguous — it can
mean "not asked yet" or "not applicable" — and the validator cannot tell the
difference. `null` means "still to ask"; `"n/a"` with a reason means asked and
answered.

**Write every prose value as a block scalar.** A field whose value is a
sentence gets `>-`, with the text indented beneath it:

```yaml
    notes: >-
      Gift recipients never interact with us, which makes transparency harder.
```

Not for tidiness. A plain value containing a colon followed by a space reads
as a nested mapping and the file stops parsing, and a sentence like *the chain
ends here: somebody decides* is the ordinary way to write English rather than a
rare accident — two of the four models this toolkit has been pointed at hit it
while being written. A value beginning with `-`, `[`, `{`, `*`, `?`, `|`, `>`,
`%`, `@`, a backtick or a quote fails the same way.

**Two of them do not fail. They quietly change what the field says.** A value
beginning with `&` is read as an anchor and the first word disappears — `&c is
a language` becomes `is a language`. A ` #` anywhere in a plain value starts a
comment, so `a note # and a caveat` becomes `a note`. Nothing reports either;
the model validates clean and the sentence a reader needs is not in it.

When a file does fail, it fails before any of this is checkable. The validator
never gets a model, so it reports no gaps — it exits 2 as a usage error and
names a line and a column rather than the colon. Writing every sentence as `>-`
costs one line and removes all of it.

**4. Then work element by element.**

Once the skeleton exists, run the validator and let its output drive the
interview. It reports gaps grouped by element, and that grouping is the right
unit to ask in: take one element's gaps per turn.

Element-sized batches work because the questions about a single data store —
what encrypts it, who can read it directly, how long it keeps things, where the
backups go — are one coherent thought for the person answering. They already
have that store in their head. Questions that hop between a store, a flow, and
an actor force a context switch on every line and get shallower answers for it.

Resist widening the batch to go faster. A first skeleton of a real system
routinely carries fifty to a hundred blocking gaps, and firing them off at once
produces a wall of questions that gets skimmed and half-answered — you will
spend more turns chasing the halves than you saved.

Follow-ups stay one at a time. When an answer is ambiguous, contradicts
something already in the model, or quietly reveals an element nobody has
mentioned, stop and ask about that alone before moving on to the next element.

After each round, update the YAML and re-run the validator. That rhythm keeps
the model and the conversation in sync, and means you always know how much is
left rather than guessing.

Report progress in the user's terms, not the validator's: "six flows mapped,
three still missing what actually travels over them" beats a dump of gap codes.

**5. Refine each part until its fields hold one answer.**

A level 0 process stands for several things. Take each one and ask whether
every single-valued field on it — `authn`, `authz`, `trust_zone`, `owner` — can
be filled with one true sentence. The tell is a hedge: a process you can only
give `authn: varies by entry point` is not one process, and no amount of
careful wording makes it one.

Where it is several, make it a subsystem:

- add a `subsystems` entry with that id, name and a one-line description;
- add its parts as processes and stores, each with `parent:` naming it;
- re-point its flows at whichever part actually carries them;
- move each field down to whichever part it is true of.

That last step is the interview, not bookkeeping. *The storefront's `authn` was
a session cookie — which of its three parts actually does that?* is the
question worth asking, and the rewrite is only how the answer gets recorded.

**Stop when the fields resolve, not at a number of elements.** A process whose
one `authn` is true of it is finished however small the system is; a
single-process tool has no subsystems and needs none. There are two levels and
no third: a part with parts of its own is a system that has outgrown one
diagram, and the honest answer there is a second model rather than a deeper
one.

An element that belongs to no part — a database both halves read and write —
keeps no `parent` at all. The rendered document gives those their own section
rather than making you choose.

**6. Chase the things people leave out.**

The validator catches structural holes. It cannot catch what the user never
mentioned, and there are recurring blind spots worth probing directly. Read
`references/question-bank.md` for the full set; the ones that pay off most
often are the back doors — admin consoles, support tooling, break-glass access,
the analytics pipeline, backups, logs, and the CI/CD system that deploys the
whole thing. People describe the happy path and forget that the ops team can
read the database.

Ask about these even when the user seems finished. Framing them as "most
systems have X — does yours?" makes it easy to say no, which is a real answer,
and easy to say "oh, right" when it isn't.

**7. Render, show, and let them correct it.**

Generate the document and put it in front of the user well before you think the
model is done. Where the model declares subsystems it opens with an overview
and then takes one part at a time, so it is worth showing from the level 0
onwards rather than only once the detail is in. People find errors in a picture that they read straight past in
a list of questions — a flow pointing the wrong way is obvious visually and
invisible in prose. Render at least once mid-interview, not only at the end.

**8. Finish deliberately.**

When the validator reports no blocking gaps, do not just stop. Advisory gaps
are judgment calls, not noise: walk through them and let the user dismiss each
one on the record, then write the dismissal into `assumptions` so the next
reader knows it was considered rather than missed.

Close by stating what the model does not cover. A DFD's honest limits are part
of the deliverable — the person who reads it in six months needs to know where
it stops.

## Running the scripts

Both scripts read the YAML model and need only Python 3 and PyYAML.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/validate_dfd.py ctm/<slug>.dfd.yaml
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/render_dfd.py ctm/<slug>.dfd.yaml -o ctm/<slug>.dfd.md
```

`validate_dfd.py` exits 0 when there are no blocking gaps and 1 when there are,
and prints them grouped as BLOCKING or ADVISORY with the element each belongs
to. **Exit 2 is a usage error** — no such file, unreadable YAML, not a mapping
— and never means the model is incomplete, so a mistyped name stops the loop
instead of looking like more work to do.
Pass `--json` if you want to reason over the output programmatically rather
than reading it. If PyYAML is missing and `uv` is available, substitute
`uv run --script` for `python3` — each script carries inline dependency metadata
and a lockfile beside it, so that installs the pinned PyYAML and needs no setup.
Otherwise install PyYAML, or parse the model yourself — do not abandon the
structured model and start freehanding a diagram.

`render_dfd.py` writes the Markdown view. Pass `--mermaid-only` to get just the
diagram block, which is useful when the user wants to paste it elsewhere.

## What the validator checks, and why it is worth satisfying

Beyond obvious things like unresolved references, four checks catch real
modeling errors rather than clerical ones, and they are worth understanding so
you can explain a gap rather than just relay it:

- **Black holes and miracles.** A process with inputs and no outputs is either
  incompletely modeled or is actually a data store. A process with outputs and
  no inputs is inventing data from nowhere — usually there is an unmentioned
  source, often a config store or a third-party feed. Both are classic signs
  the interview stopped early.
- **Unauthenticated boundary crossings.** Every flow that leaves one trust zone
  for another is where STRIDE lives. A crossing with `authn: null` is not a
  finding on its own, but it is always a question worth asking out loud.
- **A process that is a language model, unanswered.** `kind` is required on
  every process, and `llm` or `agent` pulls in three further questions — what
  untrusted content reaches the prompt, where the system prompt lives, what
  consumes the output — with a fourth for an agent, about what it may do
  without a human approving. Ask them; they are not paperwork. A model is the
  only process whose behaviour is not fully determined by its code.
- **Personal data without a retention answer.** LINDDUN's data-minimisation and
  non-compliance threats hinge on this, and "how long do you keep it" is the
  single question teams most reliably cannot answer. Surfacing that is useful
  even when the answer is "we don't know" — record that as the answer.

Read `references/threat-mapping.md` when the user wants to know which threat
categories apply to which elements, or asks what to do with the finished DFD.
It maps STRIDE and LINDDUN onto DFD element types and describes handing the
model off to a threat enumeration.

`references/STRIDE.md` and `references/LINDDUN.md` are the catalogues behind
those categories — named attack patterns anchored to CAPEC, and the LINDDUN
threat tree down to its leaves. Read one when a category needs to become
something concrete. Neither says what applies where; that stays
`threat-mapping.md`'s job alone, so the two can never disagree about it.

## Resuming an existing model

Read it, run the validator, and open by saying where it stands — what is
already answered, what is left, and which element you are picking up next.
Resuming should feel like continuing a conversation, not restarting one, and
the person may not be whoever answered last time.

From there rejoin the loop at step 4 and work element by element as usual. Do
not re-ask what the model already answers; if an existing answer looks wrong or
stale, quote it back and ask about that one thing rather than reopening the
section.

When the user describes a change to the system rather than a gap, edit the
model surgically. Rebuilding from scratch discards answers someone worked to
produce, and those answers are the expensive part.
