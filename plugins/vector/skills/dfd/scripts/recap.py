#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""What this toolkit is, and where this repository stands.

Two sections, in this order, because somebody who needs the second usually
needs the first as well and nobody needs the reverse.

**Nothing here judges anything.** Every state printed below comes from a check
that already owns the question, run as a subprocess, and what is printed is
that process's own verdict line. Handed a structured report this would have to
render one, and rendering is where softening lives; handed text, relaying is
the only thing available. That is the whole of ADR-0012, and it is the only
protection this component has — a summary is the one artefact in this toolkit
with no digest and no source, so nothing breaks when it goes quietly wrong.

**A verdict is the last line that is not a standing limit.** Three of these
checks close with one — coverage is not proof, a clean scan is no evidence, a
claim about documents is not a claim about the system — and a limit is exactly
the sentence a recap must not print where a verdict belongs. Each is a `LIMIT`
constant in the script that prints it, so this reads them back rather than
keeping copies, and tests/test_recap.py fails when a script's last line stops
matching its own constant.

It writes nothing, caches nothing, and always exits 0. A non-zero exit would
be an invitation to put orientation in a build.

The one dependency is transitive and deliberate: `find_models` is imported from
check_traceability.py rather than walking the tree a second way, and that
module imports PyYAML at the top. Answering "which models are here" twice would
be two implementations of a question that has one.
"""

import argparse
import datetime
import importlib.util
import os
import subprocess  # nosec B404
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))


def sibling(name):
    """A sibling script, imported rather than reimplemented."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


traceability = sibling("check_traceability")


def limit_of(script):
    """A check's own standing limit, read from the script that prints it.

    Copies here would be a second statement of a sentence that already has one,
    and the copy is what goes stale.
    """
    return getattr(sibling(script[: -len(".py")]), "LIMIT", None)

# The capabilities, in the order a chain runs — which is not the order
# `/vector:` lists them, and is the whole design. This is the seventh place
# this ordering is written down; tests/test_recap.py is what stops it becoming
# the stale one, by failing when a skill ships that is not named here.
CHAIN = (
    ("1", "/vector:dfd", "interview until the model is complete", "<slug>.dfd.yaml"),
    ("2", "vector:enumerate", "a verdict for every applicable pairing", "<slug>.threats.yaml"),
    ("3", "/vector:promote", "findings become vectors, or dismissals", "<slug>.vectors.yaml"),
    ("4", "/vector:matrix", "every vector gets a disposition and an owner", "the register"),
    ("5", "/vector:review", "the model read against design documents", "the model"),
    ("6", "/vector:intake", "a scanner finding meets the register", "the register"),
    ("", "/vector:wire", "the chain checked in CI, where no session exists", "a workflow"),
)

HEADLINE = ("vector — continuous threat modelling, "
            "STRIDE for security and LINDDUN for privacy")

PREMISE = "Completeness is decided by a script at every step, never by judgement."

LIMIT = "Not looked at: whether anybody read any of it."

# Each link: the label, the artefact whose absence means "not started", the
# script that decides it, and how to advance it. `model` and `review` both
# judge the model file, so `review` is never "not started" — the check itself
# says when a project has not opted in.
LINKS = (
    ("model", "dfd", "validate_dfd.py", False, "/vector:dfd"),
    ("enumeration", "threats", "check_coverage.py", False, "vector:enumerate"),
    ("register", "vectors", "check_vectors.py", False, "/vector:promote"),
    ("matrix", "vectors", "check_matrix.py", True, "/vector:matrix"),
    ("review", "dfd", "check_reviews.py", True, "/vector:review"),
)

#: Where a relayed line is folded. A check's words are never cut — only
#: wrapped, on the column the label ends at, so the whole sentence survives on
#: a screen that has to hold several models.
WIDTH = 96
GUTTER = 16

NOT_STARTED = "not started"
UNREADABLE = "could not be read"


def artefact(directory, slug, kind):
    return os.path.join(directory, f"{slug}.{kind}.yaml")


def fold(label, said, gutter=GUTTER):
    """One relayed line, wrapped onto the label's column."""
    wrapped = textwrap.wrap(said, width=WIDTH - gutter) or [said]
    head = f"  {label:<{gutter - 3}} {wrapped[0]}" if label else " " * gutter + wrapped[0]
    return [head] + [" " * gutter + line for line in wrapped[1:]]


def lines_of(text):
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def verdict_of(text, limit):
    """The check's own verdict: its last line, or the one above it when the
    last is that check's standing limit."""
    said = lines_of(text)
    if not said:
        return "(said nothing)"
    if limit is not None and said[-1] == limit:
        said = said[:-1]
    return said[-1] if said else "(said only its limit)"


def run(script, arguments):
    """One check, as a subprocess, so its words arrive as text rather than as
    something this script would have to render."""
    done = subprocess.run(  # nosec B603
        [sys.executable, os.path.join(HERE, script), *arguments],
        capture_output=True, text=True, check=False)
    return done.returncode, done.stdout, done.stderr


def link_state(directory, slug, link, as_of):
    """Three outcomes, kept apart: not started, could not be read, or what the
    check said. Collapsing the first two reports a chain in progress as a chain
    in trouble."""
    label, kind, script, dated, advance = link
    path = artefact(directory, slug, kind)
    if not os.path.exists(path):
        return label, NOT_STARTED, [], False, advance

    arguments = [path] + (["--as-of", as_of] if dated else [])
    code, out, err = run(script, arguments)
    if code == 2:
        return label, UNREADABLE, lines_of(err)[-1:], False, advance
    return label, verdict_of(out, limit_of(script)), [], code == 0, advance


def survey(root, slug, as_of, excludes):
    models = traceability.find_models(root, excludes)
    if slug:
        models = [m for m in models
                  if os.path.basename(m) == f"{slug}.dfd.yaml"]
    lines = []
    for path in models:
        directory, name = os.path.dirname(path), os.path.basename(path)
        this = name[: -len(".dfd.yaml")]
        shown = os.path.relpath(path, root).replace(os.sep, "/")
        lines.append("")
        lines.append(shown)
        nxt = None
        for link in LINKS:
            label, said, extra, passing, advance = link_state(
                directory, this, link, as_of)
            lines += fold(label, said)
            for line in extra:
                lines += fold("", line)
            if nxt is None and not passing:
                nxt = (advance, this, said)
        if nxt:
            advance, this, said = nxt
            step = (f"fix the file, then {advance} {this}" if said == UNREADABLE
                    else f"{advance} {this}")
            lines += fold("next", step)
        else:
            lines += fold("next", "nothing — every check passes")
    return models, lines


def whole_chain(root, as_of, excludes):
    """The repository-wide questions no per-model check asks: the digests
    between artefacts, and the annotation scan over tracked files.

    Its limit is printed as well as its verdict, because this is the line the
    toolkit most wants read and the one place there is room for it.
    """
    arguments = ["--root", root, "--as-of", as_of]
    for pattern in excludes:
        arguments += ["--exclude", pattern]
    code, out, err = run("check_traceability.py", arguments)
    if code == 2:
        return lines_of(err)[-1:]
    limit = limit_of("check_traceability.py")
    said = [verdict_of(out, limit)]
    if limit is not None and lines_of(out)[-1:] == [limit]:
        said.append(limit)
    return said


def render(root, slug, as_of, excludes=()):
    out = [HEADLINE, ""]
    for step, command, purpose, writes in CHAIN:
        out.append(f"  {step:<2} {command:<18} {purpose:<49} {writes}")
    out += ["", PREMISE, ""]

    models, body = survey(root, slug, as_of, excludes)
    if not models:
        out.append("No model here yet.")
        out.append("")
        out.append("  Start with /vector:dfd — it interviews you until the model is")
        out.append("  complete, and a script rather than a judgement decides when that is.")
        out.append("")
        out.append(LIMIT)
        return "\n".join(out)

    count = f"{len(models)} model(s)"
    where = f"Where this repository stands — {count}, as of {as_of}"
    out += [where, "=" * len(where)]
    out += body
    out += ["", "The chain, across this repository"]
    for line in whole_chain(root, as_of, excludes):
        out += fold("", line, gutter=2)
    out += ["", LIMIT]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="What this toolkit is, and where this repository stands.")
    parser.add_argument("slug", nargs="?",
                        help="report on one model rather than every model")
    parser.add_argument("--root", default=".", help="the directory to survey")
    parser.add_argument("--as-of", default=datetime.date.today().isoformat(),
                        metavar="YYYY-MM-DD",
                        help="the date deferrals and review cycles are judged against")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                        help="a path glob to leave out, repeatable; passed to the "
                             "whole-chain check as well, which is where it matters — "
                             "that check cannot tell prose quoting an annotation from "
                             "an annotation")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"no such directory: {args.root}", file=sys.stderr)
        sys.exit(2)
    try:
        datetime.date.fromisoformat(args.as_of)
    except ValueError:
        print(f"--as-of is not a date: {args.as_of}", file=sys.stderr)
        sys.exit(2)

    print(render(args.root, args.slug, args.as_of, args.exclude))
    # Always 0. This reports; it gates nothing, and an exit code is an
    # invitation to put orientation in a build.
    sys.exit(0)


if __name__ == "__main__":
    main()
