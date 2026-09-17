# Changelog

Notable changes to the `vector` plugin. Versions follow
[semantic versioning](https://semver.org/spec/v2.0.0.html), and users only
receive an update when `version` in `.claude-plugin/plugin.json` changes — so
every entry here corresponds to a bump, and changes with no user-visible effect
(tests, CI, repository tooling) deliberately do not appear.

There are no release tags. The marketplace entry uses a relative `source`, so
Claude Code tracks the default branch and gates updates on that `version` field;
a tag would participate in neither. A release is the commit that bumps it, and
each version below links to its own.

## [0.12.0] — 2026-09-17

### Added

- **Installable.** Until now the README told you to add a marketplace that only
  people with access to a private repository could reach. The plugin is
  published to [`alnico-claude`](https://github.com/buzzworks-be/alnico-claude),
  the public marketplace:

  ```sh
  claude plugin marketplace add buzzworks-be/alnico-claude
  claude plugin install vector@alnico-claude
  ```
- **A licence.** Apache-2.0, with `LICENSE` and `NOTICE` shipped beside the
  plugin. There was none before, which made everything above it unusable by
  anybody who reads a licence before running code.

### Changed

- `homepage` and `repository` in the manifest point at the published directory
  a reader can actually open, rather than at the private repository they were
  set to, which was a 404 for everybody this plugin is for.
- The plugin's description is now **Continuous Threat Modeling with STRIDE for
  security and LINDDUN for privacy**. It is what a browser sees first, and what
  it said before was a paragraph recounting every step of the chain — accurate,
  and no use to somebody deciding in one line whether this is the thing they
  want.

### Note on what is published

The public copy is an **export**, not a mirror: the skills, the agent, the
scripts with their lockfiles, the changelog and the licence. The design
documents, the tests and the development guidance stay in the private
repository, so a published tree carries what a session loads and nothing else.

## [0.11.0] — 2026-09-15

### Added

- **Scanner findings put to the threat model.** `/vector:intake` reads a SARIF
  file the build produced and asks one question of every finding: *where was
  this in the threat matrix, and did we evaluate it incorrectly, or should we
  adapt?* The answer lands in the register's new `answers` section.

  This is the first thing in the toolkit that can say the model is **wrong**.
  Every other check compares one artefact written by these people against
  another written by the same people; a scanner observes the system as built
  and knows nothing about what anybody claimed.

  Three answers, and they are not a severity scale: **`vector`** routes the
  finding to a threat the register tracks, **`not_a_threat`** dismisses it with
  a reason that is usually the model — a vulnerability in a component no flow
  reaches is not the same risk as the same vulnerability on the front door —
  and **`model_gap`** says the diagram does not contain the part of the system
  the finding is in, which sends the work back to `/vector:dfd`.
- **A finding on a `mitigated` vector cannot be closed by silence.** The answer
  has to say which of two things happened: the control does not do what it
  claimed (`contradiction: disposition_revised`), or the finding is wrong
  (`contradiction: false_positive`) — and *why* it is wrong is the part worth
  writing. Neither is the safe answer, and a third word does not close it. This
  is the only place in the toolkit where evidence argues with an attestation.
- **Nothing fingerprints a finding.** A finding counts as already answered when
  its scanner and rule match an answer's and its location sits under that
  answer's scope, so a renamed rule, a dropped fingerprint or a scanner upgrade
  puts the question back in front of somebody rather than suppressing it. The
  fingerprints a scan carries are recorded in `seen_as` so a person can find the
  original, and nothing matches on them.
- **A dismissal lapses when the model moves.** It records the `model_digest` it
  was argued against, so a design decision that changes the diagram sends
  *unreachable* back to be re-argued rather than inherited. Advisory rather than
  blocking: a model change lapses every dismissal at once, and that pile
  arriving on a day nobody chose must not also be a red build.
- The rendered `<slug>.matrix.md` gains an **Answered findings** section, model
  gaps and contradictions first, lapsed answers marked rather than hidden.

### Changed

- Nothing about this runs in CI. The intake is a session capability, and a
  build is never handed a scan — which is how the promise that nothing here
  fails a build on its own judgement is kept structurally rather than by
  choosing severities carefully. What CI does check is the register's own
  answers, because a broken answer is a broken register.

### Known limits

- **A clean scan is no evidence, never confirmation**, and every run says so in
  those words. A scanner finds what it knows how to look for; silence means
  only that. A finding can lower confidence in a claim and can never raise it.
- **A scope drawn wide dismisses findings nobody has seen yet.** It is the one
  silent failure in this design — every other way it fails asks the question
  again — and the person drawing the scope is the only one who can bound it.
- **SARIF 2.1.0 and nothing else.** A second format is a parser rather than a
  new capability, and a result whose rule id cannot be resolved is reported as
  unkeyable and asked about again every run, rather than given an invented key
  that looks stable and is not.

## [0.10.0] — 2026-09-15

### Added

- **The model read against the design documents that land in your
  repository.** `/vector:review` is the outermost link in the chain: every
  other check in this toolkit compares one of its own artefacts against
  another, so a model that was never right about the system passed all of
  them.

  Tell the model where your project writes its design down, in
  `system.design_sources`, and every tracked document under there becomes
  something somebody has to answer for. The skill reads each one and asks the
  question only a person can answer — does this change the modelled system? —
  then records the answer in `system.reviewed`: the path, the digest of what
  was read, the date, whether it changed anything, and why. Both answers need
  a reason; a no-impact reading with none says only that somebody clicked past.

  After that the build fails on a document nobody has read, and on one edited
  since its reading. Those are different repairs and the output says which.
  Clearing either is four lines in the same pull request as the decision,
  written by whoever is holding the most context — which is the only reason a
  check that fires on other people's work is defensible at all.
- **A document that has superseded itself is not asked for.** Where a status
  reads superseded, deprecated, withdrawn or obsolete — the convention already
  used for a mitigation's requirement — the document is dropped from the list,
  and an existing reading of one is left alone. This is what makes adopting the
  capability survivable in a repository with years of decisions in it.
- **The age of the oldest reading, reported on every run.** A number, not a
  finding, because an advisory that fires every time is a count people stop
  reading. It becomes a failure only if you set `system.review_cycle`: there is
  no default, because an expiry is repairable by re-stamping a date and the
  toolkit has no half-life to defend. Set one if an audit calendar requires it,
  and not otherwise.
- A moved document is one finding rather than two. An unreviewed file and a
  reading whose path has gone, sharing a digest, are reported as a rename —
  correct the path, nothing needs reading again.

### Changed

- `check_traceability.py` no longer needs a register. A repository that has
  built a model and promoted nothing is now one it has something to say about,
  so the currency review works from the first iteration rather than the fourth.
- The rendered `<slug>.dfd.md` gains a **Reviewed against** section, so a
  model's age is legible to somebody reading Markdown rather than YAML.

### Known limits

- **This detects that a document landed, never that the system changed.** Work
  that ships without one is invisible to it, and the output says so rather than
  leaving a green run to imply otherwise. Making an element declare where its
  code lives was weighed and rejected: application code changes many times a
  week and almost none of it touches the diagram, so the signal would fire
  constantly and be switched off.
- **Recording no impact is cheap**, as `"n/a"` on a field and
  `not_applicable` on a cell already are. Requiring a reason makes it a claim
  somebody can disagree with; nothing makes it a true one.

## [0.9.0] — 2026-09-14

### Added

- **The threat model checked on every push.** `/vector:wire` copies
  `check_traceability.py` into your repository, commits it beside your code
  with its pinned dependency, and writes a workflow that runs it in one
  command. Nothing is fetched at build time and nothing is GitHub-specific:
  any runner that can run the command is enough.

  What it checks is whether the threat model still describes the product at
  HEAD. Every mitigation names the requirement carrying its control, and the
  check resolves that document, reads its status, and compares a digest
  against its current bytes. A requirement that was edited is **stale** until
  somebody reads the change and re-affirms it. One that has been **superseded**
  fails even though its own bytes never moved, which is the case a digest can
  never catch. Model, enumeration and register digests are walked at the same
  time, and a deferral past its date fails with them.

  **It reports coverage, never proof.** A green build means a set of
  internally consistent claims is current, not that any control works, and the
  output says so on every run.
- `specified_digest` on a mitigation, recorded against the requirement it
  names. A register written before this release has none, which reports as an
  advisory rather than failing — adoption does not start with a rewrite.
- `implemented_in` may now be a list of locations. Declare where a control
  belongs and partial coverage fails: shipped on iOS and missing on Android is
  red rather than green. A plain string still means one location, and
  declaring none opts out.

### Changed

- **Source annotations are optional.** `vector: mitigates MIT-0007` still
  works, is still one line in whatever comment syntax the file uses, and is now
  checked where present rather than required — an annotation naming a
  mitigation no register has still fails at its line. The reasoning is in
  ADR-0006: an annotation attests and never observes, so a control refactored
  into a broken state and one that works carry the same comment.

## [0.8.0] — 2026-09-13

### Added

- **Threat matrix.** `/vector:matrix` walks every tracked vector with you and
  records what is being done about it: `mitigated` with a mitigation,
  `accepted` with an owner and a reason, or `deferred` with an owner, a
  reason and a date. Each state requires the field that makes it a decision
  rather than a label, and `check_matrix.py` refuses a register until every
  vector has one — and until every mitigation names where its requirement is
  written. For a control not yet built, that is the specification the
  implementer will read: the skill writes the requirement there, in the same
  sitting, and `specified_in` has to resolve to it. A deferral past its date
  fails the check; a date moved twice is reported.

  The dispositions and mitigations go into the same `<slug>.vectors.yaml`, in
  fields the promotion skill never touches. `render_matrix.py` produces
  `<slug>.matrix.md`: what is unfinished and who owns it first, then the
  matrix, the mitigations and where each lives, the acceptances with their
  reasoning in full — and where *transfer* and *avoid* are recorded, for the
  reader who expects four treatments and finds three.
- `assets/example.vectors.yaml` now carries dispositions on all eleven
  vectors and nine mitigations behind them; `assets/example.spec.md` stands in
  for the specification those mitigations were written into, and
  `assets/example.matrix.md` is the rendered matrix.

## [0.7.0] — 2026-09-13

### Added

- **Threat model documentation.** `/vector:promote` turns a finished
  enumeration into a threat model. It walks every finding with you, promotes
  the real ones to vectors with stable ids, chains the ones that are one
  concern seen from several elements, and records why the rest are not
  tracked — into `<slug>.vectors.yaml`, the register, rendered as
  `<slug>.vectors.md`.

  "Done" is a script's decision here as everywhere: `check_vectors.py` reports
  every finding nobody has decided about, and every `threat` verdict and every
  open question the model carried forward has to end up in exactly one place —
  a vector's source, an authored chain, or a dismissal with a reason.
  Promotion asks three things of each vector — what an attacker does, what it
  costs, what is already true of the system — and all three are required,
  because a vector without them is a verdict with a number on it.

  When the enumeration is re-run under it, a vector whose source disappeared
  is reported as orphaned and stays until you retire it with a reason; a
  retired id is never reused. The register is also where the threat matrix
  will add dispositions and mitigations, in the same file.
- `assets/example.vectors.yaml` and `example.vectors.md` — the worked
  example's threat model: eleven vectors over eighteen findings, four of them
  chains, the model's open question promoted, three findings dismissed with
  reasons.

## [0.6.1] — 2026-09-13

### Added

- `assets/example.dfd.md`, the rendered view of the worked model, so what
  `/vector:dfd` produces can be read before running it. The enumeration
  already shipped both halves; the model now does too, with the same test
  guarding that the view matches what the renderer produces.

## [0.6.0] — 2026-09-12

### Added

- **Threat enumeration.** `vector:enumerate` walks a finished data flow diagram
  and records a verdict for every threat category that applies to every element,
  then writes `<slug>.threats.yaml` and a rendered `<slug>.threats.md`.

  Completeness is a script's decision here too. `check_coverage.py` derives the
  applicable grid from the model and reports every pairing without a verdict, so
  the agent cannot stop when the findings feel sufficient — the worked example
  produces 284 of them from 31 elements. Every verdict names the field in the
  model that makes it true, and a dismissal must carry a reason somebody can
  disagree with.

  A privacy finding cites what it is an instance of, by id, from the LINDDUN
  threat tree: `I.2.1.2` rather than "identifying". Security findings cite a
  named attack pattern from the STRIDE catalogue where one fits.

  The rendered document leads with findings. A complete enumeration has more
  dismissals than findings by an order of magnitude, and a reader who meets two
  hundred of them first does not reach the first finding.
- `assets/example.threats.yaml` and `example.threats.md` — the worked example
  enumerated in full, as a reference for what a finished one looks like: 18
  findings, 232 controlled, 34 not applicable.

## [0.5.0] — 2026-09-10

### Added

- Processes now say what **kind** they are — `service`, `job`, `lambda`,
  `manual`, `llm` or `agent` — and a language model or an agent answers three
  more questions, with a fourth for an agent: what untrusted content reaches the
  prompt, where the system prompt lives and who can change it, what consumes the
  output and whether it is treated as data or as instruction, and what an agent
  may do without a human approving.

  These are kinds rather than new element types, because a model attracts
  exactly the threat categories any other process does. Prompt injection is
  tampering and excessive agency is elevation of privilege; both are in
  `references/STRIDE.md` as attack patterns under those categories rather than
  as a second taxonomy.
- `actors.type` accepts `ai_agent`, for an agent that calls the system from
  outside it. An agent you run is a process with `kind: agent`; the trust zone
  decides which you have.

### Changed

- **`kind` is required, so every model written before this reports a blocking
  gap on each of its processes.** Add the field to continue. This is deliberate:
  a model that does not say whether a process is a language model is one nobody
  has reviewed since that became a question worth asking, and a default value
  would have made those two indistinguishable.

### Fixed

- A `processes` enum value outside its set now reports `BAD_ENUM`. The section
  had never carried an enum, so nothing validated one — the first one added
  passed anything at all.

## [0.4.4] — 2026-09-10

### Added

- Two threat catalogues beside the mapping tables. `references/LINDDUN.md` is
  the LINDDUN threat tree in full — 72 nodes, five levels deep, so a privacy
  finding can name `I.2.1.2` rather than just "identifying".
  `references/STRIDE.md` is 114 named attack patterns grouped by STRIDE
  category, 98 of them anchored to a CAPEC entry.

  Neither says which categories apply to which elements. That stays
  `threat-mapping.md`'s job alone, because two applicability tables that can
  disagree is worse than one.

### Fixed

- A model that marks somebody as a data subject while no data entry is personal
  now reports a `NO_PERSONAL_DATA` gap. Both statements were answered, so
  nothing objected, and the contradiction went straight through to the privacy
  analysis — LINDDUN applicability reads the actor's flag, so the model would
  produce questions about linking and identifying for a person the data
  dictionary says is not in there. It is the mirror of the existing
  `NO_DATA_SUBJECT` check, which only ever looked the other way.

## [0.4.3] — 2026-09-08

### Fixed

- A malformed entry in any section — a list item that is not a mapping — now
  reports as a `BAD_ITEM` gap instead of ending the run with a Python
  traceback. It was reported correctly but left in place, so it reached the
  field checks and crashed on the way past.

## [0.4.2] — 2026-09-08

### Added

- Both scripts carry [PEP 723](https://peps.python.org/pep-0723/) inline
  dependency metadata and a hash-pinned lockfile beside them, so
  `uv run --script skills/dfd/scripts/validate_dfd.py <model>.dfd.yaml`
  resolves PyYAML with no setup. This is additive: `python3 <script>.py`
  against a system PyYAML is unchanged and remains the documented default,
  since the metadata is a comment block to it.

## [0.4.1] — 2026-09-08

### Fixed

- `is_data_subject` is now type-checked. A non-boolean value — most likely a
  quoted `"yes"` — passed the presence check and then failed an identity test
  further on, so the model came back reporting `NO_DATA_SUBJECT`: that nobody
  was marked as the subject of the personal data, when someone had been marked,
  just in a form the validator could not read.

### Added

- `BAD_BOOL`, a blocking gap for a value that should be `true` or `false` and
  is neither. **A model that set `is_data_subject` to a quoted string will now
  report this gap** where it previously reported the misleading one above.
  `NO_DATA_SUBJECT` is suppressed while any such value is unreadable, so one
  typo produces one gap rather than two, the second of them false.

## [0.4.0] — 2026-09-08

### Changed

- Renamed the plugin to `vector`, which changes how everything it ships is
  addressed: the skill is now `/vector:dfd`.

---

Earlier versions (`0.1.0`–`0.3.0`) predate this file. See the commit history
for what changed in them.

[0.12.0]: https://github.com/buzzworks-be/vector/commit/e8b1e3f
[0.11.0]: https://github.com/buzzworks-be/vector/commit/2b7e440
[0.10.0]: https://github.com/buzzworks-be/vector/commit/87c4736
[0.9.0]: https://github.com/buzzworks-be/vector/commit/4d89955
[0.8.0]: https://github.com/buzzworks-be/vector/commit/5346482
[0.7.0]: https://github.com/buzzworks-be/vector/commit/d2afb77
[0.6.1]: https://github.com/buzzworks-be/vector/commit/035b5cf
[0.6.0]: https://github.com/buzzworks-be/vector/commit/9c88938
[0.5.0]: https://github.com/buzzworks-be/vector/commit/406d093
[0.4.4]: https://github.com/buzzworks-be/vector/commit/f8975bd
[0.4.3]: https://github.com/buzzworks-be/vector/commit/da0cdc7
[0.4.2]: https://github.com/buzzworks-be/vector/commit/921a2ca
[0.4.1]: https://github.com/buzzworks-be/vector/commit/a7b9bde
[0.4.0]: https://github.com/buzzworks-be/vector/commit/ff2cea8
