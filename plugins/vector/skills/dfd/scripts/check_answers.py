#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Report every scanner finding nobody has put to the threat model.

The intake is finished when this exits 0. Each finding is asked one question —
where was this in the threat matrix, and did we evaluate it incorrectly, or
should we adapt? — and the answer is recorded in the register's `answers`
section: a scanner, a rule, optionally a path scope, and what the person
decided.

**Nothing here fingerprints a finding.** A finding counts as already answered
when its scanner and rule match an answer's, and its location sits under that
answer's scope. Scanners rename rules and renumber findings, so every way this
fails is a way that puts the question back in front of somebody — which is the
opposite of a fingerprint, whose failures suppress a question nobody knows was
asked.

This runs in a session and nowhere else. CI is never handed a SARIF file,
which is how the promise that nothing here fails a build on its own judgement
is kept structurally rather than by choosing severities carefully. What CI does
check is the register's own answers, because a broken answer is a broken
register — those checks live in check_traceability.py with every other one.

**A finding can lower confidence in a claim and can never raise it.** A scan
that reports nothing is recorded as no evidence, never as confirmation, and
this says so in those words every time it happens.
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
    """A sibling script, imported rather than reimplemented."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


traceability = sibling("check_traceability")

BLOCKING, ADVISORY = traceability.BLOCKING, traceability.ADVISORY
ANSWERS = traceability.ANSWERS
CONTRADICTIONS = traceability.CONTRADICTIONS
Report = traceability.Report
as_date = traceability.as_date
as_list = traceability.as_list
digest = traceability.digest

LIMIT = ("A finding can lower confidence in a claim and can never raise it. "
         "A clean scan is no evidence, never confirmation.")


# --- reading a scan ----------------------------------------------------------

def normalise(name):
    """`CodeQL` and `codeql` are one scanner, and so are `Trivy` and `trivy`."""
    return "-".join(str(name).strip().lower().split())


def rule_of(result, rules):
    """The rule id, by the three routes SARIF offers, or None.

    A result none of them answers is unkeyable: it can be shown to somebody and
    it cannot be answered durably, which is worth saying rather than papering
    over with an invented key.
    """
    if result.get("ruleId"):
        return str(result["ruleId"])
    index = result.get("ruleIndex")
    if isinstance(index, int) and 0 <= index < len(rules):
        rule = rules[index]
        if isinstance(rule, dict) and (rule.get("id") or rule.get("name")):
            return str(rule.get("id") or rule["name"])
    return None


def location_of(result):
    for location in as_list(result.get("locations")):
        if not isinstance(location, dict):
            continue
        physical = location.get("physicalLocation") or {}
        artifact = physical.get("artifactLocation") or {}
        if artifact.get("uri"):
            return str(artifact["uri"]).lstrip("/")
    return None


def read_sarif(path):
    """Every result in the file, flattened to what an answer is keyed on.

    SARIF 2.1.0 and nothing else. A second format is a parser rather than a new
    capability, and guessing at one before anybody asks is how a format list
    becomes a maintenance surface nobody uses.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError:
        raise SystemExit((2, f"no such scan: {path}")) from None
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SystemExit((2, f"{path} is not JSON: {exc}")) from None
    if not isinstance(document, dict) or "runs" not in document:
        raise SystemExit((2, f"{path} has no runs; SARIF 2.1.0 is the only format read here"))

    findings = []
    for run in as_list(document.get("runs")):
        if not isinstance(run, dict):
            continue
        driver = ((run.get("tool") or {}).get("driver")) or {}
        scanner = normalise(driver.get("name") or "unknown")
        rules = as_list(driver.get("rules"))
        for result in as_list(run.get("results")):
            if not isinstance(result, dict):
                continue
            findings.append({
                "scanner": scanner,
                "rule": rule_of(result, rules),
                "path": location_of(result),
                "message": str(((result.get("message") or {}).get("text")) or "").strip(),
                "level": result.get("level") or "warning",
                "suppressed": bool(as_list(result.get("suppressions"))),
                "seen_as": {k: v for k, v in (
                    ("partialFingerprints", result.get("partialFingerprints")),
                    ("fingerprints", result.get("fingerprints")),
                ) if v},
            })
    return findings


# --- matching ----------------------------------------------------------------

def scope_of(answer):
    return str(answer.get("where") or "").strip().replace(os.sep, "/").lstrip("./")


def matches(finding, answer):
    if normalise(answer.get("scanner") or "") != finding["scanner"]:
        return False
    if str(answer.get("rule") or "") != (finding["rule"] or ""):
        return False
    where = scope_of(answer)
    if not where:
        return True
    path = finding["path"] or ""
    return path == where or path.startswith(where if where.endswith("/") else where + "/")


def answers_for(finding, answers):
    """Every answer that matches, most specific first.

    The longest scope wins. Equal specificity is not resolved here, because
    resolving it would be a guess wearing a mechanism's clothes — the caller
    reports it instead.
    """
    found = [a for a in answers if matches(finding, a)]
    return sorted(found, key=lambda a: len(scope_of(a)), reverse=True)


def check(findings, register, as_of):
    report = Report()
    answers = [a for a in (register.get("answers") or []) if isinstance(a, dict)]
    vectors = {str(v.get("id")): v for v in (register.get("vectors") or [])
               if isinstance(v, dict) and v.get("id")}

    unanswered, by_rule = [], {}
    for finding in findings:
        where = f"{finding['scanner']}/{finding['rule'] or '<no rule id>'}"
        shown = f"{where} in {finding['path'] or '<no location>'}"

        if finding["suppressed"]:
            report.add(ADVISORY, "SUPPRESSED", shown,
                       "the scanner was told not to show this. A suppression says 'do not "
                       "show me this'; it does not say what the threat model decided")

        if finding["rule"] is None:
            report.add(ADVISORY, "UNKEYABLE", shown,
                       "no rule id this can read, by any of the three routes SARIF offers, "
                       "so an answer cannot stay attached to it and it will be asked again")

        candidates = answers_for(finding, answers)
        if not candidates:
            unanswered.append(finding)
            by_rule.setdefault(where, []).append(finding["path"] or "<no location>")
            report.add(BLOCKING, "UNANSWERED", shown,
                       "nobody has said where this was in the threat matrix; answer it as a "
                       f"vector, a dismissal, or a gap in the model — one of {', '.join(ANSWERS)}")
            continue

        if len(candidates) > 1 and \
                len(scope_of(candidates[0])) == len(scope_of(candidates[1])):
            report.add(BLOCKING, "AMBIGUOUS_ANSWER", shown,
                       f"{candidates[0].get('id')} and {candidates[1].get('id')} both match it "
                       "with the same scope, so which one answers it is a guess; narrow one")

    summary = {
        "findings": len(findings),
        "unanswered": len(unanswered),
        "by_rule": {rule: sorted(set(paths)) for rule, paths in sorted(by_rule.items())},
        "answers": len(answers),
        "vectors": len(vectors),
        "clean": not findings,
    }
    return report, summary


def load(path, what):
    return traceability.load(path, what)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scan", help="path to the SARIF file the build produced")
    parser.add_argument("register", help="path to the .vectors.yaml register")
    parser.add_argument("--json", action="store_true", help="emit findings and summary as JSON")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD",
                        help="the date this is judged against (default: today)")
    args = parser.parse_args(argv)

    as_of = datetime.date.today()
    if args.as_of:
        as_of = as_date(args.as_of)
        if as_of is None:
            print(f"--as-of {args.as_of!r} is not a YYYY-MM-DD date", file=sys.stderr)
            return 2

    try:
        register = load(args.register, "register")
        findings = read_sarif(args.scan)
    except SystemExit as exit_:
        if isinstance(exit_.code, tuple):
            print(exit_.code[1], file=sys.stderr)
            return exit_.code[0]
        raise

    report, summary = check(findings, register, as_of)

    if args.json:
        print(json.dumps({
            "as_of": as_of.isoformat(),
            "blocking": len(report.blocking), "advisory": len(report.advisory),
            "answered": not report.blocking, "gaps": report.gaps,
            "limit": LIMIT, **summary,
        }, indent=2, default=str))
        return 0 if not report.blocking else 1

    if summary["clean"]:
        print(f"{args.scan} reports nothing.")
        print("Recorded as no evidence. A scanner finds what it knows how to look for, so "
              "silence is not confirmation that any control works.")
        return 0

    for severity, gaps in ((BLOCKING, report.blocking), (ADVISORY, report.advisory)):
        if not gaps:
            continue
        print(f"\n{severity} — {len(gaps)} finding(s)")
        print("=" * 60)
        for gap in gaps:
            print(f"\n  {gap['element']}")
            print(f"    - {gap['message']}")

    if summary["by_rule"]:
        print("\nUnanswered, grouped by rule")
        print("=" * 60)
        print("One answer usually covers a group. Asking about each location separately is "
              "how an intake gets abandoned.")
        for rule, paths in summary["by_rule"].items():
            print(f"  {rule} — {len(paths)} location(s)")
            for path in paths[:5]:
                print(f"      {path}")
            if len(paths) > 5:
                print(f"      … and {len(paths) - 5} more")

    print(f"\n{summary['findings']} finding(s), {summary['answers']} answer(s) on record.")
    if report.blocking:
        print(f"Not answered through: {len(report.blocking)} blocking, "
              f"{len(report.advisory)} advisory.")
        print(LIMIT)
        return 1
    if report.advisory:
        print(f"Every finding has an answer. {len(report.advisory)} advisory item(s).")
    else:
        print("Every finding has an answer.")
    print(LIMIT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
