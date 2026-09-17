# STRIDE and LINDDUN, mapped onto DFD elements

This is what the finished model is for. Both frameworks work per-element: you
walk each node and edge of the diagram and ask only the threat categories that
can apply to that kind of element. That is why the model insists on typing
everything and placing it in a trust zone — without that, there is nothing to
walk.

## STRIDE

| Category            | Question                                  | Control Family |
| ------------------- | ----------------------------------------- | -------------- |
| **Spoofing**        | Can attacker pretend to be someone else?  | Authentication |
| **Tampering**       | Can attacker modify data in transit/rest? | Integrity      |
| **Repudiation**     | Can attacker deny actions?                | Logging/Audit  |
| **Info Disclosure** | Can attacker access unauthorized data?    | Encryption     |
| **DoS**             | Can attacker disrupt availability?        | Rate limiting  |
| **Elevation**       | Can attacker gain higher privileges?      | Authorization  |

## STRIDE per element

| Element | Spoofing | Tampering | Repudiation | Info disclosure | Denial of service | Elevation of privilege |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| External entity (`actors`) | ✓ | | ✓ | | | |
| Process (`processes`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Data store (`stores`) | | ✓ | ✓ | ✓ | ✓ | |
| Data flow (`flows`) | | ✓ | | ✓ | ✓ | |

Repudiation against a data store applies specifically to stores that are
themselves the audit record — a log store that can be altered destroys the
evidence everything else relies on. This is why the schema asks every process
what it logs and expects the destination to be modelled as a store.

Processes attract all six because they are the only element that makes
decisions. In practice the highest-yield question is the last column: what
would let this process act with more authority than it should have?

Sources: [Practical DevSecOps](https://www.practical-devsecops.com/threat-modeling-data-flow-diagrams/),
[Drata](https://drata.com/grc-central/risk/guide-stride-threat-model).

## LINDDUN

The taxonomy was revised in the 2024 knowledge base update; these are the
current names. The older wording (Linkability, Identifiability, Detectability,
Disclosure of information, Unawareness) still appears widely in tooling and
literature, so recognise both.

| Category | What it means |
|---|---|
| **L**inking | Two data items can be associated with the same person, even without knowing who they are. Session ids, device fingerprints, and IP addresses do this by default. |
| **I**dentifying | The identity of a person can be learned — through a leak, a deduction, or inference from data that was supposed to be pseudonymous. |
| **N**on-repudiation | A person cannot plausibly deny an action. This is the mirror image of STRIDE's repudiation: here the ability to prove what someone did is the harm, not the control. |
| **D**etecting | Involvement can be deduced from observation alone — that a person is a user of the service, or appears in a data set, without seeing any content. |
| **D**ata disclosure | Excessive collection, storage, processing, or sharing of personal data. Minimisation failures live here, not just breaches. |
| **U**nawareness & unintervenability | The person does not know their data is being processed, or cannot access, correct, or delete it. |
| **N**on-compliance | The system deviates from applicable standards, legislation, or the organisation's own stated policy. Organisational rather than technical. |

Sources: [linddun.org threat types](https://linddun.org/threat-types/),
[LINDDUN GO categories](https://linddun.org/linddun-go-categories/).

## LINDDUN per element

LINDDUN applies to the elements that touch personal data, which is why the
`data` dictionary carries `personal_data` and every store and flow references
it. Use the model to select elements before you start enumerating.

| Element | L | I | N | D | D | U | N |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| External entity (data subject) | ✓ | ✓ | | | | ✓ | |
| Process | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Data store | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| Data flow | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |

Unawareness and unintervenability attach to the data subject and to the
processes that are supposed to serve their rights, rather than to the pipes —
which is why the question bank pushes on whether a data subject access or
deletion flow exists at all. An absent flow is the finding.

## Handing the model off

When the DFD is complete, the natural next step is enumeration: walk each
element, apply only its applicable categories from the tables above, and record
what you find against the element id. The model's ids are stable, so findings
can reference them and survive later edits to the diagram.

Two things are worth carrying forward explicitly:

- **`open_questions`** from the model. Each unanswered question is usually a
  finding in waiting — "nobody knows the retention period" is a non-compliance
  threat already.
- **`assumptions`**. Every threat model rests on assumptions, and the ones
  written down are the ones that can be revisited when they turn out to be
  wrong.

Enumeration is deliberately outside this skill. The DFD is the input to it, and
keeping the two separate means the model can feed a manual review, a workshop,
or another tool without being shaped for any one of them.
