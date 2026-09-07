---
id: R-010
title: A document must offer a reader a way in partway
principle: P-7
severity: advisory
status: draft
introduced: 0.1.0   # first plugin version carrying this rule; bin/case-strip reads it
applies-to:
  - "**/*.md"
  - "**/*.rst"
  - "**/*.adoc"
  - "**/*.mdx"
---

## Statement

A document must be enterable partway: the longest stretch of prose a reader
must cross to reach one answer should not be far out of line with what the rest
of the repository's documents ask.

The measure is the **span between headings**, not length. A five-thousand-line
document sectioned every eighty lines is workable; a six-hundred-line document
with no headings is not, and ranking by length gets those two the wrong way
round.

**Scope: prose.** A span that is mostly table rows or fenced code is **not**
this rule's concern and is exempt mechanically. Nobody reads an inventory top to
bottom — they look a row up, and every row is its own entry point. The same
holds for a code block.

**Scope: documents written for people.** Instruction files read by a model —
`CLAUDE.md`, `AGENTS.md`, agent, skill and rule definitions — are excluded
mechanically, and not as a technicality. A model is handed the file whole, so
headings save it nothing; adding them to clear an R-010 finding on such a file
would cost tokens and buy nothing. Their cost is length in tokens and how often
they load, which `reading-weight` reports as a signal under S-6 and no rule
currently tests.

**Scope: repositories with enough documents to have a norm.** Below the minimum,
**not applicable** — an outlier needs a distribution to be outlying from.

**Scope: spans long enough to matter.** A short document with no headings is
fine and is never reported, whatever the median is.

## Rationale

P-7 holds that documentation is read by someone who needs one answer, and that
a corpus can hold every fact while failing that reader completely.

This is the checkable core of it, in the frame's usual backwards shape. The rule
cannot show that nobody read a document. It can show that the document offers
**no way to enter it partway** — that reaching any single answer requires
crossing a given number of lines, because there is nothing in between to
navigate by. That is a fact about the artifact, not a claim about a reader.

Length is deliberately not the test, and not only because it is the wrong
signal. A rule capping length is satisfied by `split`, which costs nothing and
changes nothing — the theatre failure `README.md` warns about. Span can only be
reduced by putting entry points into the material.

## How to check

```sh
bin/reading-weight              # the R-010 section is printed after the S-6 signal
bin/reading-weight --ref <sha> --floor 150 --margin 3.0
```

The script computes, per document, the longest span between headings and what
fraction of that span is table rows or fenced code. A span is reported when it
is at least the floor **and** at least the margin multiple of the repository's
median span, **and** less than half table or code.

Two limitations to state in any case file citing this rule:

- **Heading detection is convention-bound.** Markdown and rst styles are
  recognised; a document organised another way reads as unstructured when it is
  not. And *any* heading counts as an entry point, which over-credits a document
  with many shallow headings — see the honesty note below.
- **The thresholds were chosen, not calibrated.** This is why the rule is
  `draft`.

## Evidence to cite

- The span in lines and in reading time at the stated rate, the document's total
  length, and its heading count — all four, because the span alone invites the
  reader to assume the document is simply long.
- The repository's median span, so the outlier is visibly an outlier.
- The non-prose fraction, even when it is low. It is what separates this finding
  from a lookup table, and a reader should see that it was checked.
- **What adhered, beside what did not.** The count of comparable units in the
  window that satisfied this rule, next to the count that did not, so the
  finding is read against the practice and not alone.

## Not a violation

- **A lookup document.** Inventories, catalogs, reference tables, glossaries and
  data dictionaries are entered by search, not by reading. Mostly-tabular spans
  are exempt mechanically; a lookup document that happens to be prose-formatted
  is exempt on adjudication.
- **Generated output.** OpenAPI dumps, schema documentation, coverage reports.
  The remedy is never to restructure the file, as in R-005's `GEN` case.
- **One continuous argument.** Some things are a single line of reasoning and
  chopping them into sections would damage them — a proof, a narrative
  post-mortem, a legal or regulatory text that must stay contiguous to be
  correct.
- **A document read once, start to finish, by design.** An onboarding walkthrough
  or a tutorial has one entry point on purpose: the beginning.
- **Front matter, licence blocks and long preambles** before the first heading,
  which the span measure counts and a reader skips.
- **The document is read by a machine.** Excluded by scope, but worth naming
  here too, because the classification is by path convention and a repository
  using its own convention for agent instructions will have them measured as
  prose. A finding on a file that is plainly an instruction to a model is a
  misclassification, not a finding.
- **The corpus is uniform and short.** Where the median span is small because
  every document is small, the margin multiple fires on documents that are
  merely ordinary. Check the floor did the work and not the ratio.

## Honesty about how this one games

The frame's own criterion is to prefer rules whose cheapest evasion is the
desired behaviour, and to say so plainly where a rule falls short of that. This
one falls partway short.

The cheapest way to clear an R-010 finding is to add headings. Where those
headings name what is beneath them, gaming the rule *is* the improvement, which
is the good case. Where they do not — `## Section 2`, `## More` — the span drops
and nothing is easier to find, and the rule cannot tell the difference, because
it counts entry points and cannot read them.

So a passing result under R-010 is cheap to buy, and a case file should not
present one as evidence that documentation is navigable. Adjudication of a
*cleared* finding, where anyone bothers, means reading the new headings to see
whether they name anything.

## History

- **Draft, on derivation.** The first rule under P-7, and the first to measure
  the shape of an artifact rather than an event in history.

  Built after `bin/reading-weight` (signal S-6) already existed, which changed
  the rule for the better. The first run of that script, on real history, ranked
  a 247-line document above a 597-line one — correctly, since the short one had
  four headings and the long one thirty. It also put a data inventory and a data
  model at the top of the list, both of which are 95%+ table. Had the rule been
  written before the measurement, it would have shipped flagging exactly the two
  documents that were correctly built for their purpose. The non-prose fraction
  exists because of that run, and is mechanical rather than an adjudication note
  for the same reason.

  Verified against a synthetic corpus: a 401-line single-heading document
  reported, a 303-line one-heading inventory exempt as lookup, nine ordinary
  sectioned documents silent. On the real history it reports nothing, with both
  long spans exempted as lookup — the correct answer, reached mechanically.
