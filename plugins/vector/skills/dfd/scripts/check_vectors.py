#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Report every finding in an enumeration that nobody has decided about.

Promotion is over when this exits 0. Every `threat` verdict in the enumeration
and every open question carried forward from the model ends up in exactly one
of three places: as a vector's source, in an authored vector's chain, or in
`dismissed` with a reason. That is the whole terminating condition — an open
item is closed by doing the work or by recording the decision not to.

Two things look alike and are kept apart. An ORPHAN is a vector whose source no
longer exists in the enumeration, because the model changed and the
enumeration was re-run; it stays in the file, blocking, until a person retires
it with a reason, since it may carry a mitigation and an annotation. A
dismissal whose pairing no longer exists is merely stale — nothing downstream
references a dismissal — and is reported as UNRESOLVED so it can be dropped.

Gaps are BLOCKING (promotion is not finished, or the register says something
that cannot be true) or ADVISORY (a pattern worth a reader's eye that may still
be legitimate).
"""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

BLOCKING, ADVISORY = "BLOCKING", "ADVISORY"

HERE = os.path.dirname(os.path.abspath(__file__))

SOURCES = {"verdict", "authored", "question"}
VECTOR_ID = re.compile(r"^VEC-\d{4}$")
RETIRED_ID = re.compile(r"^(VEC|MIT)-\d{4}$")
VECTOR_FIELDS = ("id", "title", "element", "category", "source", "promoted",
                 "attack", "impact", "context")


def coverage():
    """The sibling script, for the catalogue — parsed once, there."""
    spec = importlib.util.spec_from_file_location(
        "check_coverage", os.path.join(HERE, "check_coverage.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Report:
    def __init__(self):
        self.gaps = []

    def add(self, severity, code, element, message, field=None):
        self.gaps.append({
            "severity": severity, "code": code, "element": element,
            "field": field, "message": message,
            "key": ":".join(p for p in (code, element, field) if p),
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


def answered(item, field):
    value = item.get(field)
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and not value:
        return False
    return True


def pairing(entry):
    return (entry.get("element"), entry.get("category"))


def label(pair):
    return f"{pair[0]}/{pair[1]}"


def check(register, enumeration, threats_path, catalogue=None):
    report = Report()

    for field in ("threats", "threats_digest"):
        if not answered(register, field):
            report.add(BLOCKING, "MISSING_FIELD", "<file>", f"{field} is missing or empty",
                       field=field)
    if answered(register, "threats_digest") and register["threats_digest"] != digest(threats_path):
        report.add(BLOCKING, "STALE_THREATS", "<file>",
                   "threats_digest does not match the enumeration's current bytes; "
                   "the register was reconciled against an enumeration that has since changed")

    vectors = register.get("vectors")
    if vectors is None:
        report.add(BLOCKING, "MISSING_FIELD", "<file>", "vectors is missing; an empty list is "
                   "a register with nothing promoted, an absent key is not a register",
                   field="vectors")
        vectors = []
    dismissed = register.get("dismissed") or []
    retired = register.get("retired") or []

    # --- what the enumeration offers for decision --------------------------
    verdicts = [v for v in (enumeration.get("verdicts") or []) if isinstance(v, dict)]
    threats = {pairing(v) for v in verdicts if v.get("verdict") == "threat"}
    nodes_of = {pairing(v): list(v.get("nodes") or []) for v in verdicts
                if v.get("verdict") == "threat"}
    questions = [q for q in ((enumeration.get("carried_forward") or {}).get("open_questions") or [])
                 if isinstance(q, str)]

    # --- vectors ----------------------------------------------------------
    decided = {}      # pairing or ("question", text) -> [where decided]
    seen_ids = {}
    for entry in vectors:
        if not isinstance(entry, dict):
            report.add(BLOCKING, "BAD_ITEM", "vectors", "entries must be mappings")
            continue
        ident = entry.get("id") or "<unnamed>"
        where = f"vectors/{ident}"
        if not VECTOR_ID.match(str(entry.get("id") or "")):
            report.add(BLOCKING, "BAD_ID", where,
                       f"{entry.get('id')!r} is not of the form VEC-NNNN", field="id")
        if ident in seen_ids:
            report.add(BLOCKING, "DUPLICATE_ID", where,
                       "a second vector with this id — two branches took the same "
                       "number; renumber the later one", field="id")
        seen_ids[ident] = entry
        for field in VECTOR_FIELDS:
            if not answered(entry, field):
                report.add(BLOCKING, "MISSING_FIELD", where, f"{field} is unanswered", field=field)

        source = entry.get("source")
        if source not in SOURCES:
            report.add(BLOCKING, "BAD_SOURCE", where,
                       f"{source!r} is not a source; expected one of "
                       f"{', '.join(sorted(SOURCES))}", field="source")
            continue

        primary = pairing(entry)
        if source == "verdict":
            claims = [primary]
        elif source == "authored":
            chain = entry.get("verdicts") or []
            claims = [pairing(c) for c in chain if isinstance(c, dict)]
            if len(claims) < 2:
                report.add(BLOCKING, "THIN_CHAIN", where,
                           "an authored vector chains fewer than two verdicts; a chain of one "
                           "is a promoted verdict and should say so", field="verdicts")
            elif primary not in claims:
                report.add(BLOCKING, "THIN_CHAIN", where,
                           f"the primary pairing {label(primary)} is not among the verdicts "
                           "it chains", field="verdicts")
        else:
            if not answered(entry, "question"):
                report.add(BLOCKING, "MISSING_FIELD", where, "question is unanswered",
                           field="question")
                continue
            claims = [("question", " ".join(entry["question"].split()))]

        for claim in claims:
            if claim[0] == "question":
                if claim[1] not in {" ".join(q.split()) for q in questions}:
                    report.add(BLOCKING, "ORPHAN_VECTOR", where,
                               "the open question this was promoted from is no longer carried "
                               "forward; retire the vector with a reason, or restore the question")
            elif claim not in threats:
                report.add(BLOCKING, "ORPHAN_VECTOR", where,
                           f"no threat verdict for {label(claim)} in the enumeration any more; "
                           "retire the vector with a reason rather than deleting it")
            decided.setdefault(claim, []).append(where)

    # --- dismissals -------------------------------------------------------
    for index, entry in enumerate(dismissed):
        where = f"dismissed/{index}"
        if not isinstance(entry, dict):
            report.add(BLOCKING, "BAD_ITEM", "dismissed", "entries must be mappings")
            continue
        if not answered(entry, "reason"):
            report.add(BLOCKING, "MISSING_REASON", where,
                       "a dismissal with no reason; a decision nobody can disagree with "
                       "is not a decision", field="reason")
        if answered(entry, "question"):
            text = " ".join(entry["question"].split())
            if text not in {" ".join(q.split()) for q in questions}:
                report.add(BLOCKING, "UNRESOLVED_QUESTION", where,
                           "dismisses an open question the enumeration does not carry forward")
            decided.setdefault(("question", text), []).append(where)
        elif entry.get("element") and entry.get("category"):
            pair = pairing(entry)
            if pair not in threats:
                report.add(BLOCKING, "UNRESOLVED_PAIRING", where,
                           f"dismisses {label(pair)}, which has no threat verdict in the "
                           "enumeration; a stale dismissal looks like a decision and is not")
            decided.setdefault(pair, []).append(where)
        else:
            report.add(BLOCKING, "BAD_ITEM", where,
                       "a dismissal names neither a pairing nor a question")

    # --- decided twice, undecided ------------------------------------------
    for claim, places in decided.items():
        if len(places) > 1:
            name = claim[1] if claim[0] == "question" else label(claim)
            report.add(BLOCKING, "DECIDED_TWICE", places[0],
                       f"{name} is decided in {len(places)} places: {', '.join(places)}")
    undecided = sorted(p for p in threats if p not in decided)
    for pair in undecided:
        report.add(BLOCKING, "UNDECIDED_VERDICT", pair[0],
                   "a threat verdict neither promoted, chained nor dismissed", field=pair[1])
    for question in questions:
        if ("question", " ".join(question.split())) not in decided:
            report.add(BLOCKING, "UNDECIDED_QUESTION", "carried_forward",
                       f"an open question neither promoted nor dismissed: {question}")

    # --- retired ----------------------------------------------------------
    retired_ids = set()
    for index, entry in enumerate(retired):
        where = f"retired/{index}"
        if not isinstance(entry, dict):
            report.add(BLOCKING, "BAD_ITEM", "retired", "entries must be mappings")
            continue
        ident = str(entry.get("id") or "")
        if not RETIRED_ID.match(ident):
            report.add(BLOCKING, "BAD_ID", where, f"{ident!r} is not a VEC or MIT id", field="id")
        if ident in retired_ids:
            report.add(BLOCKING, "DUPLICATE_ID", where, "retired twice", field="id")
        retired_ids.add(ident)
        for field in ("reason", "retired"):
            if not answered(entry, field):
                report.add(BLOCKING, "MISSING_FIELD", where, f"{field} is unanswered", field=field)
        if ident in seen_ids:
            report.add(BLOCKING, "REUSED_ID", where,
                       f"{ident} is both live and retired; a retired id is never reused",
                       field="id")

    # --- the register as a whole ---------------------------------------------
    if not vectors and not answered(register, "empty_because"):
        report.add(BLOCKING, "EMPTY_UNEXPLAINED", "<file>",
                   "nothing is promoted and empty_because is not stated; an empty register "
                   "with no reason is unfinished, not clean", field="empty_because")
    promoted_pairs = {c for c, places in decided.items()
                      if c[0] != "question" and any(p.startswith("vectors/") for p in places)}
    if threats and not promoted_pairs and vectors:
        report.add(ADVISORY, "ALL_DISMISSED", "<file>",
                   f"every one of the enumeration's {len(threats)} findings is dismissed; the "
                   "vectors here come only from questions or chains that resolve to nothing")

    # --- for the skill: what is left, in the shape one sitting takes ---------
    by_element = {}
    for pair in undecided:
        by_element.setdefault(pair[0], []).append(pair[1])
    shared = {}
    for pair in undecided:
        for node in nodes_of.get(pair, []):
            shared.setdefault(node, []).append(label(pair))
    shared = {n: ps for n, ps in shared.items() if len(ps) > 1}
    if catalogue:
        shared = {f"{n} {catalogue[n][1]}" if n in catalogue else n: ps for n, ps in shared.items()}
    numbers = [int(i.split("-")[1]) for i in list(seen_ids) + list(retired_ids)
               if VECTOR_ID.match(str(i))]
    guidance = {
        "undecided_by_element": by_element,
        "shared_nodes": shared,
        "next_id": f"VEC-{(max(numbers) + 1 if numbers else 1):04d}",
    }
    return report, guidance


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
    parser.add_argument("register", help="path to the .vectors.yaml register")
    parser.add_argument("--json", action="store_true", help="emit gaps and guidance as JSON")
    args = parser.parse_args(argv)

    try:
        register = load(args.register, "register")
        reference = register.get("threats")
        if not reference:
            raise SystemExit((2, f"{args.register} does not name an enumeration"))
        threats_path = os.path.join(os.path.dirname(args.register) or ".", reference)
        enumeration = load(threats_path, "enumeration")
    except SystemExit as exit_:
        if isinstance(exit_.code, tuple):
            print(exit_.code[1], file=sys.stderr)
            return exit_.code[0]
        raise

    check_coverage = coverage()
    report, guidance = check(register, enumeration, threats_path,
                             catalogue=check_coverage.catalogue(check_coverage.CATALOGUES))

    if args.json:
        print(json.dumps({
            "blocking": len(report.blocking), "advisory": len(report.advisory),
            "complete": not report.blocking, "gaps": report.gaps, **guidance,
        }, indent=2))
        return 0 if not report.blocking else 1

    for severity, gaps in ((BLOCKING, report.blocking), (ADVISORY, report.advisory)):
        if not gaps:
            continue
        groups = {}
        for gap in gaps:
            groups.setdefault(gap["element"], []).append(gap)
        print(f"\n{severity} — {len(gaps)} gap(s) across {len(groups)} place(s)")
        print("=" * 60)
        for element, items in groups.items():
            print(f"\n  {element}")
            for gap in items:
                where = f"{gap['field']}: " if gap["field"] else ""
                print(f"    - {where}{gap['message']}")
    if guidance["shared_nodes"]:
        print("\nCandidate chains — undecided findings citing the same pattern:")
        for node, pairs in guidance["shared_nodes"].items():
            print(f"  {node}: {', '.join(pairs)}")
    print()
    if report.blocking:
        print(f"Not decided: {len(report.blocking)} blocking, {len(report.advisory)} advisory. "
              f"Next id: {guidance['next_id']}.")
        return 1
    if report.advisory:
        print(f"Every finding is decided. {len(report.advisory)} advisory item(s).")
    else:
        print("Every finding is decided.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
