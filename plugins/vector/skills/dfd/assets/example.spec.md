# Acme Checkout — requirements carried in from the threat matrix

| | |
|---|---|
| **Status** | Accepted |

This file stands in for the project's own specification: an SDD, a design
document, an RFC, a README section — whatever the people building Acme
Checkout actually read before they build. It exists in the example because the
threat matrix's central requirement is that a mitigation reaches that document
rather than living only in `example.vectors.yaml`, and a worked example whose
`specified_in` references pointed nowhere would be demonstrating the failure
the capability exists to prevent.

Each section below is one requirement the matrix wrote in. The mitigation id
is the link back; the vector id says which threat the requirement answers.
Nothing here is Acme's whole specification. It is the part the threat model
put there.

## Guest email verification

*MIT-0001 · answers VEC-0001*

An order placed without an account, and a data subject request made without
one, is not accepted until the email address it names has been proven to be
under the requester's control. A six-digit code is sent to the address and has
to be returned within fifteen minutes. Attempts are limited to five per address
and twenty per source address per hour.

A guest who cannot complete the check on a data request is told what the
alternative route is and what it will need; the request is recorded as opened
either way, so the refusal is visible.

Verified by a test that a submission naming an unverified address is rejected
on both paths, and by the annotation on the verification handler once it
exists.

## Order throttle

*MIT-0002 · answers VEC-0003*

`submit-order` is rate-limited before any downstream cost is incurred: ten
orders per session per hour, and sixty per source address per hour, enforced
at the API gateway in front of the checkout API. A rejected request never
reaches the database or Stripe. The limit is a configuration value, and a
change to it is reviewed like code.

Verified by a load test in CI that submits above the limit and asserts nothing
was written and nothing was charged.

## Audit log pseudonymisation

*MIT-0003 · answers VEC-0004*

Audit events written on a support lookup carry the shopper's internal id, not
the email address. The id resolves through `orders-db` while the account
exists, and to nothing after erasure — which is the property the two-year
retention of the log then has to stand on. The stated exception to erasure is
the event itself, under the legal-obligation basis `audit-event` already
carries; the address is not part of that exception.

Existing events are rewritten once, in a migration that replaces the address
with the id, with a count of events it could not resolve reported and kept.

Verified by a test that a support lookup's audit event contains no `@`.

## Support lookup review

*MIT-0005 · answers VEC-0007*

Every month a named reviewer, not on the support team, samples support-console
lookups from the audit log — at least twenty, weighted towards agents with the
highest lookup counts — and checks each against the ticket it names. The
sign-off, the sample and any lookup that could not be justified are filed in
the compliance drive under the month.

This is the detective half of the control on VEC-0007. The preventive half is
`MIT-0004`, in code, and this review is what tells us whether it is working.

## Managed endpoints

*MIT-0006 · answers VEC-0008*

Any device that can open the support console is enrolled in device management
with full-disk encryption on, a screen lock at five minutes, local export and
clipboard capture from the console blocked, and the compliance state reported
to the identity provider. A device out of compliance cannot start a session:
the WebAuthn challenge is refused rather than the data being served.

Verified by the monthly device compliance report, filed with the support
lookup review.

## Identity document retention

*MIT-0007 · answers VEC-0009*

An identity document supplied to verify a guest's data request is a modelled
data item: classification restricted, lawful basis legal obligation, subject
the requester, retained thirty days after the request closes and then deleted
from the mailbox and the form backend by a job that reports what it removed.
It is held in one place, not forwarded, and is never attached to the request's
ticket.

Until this is built, the privacy inbox's retention rule is the control, and it
is not sufficient — which is why VEC-0009 is deferred rather than mitigated.

## Privacy notice

*MIT-0008 · answers VEC-0010*

The checkout page links the privacy notice from the step where the address is
first asked for, and the notice states, per data item the model carries, what
is collected, why, on what basis and for how long — taken from the model's
`data` entries rather than written a second time by hand, so the two cannot
disagree without the diff showing it.

Verified by a test that the rendered checkout page carries the link, and a
test that every `data` item in the model appears in the notice.
