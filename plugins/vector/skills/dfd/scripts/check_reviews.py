#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Report every design document nobody has read against this model.

The currency review is finished when this exits 0. A model declares where its
design lives, in system.design_sources, and records what it has been read
against, in system.reviewed — a path, the digest of what was read, a date,
whether it changed the model, and why. A document under those sources with no
entry is unreviewed, and one edited since its entry has changed. Those are
different repairs: the first asks somebody to read a document, the second asks
them to read a change.

Neither is what the rest of the toolkit calls stale. Stale is a derived
artefact no longer matching what it was derived from, and it is repaired by
re-running the derivation. When a review edits the model, the enumeration, the
register and the matrix all go stale by the digests already in them, and this
says so rather than doing anything new about it.

**The check itself lives in check_traceability.py**, which is the file CI runs
and the one copied into other repositories. This script adds what an interview
needs and CI does not: the worklist, in the order somebody would take it, and
what each entry is asking for. The dependency runs that way and only that way,
because the copied file cannot import anything from a plugin that is not there.

A model that declares no design_sources is not using this capability. It
reports nothing and fails nothing, and the skill is what helps a project get to
the point of declaring one.
"""

import argparse
import datetime
import importlib.util
import json
import os
import sys

try:
    # Imported to fail here rather than three frames deep in the sibling, so
    # somebody running this script gets a sentence instead of a traceback.
    import yaml  # noqa: F401
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))


def sibling(name):
    """A sibling script, imported rather than reimplemented.

    Two implementations of "which documents are unreviewed" would drift, and
    the one that drifts silently is the one running in CI.
    """
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


traceability = sibling("check_traceability")

BLOCKING, ADVISORY = traceability.BLOCKING, traceability.ADVISORY
IMPACTS = traceability.IMPACTS
REVIEW_FIELDS = traceability.REVIEW_FIELDS
Report = traceability.Report
as_date = traceability.as_date
digest = traceability.digest
repository_root = traceability.repository_root

ASKING = {
    "UNREVIEWED_DOC": "read it, and say what it means for the model",
    "CHANGED_DOC": "read the change, then revise the model or re-record the digest",
    "REVIEW_EXPIRED": "read it again, because this model asks to be",
    "RENAMED_DOC": "correct the path; nothing needs reading again",
    "ORPHANED_REVIEW": "correct the path if it moved, otherwise drop the entry",
    "EMPTY_SOURCE": "fix the source, or remove it",
    "BAD_FIELD": "write a whole number of days, or remove the field",
}


def guidance_for(report, pulse, root):
    """The worklist, in the shape one sitting takes it — the skill's half."""
    worklist = []
    for gap in report.gaps:
        if gap["code"] not in ASKING:
            continue
        entry = {"code": gap["code"], "path": gap["element"],
                 "asking": ASKING[gap["code"]], "severity": gap["severity"]}
        if gap["code"] == "CHANGED_DOC":
            target = os.path.join(root, gap["element"])
            if os.path.exists(target):
                entry["digest_now"] = digest(target)
        worklist.append(entry)
    worklist.sort(key=lambda item: (item["severity"] != BLOCKING, item["path"]))
    return {"worklist": worklist, "pulse": pulse}


def check(model, model_path, root, as_of):
    report = Report()
    pulse = traceability.check_reviews(model, model_path, root, report, as_of)
    return report, guidance_for(report, pulse, root)


def load(path, what):
    return traceability.load(path, what)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model", help="path to the .dfd.yaml model")
    parser.add_argument("--json", action="store_true", help="emit findings and guidance as JSON")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD",
                        help="the date a review cycle is judged against (default: today)")
    parser.add_argument("--root", metavar="DIR",
                        help="the repository root design_sources are relative to "
                             "(default: the nearest .git above the model)")
    args = parser.parse_args(argv)

    as_of = datetime.date.today()
    if args.as_of:
        as_of = as_date(args.as_of)
        if as_of is None:
            print(f"--as-of {args.as_of!r} is not a YYYY-MM-DD date", file=sys.stderr)
            return 2

    try:
        model = load(args.model, "model")
    except SystemExit as exit_:
        if isinstance(exit_.code, tuple):
            print(exit_.code[1], file=sys.stderr)
            return exit_.code[0]
        raise

    model_path = os.path.abspath(args.model)
    root = args.root or repository_root(os.path.dirname(model_path))
    root = os.path.abspath(root)
    report, guidance = check(model, model_path, root, as_of)

    if args.json:
        print(json.dumps({
            "as_of": as_of.isoformat(),
            "blocking": len(report.blocking), "advisory": len(report.advisory),
            "current": not report.blocking, "gaps": report.gaps, **guidance,
        }, indent=2, default=str))
        return 0 if not report.blocking else 1

    pulse = guidance["pulse"]
    if pulse is None:
        print(f"{os.path.relpath(model_path, root)} declares no design_sources, so there "
              "is nothing to review it against.")
        print("Declare where the project's design documents live to turn this on.")
        return 0

    for severity, gaps in ((BLOCKING, report.blocking), (ADVISORY, report.advisory)):
        if not gaps:
            continue
        print(f"\n{severity} — {len(gaps)} finding(s)")
        print("=" * 60)
        for gap in gaps:
            print(f"\n  {gap['element']}")
            print(f"    - {gap['message']}")
            if gap["code"] in ASKING:
                print(f"      asking: {ASKING[gap['code']]}")

    print(f"\n{pulse['reviews']} of {pulse['documents']} design document(s) reviewed.")
    if pulse["cycle"]:
        print(f"This model asks to be read again every {pulse['cycle']} days.")
    if pulse["oldest"]:
        print(f"Oldest reading: {pulse['oldest']['path']} on {pulse['oldest']['reviewed']}, "
              f"{pulse['oldest']['age_days']} days ago.")

    print()
    if report.blocking:
        print(f"Not reviewed through: {len(report.blocking)} blocking, "
              f"{len(report.advisory)} advisory.")
        return 1
    if report.advisory:
        print(f"Reviewed through every design document. "
              f"{len(report.advisory)} advisory item(s).")
    else:
        print("Reviewed through every design document.")
    print("A claim about documents, never about the system: a design change made "
          "without one is invisible here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
