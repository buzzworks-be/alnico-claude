# Threat enumeration — Acme Checkout

Generated from `example.dfd.yaml` by `render_threats.py`. Do not edit; regenerate.

## Findings

21 finding(s), grouped by the element they were found on.

### Actors

#### `shopper` — Shopper

**STRIDE spoofing** — Guest checkout accepts an email address with no proof of control.

> `AA01` Authentication Abuse/ByPass

`authenticates_how` records guest checkout as anonymous, and `submit-order` carries `email` from the browser. Nothing binds that address to the person submitting it, so an order — and the confirmation containing it — can be directed at somebody else's address. The same gap widens at `dsar-request`, where the only thing standing between a stranger and an export is documentary proof a human judges.

**LINDDUN unawareness** — Gift recipients are data subjects who have no way to know we hold their address, or to have it removed.

> `U.1.1` Unawareness as data subject · `U.2.3` Rectification/erasure

`address` records `subjects: Shoppers and their gift recipients` and `notes: Gift recipients never interact with us, which makes transparency harder`. Every path in the model that serves a data subject — `dsar-request`, `dsar-export` — starts from a shopper with an account or a documented identity. A recipient has neither, so there is no flow by which they could be informed or exercise erasure. The absence is the finding.

### Processes

#### `checkout-web` — Checkout web app

**STRIDE information disclosure** — PII scrubbing on client error reports is a filter that fails open.

> `DS06` Data Leak

`logging` is "Client errors to Sentry with PII scrubbing on; no order contents". The page holds `address` and `email` at the moment an error is most likely, and scrubbing is pattern matching: a new field, a nested object or a stack frame capturing a local variable defeats it silently. Nothing in the model says the scrubber is tested, and a scrubber nobody tests is a claim rather than a control.

**LINDDUN unawareness** — No element of the model represents how the shopper is told what is collected, or on what basis.

> `U.1.1` Unawareness as data subject

This is the only process the shopper sees, and it is where a privacy notice or a consent interaction would live. The model contains neither — no flow carries one, no store holds one, and `lawful_basis` is recorded per data item in the dictionary rather than shown to anybody. The information exists for the reviewer and not for the data subject, which is precisely the shape of an unawareness threat.

#### `checkout-api` — Checkout API

**STRIDE denial of service** — Nothing in the model records a rate limit, and the order path reaches a third party on every request.

> `DO01` Flooding

`submit-order` is `trigger: user_action` from an untrusted zone, and `charge` calls Stripe synchronously behind it. No field anywhere records throttling, quotas or a circuit breaker, so an unauthenticated flood costs us both database writes and third-party API quota. The absence of an answer is the finding; the interview recorded `authn` and `authz` for this process and nothing about availability.

**LINDDUN detecting** — Nothing records whether the API's responses reveal that an email address belongs to a customer.

> `D.3` System responses

The process authenticates shoppers and, through `dsar-request`, receives requests keyed on `email`. Whether a lookup for an unknown address is distinguishable from one for a known address — by status code, message or timing — is not answered anywhere in the model. If it is, anybody can test whether a given person shops here, which is a detecting threat that needs no credentials at all.

#### `support-console` — Support console

**LINDDUN data disclosure** — Address masking is lifted by the agent who wants to see the address, with no second party in the loop.

> `DD.4.1.1` Predetermined set of parties · `DD.1.2` Data type granularity

`authz` records that "addresses are masked unless the agent opens a ticket-linked view". Nothing in the model says who verifies that the ticket is real, relevant, or the shopper's own — so the control is a speed bump on a path the agent controls both ends of. `logging` makes every unmasking visible afterwards, which makes this detective rather than preventive, and worth deciding about deliberately: compare `dsar-handler`, which has a two-person rule for a comparable action.

#### `support-assistant` — Support assistant

**STRIDE elevation of privilege** — Text a shopper writes reaches the prompt of a process that holds a refund tool.

> `LLM02` Indirect Prompt Injection via Retrieved Content · `LLM05` Excessive Agency via Unauthorized Tool Use

`untrusted_input` records that the shopper's message and the order's free-text delivery note both go into the prompt verbatim, and `authority` gives the process a tool that moves money: refund the order in the open ticket, capped at EUR 50. Nothing in the model separates instruction from data at the point the tool call is decided, so a delivery note written to read like an instruction is indistinguishable from the system prompt. The cap bounds one loss rather than the number of them — placing orders is something the attacker already does, and every order carries its own note.

**STRIDE information disclosure** — A draft can restate the delivery address that the console deliberately masks.

> `LLM08` Sensitive Information Disclosure Through Output

`support-console`'s `authz` masks addresses unless the agent opens a ticket-linked view. `assist-request` hands this process `address` with no such condition, and `output_handling` puts the draft in front of the agent as text. A draft that quotes the address to answer a delivery question therefore puts it on the agent's screen by a path the masking rule never sees. The control and the way around it are one element apart in this model.

**LINDDUN unawareness** — The shopper is not told a model read their message or wrote the reply they receive.

> `U.1.1` Unawareness as data subject

`assist-request` carries `shopper-message`, `order` and `address` into a language model, and `output_handling` sends the result out under a named support agent. No flow in the model informs the shopper that either happened. The reply is a statement about them, generated rather than looked up — `draft-reply.notes` says as much — and the one path that exists for a shopper to ask what is held about them, `dsar-request`, has no way to surface a prompt they were never told about.

#### `dsar-handler` — Data request handler

**STRIDE spoofing** — For a guest, the only thing between a stranger and somebody else's data is documentary proof a human judges.

> `AA01` Authentication Abuse/ByPass

`dsar-request.authn` is "Identity verification against the account, or documentary proof for guests", and its `notes` admit "Guest checkout makes verification harder, since there is no account to prove". An account holder proves control of the login; a guest presents documents to a privacy team member with no baseline to compare them against. The same root cause as the `shopper` spoofing finding, but a worse outcome: there the attacker misdirects one order, here they obtain a complete export.

**LINDDUN unawareness** — A guest who cannot produce documents is locked out of their own data by the same control that protects it.

> `U.2.2` Access · `U.2.3` Rectification/erasure

`dsar-request.authn` offers account verification or documentary proof, and its `notes` record that guests have no account to prove. Tightening the check to stop the spoofing finding above makes this worse, and loosening it makes that one worse — the two are the same dial. Nothing in the model records where the dial is set, who decides, or what happens to a guest whose documents are judged insufficient. That is a lack of access and erasure control, arrived at by accident rather than by decision.

**LINDDUN non compliance** — Gift recipients are data subjects the rights process cannot serve at all.

> `NC.1.1.1` Insufficient data subject controls

`address` records `subjects: Shoppers and their gift recipients`, so a recipient's personal data is processed. Every route into this process starts from a shopper: `dsar-request` comes `from: shopper`, and verification is against a shopper's account. A recipient has no account, no order of their own to name, and no relationship to prove — so there is no path by which they could exercise access or erasure. This is the compliance face of the `shopper` unawareness finding, recorded here because this is the process that would have to serve them.

### Stores

#### `orders-db` — Orders database

**STRIDE information disclosure** — The backups sit in the same account under the same KMS key, so they add no isolation from the compromise that matters.

> `DR01` Unprotected Sensitive Data

`encryption_at_rest` is AES-256 under a customer-managed KMS key, and `backups` are "Nightly snapshots retained 35 days in the same account, same KMS key". Whoever can decrypt the live database can decrypt every snapshot, and whoever holds the account holds both. The encryption defends against a stolen disk, which is not how this database would be read; it does not defend against the credential compromise that is.

**LINDDUN non compliance** — Nobody could say whether the 90-day address purge reaches the snapshots, so addresses may persist 35 days past their stated retention.

> `NC.1.1.4` Violation of storage limitation principle

`retention` promises addresses are "purged 90 days after delivery", and `backups` are "Nightly snapshots retained 35 days". The model's own `open_questions` records that nobody could confirm whether the snapshots are covered by the purge. If they are not, the stated retention is false by up to 35 days for every address, and a storage-limitation commitment that is false is worse than one never made — it is the thing a regulator would be shown. This is the model's unanswerable question promoted, which is what those questions are for.

#### `audit-log` — Audit log

**LINDDUN data disclosure** — `email` is kept here for 2 years, well past the retention promised for it everywhere else.

> `DD.3.4` Duration/retention · `DD.3.2` Propagation

`data` is `[audit-event, email]` and `retention` is "2 years, then hard delete". But `email` itself records `retention: Life of account plus 30 days`, and `support-audit` carries `email` into this store on every support lookup. So a shopper who closes their account still has their email address here for up to two years, in a second copy nobody described as a copy. Either the audit record needs the address or it needs a pseudonym, and the model does not say which was decided.

**LINDDUN non compliance** — An erasure request cannot reach an append-only store with object lock, so it cannot be fully honoured.

> `NC.1.1.1` Insufficient data subject controls

`dsar-handler` erases on a two-person rule, and `dsar-read` reads only `orders-db`. This store holds `email` under object lock that "prevents deletion before expiry", so by construction the erasure path cannot touch it. That may well be defensible — a legal-obligation record can outlive an erasure request — but the model records no such decision, so today the difference between "we erased everything" and "we erased everything we could reach" is undocumented. The honest version of this is a stated exception, not silence.

#### `session-cache` — Session cache

**STRIDE denial of service** — Nothing survives a restart, and nothing in the model says what happens to a shopper mid-checkout when one occurs.

> `DO02` Excessive Allocation

`retention` records "30-minute TTL; nothing survives a restart", and `backups: null` is an accepted gap. A restart or an eviction under memory pressure therefore drops every live session at once: `session-read` returns nothing and `checkout-api` loses the cart and the shopper's context for everyone simultaneously. Whether that degrades to a re-login or to a failed order is not recorded anywhere, and the failure is correlated across all shoppers rather than spread.

### Flows

#### `submit-order` — Submit order

**STRIDE denial of service** — The one unauthenticated-reachable write path in the model, with no throttle recorded on it.

> `DO01` Flooding

`trigger: user_action` from `trust_zone: browser`, and a guest needs no account to use it. Every request behind it costs a database write through `persist-order` and a third-party call through `charge`. No field in the model records a rate limit, a quota or a queue. This is the flow face of the `checkout-api` availability finding: recorded separately because the fix belongs at the edge, before the request reaches the process.

#### `support-render` — Show order to agent

**STRIDE information disclosure** — The full order record lands on a staff laptop in a zone the model itself declares untrusted, and no device control is recorded anywhere.

> `DR01` Unprotected Sensitive Data

This flow crosses `prod-vpc` to `corp-net`, and the model's own assumptions say "The corporate network is not trusted; the support console authenticates every request regardless of network position". That assumption is honoured for authentication and then abandoned for data: `order`, `address` and `email` are rendered onto a device in the untrusted zone. Nothing in the model records disk encryption, screenshot or clipboard restrictions, endpoint management, or anything else about what happens to the data once it arrives. `notes` records the masking, which governs whether the address is shown, not what the laptop does with it afterwards.

#### `dsar-request` — Data subject access or erasure request

**LINDDUN data disclosure** — Verifying a guest collects identity documents that appear nowhere in the data dictionary.

> `DD.1.1` Data type sensitivity · `DD.3.4` Duration/retention

`authn` is "Identity verification against the account, or documentary proof for guests". Documentary proof means an identity document — among the most sensitive categories of personal data there is — arriving by HTTPS form or by email to the privacy inbox. No `data` entry exists for it. So it has no `classification`, no `personal_data` level, no `lawful_basis`, no `retention`, and no store modelled to hold it, which means nothing in this model can say whether it is deleted after the check or sitting in a mailbox indefinitely. The control that protects the rights process collects data the rights process cannot account for.

## Coverage

| Section | STRIDE | LINDDUN | Total |
| :--- | ---: | ---: | ---: |
| actors | 6 | 3 | 9 |
| processes | 36 | 42 | 78 |
| stores | 12 | 18 | 30 |
| flows | 69 | 138 | 207 |
| **all** | **123** | **201** | **324** |

| Verdict | Count |
| :--- | ---: |
| threat | 21 |
| controlled | 265 |
| not_applicable | 38 |

324 of 324 applicable pairings verdicted.

## Considered and dismissed

One line each. The reasons are the point: a dismissal a reader cannot disagree with is not a dismissal.

### Actors

| Element | Category | Verdict | Reason |
| :--- | :--- | :--- | :--- |
| `shopper` | STRIDE repudiation | controlled | Every order write goes through `checkout-api`, whose `logging` records structured audit events to `audit-log`, which is append-only with object lock. An authenticated shopper cannot plausibly deny placing an order. A guest can deny it, but that is the spoofing finding above rather than a second one. |
| `shopper` | LINDDUN linking | controlled | Linking a shopper's activity is the service working: `order` and `cart` are joined to a person on purpose, under `lawful_basis: Contract`. The linkability that is not deliberate is `session-id`, and it is recorded against `session-cache` rather than here. |
| `shopper` | LINDDUN identifying | controlled | The shopper is identified, deliberately. `email` carries `notes: Doubles as the login identifier, so it cannot be pseudonymised` and `lawful_basis: Contract`. Identification is the purpose, not a leak. |
| `support-agent` | STRIDE spoofing | controlled | `authenticates_how` is Okta SSO with mandatory WebAuthn, and `support-console.authn` binds the session to the device. A phishable factor is the usual way this fails and there is not one here. |
| `support-agent` | STRIDE repudiation | controlled | `support-console.logging` writes every lookup to `audit-log` with the agent identity and a reason, and `audit-event` carries `notes: Deliberately non-repudiable for staff`. That is the control working as designed. |
| `stripe-api` | STRIDE spoofing | controlled | Outbound, `charge.authn` is a restricted secret key rotated quarterly. Inbound, `charge-result.authn` is webhook signature verification, which is what stops an attacker claiming a charge succeeded. |
| `stripe-api` | STRIDE repudiation | controlled | Settlement is recorded on Stripe's side as well as ours, and `charge-result` arrives signed. Neither party can deny a charge that the other holds a signed record of. |

### Processes

| Element | Category | Verdict | Reason |
| :--- | :--- | :--- | :--- |
| `checkout-web` | STRIDE spoofing | controlled | `authn` is a session cookie issued by the API with no credentials held in the page, and `submit-order.authn` adds SameSite=Lax and a CSRF token. There is nothing in the page for an attacker to replay. |
| `checkout-web` | STRIDE tampering | controlled | The process sits in `trust_zone: browser`, described in the model as "fully under the shopper's control; nothing running here is trusted", so tampering is certain rather than possible. `authz: None — every decision is re-made server-side` is the answer, and it is the right one. |
| `checkout-web` | STRIDE repudiation | controlled | The page proves nothing and is not asked to. Attribution comes from `checkout-api.logging`, which writes audit events server-side where the shopper cannot reach them. |
| `checkout-web` | STRIDE denial of service | not_applicable | The process runs on the shopper's own device, in a trust zone they control. Denying it to themselves is not a threat to anyone else, and denying it to others means attacking the static asset host, which the model puts out of scope. |
| `checkout-web` | STRIDE elevation of privilege | not_applicable | `authz: None — every decision is re-made server-side`. The process holds no authority to escalate; the privileges worth attacking are all `checkout-api`'s, and they are enumerated there. |
| `checkout-web` | LINDDUN linking | controlled | The page holds one shopper's `cart` and `address` for one session. It joins nothing across people or visits; `session-cache` is where cross-request linkage lives. |
| `checkout-web` | LINDDUN identifying | controlled | It collects `email` and `address` from the person they belong to, which is collection rather than identification of someone who expected otherwise. |
| `checkout-web` | LINDDUN non repudiation | not_applicable | Nothing here is evidence of anything. The page signs nothing, retains nothing, and `logging` explicitly excludes order contents. |
| `checkout-web` | LINDDUN detecting | controlled | Observing the page reveals that this shopper is shopping, to the shopper. Anything observable by a third party is on the wire, and belongs to the flows rather than here. |
| `checkout-web` | LINDDUN data disclosure | controlled | It collects exactly the fields `submit-order` carries — `cart`, `address`, `email`, `card-token` — each with a `lawful_basis` recorded in the data dictionary. Nothing is gathered that the order does not need. |
| `checkout-web` | LINDDUN non compliance | controlled | Every data item it handles carries a `lawful_basis` and a `retention` in the dictionary. The compliance risks that remain are retention and data subject rights, and both are recorded where they arise — `orders-db` and `dsar-handler`. |
| `checkout-api` | STRIDE spoofing | controlled | `authn` is mTLS from the edge proxy plus the shopper's session cookie for user context, so a caller has to hold both a client certificate and a session. `trust_zone: prod-vpc` has no inbound path except the proxy. |
| `checkout-api` | STRIDE tampering | controlled | Inputs arrive over `submit-order` with TLS 1.3 and a CSRF token, and `authz` re-checks row-level ownership on every order read or write, so a tampered request fails on the object it names rather than on its shape. |
| `checkout-api` | STRIDE repudiation | controlled | `logging` writes structured audit events to `audit-log`, which is append-only with object lock preventing deletion before expiry. The service cannot erase its own trail. |
| `checkout-api` | STRIDE information disclosure | controlled | `logging` records request logs without bodies, which is the usual way addresses and emails end up somewhere nobody is guarding. Reads are constrained by the row-level ownership checks in `authz`. |
| `checkout-api` | STRIDE elevation of privilege | controlled | `authz` is row-level ownership checks on every order read or write, so holding a valid session grants no access to another shopper's order. `persist-order.authn` uses IAM database authentication rather than a shared credential the process could widen. |
| `checkout-api` | LINDDUN linking | controlled | It joins `cart` to `order` to a shopper, which `cart`'s own `notes: Purchase history is linkable to a person once joined to an order` identifies as deliberate and necessary under `lawful_basis: Contract`. |
| `checkout-api` | LINDDUN identifying | controlled | It handles `email` and `address` as identified data from the start, under a recorded contract basis. Nothing pseudonymous is re-identified here. |
| `checkout-api` | LINDDUN non repudiation | controlled | Its audit events concern orders rather than staff, and `audit-event` records `lawful_basis: Legal obligation`. A shopper being unable to deny their own order is the tax and fraud record working. |
| `checkout-api` | LINDDUN data disclosure | controlled | It writes exactly `order`, `address` and `email` to `orders-db` per `persist-order`, and `audit-write` carries only `audit-event`. Nothing is propagated further than the order needs. |
| `checkout-api` | LINDDUN unawareness | controlled | The rights machinery exists as its own process, `dsar-handler`, with flows in and out. The gaps in it are recorded there and against `shopper` rather than duplicated here. |
| `checkout-api` | LINDDUN non compliance | controlled | It enforces the contract basis it collects under and writes to stores whose retention is recorded. The storage-limitation risk lives with the store that keeps the data, which is where it is recorded. |
| `fulfilment-worker` | STRIDE spoofing | controlled | `authn` is an IAM role with no inbound network path, so there is no request to forge. Impersonating the worker requires the role, not a credential that travels. |
| `fulfilment-worker` | STRIDE tampering | controlled | `authz` is a read-only database role scoped to paid orders, so the worker cannot alter what it reads. `poll-orders.encryption_in_transit` is TLS verify-full, which stops interception on the way. |
| `fulfilment-worker` | STRIDE repudiation | controlled | `logging` writes an audit event per dispatched order to the append-only `audit-log`, so a dispatch cannot be denied or quietly un-recorded. |
| `fulfilment-worker` | STRIDE information disclosure | controlled | It reads `order` and `address` under a read-only scoped role and pushes picking instructions onward. The warehouse itself is out of scope by declaration, and treated as a consumer of orders. |
| `fulfilment-worker` | STRIDE denial of service | controlled | `poll-orders` is `trigger: scheduled` with no inbound path, so there is no request an attacker can send it. Starving it means starving the database, which is recorded against `orders-db`. |
| `fulfilment-worker` | STRIDE elevation of privilege | controlled | A read-only role scoped to paid orders is the least privilege the job can do its work with, and `poll-orders.authn` binds it at the database rather than in application code. |
| `fulfilment-worker` | LINDDUN linking | controlled | It handles one order at a time and joins nothing across shoppers. The linkage it consumes was made in `checkout-api` under the contract basis. |
| `fulfilment-worker` | LINDDUN identifying | controlled | Delivery requires an identified recipient at a `address`. There is no pseudonymous data here being resolved to a person. |
| `fulfilment-worker` | LINDDUN non repudiation | controlled | Its audit events attribute dispatches to the system, not to a shopper. Nothing here makes a data subject unable to deny an action. |
| `fulfilment-worker` | LINDDUN detecting | not_applicable | It has no inbound path and returns nothing to anybody outside the VPC, so there is no response, timing or side effect an observer could read involvement from. |
| `fulfilment-worker` | LINDDUN data disclosure | controlled | `poll-orders` carries `order` and `address` and not `email`, which is the minimisation the job needs: a picker needs somewhere to send the parcel and not a way to contact the buyer. |
| `fulfilment-worker` | LINDDUN unawareness | not_applicable | No interface to a data subject exists here — no inbound path, no response. Awareness and intervention are `dsar-handler`'s and `checkout-web`'s, and are recorded there. |
| `fulfilment-worker` | LINDDUN non compliance | controlled | It processes `order` and `address` for delivery, which is the contract basis both carry. Retention is not its decision; the store's. |
| `support-console` | STRIDE spoofing | controlled | `authn` is Okta SSO with WebAuthn enforced and the session bound to the device, and the model's assumptions state the corporate network is not trusted, so position on the network grants nothing. |
| `support-console` | STRIDE tampering | controlled | `support-read.authn` is a read-only database role, so the console cannot alter an order even if an agent wanted to. Lookups arrive over TLS 1.3. |
| `support-console` | STRIDE repudiation | controlled | `logging` writes every lookup to `audit-log` with the agent identity and a reason, into an append-only store the console cannot write over. |
| `support-console` | STRIDE information disclosure | controlled | Reads are scoped by a read-only role, addresses are masked by default per `authz`, and every unmasking is recorded. The residual risk is an authorised agent looking at more than they need, which is the data disclosure finding below rather than a second one here. |
| `support-console` | STRIDE denial of service | controlled | It sits behind the SSO proxy in `prod-vpc` with no anonymous surface, so an attacker needs an Okta session with WebAuthn before they can send it anything at all. |
| `support-console` | STRIDE elevation of privilege | controlled | `authz` is role-based and the database role is read-only, so the highest privilege reachable from here is reading an order — which is the console's whole purpose rather than an escalation. |
| `support-console` | LINDDUN linking | controlled | An agent looks up one order at a time by email or order number. Nothing here assembles a profile across shoppers, and every lookup is recorded. |
| `support-console` | LINDDUN identifying | controlled | It deals in identified data by design — an agent answering a query needs to know whose order it is. Nothing pseudonymous is resolved here. |
| `support-console` | LINDDUN non repudiation | controlled | The non-repudiation it creates is of staff actions, and `audit-event` records that as deliberate: "Deliberately non-repudiable for staff, which is a LINDDUN cost accepted on purpose". |
| `support-console` | LINDDUN detecting | controlled | Its only users are authenticated agents inside `prod-vpc`. There is no unauthenticated response from which an outsider could deduce that a person is a customer. |
| `support-console` | LINDDUN unawareness | not_applicable | Its users are staff, not data subjects. A shopper never reaches this process, so it can neither inform them nor take instruction from them; those paths are `checkout-web`'s and `dsar-handler`'s. |
| `support-console` | LINDDUN non compliance | controlled | Access is logged with a stated reason, which is what an audit of support access asks for, and the read-only role prevents the console becoming a way to change records outside the order path. |
| `support-assistant` | STRIDE spoofing | controlled | `authn` is an IAM role with no public route; only `support-console` can reach it. Impersonating the caller means holding the console's identity, which is recorded against `support-console`. |
| `support-assistant` | STRIDE tampering | controlled | `system_prompt` is held in the repository and shipped with the service, not editable from the console and not assembled from anything a shopper writes. Changing what the process is told to do means changing the deployed artefact. Tampering with the data inside the prompt is the elevation of privilege finding above rather than a second one. |
| `support-assistant` | STRIDE repudiation | controlled | `logging` records the prompt, every tool call and every refund decision to `audit-log`, which is append-only with object lock. Neither the process nor the agent who accepted a draft can deny a refund. |
| `support-assistant` | STRIDE denial of service | controlled | Reachable only from `support-console`, which is behind Okta SSO with WebAuthn. Losing it degrades to an agent writing the reply themselves, since `output_handling` already requires them to press send. |
| `support-assistant` | LINDDUN linking | controlled | `tech` records that no conversation state is kept between tickets, and `authority` scopes the process to the order in the open one. Nothing here joins two tickets or two shoppers. |
| `support-assistant` | LINDDUN identifying | controlled | It works on an identified order because the ticket is about one, and `authority` holds it there. Identification is the function rather than a side effect. |
| `support-assistant` | LINDDUN non repudiation | controlled | Deliberate, per `audit-event.notes`: the prompt and the tool calls are logged precisely so a refund is attributable. |
| `support-assistant` | LINDDUN detecting | not_applicable | `authn` records no inbound path from outside `prod-vpc`. Nothing outside can time it or watch it respond. |
| `support-assistant` | LINDDUN data disclosure | controlled | `assist-request` carries `order`, `address` and `shopper-message` and not `email` — the console already knows who it is talking to, so the identifier stays out. The address travels because the questions this process answers are about delivery. What it then does with the address is the information disclosure finding above. |
| `support-assistant` | LINDDUN non compliance | controlled | `output_handling` keeps a named agent between every generated statement and the shopper, so nothing the shopper reads is an automated decision. The one thing decided without a human is a refund under EUR 50, which runs in the shopper's favour. What is not covered is telling them any of this happened, and that is the unawareness finding above. |
| `dsar-handler` | STRIDE tampering | controlled | `authz` is a two-person rule on erasure runs, so the destructive path needs two identities. `dsar-read.authn` restricts the read to an approved run rather than to anyone holding the role. |
| `dsar-handler` | STRIDE repudiation | controlled | `logging` is a full audit trail of every request, approval and export, into the append-only `audit-log`. Both the requester and the approver are recorded. |
| `dsar-handler` | STRIDE information disclosure | controlled | Reads are limited to approved runs and the export goes out over TLS 1.3. Whether the right person receives it depends on verification, which is the spoofing finding above. |
| `dsar-handler` | STRIDE denial of service | controlled | `dsar-read` is `trigger: manual` behind an approval, so volume is bounded by the privacy team rather than by a requester. A flood of requests costs human time, which is a staffing problem rather than an availability one. |
| `dsar-handler` | STRIDE elevation of privilege | controlled | The job holds the broadest read in the system, and the two-person rule on erasure plus approval-scoped reads are what keep that from being usable by one person alone. |
| `dsar-handler` | LINDDUN linking | controlled | Assembling everything held about one person is exactly the linkage a subject access request requires. Doing it for the wrong person is the spoofing finding, not a linking one. |
| `dsar-handler` | LINDDUN identifying | controlled | It works from an identified `email` supplied by the requester. No pseudonymous data is resolved beyond what the request itself asks for. |
| `dsar-handler` | LINDDUN non repudiation | controlled | Its audit trail attributes approvals to staff, which `audit-event` records as a deliberate accepted cost. A shopper's own request being recorded is what makes the response defensible. |
| `dsar-handler` | LINDDUN detecting | controlled | A request arrives before any response exists, and the reply goes only to the verified requester. Whether an unknown address is distinguishable from a known one is recorded against `checkout-api`, where the lookup happens. |
| `dsar-handler` | LINDDUN data disclosure | controlled | `dsar-read` carries `order`, `address` and `email` — everything held, which is what an access request is for. Sending less would fail the request rather than minimise it. |

### Stores

| Element | Category | Verdict | Reason |
| :--- | :--- | :--- | :--- |
| `orders-db` | STRIDE tampering | controlled | `access_control` is service roles only, with human access break-glass through PAM and an alert to the on-call. Write paths are `persist-order` with IAM database authentication; every other reader holds a read-only role. |
| `orders-db` | STRIDE repudiation | not_applicable | Repudiation against a store applies to a store that is itself the evidence, and this one is not: order changes and support lookups are recorded in `audit-log`, which is append-only with object lock. Altering `orders-db` destroys the current state, not the record of how it got there. |
| `orders-db` | STRIDE denial of service | controlled | Nightly snapshots retained 35 days are a recovery path for destruction, and `access_control` keeps the delete privilege behind PAM with an alert. Exhaustion through the order path is recorded against `checkout-api`, where the unthrottled entry point is. |
| `orders-db` | LINDDUN linking | controlled | It holds `order`, `address` and `email` joined per shopper, which is the linkage the contract basis is recorded for. `cart`'s own note that purchase history becomes linkable once joined to an order describes this store working as intended. |
| `orders-db` | LINDDUN identifying | controlled | Everything here is identified data collected from the person it concerns. `email` carries a note that it cannot be pseudonymised because it is the login identifier, which is a recorded decision rather than an oversight. |
| `orders-db` | LINDDUN non repudiation | controlled | `order` is kept 7 years under a tax obligation, so a shopper cannot deny a purchase for that period. That is the obligation, not a threat the model can design away. |
| `orders-db` | LINDDUN detecting | not_applicable | The store answers no query from outside `prod-vpc`. Every reader — `checkout-api`, `fulfilment-worker`, `support-console`, `dsar-handler` — is an authenticated service, so there is no response an observer could infer membership from. |
| `orders-db` | LINDDUN data disclosure | controlled | It holds the three items the order needs and no more, each with a recorded `lawful_basis`. The retention question is real and recorded under non-compliance below, where the deadline lives. |
| `audit-log` | STRIDE tampering | controlled | `access_control` is write-only for services, and `encryption_at_rest` records object lock preventing deletion before expiry. No path in the model can rewrite an entry, including the services that wrote it. |
| `audit-log` | STRIDE repudiation | controlled | This is the store that is the evidence, which is why the check applies here and not to the other two. Append-only with object lock, replicated cross-region, and written by three separate processes over authenticated flows. |
| `audit-log` | STRIDE information disclosure | controlled | `access_control` requires a security team role to read, and the writers hold write-only credentials. An attacker who compromises a service gains the ability to add noise, not to read the history. |
| `audit-log` | STRIDE denial of service | controlled | Cross-region replication with a matching 2-year expiry survives the loss of a region. Flooding it with events requires compromising a writer, which is that writer's finding rather than this store's. |
| `audit-log` | LINDDUN linking | controlled | `audit-event` links staff actions to shoppers' orders, which is the point of an audit record and its recorded `lawful_basis: Legal obligation`. |
| `audit-log` | LINDDUN identifying | controlled | It holds `email` and identified staff names because an audit trail that cannot name who did what to whom is not one. |
| `audit-log` | LINDDUN non repudiation | controlled | `audit-event` records this explicitly: "Deliberately non-repudiable for staff, which is a LINDDUN cost accepted on purpose". A decision on the record, not a hole. |
| `audit-log` | LINDDUN detecting | not_applicable | Reading it needs a security team role and there is no path from outside `prod-vpc`. Nothing here is observable by someone who could learn a person's involvement from it. |
| `session-cache` | STRIDE tampering | controlled | `access_control` is the Checkout API service role only, and `session-write.authn` is Redis AUTH plus a security group. Nothing else in the model has a path to it. |
| `session-cache` | STRIDE repudiation | not_applicable | Not an evidence store. Sessions are working state with a 30-minute TTL; what a shopper did is recorded in `audit-log` through `checkout-api`. |
| `session-cache` | STRIDE information disclosure | controlled | `encryption_at_rest` is "In-memory only, encrypted volume; no persistence to disk" and `retention` is a 30-minute TTL with nothing surviving a restart, so there is very little here to read and not for long. The accepted gap on `backups` is consistent with that. |
| `session-cache` | LINDDUN linking | controlled | `session-id` carries `notes: Links otherwise separate requests to one person; a classic linkability vector`, which is exactly what this store exists to do. The control is the bound: a 30-minute TTL, nothing persisted, and `lawful_basis: Legitimate interests` recorded for it. |
| `session-cache` | LINDDUN identifying | controlled | It maps `session-id` to a shopper id, which is identification within our own system rather than a pseudonym being broken. The identifiers never leave `prod-vpc`. |
| `session-cache` | LINDDUN non repudiation | not_applicable | Nothing here is evidence of an action. A session id expiring in thirty minutes cannot be used to hold anybody to a claim. |
| `session-cache` | LINDDUN detecting | not_applicable | Reachable only by the Checkout API service role inside `prod-vpc`, with no response path to an observer. Timing observable from outside belongs to the flows and to `checkout-api`. |
| `session-cache` | LINDDUN data disclosure | controlled | It holds `session-id` and `cart` and neither `email` nor `address`, which is the minimisation a session needs. The 30-minute TTL bounds the duration as well as the content. |
| `session-cache` | LINDDUN non compliance | controlled | Both items carry a `lawful_basis` of legitimate interests and a 30-minute retention that the TTL actually enforces, which is the rare case of a stated retention implemented by the mechanism rather than by a job that might not run. |

### Flows

| Element | Category | Verdict | Reason |
| :--- | :--- | :--- | :--- |
| `browse` | STRIDE tampering | controlled | The cart is built inside `trust_zone: browser`, so the shopper can set it to anything; `checkout-web.authz` records that every decision is re-made server-side, and `checkout-api.authz` re-checks on the way in. |
| `browse` | STRIDE information disclosure | not_applicable | `encryption_in_transit` is "n/a — never leaves the browser". There is no channel to intercept; the data is already on the observer's own machine. |
| `browse` | STRIDE denial of service | not_applicable | An in-page interaction a shopper can only deny to themselves. |
| `browse` | LINDDUN linking | controlled | `cart` is pseudonymous and stays in the page until checkout. The linkage to a person happens at `submit-order`, under the contract basis. |
| `browse` | LINDDUN identifying | not_applicable | Carries `cart` only, and `authn` is "n/a — anonymous until checkout". Nothing in the flow could identify anybody. |
| `browse` | LINDDUN non repudiation | not_applicable | Nothing is recorded, signed or retained, so nothing here could be used to stop a shopper denying anything. |
| `browse` | LINDDUN detecting | not_applicable | Never leaves the browser, so there is no traffic or side effect from which an observer could deduce involvement. |
| `browse` | LINDDUN data disclosure | controlled | `cart` carries `lawful_basis: Legitimate interests` and a 30-minute retention. Building a cart is the minimum the transaction needs. |
| `browse` | LINDDUN non compliance | controlled | Pseudonymous data under a recorded legitimate-interests basis. That the shopper is never told is real and recorded against `checkout-web`, where a notice would have to live. |
| `tokenise-card` | STRIDE tampering | controlled | TLS 1.3 to Stripe with `authn` a publishable key. Tampering with a tokenisation request produces a token for the attacker's own card, which `charge` then fails to settle against our order. |
| `tokenise-card` | STRIDE information disclosure | controlled | This is the flow the model's first assumption rests on — "Card numbers never reach our servers; Stripe Elements tokenises in-browser" — so the card number is exposed to the browser and Stripe and to nothing of ours. TLS 1.3 covers the hop. |
| `tokenise-card` | STRIDE denial of service | controlled | Stripe's availability, not ours. `charge` failing is recorded against `checkout-api`, which is the process that depends on it. |
| `tokenise-card` | LINDDUN linking | controlled | `card-token` carries `notes: Meaningless without Stripe's vault, but links a shopper to a payment instrument`. The linkage is Stripe's to make and is what settling a payment requires. |
| `tokenise-card` | LINDDUN identifying | not_applicable | `card-token` is `personal_data: pseudonymous` with `examples: tok_1A2b3C` and is meaningless without Stripe's vault, which we have no access to. Nothing in this flow can be resolved to a person by us or by an observer. |
| `tokenise-card` | LINDDUN non repudiation | controlled | A token is not evidence of a purchase; `charge-result` and the audit log are. Non-repudiation of payment is Stripe's record and ours jointly. |
| `tokenise-card` | LINDDUN detecting | controlled | An observer on the shopper's network sees a request to Stripe, which reveals that they are paying for something somewhere. TLS 1.3 with SNI is the state of the art available; the destination being observable is a property of the internet rather than of this design. |
| `tokenise-card` | LINDDUN data disclosure | controlled | Carries only `card-token`. Routing the card number around our servers entirely is the strongest minimisation in the model. |
| `tokenise-card` | LINDDUN non compliance | controlled | `card-token` records `retention: Not stored; passed through and discarded` under a contract basis, and Stripe is named in scope as a third-party service rather than left implicit. |
| `submit-order` | STRIDE tampering | controlled | The model's most sensitive boundary crossing — `browser` to `prod-vpc` with `cart`, `address`, `email` and `card-token` — and the one with the most recorded: TLS 1.3, a SameSite=Lax session cookie, a CSRF token, and row-level ownership re-checked in `checkout-api.authz`. |
| `submit-order` | STRIDE information disclosure | controlled | TLS 1.3 on the wire. What the shopper's own browser can see of their own order is not disclosure; what an error report might carry is recorded against `checkout-web`. |
| `submit-order` | LINDDUN linking | controlled | This is where `cart` stops being pseudonymous and becomes linked to a person, exactly as `cart.notes` describes. It is the transaction, under a recorded contract basis. |
| `submit-order` | LINDDUN identifying | controlled | `email` and `address` arrive identified, from the person they belong to. For a guest, that the address is unverified is the `shopper` spoofing finding rather than an identification threat. |
| `submit-order` | LINDDUN non repudiation | controlled | The order this creates is deliberately non-repudiable for tax purposes — `order` carries a 7-year retention — and `audit-write` records it. |
| `submit-order` | LINDDUN detecting | controlled | One HTTPS POST among many to the same host. An observer learns that somebody bought something, not who or what. |
| `submit-order` | LINDDUN data disclosure | controlled | Four items, each needed: `cart` and `card-token` to charge, `address` to deliver, `email` to confirm. Each carries a `lawful_basis` in the dictionary. |
| `submit-order` | LINDDUN non compliance | controlled | Collection under the contract basis recorded for every item it carries. The absent notice is recorded against `checkout-web`, and retention against the store that keeps it. |
| `charge` | STRIDE tampering | controlled | TLS 1.3 with `authn` a restricted secret key rotated quarterly, from `prod-vpc` where `access_control` keeps the key out of reach. |
| `charge` | STRIDE information disclosure | controlled | Carries `card-token` and `order`, never a card number — the model's first assumption. A restricted key limits what a leaked credential could read back from Stripe. |
| `charge` | STRIDE denial of service | controlled | Stripe's availability. What it costs us when unthrottled is recorded against `checkout-api` and `submit-order`. |
| `charge` | LINDDUN linking | controlled | Joins `card-token` to `order`, which is settling a payment. The linkage lives in Stripe's vault under our contract with them. |
| `charge` | LINDDUN identifying | controlled | `order` is identified data going to a named processor in scope. Stripe necessarily learns who is paying; that is what a payment processor does. |
| `charge` | LINDDUN non repudiation | controlled | A settled charge is meant to be undeniable by both parties. That is the purpose of the record, and `charge-result` arrives signed. |
| `charge` | LINDDUN detecting | controlled | Server-to-server inside TLS 1.3, from a VPC with no inbound path. An observer sees our traffic to Stripe in aggregate, not a person in it. |
| `charge` | LINDDUN data disclosure | controlled | Two items, both required to settle. No `address` and no `email` are sent to Stripe, which is more minimisation than the integration needed. |
| `charge` | LINDDUN non compliance | controlled | Stripe is declared in scope as a third-party service with its own trust zone and `controlled_by: third_party`, so the transfer is modelled rather than hidden inside a process. |
| `charge-result` | STRIDE tampering | controlled | `authn` is webhook signature verification, which is precisely the control for an inbound claim from a third party. Without it anybody could assert that an order was paid. |
| `charge-result` | STRIDE information disclosure | controlled | TLS 1.3, carrying `order` only. Nothing about the payment instrument comes back. |
| `charge-result` | STRIDE denial of service | controlled | A webhook endpoint is a public surface, but signature verification rejects unsigned traffic before it reaches any order logic. The cost of a flood is recorded against `checkout-api`. |
| `charge-result` | LINDDUN linking | controlled | Returns an outcome against an `order` we already hold. No new linkage is created by it. |
| `charge-result` | LINDDUN identifying | controlled | `order` is already identified on our side. The response adds a payment outcome, not an identity. |
| `charge-result` | LINDDUN non repudiation | controlled | Signed by Stripe, which is what makes the settlement provable. Deliberate. |
| `charge-result` | LINDDUN detecting | controlled | Inbound to `prod-vpc` over TLS 1.3. An observer of the webhook endpoint learns that charges happen, which is true of every shop. |
| `charge-result` | LINDDUN data disclosure | controlled | One item inbound. Nothing personal is disclosed to anyone by a result arriving. |
| `charge-result` | LINDDUN non compliance | controlled | Part of the modelled Stripe relationship, under the contract basis `order` records. |
| `persist-order` | STRIDE tampering | controlled | `encryption_in_transit` is TLS verify-full, which authenticates the database rather than merely encrypting to it, and `authn` is IAM database authentication rather than a password that could be replayed. |
| `persist-order` | STRIDE information disclosure | controlled | Inside `prod-vpc` with verify-full TLS. The disclosure risk for this data is at rest and in the snapshots, recorded against `orders-db`. |
| `persist-order` | STRIDE denial of service | controlled | Synchronous on the order path, so exhausting it means exhausting `submit-order`, where the unthrottled entry point is recorded. |
| `persist-order` | LINDDUN linking | controlled | Writes `order`, `address` and `email` as one shopper's record, which is the linkage the contract basis covers. |
| `persist-order` | LINDDUN identifying | controlled | Identified data written to a store that holds it identified, deliberately and with `email.notes` explaining why it cannot be pseudonymised. |
| `persist-order` | LINDDUN non repudiation | controlled | Creates the 7-year tax record. Undeniability is the obligation. |
| `persist-order` | LINDDUN detecting | not_applicable | Service to store inside `prod-vpc`, with no path from which an outsider could observe it at all. |
| `persist-order` | LINDDUN data disclosure | controlled | Writes exactly what the order needs. The question of how long it stays is `orders-db`'s, and is recorded there as a finding. |
| `persist-order` | LINDDUN non compliance | controlled | Each item written carries a recorded basis. The storage-limitation finding belongs to the store, not to the write. |
| `session-write` | STRIDE tampering | controlled | `authn` is Redis AUTH plus a security group, and `session-cache`'s `access_control` admits only the Checkout API service role. Worth noting that `encryption_in_transit` is TLS 1.2 where every other hop in the model is 1.3 — not broken, but the only path below the floor the rest of the system sets. |
| `session-write` | STRIDE information disclosure | controlled | TLS 1.2 inside `prod-vpc`, carrying `session-id` and `cart` and neither `email` nor `address`. The weakest transport in the model carries the least sensitive payload, which is the right way round. |
| `session-write` | STRIDE denial of service | controlled | Filling the cache is bounded by the 30-minute TTL. What happens when it does fill or restart is recorded against `session-cache`. |
| `session-write` | LINDDUN linking | controlled | Writing `session-id` against a shopper is the linkage `session-id.notes` calls a classic linkability vector, bounded by the TTL recorded on the store. |
| `session-write` | LINDDUN identifying | controlled | Maps a pseudonymous identifier to an internal shopper id inside our own boundary. No identity is revealed to anybody by it. |
| `session-write` | LINDDUN non repudiation | not_applicable | A 30-minute session record is not evidence. Attribution comes from the audit log. |
| `session-write` | LINDDUN detecting | not_applicable | Service to cache inside `prod-vpc`, unobservable from outside. |
| `session-write` | LINDDUN data disclosure | controlled | Two items, both needed to continue a session, neither of them an identifier of a person on its own. |
| `session-write` | LINDDUN non compliance | controlled | Legitimate interests recorded for both items, with a retention the TTL enforces mechanically. |
| `session-read` | STRIDE tampering | controlled | Same channel as `session-write` — Redis AUTH, security group, TLS 1.2 — and `checkout-api.authz` re-checks ownership on whatever the session claims, so a tampered session cannot reach another shopper's order. |
| `session-read` | STRIDE information disclosure | controlled | Returns the session's own `cart` inside `prod-vpc`. Cross-session reads are prevented by the key being the session id and by the ownership re-check on use. |
| `session-read` | STRIDE denial of service | controlled | A miss returns nothing rather than failing, which is why what `checkout-api` does with an empty result matters — recorded against `session-cache`. |
| `session-read` | LINDDUN linking | controlled | Resolving a session to a shopper is the linkage the session exists for, bounded by the TTL. |
| `session-read` | LINDDUN identifying | controlled | Internal resolution of a pseudonym we issued, inside our own boundary. |
| `session-read` | LINDDUN non repudiation | not_applicable | Reading working state creates no evidence about anybody. |
| `session-read` | LINDDUN detecting | not_applicable | Cache to service inside `prod-vpc`, with no externally observable behaviour. |
| `session-read` | LINDDUN data disclosure | controlled | Returns only what was written: `session-id` and `cart`. |
| `session-read` | LINDDUN non compliance | controlled | Same recorded basis and TTL-enforced retention as the write. |
| `audit-write` | STRIDE tampering | controlled | TLS 1.3 with an IAM role to an append-only store with object lock, so an event cannot be altered after it lands. A compromised `checkout-api` could write false events but not remove true ones. |
| `audit-write` | STRIDE information disclosure | controlled | TLS 1.3 inside `prod-vpc`, and the writer holds write-only access per `audit-log.access_control`, so this path cannot be turned around to read the history. |
| `audit-write` | STRIDE denial of service | controlled | Cross-region replication on the store side. A flood of events requires compromising the writer, which is that process's finding. |
| `audit-write` | LINDDUN linking | controlled | `audit-event` links an action to an order and a person under a recorded legal-obligation basis. That is the record's purpose. |
| `audit-write` | LINDDUN identifying | controlled | Carries `audit-event` and not `email`; identification is by internal order reference on this path. Contrast `support-audit`, which does carry the address and is recorded against the store. |
| `audit-write` | LINDDUN non repudiation | controlled | Creating non-repudiable records is the point, and `audit-event.notes` records that the cost is accepted on purpose. |
| `audit-write` | LINDDUN detecting | not_applicable | Service to store inside `prod-vpc`. No external observer of this hop exists. |
| `audit-write` | LINDDUN data disclosure | controlled | One item, and notably not `email`. The audit path that does carry an address is `support-audit`, and the consequence is recorded against `audit-log`. |
| `audit-write` | LINDDUN non compliance | controlled | Legal obligation recorded as the basis, with a 2-year retention on the store. Whether that retention conflicts with erasure is recorded against `audit-log`. |
| `order-response` | STRIDE tampering | controlled | TLS 1.3 with the session cookie. A tampered response misleads only the shopper's own page; the order itself is whatever `orders-db` holds. |
| `order-response` | STRIDE information disclosure | controlled | Returns the shopper's own `order` over TLS 1.3, scoped by the row-level ownership checks in `checkout-api.authz`. |
| `order-response` | STRIDE denial of service | controlled | A response on an existing request. Availability is the API's, recorded there. |
| `order-response` | LINDDUN linking | controlled | Returns one order to the person who placed it. No new linkage. |
| `order-response` | LINDDUN identifying | controlled | Identified data returned to the person it identifies. |
| `order-response` | LINDDUN non repudiation | controlled | A confirmation is evidence for the shopper as much as against them, and the authoritative record is the audit log. |
| `order-response` | LINDDUN detecting | controlled | One TLS 1.3 response among many. Response size could in principle distinguish a completed order from a rejected one, which is the same question recorded against `checkout-api` under detecting. |
| `order-response` | LINDDUN data disclosure | controlled | One item, to its own subject. |
| `order-response` | LINDDUN non compliance | controlled | Contract basis, and confirming an order is part of performing it. |
| `render-confirmation` | STRIDE tampering | not_applicable | `encryption_in_transit` is "n/a — never leaves the browser". The shopper can rewrite their own page; the order is whatever `orders-db` holds. |
| `render-confirmation` | STRIDE information disclosure | not_applicable | Shows the shopper their own order on their own device. There is no channel and no second party. |
| `render-confirmation` | STRIDE denial of service | not_applicable | In-page rendering, deniable only to oneself. |
| `render-confirmation` | LINDDUN linking | controlled | One order shown to the person who placed it. No linkage is created. |
| `render-confirmation` | LINDDUN identifying | controlled | Identified data shown to its own subject — except where the subject is wrong, which is the guest verification finding on `shopper`. |
| `render-confirmation` | LINDDUN non repudiation | not_applicable | A rendered page retains nothing and proves nothing. |
| `render-confirmation` | LINDDUN detecting | not_applicable | Never leaves the browser; nothing observable. |
| `render-confirmation` | LINDDUN data disclosure | controlled | One item, to its own subject, on their own device. |
| `render-confirmation` | LINDDUN non compliance | controlled | Contract basis; confirming an order is performing it. |
| `poll-orders` | STRIDE tampering | controlled | TLS verify-full with IAM database authentication and a read-only role, so the worker cannot alter what it polls. |
| `poll-orders` | STRIDE information disclosure | controlled | Inside `prod-vpc`, verify-full TLS, carrying `order` and `address` under a role scoped to paid orders. |
| `poll-orders` | STRIDE denial of service | controlled | `trigger: scheduled` with a read-only role; polling cannot be induced from outside, and its load is predictable. |
| `poll-orders` | LINDDUN linking | controlled | One order and its delivery address, which is the linkage delivery requires. |
| `poll-orders` | LINDDUN identifying | controlled | A parcel needs a named recipient at an address. Identification is the function. |
| `poll-orders` | LINDDUN non repudiation | controlled | Dispatch is recorded in `audit-log` by `fulfilment-audit`, attributing a system action rather than binding a shopper to a claim. |
| `poll-orders` | LINDDUN detecting | not_applicable | Store to service inside `prod-vpc`, with no inbound path to the worker at all. |
| `poll-orders` | LINDDUN data disclosure | controlled | Carries `order` and `address` and deliberately not `email`: a picker needs somewhere to send the parcel, not a way to contact the buyer. |
| `poll-orders` | LINDDUN non compliance | controlled | Contract basis for both items. The warehouse beyond is declared out of scope as a consumer of orders rather than left unmodelled. |
| `fulfilment-audit` | STRIDE tampering | controlled | TLS 1.3, IAM role, append-only destination with object lock. |
| `fulfilment-audit` | STRIDE information disclosure | controlled | Write-only access to the log, so the path cannot be reversed to read it. |
| `fulfilment-audit` | STRIDE denial of service | controlled | One event per dispatched order, bounded by order volume. |
| `fulfilment-audit` | LINDDUN linking | controlled | Links a dispatch to an order under the legal-obligation basis `audit-event` records. |
| `fulfilment-audit` | LINDDUN identifying | controlled | Carries `audit-event` only; identification is by order reference. |
| `fulfilment-audit` | LINDDUN non repudiation | controlled | Deliberate, and recorded as an accepted cost in `audit-event.notes`. |
| `fulfilment-audit` | LINDDUN detecting | not_applicable | Service to store inside `prod-vpc`, unobservable from outside. |
| `fulfilment-audit` | LINDDUN data disclosure | controlled | One item, and not the address it just handled. |
| `fulfilment-audit` | LINDDUN non compliance | controlled | Legal-obligation basis; the retention conflict is recorded against `audit-log`. |
| `support-lookup` | STRIDE tampering | controlled | TLS 1.3 with an Okta SSO session and WebAuthn, and the model's assumption that network position grants nothing means a tampered request still needs the session. |
| `support-lookup` | STRIDE information disclosure | controlled | Carries `email` from `corp-net` to `prod-vpc` over TLS 1.3. The search term is the least of what the console then shows, which is recorded on `support-render`. |
| `support-lookup` | STRIDE denial of service | controlled | Behind the SSO proxy with WebAuthn, so there is no anonymous request to flood it with. |
| `support-lookup` | LINDDUN linking | controlled | One lookup of one shopper by an identified agent, recorded with a reason in the audit log. |
| `support-lookup` | LINDDUN identifying | controlled | An agent answering a query about an order has to name the shopper. That is the function. |
| `support-lookup` | LINDDUN non repudiation | controlled | The agent's non-repudiation is deliberate per `audit-event.notes`, and it is what makes support access auditable at all. |
| `support-lookup` | LINDDUN detecting | controlled | Only authenticated agents can send it anything, so there is no unauthenticated response an outsider could read existence from. |
| `support-lookup` | LINDDUN data disclosure | controlled | One item as a search term. What comes back is the disclosure worth arguing about, and it is recorded against `support-console` and `support-render`. |
| `support-lookup` | LINDDUN non compliance | controlled | Every lookup is logged with a stated reason, which is what an audit of support access asks to see. |
| `support-read` | STRIDE tampering | controlled | Verify-full TLS, IAM database authentication, read-only role. The console cannot alter an order even if an agent tried. |
| `support-read` | STRIDE information disclosure | controlled | Inside `prod-vpc` under a read-only role. That the full record including `address` crosses into the console is the disclosure decision, recorded against `support-console`. |
| `support-read` | STRIDE denial of service | controlled | Reads are per lookup, and lookups need an authenticated agent. |
| `support-read` | LINDDUN linking | controlled | Returns one shopper's order, address and email together, which is the record as stored. |
| `support-read` | LINDDUN identifying | controlled | Identified data, read for the purpose of answering that person's query. |
| `support-read` | LINDDUN non repudiation | controlled | The read is recorded against the agent, which is the deliberate staff non-repudiation. |
| `support-read` | LINDDUN detecting | not_applicable | Store to service inside `prod-vpc`; nothing observable externally. |
| `support-read` | LINDDUN data disclosure | controlled | Reads all three items because an agent may need any of them; the narrowing happens at the display, where masking applies, and the weakness in that masking is recorded against `support-console`. |
| `support-read` | LINDDUN non compliance | controlled | Contract basis, read under a logged and reasoned access. |
| `support-render` | STRIDE tampering | controlled | TLS 1.3 with an Okta SSO session. Tampering with what an agent sees changes no record; the store is read-only to this path. |
| `support-render` | STRIDE denial of service | controlled | A response to an authenticated request; availability is the console's. |
| `support-render` | LINDDUN linking | controlled | Shows one shopper's record to one agent, with the lookup logged. |
| `support-render` | LINDDUN identifying | controlled | Identification is the purpose of a support lookup. |
| `support-render` | LINDDUN non repudiation | controlled | The viewing is recorded against the agent, deliberately. |
| `support-render` | LINDDUN detecting | controlled | Visible only to an authenticated agent inside the SSO estate. |
| `support-render` | LINDDUN data disclosure | controlled | `notes` records that the address is masked unless the view is linked to an open ticket. That the agent controls both ends of that condition is recorded as a finding against `support-console`. |
| `support-render` | LINDDUN non compliance | controlled | Access logged with a reason, address masked by default. The residual risks are recorded on the console and on this flow's disclosure finding. |
| `support-audit` | STRIDE tampering | controlled | TLS 1.3, IAM role, append-only destination with object lock. |
| `support-audit` | STRIDE information disclosure | controlled | Write-only into the log; the path cannot be reversed to read history. |
| `support-audit` | STRIDE denial of service | controlled | One event per lookup, and lookups require an authenticated agent. |
| `support-audit` | LINDDUN linking | controlled | Links an agent to a shopper's record, which is the accountability the log exists for. |
| `support-audit` | LINDDUN identifying | controlled | Carries `email` as well as `audit-event`, so the entry names the shopper rather than an internal reference. That is deliberate for a support audit; what it costs in retention is recorded against `audit-log`. |
| `support-audit` | LINDDUN non repudiation | controlled | Deliberate for staff, per `audit-event.notes`. |
| `support-audit` | LINDDUN detecting | not_applicable | Service to store inside `prod-vpc`, unobservable from outside. |
| `support-audit` | LINDDUN data disclosure | controlled | This is the flow that puts `email` into a store that keeps it for two years, past the address's own stated retention. Recorded as a finding where the duration lives, against `audit-log`; the flow itself carries only what the audit entry needs to be meaningful. |
| `support-audit` | LINDDUN non compliance | controlled | Legal-obligation basis. The erasure conflict it contributes to is recorded against `audit-log`. |
| `assist-request` | STRIDE tampering | controlled | TLS 1.3 and an IAM role between two processes in `prod-vpc`. `notes` records that the shopper's message crosses into the prompt unaltered, which is what the flow is for; that the receiving process cannot tell an instruction from data is recorded against `support-assistant` under elevation of privilege. |
| `assist-request` | STRIDE information disclosure | controlled | TLS 1.3 inside the VPC, IAM role on both ends. What this flow hands over is the data disclosure verdict below; what the assistant does with it is recorded against `support-assistant`. |
| `assist-request` | STRIDE denial of service | controlled | One call per draft, and `authn` requires the console's own agent session behind SSO. |
| `assist-request` | LINDDUN linking | controlled | One order per call, and `support-assistant.tech` keeps no state between tickets, so nothing is joined across them. |
| `assist-request` | LINDDUN identifying | controlled | `order` and `address` are identified data by the model's own classification, and the ticket is about that one shopper. |
| `assist-request` | LINDDUN non repudiation | controlled | Deliberate, per `audit-event.notes`; the prompt this flow carries is recorded by `assist-audit`. |
| `assist-request` | LINDDUN detecting | not_applicable | Process to process inside `prod-vpc`, unobservable from outside. |
| `assist-request` | LINDDUN data disclosure | controlled | Narrower than `support-read`, which carries `order`, `address` and `email`: the identifier is left behind because the assistant has no use for it. DD.3.2 would need data to travel further than the function requires, and this flow was cut to the function. |
| `assist-request` | LINDDUN non compliance | controlled | Same `lawful_basis: Contract` the source data already carries, and `shopper-message` states a retention that matches the ticket it belongs to. |
| `assist-draft` | STRIDE tampering | controlled | TLS 1.3 and an IAM role inside the VPC. The console does not treat what comes back as markup either — `support-assistant.output_handling` renders the draft as plain text, never as HTML. |
| `assist-draft` | STRIDE information disclosure | controlled | TLS 1.3 inside the VPC. That the draft can contain a masked address is recorded against `support-assistant`, where the decision to include it is made. |
| `assist-draft` | STRIDE denial of service | controlled | One response per request; losing it costs a draft, not the ticket. |
| `assist-draft` | LINDDUN linking | controlled | Carries one draft about one order and nothing that joins tickets. |
| `assist-draft` | LINDDUN identifying | controlled | `draft-reply` is a statement about the shopper whose ticket it answers; naming them back to themselves is the point. |
| `assist-draft` | LINDDUN non repudiation | controlled | Deliberate, per `audit-event.notes`; recorded by `assist-audit`. |
| `assist-draft` | LINDDUN detecting | not_applicable | Process to process inside `prod-vpc`, unobservable from outside. |
| `assist-draft` | LINDDUN data disclosure | controlled | One draft, to the console that asked for it, kept for as long as the ticket per `draft-reply.retention`. It goes no further without an agent pressing send. |
| `assist-draft` | LINDDUN non compliance | controlled | `support-assistant.output_handling` means nothing generated reaches a shopper unreviewed, so a wrong statement is caught by a person before it becomes something to rectify. |
| `assist-audit` | STRIDE tampering | controlled | TLS 1.3, IAM role, append-only destination with object lock. |
| `assist-audit` | STRIDE information disclosure | controlled | Write-only into the log; the path cannot be reversed to read history. |
| `assist-audit` | STRIDE denial of service | controlled | One event per draft, and a draft requires an authenticated agent. |
| `assist-audit` | LINDDUN linking | controlled | Links an agent, a shopper's order and a prompt, which is the accountability the log exists for. |
| `assist-audit` | LINDDUN identifying | controlled | Carries `audit-event` only, so the entry names the order rather than restating the shopper's address. What the log's retention costs is recorded against `audit-log`. |
| `assist-audit` | LINDDUN non repudiation | controlled | Deliberate for staff, per `audit-event.notes`. |
| `assist-audit` | LINDDUN detecting | not_applicable | Service to store inside `prod-vpc`, unobservable from outside. |
| `assist-audit` | LINDDUN data disclosure | controlled | Carries only what the audit entry needs to be meaningful. The prompt text it references includes `shopper-message`, so what two-year retention costs is recorded against `audit-log` with the rest of the log's duration finding. |
| `assist-audit` | LINDDUN non compliance | controlled | Legal-obligation basis, same as the other audit writes. The erasure conflict it contributes to is recorded against `audit-log`. |
| `dsar-request` | STRIDE tampering | controlled | TLS 1.3, and `authz` on the handler is a two-person rule for erasure, so a tampered request cannot by itself destroy anything. |
| `dsar-request` | STRIDE information disclosure | controlled | Carries `email` inbound over TLS 1.3. What goes back out is `dsar-export`, and the verification it depends on is recorded as a finding against `dsar-handler`. |
| `dsar-request` | STRIDE denial of service | controlled | `trigger: user_action` but every run is manual and approved, so volume costs human time rather than availability. |
| `dsar-request` | LINDDUN linking | controlled | A person asking about their own data necessarily links themselves to it. |
| `dsar-request` | LINDDUN identifying | controlled | Identification is the prerequisite: an unidentified request cannot be answered safely. Whether it is identification enough is the spoofing finding on `dsar-handler`. |
| `dsar-request` | LINDDUN non repudiation | controlled | `dsar-handler.logging` records every request and approval, which is what makes the response defensible to a regulator. |
| `dsar-request` | LINDDUN detecting | controlled | A request is submitted before any response exists. Whether a reply distinguishes a known address from an unknown one is recorded against `checkout-api`. |
| `dsar-request` | LINDDUN non compliance | controlled | Having a route for access and erasure at all is what compliance asks first. The two failures of that route — gift recipients with no path, and guests who cannot prove identity — are recorded against `dsar-handler`. |
| `dsar-read` | STRIDE tampering | controlled | Verify-full TLS with IAM database authentication, and `authn` restricts it to an approved run rather than to anyone holding the role. |
| `dsar-read` | STRIDE information disclosure | controlled | The broadest read in the model, and the one most tightly gated: approved run only, `trigger: manual`, inside `prod-vpc`. |
| `dsar-read` | STRIDE denial of service | controlled | Manual and approved, so it cannot be induced at volume. |
| `dsar-read` | LINDDUN linking | controlled | Assembling everything held about one person is what a subject access request is. |
| `dsar-read` | LINDDUN identifying | controlled | Works from an identified `email` the requester supplied. |
| `dsar-read` | LINDDUN non repudiation | controlled | The run is recorded with its approver, which is the audit an access request needs. |
| `dsar-read` | LINDDUN detecting | not_applicable | Store to service inside `prod-vpc`; nothing externally observable. |
| `dsar-read` | LINDDUN data disclosure | controlled | Reads everything held, because that is the request. It reads only `orders-db`, though — the `email` held in `audit-log` is not assembled, which is the completeness finding recorded there. |
| `dsar-read` | LINDDUN non compliance | controlled | Serving access requests is the obligation. That the export is incomplete by construction is recorded against `audit-log`. |
| `dsar-export` | STRIDE tampering | controlled | `authn` is a one-time link tied to the verified identity with a 72-hour expiry, over TLS 1.3. A link that has been used cannot be re-used. |
| `dsar-export` | STRIDE information disclosure | controlled | An expiring signed download link is the right shape for this, and it is as strong as the identity it is tied to — which is the spoofing finding against `dsar-handler`. The 72-hour window means the link outlives the request in whatever inbox received it, bounded by being one-time. |
| `dsar-export` | STRIDE denial of service | controlled | One link per approved run. |
| `dsar-export` | LINDDUN linking | controlled | Delivers one person's own record to them. |
| `dsar-export` | LINDDUN identifying | controlled | The link is tied to the verified identity, so identification is the control rather than the risk. |
| `dsar-export` | LINDDUN non repudiation | controlled | The export is logged, which is how we can show the request was answered. |
| `dsar-export` | LINDDUN detecting | controlled | A signed link reveals nothing to an observer who cannot open it, and it is single-use. |
| `dsar-export` | LINDDUN data disclosure | controlled | Discloses everything, to the person it is about. Sending less would fail the request rather than minimise it. |
| `dsar-export` | LINDDUN non compliance | controlled | Delivering the export completes the obligation `dsar-request` opened. Its incompleteness is recorded against `audit-log`. |

## Carried forward from the model

### Open questions

- Nobody could confirm whether the nightly database snapshots are covered by the 90-day address purge, or whether they retain addresses for 35 days past it.

### Assumptions

- Card numbers never reach our servers; Stripe Elements tokenises in-browser.
- The corporate network is not trusted; the support console authenticates every request regardless of network position.

## Limits

**Coverage is mechanically checkable; seriousness is not.** Every pairing here has a verdict, which is what the script can prove. That any of them was answered seriously is not something a script can establish, and a complete enumeration of shallow dismissals would satisfy every check that produced this document.

**This is analysis of a model, not of a system.** Every finding rests on the model being an accurate description, and on the assumptions carried forward above. Where the system and the model differ, this document describes the model.

<!-- vector: rendered from example.threats.yaml sha256:bb75b14e00c571f724b9539975dd7de10a3ac6f0983bccaf4d59d9f00d81ccf9 -->
