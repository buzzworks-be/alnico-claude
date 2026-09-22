#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Render a threat enumeration as Markdown.

A pure function of the enumeration, as render_dfd.py is of the model.
Regenerate rather than hand-editing: the YAML stays the source of truth.

Findings come first. The coverage a complete enumeration produces is large —
324 verdicts for a 35-element model — and a reader who meets three hundred
dismissals before the first finding does not reach the finding.
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


def coverage():
    """The sibling script, for the grid and the catalogues.

    Imported rather than reimplemented: the applicable grid and the node
    taxonomy are each stated once, and a renderer that computed either of them
    a second way could disagree with the check that gates the document.
    """
    return sibling("check_coverage")


def sibling(name):
    """A sibling script, imported rather than reimplemented."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def label(category):
    framework, _, name = category.partition("/")
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


def cited(nodes, catalogue):
    out = []
    for node in nodes or []:
        entry = catalogue.get(node)
        out.append(f"`{node}` {entry[1]}" if entry else f"`{node}`")
    return out


def render(enumeration, model, catalogue, grid, findings_only=False):
    verdicts = enumeration.get("verdicts") or []
    lines = [f"# Threat enumeration — {model.get('system', {}).get('name', 'unnamed')}",
             "",
             f"Generated from `{enumeration.get('model')}` by `render_threats.py`. "
             "Do not edit; regenerate.",
             ""]

    threats = [v for v in verdicts if v.get("verdict") == "threat"]

    lines += ["## Findings", ""]
    if not threats:
        lines += ["None. Every applicable pairing was considered and dismissed, "
                  "which is a result worth reading twice rather than a clean bill "
                  "of health.", ""]
    else:
        lines += [f"{len(threats)} finding(s), grouped by the element they were "
                  "found on.", ""]
        for section in SECTIONS:
            here = [t for t in threats if name_of(model, t["element"])[1] == section]
            if not here:
                continue
            lines += [f"### {section.title()}", ""]
            for element in dict.fromkeys(t["element"] for t in here):
                display, _ = name_of(model, element)
                lines += [f"#### `{element}` — {display}", ""]
                for threat in [t for t in here if t["element"] == element]:
                    lines += [f"**{label(threat['category'])}** — "
                              f"{cell(threat.get('summary'))}", ""]
                    references = cited(threat.get("nodes"), catalogue)
                    if references:
                        lines += ["> " + " · ".join(references), ""]
                    lines += [cell(threat.get("detail")), ""]

    if findings_only:
        return "\n".join(lines).rstrip() + "\n"

    # --- coverage ---------------------------------------------------------
    lines += ["## Coverage", ""]
    counts = {}
    for verdict in verdicts:
        _, section = name_of(model, verdict["element"])
        framework = str(verdict.get("category", "")).partition("/")[0]
        counts[(section, framework)] = counts.get((section, framework), 0) + 1
    lines += ["| Section | STRIDE | LINDDUN | Total |", "| :--- | ---: | ---: | ---: |"]
    for section in SECTIONS:
        stride = counts.get((section, "stride"), 0)
        linddun = counts.get((section, "linddun"), 0)
        if stride or linddun:
            lines.append(f"| {section} | {stride} | {linddun} | {stride + linddun} |")
    lines += [f"| **all** | **{sum(v for (_, f), v in counts.items() if f == 'stride')}** "
              f"| **{sum(v for (_, f), v in counts.items() if f == 'linddun')}** "
              f"| **{len(verdicts)}** |", ""]

    tally = {}
    for verdict in verdicts:
        tally[verdict.get("verdict")] = tally.get(verdict.get("verdict"), 0) + 1
    lines += ["| Verdict | Count |", "| :--- | ---: |"]
    for kind in ("threat", "controlled", "not_applicable"):
        lines.append(f"| {kind} | {tally.get(kind, 0)} |")
    lines += ["",
              f"{len(verdicts)} of {len(grid)} applicable pairings verdicted.",
              ""]

    # --- dismissed --------------------------------------------------------
    lines += ["## Considered and dismissed", "",
              "One line each. The reasons are the point: a dismissal a reader "
              "cannot disagree with is not a dismissal.", ""]
    for section in SECTIONS:
        rows = [v for v in verdicts
                if v.get("verdict") != "threat"
                and name_of(model, v["element"])[1] == section]
        if not rows:
            continue
        lines += [f"### {section.title()}", "",
                  "| Element | Category | Verdict | Reason |",
                  "| :--- | :--- | :--- | :--- |"]
        for row in rows:
            lines.append(f"| `{row['element']}` | {label(row['category'])} "
                         f"| {row.get('verdict')} | {cell(row.get('reason'))} |")
        lines.append("")

    # --- carried forward --------------------------------------------------
    carried = enumeration.get("carried_forward") or {}
    lines += ["## Carried forward from the model", ""]
    for key, heading in (("open_questions", "Open questions"),
                         ("assumptions", "Assumptions")):
        items = carried.get(key) or []
        lines += [f"### {heading}", ""]
        lines += [f"- {cell(item)}" for item in items] or ["None recorded."]
        lines.append("")

    lines += [
        "## Limits", "",
        "**Coverage is mechanically checkable; seriousness is not.** Every "
        "pairing here has a verdict, which is what the script can prove. That "
        "any of them was answered seriously is not something a script can "
        "establish, and a complete enumeration of shallow dismissals would "
        "satisfy every check that produced this document.",
        "",
        "**This is analysis of a model, not of a system.** Every finding rests "
        "on the model being an accurate description, and on the assumptions "
        "carried forward above. Where the system and the model differ, this "
        "document describes the model.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("enumeration", help="path to the .threats.yaml enumeration")
    parser.add_argument("-o", "--output", help="write here instead of stdout")
    parser.add_argument("--findings-only", action="store_true",
                        help="just the findings, for pasting into a review")
    args = parser.parse_args(argv)

    check = coverage()
    try:
        with open(args.enumeration) as handle:
            enumeration = yaml.safe_load(handle)
        reference = (enumeration or {}).get("model")
        if not isinstance(enumeration, dict) or not reference:
            sys.exit(f"{args.enumeration} is not an enumeration: no model named")
        model_path = os.path.join(os.path.dirname(args.enumeration) or ".", reference)
        with open(model_path) as handle:
            model = yaml.safe_load(handle)
    except FileNotFoundError as exc:
        sys.exit(f"no such file: {exc.filename}")
    except yaml.YAMLError as exc:
        sys.exit(f"not valid YAML: {exc}")

    grid = check.applicable(model, enumeration.get("analysis") or [])
    document = render(enumeration, model, check.catalogue(check.CATALOGUES), grid,
                      findings_only=args.findings_only)

    if not args.findings_only:
        document = sibling("check_traceability").stamp(document, args.enumeration)
    if args.output:
        with open(args.output, "w") as handle:
            handle.write(document)
    else:
        sys.stdout.write(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
