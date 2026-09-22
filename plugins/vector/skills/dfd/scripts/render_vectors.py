#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Render a register as the threat model document.

What is tracked and why, then why the rest is not. A pure function of the
register: regenerate rather than hand-editing, since the YAML is the source of
truth. This is a different view of the same file from the matrix, because it
serves a different reader — this is read to understand the threat model, the
matrix to see what is being done about it.
"""

import argparse
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
    """A sibling script, imported rather than reimplemented.

    The catalogue is parsed in check_coverage.py and the orphan report is
    computed in check_vectors.py; a renderer that did either a second way could
    disagree with the checks that gate the document.
    """
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


def name_of(model, element):
    for section in SECTIONS:
        for item in model.get(section) or []:
            if isinstance(item, dict) and item.get("id") == element:
                return item.get("name") or element, section
    return element, "unknown"


def element_heading(element, display):
    return f"`{element}` — {display}"


def vector_heading(vector, orphaned=()):
    """The heading this document gives a vector, as one function.

    A heading rather than bold text because this is the one place every vector
    is written out in full, so it is what everything else points at — and only
    a heading has a fragment to point at. render_matrix.py derives its links
    from this string rather than from a copy of the format, so a change here
    moves them with it instead of breaking them silently.
    """
    flag = " · **orphaned**" if vector.get("id") in orphaned else ""
    return f"{vector.get('id')} — {cell(vector.get('title'))}{flag}"


def cited(nodes, catalogue):
    return [f"`{n}` {catalogue[n][1]}" if n in catalogue else f"`{n}`" for n in nodes]


def nodes_for(vector, enumeration):
    """The catalogue nodes the vector's source verdict(s) cited."""
    index = {(v.get("element"), v.get("category")): v.get("nodes") or []
             for v in enumeration.get("verdicts") or [] if isinstance(v, dict)}
    if vector.get("source") == "authored":
        pairs = [(c.get("element"), c.get("category")) for c in vector.get("verdicts") or []]
    elif vector.get("source") == "verdict":
        pairs = [(vector.get("element"), vector.get("category"))]
    else:
        pairs = []
    out = []
    for pair in pairs:
        for node in index.get(pair, []):
            if node not in out:
                out.append(node)
    return out


def render(register, enumeration, model, catalogue, report, tracked_only=False):
    vectors = [v for v in register.get("vectors") or [] if isinstance(v, dict)]
    orphaned = {g["element"].split("/", 1)[1] for g in report.gaps if g["code"] == "ORPHAN_VECTOR"}
    lines = [f"# Threat model — {model.get('system', {}).get('name', 'unnamed')}",
             "",
             f"Generated from `{register.get('threats')}` and the register beside it by "
             "`render_vectors.py`. Do not edit; regenerate.",
             ""]

    # --- tracked ----------------------------------------------------------
    lines += ["## Tracked vectors", ""]
    if not vectors:
        why = register.get("empty_because")
        lines += ["None." + (f" {cell(why)}" if why else "") ]
        lines.append("")
    else:
        lines += [f"{len(vectors)} vector(s), grouped by the element each is anchored to. "
                  "A chain lists the findings it ties together.", ""]
        for section in SECTIONS:
            here = [v for v in vectors if name_of(model, v.get("element"))[1] == section]
            if not here:
                continue
            lines += [f"### {section.title()}", ""]
            for element in dict.fromkeys(v.get("element") for v in here):
                display, _ = name_of(model, element)
                lines += [f"#### {element_heading(element, display)}", ""]
                for vector in [v for v in here if v.get("element") == element]:
                    lines += [f"##### {vector_heading(vector, orphaned)}", "",
                              f"{label(vector.get('category'))} · "
                              f"promoted {cell(vector.get('promoted'))}"
                              + (" · from the open question"
                                 if vector.get("source") == "question" else "")]
                    references = cited(nodes_for(vector, enumeration), catalogue)
                    if references:
                        lines += ["", "> " + " · ".join(references)]
                    if vector.get("source") == "authored":
                        chain = ", ".join(f"`{c.get('element')}` {label(c.get('category'))}"
                                          for c in vector.get("verdicts") or []
                                          if isinstance(c, dict))
                        lines += ["", f"Chains: {chain}"]
                    if vector.get("source") == "question":
                        lines += ["", f"> {cell(vector.get('question'))}"]
                    lines += ["",
                              f"**Attack.** {cell(vector.get('attack'))}", "",
                              f"**Impact.** {cell(vector.get('impact'))}", "",
                              f"**Context.** {cell(vector.get('context'))}", ""]

    if tracked_only:
        return "\n".join(lines).rstrip() + "\n"

    # --- not promoted -----------------------------------------------------
    dismissed = [d for d in register.get("dismissed") or [] if isinstance(d, dict)]
    lines += ["## Not promoted", "",
              "Every finding considered and not tracked, with the reason. The reason is the "
              "point: a dismissal nobody can disagree with is not a decision.", ""]
    if not dismissed:
        lines += ["None.", ""]
    else:
        lines += ["| Finding | Reason |", "| :--- | :--- |"]
        for entry in dismissed:
            if entry.get("question"):
                what = f"open question: {cell(entry['question'])}"
            else:
                what = f"`{entry.get('element')}` {label(entry.get('category'))}"
            lines.append(f"| {what} | {cell(entry.get('reason'))} |")
        lines.append("")

    # --- orphaned ---------------------------------------------------------
    lines += ["## Orphaned", ""]
    if not orphaned:
        lines += ["None. Every vector's source is still a finding in the enumeration.", ""]
    else:
        lines += ["Vectors whose source is no longer in the enumeration — the model changed "
                  "and the enumeration was re-run. Each stays until a person retires it with a "
                  "reason; it may carry a mitigation and an annotation.", ""]
        for gap in report.gaps:
            if gap["code"] == "ORPHAN_VECTOR":
                lines.append(f"- **{gap['element'].split('/', 1)[1]}** — {cell(gap['message'])}")
        lines.append("")

    # --- retired ----------------------------------------------------------
    retired = [r for r in register.get("retired") or [] if isinstance(r, dict)]
    lines += ["## Retired", ""]
    if not retired:
        lines += ["None.", ""]
    else:
        lines += ["| Id | Retired | Reason |", "| :--- | :--- | :--- |"]
        lines += [f"| {cell(r.get('id'))} | {cell(r.get('retired'))} | {cell(r.get('reason'))} |"
                  for r in retired]
        lines.append("")

    # --- open questions ---------------------------------------------------
    questions = [q for q in ((enumeration.get("carried_forward") or {}).get("open_questions") or [])
                 if isinstance(q, str)]
    lines += ["## Open questions from the model", ""]
    if not questions:
        lines += ["None were carried forward.", ""]
    else:
        def norm(value):
            return " ".join(str(value).split())

        fate = {}
        for vector in vectors:
            if vector.get("source") == "question":
                fate[norm(vector.get("question"))] = f"promoted as **{vector.get('id')}**"
        for entry in dismissed:
            if entry.get("question"):
                fate.setdefault(norm(entry["question"]),
                                f"not promoted — {cell(entry.get('reason'))}")
        lines += ["| Question | What became of it |", "| :--- | :--- |"]
        lines += [f"| {cell(q)} | {fate.get(norm(q), '**undecided**')} |" for q in questions]
        lines.append("")

    lines += [
        "## Limits", "",
        "**Every finding was decided; nothing proves the right ones were promoted.** "
        "The script can show that each threat verdict and each open question ended up "
        "as a vector, in a chain, or dismissed with a reason. Whether those were the "
        "right calls is the judgement this step exists for, and no check reaches it.",
        "",
        "**A vector is a decision to track, not a decision to act.** What is being done "
        "about each is the matrix, rendered separately from the same register.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("register", help="path to the .vectors.yaml register")
    parser.add_argument("-o", "--output", help="write here instead of stdout")
    parser.add_argument("--tracked-only", action="store_true",
                        help="just the tracked vectors, for pasting into a review")
    args = parser.parse_args(argv)

    check_coverage, check_vectors = sibling("check_coverage"), sibling("check_vectors")
    try:
        with open(args.register) as handle:
            register = yaml.safe_load(handle)
        reference = (register or {}).get("threats")
        if not isinstance(register, dict) or not reference:
            sys.exit(f"{args.register} is not a register: no enumeration named")
        threats_path = os.path.join(os.path.dirname(args.register) or ".", reference)
        with open(threats_path) as handle:
            enumeration = yaml.safe_load(handle)
        model_path = os.path.join(os.path.dirname(threats_path) or ".",
                                  enumeration.get("model", ""))
        with open(model_path) as handle:
            model = yaml.safe_load(handle)
    except FileNotFoundError as exc:
        sys.exit(f"no such file: {exc.filename}")
    except yaml.YAMLError as exc:
        sys.exit(f"not valid YAML: {exc}")

    catalogue = check_coverage.catalogue(check_coverage.CATALOGUES)
    report, _ = check_vectors.check(register, enumeration, threats_path, catalogue=catalogue)
    document = render(register, enumeration, model, catalogue, report,
                      tracked_only=args.tracked_only)
    if not args.tracked_only:
        document = sibling("check_traceability").stamp(document, args.register)
    if args.output:
        with open(args.output, "w") as handle:
            handle.write(document)
    else:
        sys.stdout.write(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
