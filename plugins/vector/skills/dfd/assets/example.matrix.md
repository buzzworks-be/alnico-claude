# Threat matrix — Acme Checkout

Generated from the register beside [`example.threats.yaml`](example.threats.yaml) by `render_matrix.py`, as of 2026-09-13. Do not edit; regenerate.

## Summary

| | Vectors |
| :--- | ---: |
| Tracked | 14 |
| Mitigated | 7 |
| Accepted | 2 |
| Deferred | 5 |
| Undecided | 0 |
| Carrying no mitigation | 3 |

## Deferrals, soonest first

What has been decided and not done, with who owns it and until when. A deferral past its date fails the check; a date that has been moved shows every date it has had.

| Vector | Until | Owner | Mitigation | Reason |
| :--- | :--- | :--- | :--- | :--- |
| [**VEC-0005**](example.vectors.md#vec-0005--nobody-could-say-whether-the-backup-snapshots-honour-the-address-purge) Nobody could say whether the backup snapshots honour the address purge | 2026-10-31 | Ruben De Smet, platform lead | — | Nothing can be mitigated or accepted until the question is answered: whether the purge reaches the snapshots is a fact about the backup job that nobody in the room could state. The owner is finding out, and the answer decides which of the other two states this becomes. |
| [**VEC-0009**](example.vectors.md#vec-0009--verifying-a-guest-collects-identity-documents-the-model-does-not-know-it-holds) Verifying a guest collects identity documents the model does not know it holds | 2026-11-30 | Ines Verhaeghe, privacy lead | [`MIT-0007`](#mit-0007--identity-documents-are-modelled-held-once-and-deleted-thirty-days-after-the-request-closes) | The document is now a modelled data item with a retention and a deletion job in the specification, and the job does not exist. Until it does, the privacy inbox's own retention rule is the only control, and it was not written with identity documents in mind. |
| [**VEC-0004**](example.vectors.md#vec-0004--the-audit-log-keeps-email-past-its-own-retention-beyond-erasures-reach) The audit log keeps email past its own retention, beyond erasure's reach | 2026-12-31 | Ines Verhaeghe, privacy lead | [`MIT-0003`](#mit-0003--audit-events-carry-the-shopper-id-not-the-email-address) | The decision the vector asked for has been made — audit events will carry the shopper id rather than the address, and the event itself is the stated exception to erasure — and the migration that makes it true of the existing two years of events is not done. Carried until it is. |
| [**VEC-0012**](example.vectors.md#vec-0012--a-shoppers-own-words-reach-the-prompt-of-a-process-that-can-move-money) A shopper's own words reach the prompt of a process that can move money | 2027-01-31 (2027.1 — support console release) | Maya Okonkwo, support engineering lead | [`MIT-0010`](#mit-0010--the-assistant-proposes-a-refund-an-agent-issues-it) | The proposal flow is specified and is a product change rather than a patch: the console needs a confirmation step, the payment path needs to stop accepting a tool call, and the rejection log needs somewhere to go. It lands with the support console's next release. Until then the tool issues refunds under the EUR 50 cap and the exposure is carried here. |
| [**VEC-0001**](example.vectors.md#vec-0001--a-guests-identity-is-never-verified-at-checkout-or-on-a-data-request) A guest's identity is never verified, at checkout or on a data request | 2027-03-31 (2027.1 — guest path rework) | Ines Verhaeghe, privacy lead | [`MIT-0001`](#mit-0001--bind-the-guest-email-before-an-order-or-a-data-request-is-accepted) | The control is designed and written into the specification, and it is not built: guest verification lands with the partner-onboarding work that reworks the guest path, rather than ahead of it. Until then the exposure is real on both paths and is carried under this date. |

## The matrix

| Vector | Element | Category | Disposition | Owner | Mitigations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [**VEC-0010**](example.vectors.md#vec-0010--nothing-in-the-model-tells-a-shopper-what-is-collected-or-on-what-basis) Nothing in the model tells a shopper what is collected or on what basis | `checkout-web` Checkout web app | LINDDUN unawareness | mitigated | — | [`MIT-0008`](#mit-0008--the-checkout-page-links-a-privacy-notice-generated-from-the-models-data-entries) |
| [**VEC-0011**](example.vectors.md#vec-0011--pii-scrubbing-on-client-error-reports-is-a-filter-that-fails-open) PII scrubbing on client error reports is a filter that fails open | `checkout-web` Checkout web app | STRIDE information disclosure | mitigated | — | [`MIT-0009`](#mit-0009--a-test-fails-when-a-known-pii-shape-reaches-the-error-reporter) |
| [**VEC-0003**](example.vectors.md#vec-0003--the-order-path-has-no-throttle-anywhere-in-the-model) The order path has no throttle anywhere in the model | `checkout-api` Checkout API | STRIDE denial of service | mitigated | — | [`MIT-0002`](#mit-0002--rate-limit-submit-order-before-any-downstream-cost) |
| [**VEC-0007**](example.vectors.md#vec-0007--address-masking-in-the-support-console-is-lifted-by-the-agent-who-wants-it) Address masking in the support console is lifted by the agent who wants it | `support-console` Support console | LINDDUN data disclosure | mitigated | — | [`MIT-0004`](#mit-0004--a-ticket-linked-view-needs-a-ticket-the-shopper-opened-checked-server-side), [`MIT-0005`](#mit-0005--support-lookups-are-sampled-and-reviewed-monthly) |
| [**VEC-0012**](example.vectors.md#vec-0012--a-shoppers-own-words-reach-the-prompt-of-a-process-that-can-move-money) A shopper's own words reach the prompt of a process that can move money | `support-assistant` Support assistant | STRIDE elevation of privilege | deferred | Maya Okonkwo, support engineering lead | [`MIT-0010`](#mit-0010--the-assistant-proposes-a-refund-an-agent-issues-it) |
| [**VEC-0013**](example.vectors.md#vec-0013--an-assistants-draft-can-restate-an-address-the-console-masked) An assistant's draft can restate an address the console masked | `support-assistant` Support assistant | STRIDE information disclosure | mitigated | — | [`MIT-0011`](#mit-0011--send-the-assistant-the-address-only-when-the-agent-may-already-see-it) |
| [**VEC-0014**](example.vectors.md#vec-0014--nobody-tells-the-shopper-a-model-read-their-message-and-wrote-the-reply) Nobody tells the shopper a model read their message and wrote the reply | `support-assistant` Support assistant | LINDDUN unawareness | mitigated | — | [`MIT-0008`](#mit-0008--the-checkout-page-links-a-privacy-notice-generated-from-the-models-data-entries) |
| [**VEC-0001**](example.vectors.md#vec-0001--a-guests-identity-is-never-verified-at-checkout-or-on-a-data-request) A guest's identity is never verified, at checkout or on a data request | `dsar-handler` Data request handler | STRIDE spoofing | deferred | Ines Verhaeghe, privacy lead | [`MIT-0001`](#mit-0001--bind-the-guest-email-before-an-order-or-a-data-request-is-accepted) |
| [**VEC-0002**](example.vectors.md#vec-0002--gift-recipients-are-data-subjects-the-system-cannot-inform-or-serve) Gift recipients are data subjects the system cannot inform or serve | `dsar-handler` Data request handler | LINDDUN non compliance | accepted | Ines Verhaeghe, privacy lead | — |
| [**VEC-0005**](example.vectors.md#vec-0005--nobody-could-say-whether-the-backup-snapshots-honour-the-address-purge) Nobody could say whether the backup snapshots honour the address purge | `orders-db` Orders database | LINDDUN non compliance | deferred | Ruben De Smet, platform lead | — |
| [**VEC-0006**](example.vectors.md#vec-0006--backups-add-no-isolation-from-the-compromise-that-matters) Backups add no isolation from the compromise that matters | `orders-db` Orders database | STRIDE information disclosure | accepted | Ruben De Smet, platform lead | — |
| [**VEC-0004**](example.vectors.md#vec-0004--the-audit-log-keeps-email-past-its-own-retention-beyond-erasures-reach) The audit log keeps email past its own retention, beyond erasure's reach | `audit-log` Audit log | LINDDUN non compliance | deferred | Ines Verhaeghe, privacy lead | [`MIT-0003`](#mit-0003--audit-events-carry-the-shopper-id-not-the-email-address) |
| [**VEC-0008**](example.vectors.md#vec-0008--the-full-order-record-lands-on-a-laptop-in-a-zone-the-model-calls-untrusted) The full order record lands on a laptop in a zone the model calls untrusted | `support-render` Show order to agent | STRIDE information disclosure | mitigated | — | [`MIT-0006`](#mit-0006--only-managed-compliant-devices-can-open-the-support-console) |
| [**VEC-0009**](example.vectors.md#vec-0009--verifying-a-guest-collects-identity-documents-the-model-does-not-know-it-holds) Verifying a guest collects identity documents the model does not know it holds | `dsar-request` Data subject access or erasure request | LINDDUN data disclosure | deferred | Ines Verhaeghe, privacy lead | [`MIT-0007`](#mit-0007--identity-documents-are-modelled-held-once-and-deleted-thirty-days-after-the-request-closes) |

## Mitigations

Each control, where its requirement is written, where it lives, and every vector it serves. A mitigation with a specification and no implementation is designed and not built; one with an implementation and no specification was found in the code rather than required of it.

### MIT-0001 — Bind the guest email before an order or a data request is accepted

A six-digit code is sent to the address and must be returned within fifteen minutes; five attempts per address and twenty per source address per hour. A guest who cannot complete it on a data request is told the alternative route, and the request is recorded as opened either way.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#guest-email-verification`](example.spec.md#guest-email-verification) |
| Implemented in | — |
| Verification | code |
| Serves | [`VEC-0001`](example.vectors.md#vec-0001--a-guests-identity-is-never-verified-at-checkout-or-on-a-data-request) |

### MIT-0002 — Rate-limit submit-order before any downstream cost

Ten orders per session and sixty per source address per hour, enforced at the API gateway in front of the checkout API, so a rejected request never reaches the database or Stripe.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#order-throttle`](example.spec.md#order-throttle) |
| Implemented in | `infra/gateway/rate-limits.yaml` |
| Verification | code |
| Serves | [`VEC-0003`](example.vectors.md#vec-0003--the-order-path-has-no-throttle-anywhere-in-the-model) |

### MIT-0003 — Audit events carry the shopper id, not the email address

Support-lookup audit events record the internal shopper id, which resolves to nothing after erasure. Existing events are rewritten once by a migration that reports what it could not resolve.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#audit-log-pseudonymisation`](example.spec.md#audit-log-pseudonymisation) |
| Implemented in | — |
| Verification | code |
| Serves | [`VEC-0004`](example.vectors.md#vec-0004--the-audit-log-keeps-email-past-its-own-retention-beyond-erasures-reach) |

### MIT-0004 — A ticket-linked view needs a ticket the shopper opened, checked server-side

The console unmasks an address only when the request names a ticket, the ticket exists, and its reporter is the order's shopper; the check runs in the support-console service, not the browser.

| | |
| :--- | :--- |
| Specified in | — |
| Implemented in | `src/support-console/views/order.ts` |
| Verification | code |
| Serves | [`VEC-0007`](example.vectors.md#vec-0007--address-masking-in-the-support-console-is-lifted-by-the-agent-who-wants-it) |

### MIT-0005 — Support lookups are sampled and reviewed monthly

A named reviewer outside the support team samples at least twenty lookups a month from the audit log, weighted to the agents with the most, and checks each against the ticket it names.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#support-lookup-review`](example.spec.md#support-lookup-review) |
| Implemented in | — |
| Verification | manual |
| Evidence | Signed monthly review, sample and exceptions in the compliance drive. |
| Serves | [`VEC-0007`](example.vectors.md#vec-0007--address-masking-in-the-support-console-is-lifted-by-the-agent-who-wants-it) |

### MIT-0006 — Only managed, compliant devices can open the support console

Device management enforces disk encryption, a five-minute screen lock and blocked local export; the identity provider refuses the WebAuthn challenge from a device out of compliance.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#managed-endpoints`](example.spec.md#managed-endpoints) |
| Implemented in | `infra/mdm/support-baseline.yaml` |
| Verification | manual |
| Evidence | Monthly device compliance report, filed with the support lookup review. |
| Serves | [`VEC-0008`](example.vectors.md#vec-0008--the-full-order-record-lands-on-a-laptop-in-a-zone-the-model-calls-untrusted) |

### MIT-0007 — Identity documents are modelled, held once, and deleted thirty days after the request closes

A guest's identity document is a restricted data item held in one place, never forwarded or attached to the ticket, and removed by a job that reports what it deleted.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#identity-document-retention`](example.spec.md#identity-document-retention) |
| Implemented in | — |
| Verification | code |
| Serves | [`VEC-0009`](example.vectors.md#vec-0009--verifying-a-guest-collects-identity-documents-the-model-does-not-know-it-holds) |

### MIT-0008 — The checkout page links a privacy notice generated from the model's data entries

The notice states what is collected, why, on what basis and for how long, per data item, from the same entries the model carries, and is linked from the step that first asks for an address.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#privacy-notice`](example.spec.md#privacy-notice) |
| Implemented in | `src/checkout-web/pages/checkout.tsx` |
| Verification | code |
| Serves | [`VEC-0010`](example.vectors.md#vec-0010--nothing-in-the-model-tells-a-shopper-what-is-collected-or-on-what-basis), [`VEC-0014`](example.vectors.md#vec-0014--nobody-tells-the-shopper-a-model-read-their-message-and-wrote-the-reply) |

### MIT-0009 — A test fails when a known PII shape reaches the error reporter

The client error pipeline is exercised with a page state holding an address and an email, and the test asserts neither appears in what is sent to Sentry.

| | |
| :--- | :--- |
| Specified in | — |
| Implemented in | `src/checkout-web/telemetry/scrub.test.ts` |
| Verification | code |
| Serves | [`VEC-0011`](example.vectors.md#vec-0011--pii-scrubbing-on-client-error-reports-is-a-filter-that-fails-open) |

### MIT-0010 — The assistant proposes a refund; an agent issues it

The refund tool returns a proposal — amount, order and stated reason — which the console shows beside the draft and which settles nothing until an agent confirms it. The confirmation carries the agent identity and is what reaches the payment path. A rejected proposal is logged as a rejection with the prompt that produced it, and rejections are reviewed with the support lookup sample.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#assistant-refund-proposals`](example.spec.md#assistant-refund-proposals) |
| Implemented in | — |
| Verification | code |
| Serves | [`VEC-0012`](example.vectors.md#vec-0012--a-shoppers-own-words-reach-the-prompt-of-a-process-that-can-move-money) |

### MIT-0011 — Send the assistant the address only when the agent may already see it

`assist-request` carries the delivery address only where the console has unmasked it for the agent under the ticket-linked rule in MIT-0004, and the masked form otherwise, so a draft cannot restate what the console withheld. The audit event records which form was sent.

| | |
| :--- | :--- |
| Specified in | [`example.spec.md#assistant-address-masking`](example.spec.md#assistant-address-masking) |
| Implemented in | `src/support-console/views/assistant.ts` |
| Verification | code |
| Serves | [`VEC-0013`](example.vectors.md#vec-0013--an-assistants-draft-can-restate-an-address-the-console-masked) |

## Acceptances

Exposure knowingly carried: who accepted it, and on what reasoning, in full. An acceptance is a claim its owner can be asked to defend.

### VEC-0002 — Gift recipients are data subjects the system cannot inform or serve

Accepted by **Ines Verhaeghe, privacy lead** on 2026-09-13.

A recipient's address is the shopper's disclosure, held for ninety days and then purged. A rights route for someone who never interacts with us needs a notion of subject the data model does not have, and no such request has ever arrived. Carried knowingly; revisited if one does, or if `address.retention` ever grows.

### VEC-0006 — Backups add no isolation from the compromise that matters

Accepted by **Ruben De Smet, platform lead** on 2026-09-13.

Snapshots under a separate key in a separate account is a platform programme with no date, and the compromise that reaches the live key already reaches everything the snapshots would add. Break-glass through PAM guards the credential path; the residual is blast radius once that fails, and it is carried by name rather than deferred to a date nobody can give.

## Retired

No mitigation has been retired.

## Answered findings

Everything above was written by the people whose work it describes. A scanner observes the system as built and knows none of it, which is why these are the only rows here that can contradict the rest.

**A finding can lower confidence in a claim and can never raise it.** A scan that reports nothing is recorded as no evidence, never as confirmation.

### ANS-0003 — trivy `CVE-2025-31910`

**The model does not describe this part of the system.** The repair is the diagram rather than this register.

| Scope | `infra/edge-proxy/` |
| :--- | :--- |
| Answer | model_gap |
| Answered | 2026-09-13 |
| Why | The edge proxy is not in this model. Every flow from the browser reaches `checkout-api` through it, it terminates TLS, and it is where MIT-0002's throttle actually runs — and the diagram does not contain it, so nothing was ever enumerated against it. This is the most serious answer of the four: the repair is the model, not this register. |

### ANS-0001 — codeql `js/missing-rate-limiting`

**Contradiction — judged a false positive**, with the reasoning below rather than a silent suppression.

| Scope | `src/checkout-api/` |
| :--- | :--- |
| Answer | vector |
| Vector | [VEC-0003](example.vectors.md#vec-0003--the-order-path-has-no-throttle-anywhere-in-the-model) |
| Answered | 2026-09-13 |
| Why | VEC-0003 is dispositioned mitigated by MIT-0002, and this says it is not. It is: the throttle runs at the edge proxy in front of the API, which is outside the tree this scan covers and which the model does not contain at all. The scanner is right that the handler has no limit and wrong that nothing limits it. Recorded rather than suppressed, because the next person to read this deserves the argument rather than silence. |

### ANS-0002 — codeql `js/clear-text-logging`

| Scope | `src/support-console/` |
| :--- | :--- |
| Answer | vector |
| Vector | [VEC-0004](example.vectors.md#vec-0004--the-audit-log-keeps-email-past-its-own-retention-beyond-erasures-reach) |
| Answered | 2026-09-13 |
| Why | This is the address reaching the audit log, which is the exposure VEC-0004 already tracks — the log keeps it past the 90-day purge and out of erasure's reach. The finding is evidence for the deferral rather than against it, and it does not change the date. |

### ANS-0004 — trivy `CVE-2025-44701`

| Scope | `apps/marketing/` |
| :--- | :--- |
| Answer | not_a_threat |
| Answered | 2026-09-13 |
| Why | The marketing site is out of scope in this model and shares no data with checkout — no flow connects them and it holds nothing about a shopper. The same advisory on `checkout-web` would not get this answer, which is the whole reason a scanner finding is worth putting to a threat model. |

## Where transfer and avoid are recorded

Three dispositions, where a reader arriving from an ISO-shaped process expects four. The other two are recorded a layer up, in the artefacts that decide what applies, and this document points at them rather than restating them:

| Treatment | Recorded as | In |
| :--- | :--- | :--- |
| Mitigate | `mitigated` and a mitigation id | this matrix |
| Accept | `accepted`, an owner and a reason | this matrix |
| Transfer | the third party is an **element** in the model, with its own flows and threats; the disposition here is `mitigated` where they operate the control and `accepted` where only the loss is financed | `acme-checkout.dfd.yaml`, this matrix |
| Avoid | **not a vector at all** — a threat found not to apply, with a reason, or a finding not promoted, with a reason, or a vector retired because the exposure was designed out | [`example.threats.yaml`](example.threats.yaml) (its `controlled` and `not_applicable` verdicts), the register's `dismissed` and `retired` sections |

## Limits

**A disposition is a claim, not a fact.** "Mitigated" means somebody said so and named a control. The check requires the control to have a place — a specification, an implementation — and stops there; whether the code honours the requirement is a code review, and an annotation on the wrong function would satisfy every check here.

**A specification reference proves the requirement was written, never that it was met.** It moves the mitigation to where an implementer will meet it, which is the point, and no further.

**An `until` can be pushed.** A deferral moved forward every quarter stays green forever. Every date it has had is shown above, which is the only mitigation there is.

<!-- vector: rendered from example.vectors.yaml sha256:484b3fe103aa936959d3cd607d953b573470bd945eae4cf6ce8bde3ce05c54db -->
