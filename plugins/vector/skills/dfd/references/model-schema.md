# DFD model schema

The model is a single YAML file, `<slug>.dfd.yaml`. Every field the validator
knows about is listed here. Use explicit `null` for "not asked yet" and the
string `"n/a"` (with a reason in the adjacent `notes` field where one exists)
for "asked, does not apply".

Identifiers are short kebab-case strings, unique across the whole file — not
just within their section — because flows reference actors, processes, and
stores interchangeably.

## Contents

- [`system`](#system) — scope and intent
- [`trust_zones`](#trust_zones) — the boundaries everything else is placed in
- [`actors`](#actors) — external entities
- [`processes`](#processes) — things that transform data
- [`stores`](#stores) — things that hold data at rest
- [`data`](#data) — the data dictionary, referenced by stores and flows
- [`flows`](#flows) — the edges

## system

```yaml
system:
  name: Acme Checkout
  slug: acme-checkout
  description: One or two sentences on what it does and for whom.
  analysis: [stride, linddun]     # one or both; drives which gaps are blocking
  scope:
    in_scope:
      - The checkout web app and its payment orchestration service
    out_of_scope:
      - The warehouse system; treated as an external entity
  assumptions:
    - Card data never touches our servers; Stripe Elements tokenises in-browser.
  open_questions:
    - Nobody could confirm the retention period on the analytics warehouse.
```

`analysis` matters: with `linddun` present, personal-data and retention fields
become blocking rather than advisory. With only `stride`, they stay advisory so
a pure security model is not blocked on privacy questions.

`open_questions` is for things the user genuinely does not know. Recording them
is better than leaving a field `null`, because it distinguishes "we asked and
they could not answer" from "we never got there".

### accepted_gaps

```yaml
system:
  accepted_gaps:
    - NO_RIGHTS_FLOW:flows
    - MISSING_FIELD:stores/session-cache:backups
```

The validator reports gaps by a stable key, printed as `key:` under each one.
Listing a key here retires that gap. Use it only for gaps the user has actually
considered and dismissed, and write the reasoning into `assumptions` alongside
— the point is to distinguish a decision from an oversight, which is exactly
what someone reading the model in six months needs to know.

## trust_zones

A trust zone is a region under one party's control where you would not need a
new authentication decision to move between elements. Zones are what make a DFD
a threat model rather than an architecture drawing.

```yaml
trust_zones:
  - id: browser
    name: User's browser
    description: Untrusted; the user controls it entirely.
    controlled_by: end_user       # us | end_user | cloud_provider | third_party | unknown
  - id: prod-vpc
    name: Production VPC
    description: Our AWS account, private subnets.
    controlled_by: us
```

Model the user's own device as its own zone. It is the most common omission and
the source of a large fraction of real findings.

## actors

External entities: anything that talks to the system but is not part of it.

```yaml
actors:
  - id: shopper
    name: Shopper
    type: human                   # human | external_system | third_party_service | ai_agent
    description: Buys things.
    trust_zone: browser
    authenticates_how: Email + password, optional TOTP.   # null if anonymous
    is_data_subject: true         # LINDDUN: is this a person whose data you hold?
```

`is_data_subject` is not the same as `type: human`. A support agent is a human
who is not the subject of the data they handle; a shopper is both.

`ai_agent` is for an agent that calls the system from outside it. An agent you
run is a process with `kind: agent` instead — see below. The trust zone decides
which, as it does for everything else, and the distinction is real because an
actor attracts only spoofing and repudiation where a process attracts all six.

## processes

Anything that acts on data: a service, a job, a lambda, a manual step a person
performs. Manual steps count — an ops engineer running a query is a process.

```yaml
processes:
  - id: checkout-api
    name: Checkout API
    description: Validates carts, creates orders, calls the payment provider.
    trust_zone: prod-vpc
    owner: Payments team          # who is accountable, not who wrote it
    kind: service                 # service | job | lambda | manual | llm | agent
    tech: Go service on ECS
    authn: mTLS from the edge proxy; JWT for user context.
    authz: Row-level checks on order ownership.
    logging: Structured audit log to CloudWatch, 90 days.
```

### `kind: llm` and `kind: agent`

A process running a language model attracts exactly the threat categories any
other process does, so it is a kind rather than an element type of its own. What
it has that others do not is three more answers, and an agent a fourth:

```yaml
  - id: support-triage
    name: Support triage assistant
    description: Summarises an inbound ticket and drafts a suggested reply.
    trust_zone: prod-vpc
    owner: Support engineering
    kind: llm
    tech: Claude via the Anthropic API
    authn: Service API key from the secret manager.
    authz: Read-only on tickets; no write path.
    logging: Prompt and completion ids to the audit log; bodies not retained.
    untrusted_input: >-
      The ticket body, written by whoever opened it, goes into the prompt.
    system_prompt: >-
      In source, changed only through review; no runtime override.
    output_handling: >-
      Rendered as plain text into the agent console. Never executed, never
      passed to a tool, never written back to the ticket without a human.
```

| Field | Required on | What it is for |
|---|---|---|
| `untrusted_input` | `llm`, `agent` | Whether content from outside the trust boundary reaches the prompt. "Nothing does" is an answer — say what stops it. |
| `system_prompt` | `llm`, `agent` | Where the instructions live and who can change them. A prompt a deploy can edit is not a prompt in review. |
| `output_handling` | `llm`, `agent` | What consumes the output, and whether it is treated as data or as instruction. |
| `authority` | `agent` | What it may do without a human approving. "Nothing without approval" is complete. |

**Tools an agent can call are flows, not a field.** Model each one as an edge
from the agent to what it calls, so the diagram shows the authority and the
enumeration walks it. A list on the node would be neither.

None of these introduce new threat categories. Prompt injection is tampering —
untrusted input reaching a control path — and excessive agency is elevation of
privilege; `references/STRIDE.md` carries them as attack patterns under those
categories, which is where they belong.

`logging` carries weight in both frameworks: it is STRIDE's repudiation control
and simultaneously a LINDDUN non-repudiation and detecting threat, because logs
are themselves a store of personal data. If a process logs, say so, and model
the log destination as a store.

## stores

```yaml
stores:
  - id: orders-db
    name: Orders database
    description: Postgres; orders, line items, addresses.
    trust_zone: prod-vpc
    kind: database                # database | object_store | queue | cache | file | log | third_party | paper
    data: [order, address, email]
    encryption_at_rest: AES-256, AWS-managed KMS key.
    access_control: Service role only; break-glass via PAM, audited.
    retention: Orders 7 years (tax); addresses purged 90 days after delivery.
    backups: Nightly snapshots, 35 days, same account.
```

`backups` is separate from `retention` on purpose. A 90-day purge policy means
nothing if snapshots hold the data for a year, and teams routinely miss this.

## data

The data dictionary. Stores and flows reference these ids, so each item is
described once.

```yaml
data:
  - id: email
    name: Email address
    classification: confidential  # public | internal | confidential | restricted
    personal_data: personal       # none | pseudonymous | personal | special_category
    subjects: Shoppers
    examples: alice@example.com
    lawful_basis: Contract        # privacy models only; null otherwise
    retention: Life of account + 30 days
    notes: Also used as the login identifier, so it cannot be pseudonymised.
```

`special_category` means GDPR Article 9 data — health, biometrics, sexuality,
religion, politics, union membership, race — plus anything your jurisdiction
treats as equivalent. It changes the analysis enough to be worth flagging
explicitly rather than folding into `personal`.

`pseudonymous` is for data that identifies a person only in combination with a
key held elsewhere. It is not anonymous, and LINDDUN's linking threats apply to
it in full.

## flows

The edges. Direction matters — model a request and its response as two flows
when they carry meaningfully different data, and as one when they do not.

```yaml
flows:
  - id: submit-order
    name: Submit order
    from: shopper                 # any actor, process, or store id
    to: checkout-api
    data: [cart, address, email]
    protocol: HTTPS/1.1 POST
    encryption_in_transit: TLS 1.3
    authn: Session cookie, SameSite=Lax
    trigger: user_action          # user_action | scheduled | event | manual
    notes: null
```

The validator computes boundary crossings from the `trust_zone` of the two
endpoints, so you do not assert them. A flow whose endpoints are in different
zones and whose `authn` is `null` is reported, because that is precisely where
spoofing and tampering threats live.
