# Question bank

Questions worth asking that the validator cannot infer. Do not read this aloud
in order — it is a checklist of blind spots, and most sessions need a third of
it. Pick what the system under discussion makes relevant.

The framing that works best for the omission-hunting questions is "most systems
have X — does yours?", because it costs the user nothing to say no and gives
them permission to remember something they forgot.

## Contents

- [Opening batch](#opening-batch)
- [The back doors people forget](#the-back-doors-people-forget)
- [Per-element follow-ups](#per-element-follow-ups)
- [Language models and agents](#language-models-and-agents)
- [Privacy questions that need care](#privacy-questions-that-need-care)
- [Closing the model](#closing-the-model)

## Opening batch

Ask these together, at the start, while the whole system is in the user's head.

- What does this system do, and for whom?
- Who or what talks to it — people, other services of yours, vendors?
- Where does it stop? What is deliberately outside this diagram?
- Is this for a security review, a privacy review, or both?
- Does it touch personal data at all?

## The back doors people forget

Users describe the happy path. These are the flows that exist anyway, and they
are where a disproportionate share of real findings come from.

- **Admin and support.** Is there an internal console? Who can read customer
  data through it, and is that access logged?
- **Break-glass.** When production is broken at 3am, how does someone get in?
  Does that path bypass the normal controls?
- **Analytics and reporting.** Does data get copied to a warehouse, a BI tool,
  a product analytics SDK? Those are flows and stores like any other.
- **Anything with a model in it.** A summariser, a chat assistant, a
  classifier, an autocomplete. People describe these as features rather than as
  processes, so they are frequently missing from the diagram entirely — and
  they are the one kind of process that can be talked into acting against you.
- **Backups.** Where do they go, who can restore them, and does the retention
  policy actually apply to them?
- **Logs.** What ends up in them, where do they ship, who reads them, how long
  do they live? Logs are a store of personal data that nobody models.
- **CI/CD.** What deploys this, and what does that pipeline have access to?
- **Third-party SDKs.** Anything embedded in a mobile app or web page that
  phones home is an external flow the user did not mention.
- **Email, SMS, push.** Notifications carry data out through a vendor.
- **Data subject requests.** How does someone get a copy of their data, or have
  it deleted? That is a real flow, and if it is manual, model the human step.
- **Offboarding and account deletion.** What actually happens, and where does
  the data survive?

## Per-element follow-ups

**For an actor** — how do you know it is who it claims to be? What happens when
it is not authenticated at all? Is this actor the subject of the data, or a
handler of someone else's?

**For a process** — what kind is it: a service, a scheduled job, a lambda, a
manual step someone performs, a language model, an agent that acts on its own?
What does it do to the data, not just move it? Who owns it?
Can it be reached from outside its trust zone? What does it log? What happens
when it fails — is there a fallback path that skips a control?

**For a store** — what is actually in it, at the field level? Encrypted at
rest, and who holds the key? Who can read it directly, bypassing the
application? What is the retention policy, and does anything enforce it? Are
there copies — replicas, snapshots, a staging refresh from production?

**For a flow** — what data travels on it, specifically? Over what protocol,
encrypted how? What authenticates it? What triggers it? Is there a response
flow carrying different data back?

## Language models and agents

Ask these when a process is `kind: llm` or `kind: agent`. They exist because a
model is the only process whose behaviour is not fully determined by its code,
which makes the usual questions insufficient rather than wrong.

**What untrusted content reaches the prompt?** The highest-yield question here
by a distance. A ticket body, a user message, a fetched page, a retrieved
document, another tool's output — any of it arriving in the context is
untrusted input reaching a control path, which is tampering with extra steps.
"Nothing does" is a legitimate answer and should be followed by "what stops
it?".

**Where does the system prompt live, and who can change it?** In source under
review is a different risk from a value in a config a deploy can edit, which is
different again from something an admin can type into a form at runtime.

**What happens to the output?** Rendered as markup, executed, passed to a tool,
written to a store, shown to a customer, used to make a decision about someone.
Output treated as instruction rather than data is where a prompt injection
becomes an incident rather than a curiosity.

**For an agent, what can it do without anyone approving?** Send the email, issue
the refund, open the pull request, call the tool. "Nothing without approval" is
a complete answer and a good one. Anything else is the blast radius, and it
belongs in the diagram: **model each tool the agent can call as a flow**, so the
authority is visible as an edge rather than buried in a sentence.

**Two more worth asking even though nothing requires them.** Does the model see
personal data — because if it does, retention now includes whatever the provider
keeps, and that is a LINDDUN question with a contract attached. And is the
provider inside your trust boundary or outside it? A hosted model is a
third-party service and should be an actor or a store in its own right, not an
implementation detail of the process calling it.

## Privacy questions that need care

These are the LINDDUN-driven questions. Ask them when personal data is in play.
Several are ones teams cannot answer, and "we don't know" recorded in
`open_questions` is a legitimate and useful outcome — often the most useful
thing the exercise produces.

- Whose data is this? Customers, employees, people who never signed up?
- Can two records be linked back to the same person, even without a name? Device
  ids, session ids, and IP addresses usually can.
- How long is it kept, and what enforces that?
- Does the person know you have it? Where were they told?
- Can they see it, correct it, or get it deleted — and through which flow?
- Who outside the organisation receives it, and under what agreement?
- Does it leave the jurisdiction it was collected in?
- Is any of it special category data — health, biometrics, sexuality, religion,
  politics, union membership, race?
- Is any of it collected because it might be useful later rather than because
  something needs it now?

## Closing the model

- Walk the diagram out loud and ask what is wrong with it. People correct a
  picture far more readily than they volunteer information.
- Which of these elements would hurt most if it were breached?
- What did we not talk about that you were expecting to?
- What is in this diagram that you are not confident about?

That last question is the one that produces the honest limits section, and a
DFD without honest limits gets over-trusted by whoever reads it next.
