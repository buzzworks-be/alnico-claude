#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Render a register as the threat matrix.

What is being done about each vector, by whom, and where the control is
written. A pure function of the register and the date it is read on:
regenerate rather than hand-editing, since the YAML is the source of truth.
This is the other view of the file render_vectors.py renders — that one is
read to understand the threat model, this one to see what is being done about
it — and its two readers want different things first: the engineer needs what
is unfinished, the auditor needs what was decided and by whom. The order below
serves both early.
"""

import argparse
import datetime
import importlib.util
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = ("actors", "processes", "stores", "flows")
FRAMEWORKS = {"stride": "STRIDE", "linddun": "LINDDUN"}


def sibling(name):
    """A sibling script, imported rather than reimplemented — the checks that
    gate the document are the ones it reports from."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def label(category):
    framework, _, name = str(category).partition("/")
    return f"{FRAMEWORKS.get(framework, framework)} {name.replace('_', ' ')}"


def cell(value):
    if value is None:
        return "—"
    text = " ".join(str(value).split())
    return text.replace("|", "\\|") if text else "—"


def date(value):
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return cell(value)


def name_of(model, element):
    for section in SECTIONS:
        for item in model.get(section) or []:
            if isinstance(item, dict) and item.get("id") == element:
                return item.get("name") or element, section
    return element, "unknown"


def ids(values):
    if not values:
        return "—"
    if not isinstance(values, list):
        values = [values]
    return ", ".join(f"`{v}`" for v in values)


def in_order(vectors, model):
    """Vectors in the model's order — section, then element, then as listed."""
    rank = {}
    for index, section in enumerate(SECTIONS):
        for position, item in enumerate(model.get(section) or []):
            if isinstance(item, dict):
                rank[item.get("id")] = (index, position)
    return sorted(vectors, key=lambda v: rank.get(v.get("element"), (len(SECTIONS), 0)))


def render(register, model, report, as_of, open_only=False):
    vectors = [v for v in register.get("vectors") or [] if isinstance(v, dict)]
    mitigations = [m for m in register.get("mitigations") or [] if isinstance(m, dict)]
    retired = [r for r in register.get("retired") or [] if isinstance(r, dict)]
    flagged = {}
    for gap in report.gaps:
        flagged.setdefault(gap["element"], []).append(gap["code"])

    def state(vector):
        disposition = vector.get("disposition")
        if not isinstance(disposition, dict) or not disposition.get("state"):
            return None
        return disposition["state"]

    def disposition(vector):
        return vector.get("disposition") if isinstance(vector.get("disposition"), dict) else {}

    undecided = [v for v in vectors if state(v) not in ("mitigated", "accepted", "deferred")]
    counts = {s: sum(1 for v in vectors if state(v) == s)
              for s in ("mitigated", "accepted", "deferred")}
    without = [v for v in vectors if state(v) and not disposition(v).get("mitigations")]

    lines = [f"# Threat matrix — {model.get('system', {}).get('name', 'unnamed')}",
             "",
             f"Generated from the register beside `{register.get('threats')}` by "
             f"`render_matrix.py`, as of {as_of.isoformat()}. Do not edit; regenerate.",
             ""]

    # --- 1. summary ---------------------------------------------------------
    lines += ["## Summary", ""]
    if not vectors:
        why = register.get("empty_because")
        lines += ["No vectors are tracked." + (f" {cell(why)}" if why else ""), ""]
    else:
        lines += ["| | Vectors |", "| :--- | ---: |",
                  f"| Tracked | {len(vectors)} |",
                  f"| Mitigated | {counts['mitigated']} |",
                  f"| Accepted | {counts['accepted']} |",
                  f"| Deferred | {counts['deferred']} |",
                  f"| **Undecided** | **{len(undecided)}** |" if undecided
                  else f"| Undecided | {len(undecided)} |",
                  f"| Carrying no mitigation | {len(without)} |",
                  ""]
        if undecided:
            lines += ["Undecided: " + ", ".join(f"**{v.get('id')}**" for v in undecided)
                      + ". The matrix is not finished while one remains.", ""]

    # --- 2. deferrals -------------------------------------------------------
    deferred = []
    for vector in vectors:
        if state(vector) == "deferred":
            until = disposition(vector).get("until")
            key = date(until) if until is not None else "9999"
            deferred.append((key, vector))
    deferred.sort(key=lambda pair: pair[0])
    lines += ["## Deferrals, soonest first", ""]
    if not deferred:
        lines += ["None.", ""]
    else:
        lines += ["What has been decided and not done, with who owns it and until when. "
                  "A deferral past its date fails the check; a date that has been moved "
                  "shows every date it has had.", "",
                  "| Vector | Until | Owner | Mitigation | Reason |",
                  "| :--- | :--- | :--- | :--- | :--- |"]
        for _, vector in deferred:
            d = disposition(vector)
            until = date(d.get("until")) if d.get("until") is not None else "—"
            if d.get("until_label"):
                until = f"{until} ({cell(d['until_label'])})"
            codes = flagged.get(f"vectors/{vector.get('id')}", [])
            if "EXPIRED" in codes:
                until = f"**{until} — expired**"
            pushed = [h for h in d.get("history") or []
                      if isinstance(h, dict) and h.get("state") == "deferred" and h.get("until")]
            if pushed:
                until += " · previously " + ", ".join(date(h["until"]) for h in pushed)
            lines.append(f"| **{vector.get('id')}** {cell(vector.get('title'))} | {until} | "
                         f"{cell(d.get('owner'))} | {ids(d.get('mitigations'))} | "
                         f"{cell(d.get('reason'))} |")
        lines.append("")

    if open_only:
        return "\n".join(lines).rstrip() + "\n"

    # --- 3. the matrix ------------------------------------------------------
    lines += ["## The matrix", ""]
    if not vectors:
        lines += ["None.", ""]
    else:
        lines += ["| Vector | Element | Category | Disposition | Owner | Mitigations |",
                  "| :--- | :--- | :--- | :--- | :--- | :--- |"]
        for vector in in_order(vectors, model):
            d = disposition(vector)
            s = state(vector)
            display, _ = name_of(model, vector.get("element"))
            shown = "**undecided**" if s is None else s
            codes = flagged.get(f"vectors/{vector.get('id')}", [])
            if s == "deferred" and "EXPIRED" in codes:
                shown = "deferred — **expired**"
            elif s is None and d.get("state"):
                shown = f"**{cell(d.get('state'))}** — not a disposition"
            if d.get("history"):
                shown += f" · changed {len(d['history'])}×"
            lines.append(f"| **{vector.get('id')}** {cell(vector.get('title'))} | "
                         f"`{vector.get('element')}` {cell(display)} | "
                         f"{label(vector.get('category'))} | {shown} | "
                         f"{cell(d.get('owner'))} | {ids(d.get('mitigations'))} |")
        lines.append("")

    # --- 4. mitigations -----------------------------------------------------
    lines += ["## Mitigations", ""]
    if not mitigations:
        lines += ["None.", ""]
    else:
        lines += ["Each control, where its requirement is written, where it lives, and "
                  "every vector it serves. A mitigation with a specification and no "
                  "implementation is designed and not built; one with an implementation "
                  "and no specification was found in the code rather than required of it.",
                  ""]
        for entry in mitigations:
            where = f"mitigations/{entry.get('id')}"
            flags = [c for c in flagged.get(where, []) if c == "ORPHAN_MITIGATION"]
            lines += [f"### {entry.get('id')} — {cell(entry.get('title'))}"
                      + (" · **orphaned**" if flags else ""), "",
                      cell(entry.get("control")), "",
                      "| | |", "| :--- | :--- |",
                      f"| Specified in | {cell(entry.get('specified_in'))} |",
                      f"| Implemented in | {cell(entry.get('implemented_in'))} |",
                      f"| Verification | {cell(entry.get('verification'))} |"]
            if entry.get("evidence") or entry.get("verification") == "manual":
                lines.append(f"| Evidence | {cell(entry.get('evidence'))} |")
            lines += [f"| Serves | {ids(entry.get('vectors'))} |", ""]

    # --- 5. acceptances -----------------------------------------------------
    accepted = [v for v in in_order(vectors, model) if state(v) == "accepted"]
    lines += ["## Acceptances", ""]
    if not accepted:
        lines += ["None.", ""]
    else:
        lines += ["Exposure knowingly carried: who accepted it, and on what reasoning, in "
                  "full. An acceptance is a claim its owner can be asked to defend.", ""]
        for vector in accepted:
            d = disposition(vector)
            lines += [f"### {vector.get('id')} — {cell(vector.get('title'))}", "",
                      f"Accepted by **{cell(d.get('owner'))}** on {date(d.get('decided'))}.", "",
                      cell(d.get("reason")), ""]
            for previous in d.get("history") or []:
                if isinstance(previous, dict):
                    until = f", until {date(previous['until'])}" if previous.get("until") else ""
                    lines += [f"> Previously *{cell(previous.get('state'))}*{until}"
                              f" ({date(previous.get('decided'))}): "
                              f"{cell(previous.get('reason'))}",
                              ""]

    # --- 6. retired ---------------------------------------------------------
    orphans = [g for g in report.gaps if g["code"] == "ORPHAN_MITIGATION"]
    retired_mitigations = [r for r in retired if str(r.get("id", "")).startswith("MIT-")]
    lines += ["## Retired", ""]
    if orphans:
        lines += ["Mitigations serving no live vector. Each stays, blocking, until a person "
                  "retires it with a reason: it may be real code that now protects nothing "
                  "anyone tracks, and that is a decision rather than a tidy-up.", ""]
        lines += [f"- **{g['element'].split('/', 1)[1]}** — {cell(g['message'])}" for g in orphans]
        lines.append("")
    if not retired_mitigations:
        lines += ["No mitigation has been retired.", ""]
    else:
        lines += ["| Id | Retired | Reason |", "| :--- | :--- | :--- |"]
        lines += [f"| {cell(r.get('id'))} | {date(r.get('retired'))} | {cell(r.get('reason'))} |"
                  for r in retired_mitigations]
        lines.append("")

    # --- 6b. answered findings ----------------------------------------------
    answers = [a for a in (register.get("answers") or []) if isinstance(a, dict)]
    if answers:
        lapsed = {g["element"].split("/", 1)[-1] for g in report.gaps
                  if g["code"] == "LAPSED_ANSWER"}
        lines += ["## Answered findings", ""]
        lines += ["Everything above was written by the people whose work it describes. A "
                  "scanner observes the system as built and knows none of it, which is why "
                  "these are the only rows here that can contradict the rest.", "",
                  "**A finding can lower confidence in a claim and can never raise it.** A "
                  "scan that reports nothing is recorded as no evidence, never as "
                  "confirmation.", ""]

        # Contradictions and model gaps first, because they are what a reader
        # came for: one says an attestation may be false, the other says the
        # diagram is missing part of the running system.
        def ordering(entry):
            if entry.get("answer") == "model_gap":
                return (0, str(entry.get("id")))
            if entry.get("contradiction"):
                return (1, str(entry.get("id")))
            return (2, str(entry.get("id")))

        for entry in sorted(answers, key=ordering):
            ident = str(entry.get("id"))
            answer = str(entry.get("answer") or "")
            where = cell(entry.get("where")) if entry.get("where") else "anywhere"
            heading = f"### {ident} — {cell(entry.get('scanner'))} `{cell(entry.get('rule'))}`"
            if ident in lapsed:
                heading += " · **lapsed**"
            lines += [heading, ""]
            if answer == "model_gap":
                lines += ["**The model does not describe this part of the system.** The "
                          "repair is the diagram rather than this register.", ""]
            elif entry.get("contradiction") == "disposition_revised":
                lines += ["**Contradiction — the control did not do what it claimed.** The "
                          "disposition moved.", ""]
            elif entry.get("contradiction") == "false_positive":
                lines += ["**Contradiction — judged a false positive**, with the reasoning "
                          "below rather than a silent suppression.", ""]
            lines += [f"| Scope | `{where}` |", "| :--- | :--- |",
                      f"| Answer | {answer or '—'} |"]
            if entry.get("vector"):
                lines.append(f"| Vector | {cell(entry.get('vector'))} |")
            lines += [f"| Answered | {date(entry.get('answered'))} |",
                      f"| Why | {cell(entry.get('reason'))} |", ""]
            if ident in lapsed:
                lines += ["> Argued against a model that has since changed. Read the change, "
                          "then re-argue it or record the new digest to say you have.", ""]

    # --- 7. transfer and avoid ----------------------------------------------
    slug = model.get("system", {}).get("slug", "<slug>")
    lines += [
        "## Where transfer and avoid are recorded", "",
        "Three dispositions, where a reader arriving from an ISO-shaped process expects "
        "four. The other two are recorded a layer up, in the artefacts that decide what "
        "applies, and this document points at them rather than restating them:", "",
        "| Treatment | Recorded as | In |", "| :--- | :--- | :--- |",
        "| Mitigate | `mitigated` and a mitigation id | this matrix |",
        "| Accept | `accepted`, an owner and a reason | this matrix |",
        f"| Transfer | the third party is an **element** in the model, with its own flows "
        f"and threats; the disposition here is `mitigated` where they operate the control "
        f"and `accepted` where only the loss is financed | `{slug}.dfd.yaml`, this matrix |",
        f"| Avoid | **not a vector at all** — a threat found not to apply, with a reason, "
        f"or a finding not promoted, with a reason, or a vector retired because the "
        f"exposure was designed out | `{cell(register.get('threats'))}` (its "
        f"`controlled` and `not_applicable` verdicts), the register's `dismissed` and "
        f"`retired` sections |",
        "",
    ]

    # --- 8. limits ----------------------------------------------------------
    lines += [
        "## Limits", "",
        "**A disposition is a claim, not a fact.** \"Mitigated\" means somebody said so "
        "and named a control. The check requires the control to have a place — a "
        "specification, an implementation — and stops there; whether the code honours "
        "the requirement is a code review, and an annotation on the wrong function "
        "would satisfy every check here.",
        "",
        "**A specification reference proves the requirement was written, never that "
        "it was met.** It moves the mitigation to where an implementer will meet it, "
        "which is the point, and no further.",
        "",
        "**An `until` can be pushed.** A deferral moved forward every quarter stays "
        "green forever. Every date it has had is shown above, which is the only "
        "mitigation there is.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("register", help="path to the .vectors.yaml register")
    parser.add_argument("-o", "--output", help="write here instead of stdout")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD",
                        help="the date deferrals are judged against (default: today)")
    parser.add_argument("--root", metavar="DIR",
                        help="the repository root specified_in paths are relative to")
    parser.add_argument("--open-only", action="store_true",
                        help="just the summary and the deferrals, for a stand-up")
    args = parser.parse_args(argv)

    check_matrix = sibling("check_matrix")
    as_of = datetime.date.today()
    if args.as_of:
        as_of = check_matrix.as_date(args.as_of)
        if as_of is None:
            sys.exit(f"--as-of {args.as_of!r} is not a YYYY-MM-DD date")
    try:
        with open(args.register) as handle:
            register = yaml.safe_load(handle)
        reference = (register or {}).get("threats")
        if not isinstance(register, dict) or not reference:
            sys.exit(f"{args.register} is not a register: no enumeration named")
        here = os.path.dirname(os.path.abspath(args.register))
        threats_path = os.path.join(here, reference)
        with open(threats_path) as handle:
            enumeration = yaml.safe_load(handle)
        model_path = os.path.join(here, enumeration.get("model", ""))
        with open(model_path) as handle:
            model = yaml.safe_load(handle)
    except FileNotFoundError as exc:
        sys.exit(f"no such file: {exc.filename}")
    except yaml.YAMLError as exc:
        sys.exit(f"not valid YAML: {exc}")

    bases = (here, args.root or check_matrix.repository_root(here))
    report, _ = check_matrix.check(register, threats_path, as_of, bases=bases,
                                   model_path=model_path)
    document = render(register, model, report, as_of, open_only=args.open_only)
    if args.output:
        with open(args.output, "w") as handle:
            handle.write(document)
    else:
        sys.stdout.write(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
