#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Report every vector nobody has decided about, and every mitigation that is
not written down anywhere the work will meet it.

The matrix is finished when this exits 0. Every vector carries a disposition
from a closed vocabulary — mitigated, accepted, deferred — and each state
requires the field that makes it a claim rather than a label: a mitigation id,
an owner and a reason, or an owner, a reason and a date. Every mitigation names
where its requirement is written: the specification the implementer builds
from, the code where the control lives, or both. A mitigation that exists only
in this file is the thing the matrix exists to prevent.

**The checks themselves live in check_traceability.py**, which is the file CI
runs and the one copied into other repositories. This script adds what an
interview needs and CI does not: what is left to decide, grouped the way one
sitting takes it, and the next id to hand out. The dependency runs that way and
only that way, because the copied file cannot import anything from a plugin
that is not there.

Dates are compared against --as-of, so an expiry is reproducible: without it,
a deferral passing today and failing tomorrow makes the suite a time bomb.

Gaps are BLOCKING (the matrix is not finished, or says something that cannot
be true) or ADVISORY (a pattern worth a reader's eye that may still be
legitimate).
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

    Two implementations of "every vector has a disposition" would drift, and
    the one that drifts silently is the one running in CI.
    """
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


traceability = sibling("check_traceability")

BLOCKING, ADVISORY = traceability.BLOCKING, traceability.ADVISORY
STATES = traceability.STATES
VERIFICATIONS = traceability.VERIFICATIONS
MITIGATION_ID = traceability.MITIGATION_ID
Report = traceability.Report
as_date = traceability.as_date
as_list = traceability.as_list
answered = traceability.answered
digest = traceability.digest
repository_root = traceability.repository_root
resolves = traceability.resolves


def guidance_for(register, as_of):
    """What is left, in the shape one sitting takes — the skill's half."""
    vectors = [v for v in (register.get("vectors") or []) if isinstance(v, dict)]
    retired_ids = {str(r.get("id")) for r in (register.get("retired") or [])
                   if isinstance(r, dict)}

    undispositioned, deferrals = {}, []
    for entry in vectors:
        disposition = entry.get("disposition")
        if not isinstance(disposition, dict) or disposition.get("state") not in STATES:
            if not isinstance(disposition, dict) or not disposition:
                undispositioned.setdefault(str(entry.get("element")), []).append(
                    str(entry.get("id")))
            continue
        if disposition.get("state") != "deferred":
            continue
        until = as_date(disposition.get("until"))
        if until is not None:
            deferrals.append({"id": str(entry.get("id")), "until": until.isoformat(),
                              "days_left": (until - as_of).days,
                              "owner": disposition.get("owner"),
                              "label": disposition.get("until_label")})

    live = [str(m.get("id")) for m in (register.get("mitigations") or [])
            if isinstance(m, dict) and m.get("id")]
    numbers = [int(i.split("-")[1]) for i in live + list(retired_ids)
               if MITIGATION_ID.match(str(i))]
    return {
        "undispositioned_by_element": undispositioned,
        "deferrals": sorted(deferrals, key=lambda d: d["until"]),
        "next_id": f"MIT-{(max(numbers) + 1 if numbers else 1):04d}",
    }


def check(register, threats_path, as_of, bases=(), model_path=None):
    """model_path is optional, and what it buys is one advisory: a scanner
    answer argued against a model that has since moved. The matrix interview
    has no use for it — dispositions are not what lapses — but the rendered
    document does, because a reader should see that an argument has expired.
    """
    report = traceability.check_register(register, threats_path, as_of, bases=bases,
                                         model_path=model_path)
    return report, guidance_for(register, as_of)


def load(path, what):
    return traceability.load(path, what)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("register", help="path to the .vectors.yaml register")
    parser.add_argument("--json", action="store_true", help="emit gaps and guidance as JSON")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD",
                        help="the date deferrals are judged against (default: today)")
    parser.add_argument("--root", metavar="DIR",
                        help="the repository root specified_in paths are relative to "
                             "(default: the nearest .git above the register)")
    args = parser.parse_args(argv)

    as_of = datetime.date.today()
    if args.as_of:
        as_of = as_date(args.as_of)
        if as_of is None:
            print(f"--as-of {args.as_of!r} is not a YYYY-MM-DD date", file=sys.stderr)
            return 2

    try:
        register = load(args.register, "register")
        reference = register.get("threats")
        if not reference:
            raise SystemExit((2, f"{args.register} does not name an enumeration"))
        here = os.path.dirname(os.path.abspath(args.register))
        threats_path = os.path.join(here, reference)
        if not os.path.exists(threats_path):
            raise SystemExit((2, f"no such enumeration: {threats_path}"))
    except SystemExit as exit_:
        if isinstance(exit_.code, tuple):
            print(exit_.code[1], file=sys.stderr)
            return exit_.code[0]
        raise

    bases = (here, args.root or repository_root(here))
    report, guidance = check(register, threats_path, as_of, bases=bases)

    if args.json:
        print(json.dumps({
            "as_of": as_of.isoformat(),
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
    if guidance["deferrals"]:
        print(f"\nDeferrals, soonest first (as of {as_of.isoformat()}):")
        for entry in guidance["deferrals"]:
            label = f" ({entry['label']})" if entry.get("label") else ""
            print(f"  {entry['id']}: until {entry['until']}{label}, {entry['days_left']} day(s), "
                  f"owner {entry.get('owner') or 'unnamed'}")
    print()
    if report.blocking:
        print(f"Not decided: {len(report.blocking)} blocking, {len(report.advisory)} advisory. "
              f"Next id: {guidance['next_id']}.")
        return 1
    if report.advisory:
        print(f"Every vector is dispositioned. {len(report.advisory)} advisory item(s).")
    else:
        print("Every vector is dispositioned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
