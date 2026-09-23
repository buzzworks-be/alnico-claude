# Threat model — Acme Checkout

Generated from `example.threats.yaml` and the register beside it by `render_vectors.py`. Do not edit; regenerate.

## Tracked vectors

14 vector(s), grouped by the element each is anchored to. A chain lists the findings it ties together.

### Processes

#### `dsar-handler` — Data request handler

##### VEC-0001 — A guest's identity is never verified, at checkout or on a data request

STRIDE spoofing · promoted 2026-09-13

> `AA01` Authentication Abuse/ByPass · `U.2.2` Access · `U.2.3` Rectification/erasure

Chains: `shopper` STRIDE spoofing, `dsar-handler` STRIDE spoofing, `dsar-handler` LINDDUN unawareness

**Attack.** Submit an order, or a data access request, naming somebody else's email address. `shopper.authenticates_how` records guest checkout as anonymous, and `dsar-request.authn` falls back to "documentary proof for guests" that a privacy team member judges with no account to compare it against.

**Impact.** At checkout, an order and its confirmation directed at a stranger. On a data request, a complete export delivered to a stranger — a reportable breach. The same missing control causes both, and the third finding in this chain is the same dial turned the other way: tighten verification to stop the stranger and a genuine guest with no documents is locked out of their own data.

**Context.** Account holders prove control of the login and are not affected. The model records that guest verification is "harder" and stops there — who judges the documents, against what, and what happens on refusal are all unrecorded, so this is a decision that has not been made rather than one that was made badly.

##### VEC-0002 — Gift recipients are data subjects the system cannot inform or serve

LINDDUN non compliance · promoted 2026-09-13

> `U.1.1` Unawareness as data subject · `U.2.3` Rectification/erasure · `NC.1.1.1` Insufficient data subject controls

Chains: `shopper` LINDDUN unawareness, `dsar-handler` LINDDUN non compliance

**Attack.** None needed. `address.subjects` is "Shoppers and their gift recipients", and `address.notes` records that recipients never interact with us. Every route into the rights process starts from a shopper with an account or a documented identity; a recipient has neither and no order to name.

**Impact.** A class of data subject with no way to learn their address is held, and no way to have it removed. That is an unawareness harm and a rights failure at once, and it is structural — no flow in the model could carry a recipient's request even if one arrived.

**Context.** Retention bounds it: `address.retention` is 90 days after delivery, so the exposure is short-lived per address. The model has no notion of a subject who is not a shopper, which is why the enumeration found this as an absence rather than a weak control.

#### `checkout-api` — Checkout API

##### VEC-0003 — The order path has no throttle anywhere in the model

STRIDE denial of service · promoted 2026-09-13

> `DO01` Flooding

Chains: `checkout-api` STRIDE denial of service, `submit-order` STRIDE denial of service

**Attack.** Flood `submit-order`. It is `trigger: user_action` from the browser zone, a guest needs no account to reach it, and every request behind it costs a `persist-order` write and a synchronous `charge` call to Stripe.

**Impact.** Database and third-party API quota consumed by an unauthenticated caller, and the checkout unavailable to paying shoppers while it lasts. The Stripe cost is the part a rate limit on our side has to absorb before the request leaves.

**Context.** No field in the model records a rate limit, a quota, a queue or a circuit breaker on any element. The interview asked `authn` and `authz` of this process and nothing about availability, so this may be an unrecorded control rather than a missing one — but until it is recorded the model says there is none.

#### `support-console` — Support console

##### VEC-0007 — Address masking in the support console is lifted by the agent who wants it

LINDDUN data disclosure · promoted 2026-09-13

> `DD.4.1.1` Predetermined set of parties · `DD.1.2` Data type granularity

**Attack.** An agent opens a ticket-linked view. `support-console.authz` records that addresses are masked "unless the agent opens a ticket-linked view", and nothing in the model says who checks that the ticket is real, relevant, or the shopper's own.

**Impact.** Any agent can read any shopper's delivery address at will. The masking is a speed bump on a path the agent controls both ends of.

**Context.** `support-console.logging` records every lookup with the agent identity and a reason, so this is detective rather than absent — an agent doing it habitually would be visible afterwards. Compare `dsar-handler`, which has a two-person rule for a comparable read.

#### `checkout-web` — Checkout web app

##### VEC-0010 — Nothing in the model tells a shopper what is collected or on what basis

LINDDUN unawareness · promoted 2026-09-13

> `U.1.1` Unawareness as data subject

**Attack.** None needed. `checkout-web` is the only process the shopper sees, and the model contains no privacy notice, no consent interaction, and no flow or store that would carry one. `lawful_basis` is recorded per data item for the reviewer and shown to nobody.

**Impact.** Collection under a contract basis is likely lawful; collection nobody was told about is still an unawareness harm and a transparency failure. The information exists for the auditor and not for the data subject, which is exactly the wrong way round.

**Context.** A notice almost certainly exists on the real site and was simply not modelled — a notice is not a flow. That is itself worth knowing: the model has no way to represent the thing this vector is about.

##### VEC-0011 — PII scrubbing on client error reports is a filter that fails open

STRIDE information disclosure · promoted 2026-09-13

> `DS06` Data Leak

**Attack.** Trigger a client error while the page holds `address` and `email` — which is when errors are likeliest. `checkout-web.logging` sends client errors to Sentry "with PII scrubbing on", and scrubbing is pattern matching that a new field, a nested object or a captured local variable defeats silently.

**Impact.** Shopper addresses and email addresses in a third-party error tracker, under that tracker's retention and access, with no record that anyone would notice.

**Context.** Nothing in the model says the scrubber is tested, and a scrubber nobody tests is a claim rather than a control. The fix is small — a test that fails when a known PII shape reaches Sentry — which is why this is tracked rather than dismissed as theoretical.

#### `support-assistant` — Support assistant

##### VEC-0012 — A shopper's own words reach the prompt of a process that can move money

STRIDE elevation of privilege · promoted 2026-09-13

> `LLM02` Indirect Prompt Injection via Retrieved Content · `LLM05` Excessive Agency via Unauthorized Tool Use

**Attack.** Place an order with a delivery note written as an instruction, then open a support ticket about it. `support-assistant.untrusted_input` records that both the note and the message go into the prompt verbatim, and `authority` gives the process a tool that refunds the order in the open ticket up to EUR 50.

**Impact.** A refund the shopper was not owed, issued by a process whose decision no person reviewed. The cap bounds one loss and not how many: placing orders is something the attacker already does, and each carries its own note.

**Context.** Everything else about this process is tight — `system_prompt` is shipped with the service and never assembled from shopper input, `authority` scopes the tool to one order, and `logging` records every call. What is missing is not a boundary around the model but a person between the tool call and the money, and that is what the mitigation adds.

##### VEC-0013 — An assistant's draft can restate an address the console masked

STRIDE information disclosure · promoted 2026-09-13

> `LLM08` Sensitive Information Disclosure Through Output

**Attack.** Open a ticket-less lookup in the support console, where `support-console.authz` masks the address, and ask the assistant to draft a delivery answer. `assist-request` carries `address` with no such condition, and `support-assistant.output_handling` puts the draft in front of the agent.

**Impact.** The address the console deliberately withheld, on the agent's screen, by a route the masking rule does not cover — and in the audit log as part of the prompt, where `audit-log.retention` keeps it for two years.

**Context.** This is the cost of adding an element beside a control rather than inside it. VEC-0007 and `MIT-0004` bought the ticket-linked rule; a second reader of the same data was added later and nobody carried the rule across. The mitigation is to send the assistant what the agent is allowed to see, and no more.

##### VEC-0014 — Nobody tells the shopper a model read their message and wrote the reply

LINDDUN unawareness · promoted 2026-09-13

> `U.1.1` Unawareness as data subject

**Attack.** None needed. `assist-request` carries `shopper-message`, `order` and `address` into a language model, and `assist-draft` returns a statement about the shopper that `support-assistant.output_handling` sends out under a named agent. No flow in the model tells them either thing happened.

**Impact.** An unawareness harm on its own, and it compounds: `draft-reply.notes` records that the reply is generated rather than looked up, so a shopper who cannot know a model wrote it also cannot know to doubt it. The prompt is kept for two years in `audit-log` and `dsar-request` has no way to surface something the shopper was never told existed.

**Context.** The same control answers this and VEC-0010 — a notice that says what is collected and why — which is why one mitigation carries both rather than two ids drifting apart. What is new here is the disclosure in the reply itself, because a notice nobody opens is not what makes this one visible.

### Stores

#### `audit-log` — Audit log

##### VEC-0004 — The audit log keeps email past its own retention, beyond erasure's reach

LINDDUN non compliance · promoted 2026-09-13

> `DD.3.4` Duration/retention · `DD.3.2` Propagation · `NC.1.1.1` Insufficient data subject controls

Chains: `audit-log` LINDDUN data disclosure, `audit-log` LINDDUN non compliance

**Attack.** None needed. `support-audit` writes `email` into `audit-log` on every support lookup, `audit-log.retention` is 2 years, and `email.retention` is life of account plus 30 days. `dsar-read` reads only `orders-db`, and the log's object lock prevents deletion before expiry by design.

**Impact.** A shopper who closes their account has their email address here for up to two years, in a copy nobody described as one. An erasure request cannot reach it, so "we erased everything" is untrue and "we erased everything we could reach" is undocumented — either of which a regulator would be shown.

**Context.** This may be entirely defensible: a legal-obligation record can outlive an erasure request, and `audit-event` carries that basis. What is missing is the decision — whether the log needs the address or a pseudonym, and what the stated exception to erasure is. Recording that is most of the mitigation.

#### `orders-db` — Orders database

##### VEC-0005 — Nobody could say whether the backup snapshots honour the address purge

LINDDUN non compliance · promoted 2026-09-13 · from the open question

> Nobody could confirm whether the nightly database snapshots are covered by the 90-day address purge, or whether they retain addresses for 35 days past it.

**Attack.** None needed. A subject access request, or a regulator, asks what is retained. `orders-db.retention` promises addresses purged 90 days after delivery; `orders-db.backups` are nightly snapshots kept 35 days.

**Impact.** If the purge does not reach the snapshots, the stated retention is false by up to 35 days for every address ever delivered to. A storage-limitation commitment that is false is worse than one never made.

**Context.** This started life as the interview's one unanswerable question and was carried forward unchanged. The enumeration found the same concern on `orders-db` as a non-compliance finding, which is dismissed below in favour of tracking it here, where it began: the vector's first job is to get the question answered.

##### VEC-0006 — Backups add no isolation from the compromise that matters

STRIDE information disclosure · promoted 2026-09-13

> `DR01` Unprotected Sensitive Data

**Attack.** Compromise the AWS account, or the KMS key. `orders-db.backups` are "Nightly snapshots retained 35 days in the same account, same KMS key", so whoever can decrypt the live database can decrypt every snapshot.

**Impact.** Thirty-five days of history exposed alongside the live data, including addresses the purge has already removed from the live table. The encryption defends a stolen disk, which is not how this database would be read.

**Context.** `access_control` is service roles with break-glass through PAM, so the credential path is guarded. The finding is about blast radius once that guard fails, not about how likely it is to.

### Flows

#### `support-render` — Show order to agent

##### VEC-0008 — The full order record lands on a laptop in a zone the model calls untrusted

STRIDE information disclosure · promoted 2026-09-13

> `DR01` Unprotected Sensitive Data

**Attack.** Compromise, lose, or photograph a support agent's laptop. `support-render` carries `order`, `address` and `email` from `prod-vpc` into `corp-net`, and the model's own assumptions say the corporate network is not trusted.

**Impact.** Every shopper an agent has looked up, on a device with no recorded control over what happens to the data after it arrives — no disk encryption, screenshot or clipboard restriction, or endpoint management appears anywhere in the model.

**Context.** The untrusted-network assumption is honoured for authentication — WebAuthn, device-bound sessions — and abandoned for data. Those controls very likely exist and were not asked about; the vector's first job is to find out.

#### `dsar-request` — Data subject access or erasure request

##### VEC-0009 — Verifying a guest collects identity documents the model does not know it holds

LINDDUN data disclosure · promoted 2026-09-13

> `DD.1.1` Data type sensitivity · `DD.3.4` Duration/retention

**Attack.** None needed. `dsar-request.authn` accepts "documentary proof for guests" by HTTPS form or by email to the privacy inbox. No `data` entry exists for an identity document, so it has no classification, no lawful basis, no retention and no store modelled to hold it.

**Impact.** Among the most sensitive personal data the system touches, sitting in a mailbox or a form backend with nothing able to say whether it is deleted after the check or kept indefinitely. The control protecting the rights process collects data the rights process cannot account for.

**Context.** Chained conceptually to VEC-0001 — it is the cost of the verification that vector says is too weak — but tracked separately because its mitigation is different: model the document, decide its retention, and delete on schedule, regardless of how verification is strengthened.

## Not promoted

Every finding considered and not tracked, with the reason. The reason is the point: a dismissal nobody can disagree with is not a decision.

| Finding | Reason |
| :--- | :--- |
| `checkout-api` LINDDUN detecting | Real but small. Login already reveals account existence by design, since email is the login identifier, so closing a timing side channel on the DSAR path changes little. Revisit if an anonymous lookup is ever added. |
| `session-cache` STRIDE denial of service | A restart drops every live session, which is a nuisance for shoppers mid-checkout and not a threat: the cart is rebuilt, no order is lost, and `retention` says nothing was meant to survive. Operational, for a runbook rather than the threat model. |
| `orders-db` LINDDUN non compliance | Promoted as VEC-0005 from the model's own open question rather than from this finding. The two are one concern and the question is where it started; tracking both would be two ids for one decision. |

## Orphaned

None. Every vector's source is still a finding in the enumeration.

## Retired

None.

## Open questions from the model

| Question | What became of it |
| :--- | :--- |
| Nobody could confirm whether the nightly database snapshots are covered by the 90-day address purge, or whether they retain addresses for 35 days past it. | promoted as **VEC-0005** |

## Limits

**Every finding was decided; nothing proves the right ones were promoted.** The script can show that each threat verdict and each open question ended up as a vector, in a chain, or dismissed with a reason. Whether those were the right calls is the judgement this step exists for, and no check reaches it.

**A vector is a decision to track, not a decision to act.** What is being done about each is the matrix, rendered separately from the same register.

<!-- vector: rendered from example.vectors.yaml sha256:ac9a8635625b08c5f9bf54307ca580a282472ba558e00be2c64388d69de7532f -->
