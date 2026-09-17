#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Report every threat-model pairing that has no verdict.

The enumeration is over when this exits 0. A pairing is one element and one
threat category that can apply to it; which categories those are comes from the
tables in references/threat-mapping.md, held here as data.

Gaps are BLOCKING (the enumeration is not finished, or says something that
cannot be true) or ADVISORY (a pattern worth a reader's attention that may
still be legitimate).

A threat verdict also cites the sub-threats it is an instance of, by id, from
the catalogues in references/. Those are read at run time rather than copied in
here, so the documents stay the one place the taxonomy is stated.
"""

import argparse
import hashlib
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

BLOCKING, ADVISORY = "BLOCKING", "ADVISORY"

STRIDE = ("spoofing", "tampering", "repudiation", "information_disclosure",
          "denial_of_service", "elevation_of_privilege")
LINDDUN = ("linking", "identifying", "non_repudiation", "detecting",
           "data_disclosure", "unawareness", "non_compliance")

SECTIONS = ("actors", "processes", "stores", "flows")

# The two tables in references/threat-mapping.md, as data. tests/test_coverage.py
# parses that document and asserts these match it, so neither can be edited
# alone.
APPLIES = {
    "stride": {
        "actors": {"spoofing", "repudiation"},
        "processes": set(STRIDE),
        "stores": {"tampering", "repudiation", "information_disclosure",
                   "denial_of_service"},
        "flows": {"tampering", "information_disclosure", "denial_of_service"},
    },
    "linddun": {
        "actors": {"linking", "identifying", "unawareness"},
        "processes": set(LINDDUN),
        "stores": set(LINDDUN) - {"unawareness"},
        "flows": set(LINDDUN) - {"unawareness"},
    },
}

CATEGORIES = {"stride": set(STRIDE), "linddun": set(LINDDUN)}

VERDICTS = {"threat", "controlled", "not_applicable"}

# Which catalogue root each category's sub-threats hang from. LINDDUN's tree is
# rooted on the category abbreviation; STRIDE's patterns are grouped under the
# category letter instead, so the catalogue itself supplies the membership.
LINDDUN_ROOT = {
    "linking": "L", "identifying": "I", "non_repudiation": "NR", "detecting": "D",
    "data_disclosure": "DD", "unawareness": "U", "non_compliance": "NC",
}
STRIDE_LETTER = {
    "spoofing": "S", "tampering": "T", "repudiation": "R",
    "information_disclosure": "I", "denial_of_service": "D",
    "elevation_of_privilege": "E",
}

CATALOGUES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references")

PERSONAL = {"pseudonymous", "personal", "special_category"}

# Conditions beyond element type. The LINDDUN half of the grid is about personal
# data, so an element that touches none of it is not in that half at all.
CONDITIONAL = {
    ("linddun", "actors"): "is not marked as a data subject",
    ("linddun", "stores"): "holds no personal data",
    ("linddun", "flows"): "carries no personal data",
}


def catalogue(directory):
    """Read the two threat catalogues into {node id: (category, title)}.

    The title is carried alongside the category because `render_threats.py`
    needs it and would otherwise parse the same two documents a second way.

    Parsed rather than duplicated here as constants: 186 ids copied into this
    file would be a second source of truth for something the documents already
    state, and the two would drift. The cost is that this script now needs its
    references beside it, which is how it ships.
    """
    nodes = {}

    linddun = os.path.join(directory, "LINDDUN.md")
    with open(linddun) as handle:
        roots = {v: k for k, v in LINDDUN_ROOT.items()}
        for line in handle:
            match = re.match(r"^#{2,6}\s+([A-Z]{1,2}(?:\.\d+)*)\s+—?\s*(.*)$", line)
            if match and match.group(1).split(".")[0] in roots:
                nodes[match.group(1)] = ("linddun/" + roots[match.group(1).split(".")[0]],
                                         match.group(2).strip())

    stride = os.path.join(directory, "STRIDE.md")
    letters = {v: k for k, v in STRIDE_LETTER.items()}
    category = None
    with open(stride) as handle:
        for line in handle:
            match = re.match(r"^## ([A-Z]) — ", line)
            if match:
                category = letters.get(match.group(1))
                continue
            match = re.match(r"^\| ([A-Z]+\d+) \| (.+?) \|", line)
            if match and category:
                nodes[match.group(1)] = ("stride/" + category, match.group(2).strip())
    return nodes


class Report:
    def __init__(self):
        self.gaps = []

    def add(self, severity, code, element, message, category=None):
        self.gaps.append({
            "severity": severity, "code": code, "element": element,
            "category": category, "message": message,
            "key": ":".join(p for p in (code, element, category) if p),
        })

    @property
    def blocking(self):
        return [g for g in self.gaps if g["severity"] == BLOCKING]

    @property
    def advisory(self):
        return [g for g in self.gaps if g["severity"] == ADVISORY]


def digest(path):
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def personal(item, data_index):
    """True when this element references any data entry holding personal data."""
    for ident in item.get("data") or []:
        if data_index.get(ident) in PERSONAL:
            return True
    return False


def applicable(model, analysis):
    """Every pairing the frameworks ask about, as {(element_id, category)}.

    This is the grid. Its size is the enumeration's terminating condition, so
    the conditions below are the whole reason a model of 31 elements produces
    284 questions rather than 31 times thirteen.
    """
    data_index = {d.get("id"): d.get("personal_data")
                  for d in model.get("data") or [] if isinstance(d, dict)}
    grid = set()
    for framework in ("stride", "linddun"):
        if framework not in analysis:
            continue
        for section in SECTIONS:
            for item in model.get(section) or []:
                if not isinstance(item, dict) or not item.get("id"):
                    continue
                if framework == "linddun":
                    if section == "actors" and item.get("is_data_subject") is not True:
                        continue
                    if section in ("stores", "flows") and not personal(item, data_index):
                        continue
                for category in APPLIES[framework][section]:
                    grid.add((item["id"], f"{framework}/{category}"))
    return grid


def element_types(model):
    return {item["id"]: section
            for section in SECTIONS
            for item in model.get(section) or []
            if isinstance(item, dict) and item.get("id")}


def answered(item, field):
    value = item.get(field)
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def check(enumeration, model, model_path, nodes=None):
    report = Report()
    nodes = catalogue(CATALOGUES) if nodes is None else nodes

    for field in ("model", "model_digest", "analysis"):
        if not enumeration.get(field):
            report.add(BLOCKING, "MISSING_FIELD", "<file>",
                       f"{field} is missing or empty")

    # An empty verdicts list is the skeleton the agent writes on its first turn,
    # and every pairing it lacks is already reported as UNCOVERED. Absent is a
    # different thing: the file does not claim to be an enumeration at all.
    if not isinstance(enumeration.get("verdicts"), list):
        report.add(BLOCKING, "MISSING_FIELD", "<file>",
                   "verdicts is missing or is not a list")

    for field in ("open_questions", "assumptions"):
        carried = enumeration.get("carried_forward")
        if not isinstance(carried, dict) or field not in carried:
            report.add(BLOCKING, "MISSING_FIELD", "carried_forward",
                       f"{field} is not carried forward from the model; "
                       "an empty list is an answer, an absent key is not")

    if enumeration.get("model_digest") and enumeration["model_digest"] != digest(model_path):
        report.add(BLOCKING, "STALE_MODEL", "<file>",
                   "model_digest does not match the model's current bytes; "
                   "the enumeration describes a model that has since changed")

    analysis = enumeration.get("analysis") or []
    if not isinstance(analysis, list):
        analysis = []
    types = element_types(model)
    grid = applicable(model, analysis)
    seen = {}

    for entry in enumeration.get("verdicts") or []:
        if not isinstance(entry, dict):
            report.add(BLOCKING, "BAD_ITEM", "verdicts", "entries must be mappings")
            continue
        element = entry.get("element")
        category = entry.get("category")
        where = f"{element}" if element else "<unnamed>"

        if element not in types:
            report.add(BLOCKING, "UNRESOLVED_ELEMENT", where,
                       "no element with this id in the model", category)
            continue

        framework, _, name = str(category or "").partition("/")
        if framework not in CATEGORIES or name not in CATEGORIES[framework]:
            report.add(BLOCKING, "BAD_CATEGORY", where,
                       f"{category!r} is not a threat category; expected "
                       "stride/<name> or linddun/<name>", category)
            continue
        if framework not in analysis:
            report.add(BLOCKING, "BAD_CATEGORY", where,
                       f"{framework} is not in this model's analysis", category)
            continue
        section = types[element]
        if name not in APPLIES[framework][section]:
            report.add(BLOCKING, "BAD_CATEGORY", where,
                       f"{category} does not apply to a {section[:-1]}", category)
            continue
        if (element, category) not in grid:
            report.add(BLOCKING, "BAD_CATEGORY", where,
                       f"{category} does not apply here: this {section[:-1]} "
                       f"{CONDITIONAL[(framework, section)]}", category)
            continue

        pairing = (element, category)
        if pairing in seen:
            report.add(BLOCKING, "DUPLICATE_VERDICT", where,
                       "a second verdict for a pairing already verdicted", category)
            continue
        seen[pairing] = entry

        verdict = entry.get("verdict")
        if verdict not in VERDICTS:
            report.add(BLOCKING, "BAD_VERDICT", where,
                       f"{verdict!r} is not a verdict; expected one of "
                       f"{', '.join(sorted(VERDICTS))}", category)
            continue
        if verdict == "threat":
            for field in ("summary", "detail"):
                if not answered(entry, field):
                    report.add(BLOCKING, "MISSING_DETAIL", where,
                               f"a threat with no {field}", category)
            check_nodes(report, entry, where, category, framework, nodes)
        elif not answered(entry, "reason"):
            report.add(BLOCKING, "MISSING_REASON", where,
                       f"a {verdict} verdict with no reason; a dismissal a reader "
                       "cannot disagree with is not a dismissal", category)

    for element, category in sorted(grid - set(seen)):
        report.add(BLOCKING, "UNCOVERED", element,
                   "no verdict for this pairing", category)

    for element in sorted({e for e, _ in grid}):
        verdicts = [v.get("verdict") for (el, _), v in seen.items() if el == element]
        if verdicts and all(v == "not_applicable" for v in verdicts):
            report.add(ADVISORY, "ALL_DISMISSED", element,
                       f"every one of this {types[element][:-1]}'s "
                       f"{len(verdicts)} categories was dismissed as not applicable")

    return report, grid


def check_nodes(report, entry, where, category, framework, nodes):
    """A finding should name what it is an instance of, not only its category.

    Required for LINDDUN, whose tree covers every category to its leaves.
    Optional for STRIDE, because the catalogue's coverage is uneven — four of
    the fifteen element-and-category cells the grid asks about have no pattern
    to cite at all, and a requirement nobody can satisfy is one people route
    around rather than meet.
    """
    cited = entry.get("nodes") or []
    if not isinstance(cited, list):
        report.add(BLOCKING, "BAD_NODES", where, "nodes must be a list", category)
        return
    if not cited:
        if framework == "linddun":
            report.add(BLOCKING, "MISSING_NODE", where,
                       "a LINDDUN threat citing no node from the catalogue; "
                       "name what this is an instance of, at any depth",
                       category)
        return

    for node in cited:
        entry = nodes.get(node)
        owner = entry[0] if entry else None
        if owner is None:
            report.add(BLOCKING, "UNKNOWN_NODE", where,
                       f"{node!r} is not in the threat catalogue", category)
        elif owner != category:
            report.add(BLOCKING, "WRONG_NODE", where,
                       f"{node} belongs to {owner}, not to this verdict's category",
                       category)
        elif framework == "linddun" and "." not in str(node):
            report.add(ADVISORY, "SHALLOW_NODE", where,
                       f"{node} is the category itself; a sub-threat would say "
                       "something the category field does not",
                       category)


def load(path, what):
    try:
        with open(path) as handle:
            document = yaml.safe_load(handle)
    except FileNotFoundError:
        # from None, because the traceback is noise: the caller turns this into a
        # usage message and exit 2, and the chained OSError says nothing more.
        raise SystemExit((2, f"no such {what}: {path}")) from None
    except yaml.YAMLError as exc:
        raise SystemExit((2, f"{path} is not valid YAML: {exc}")) from None
    if not isinstance(document, dict):
        raise SystemExit((2, f"{path} should be a mapping"))
    return document


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("enumeration", help="path to the .threats.yaml enumeration")
    parser.add_argument("--json", action="store_true", help="emit gaps as JSON")
    args = parser.parse_args(argv)

    try:
        enumeration = load(args.enumeration, "enumeration")
        reference = enumeration.get("model")
        if not reference:
            raise SystemExit((2, f"{args.enumeration} does not name a model"))
        model_path = os.path.join(os.path.dirname(args.enumeration) or ".", reference)
        model = load(model_path, "model")
    except SystemExit as exit_:
        if isinstance(exit_.code, tuple):
            code, message = exit_.code
            print(message, file=sys.stderr)
            return code
        raise

    report, grid = check(enumeration, model, model_path)

    if args.json:
        print(json.dumps({
            "pairings": len(grid),
            "blocking": len(report.blocking),
            "advisory": len(report.advisory),
            "complete": not report.blocking,
            "gaps": report.gaps,
        }, indent=2))
        return 0 if not report.blocking else 1

    # Grouped by element, as validate_dfd.py groups gaps: one element's
    # remaining categories are one sitting's work for whoever is enumerating.
    for severity, gaps in ((BLOCKING, report.blocking), (ADVISORY, report.advisory)):
        if not gaps:
            continue
        groups = {}
        for gap in gaps:
            groups.setdefault(gap["element"], []).append(gap)
        print(f"\n{severity} — {len(gaps)} gap(s) across {len(groups)} element(s)")
        print("=" * 60)
        for element, items in groups.items():
            print(f"\n  {element}")
            for gap in items:
                where = f"{gap['category']}: " if gap["category"] else ""
                print(f"    - {where}{gap['message']}")

    print()
    covered = len(grid) - len([g for g in report.blocking if g["code"] == "UNCOVERED"])
    print(f"{covered}/{len(grid)} pairings verdicted.")
    if report.blocking:
        print(f"Not complete: {len(report.blocking)} blocking, "
              f"{len(report.advisory)} advisory.")
        return 1
    if report.advisory:
        print(f"Coverage complete. {len(report.advisory)} advisory item(s) — coverage "
              "is not seriousness, and these are where that shows.")
    else:
        print("Coverage complete: every applicable pairing has a verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
