---
id: R-007
title: Machine-paced work declares itself
principle: P-4
severity: warning
status: active
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*"
---

## Statement

Where the physics of a run demonstrate machine production — sustained output
above what a person can write by hand — the history must say so: at least one
commit in the run carries machine attribution (a co-author trailer, a bot
identity, a generation marker).

The finding is never "machine-made" and never "unattributed". It is the
conjunction: **machine-paced and undeclared.** Both halves are load-bearing,
and each alone is explicitly not a finding:

- Absence of attribution proves nothing (S-3: attribution is opt-in and
  trivially stripped; a signal the measured thing can switch off must never
  carry a rule alone).
- Machine pace with attribution is not a finding either — that is machine work
  declaring itself, which is exactly what this rule asks for.

## Rationale

P-4 holds that history says truthfully what produced the work. Attribution's
fatal weakness as a signal is that its absence is silent — a tool told not to
write trailers leaves history indistinguishable from hand-written work. The
way through is corroboration by something that cannot be switched off: pace.
Sustained production above the writing ceiling — a generous bound that
includes thinking, testing and correcting — is not achievable by hand. When a
run's arithmetic shows that, machine involvement is demonstrated by physics,
and the only remaining question is whether the history admits it.

The writing ceiling is set well above real sustained hand rates for the same
reason R-001's reading rate is: a finding should be unarguable, not merely
suspicious.

## How to check

```sh
bin/digest-rate --since "<window start>" --until "<window end>"
```

Runs are as defined by R-006 (same tool, findings tagged per rule). A run
fails R-007 when its rate meets `--write-rate` **and** no commit in it is
attributed. One attributed commit clears the whole run: the run then declares
machine involvement, and apportioning it commit-by-commit is more precision
than a trailer can carry.

## Evidence to cite

The run, its rate against the writing ceiling, and the attribution scan that
came back empty — trailers, author identities, body markers. Quote the
detection patterns used: a reader must be able to argue the scan missed a
convention this repository uses.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **Everything in R-006's "Not a violation" applies here first** — mechanical
  churn, staged work, reverts. Each can produce super-human pace without any
  machine authorship. Staged work matters doubly here: a hand-built change
  carved into quick commits shows machine pace with honestly absent
  attribution. Check the diff for the mechanical cases and ask about staging
  before citing.
- **An attribution convention the scan does not know.** Detection is a pattern
  list; a repository may declare machine involvement in a form it misses (a
  DCO-style trailer, a policy file, commit prefixes). Look for one before
  citing — the rule is about undeclared work, not unconventional declarations.
- **Slow machine work is invisible here, and that is accepted.** An agent
  producing at human pace clears this rule unseen. The rule does not claim to
  find all undeclared machine work — only the portion the physics can prove,
  which is the portion worth a finding at all.

A **warning**. Verified against real history for the non-firing direction — a
repository whose machine work is consistently attributed produces zero
findings at machine pace — and against synthetic data for the firing one.
