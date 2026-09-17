#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Does the threat model still describe the product at HEAD?

This is the one check that runs where no Claude Code session exists, and the
only thing in the toolkit allowed to fail a build. It finds every register in
the repository, reads the design documents the mitigations reference, and walks
the digests that chain the artefacts together — model to enumeration to
register to specification. Anything that moved without somebody noticing is a
finding. Above all of that it asks the one question whose answer comes from
outside the toolkit: which of the project's own design documents has nobody
read against the model?

**It reports coverage, never proof.** Every claim it checks was written by the
people whose work it describes, so what it verifies is that a set of internally
consistent claims is current. Whether a control actually works is QA's, and the
one mechanical challenge from outside these documents is a vulnerability
scanner contradicting a claim.

Two things it will not do. It never reaches the network, so a URL reference is
accepted as resolving and is never fetched. And it treats a status it does not
recognise as current, because it is looking for a retirement rather than
validating a vocabulary it does not own.

This file is copied into the repository it checks, so it imports nothing from
the plugin and everything it needs is here. check_matrix.py imports the
register checks from it; the dependency runs that way and only that way.
"""

import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import re
import subprocess  # nosec B404
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

# Rewritten by the skill that vendors this file, so a build log says which
# version made the claim. In the plugin's own copy it stays as it is.
VENDORED_FROM = "plugin source"

BLOCKING, ADVISORY = "BLOCKING", "ADVISORY"

STATES = ("mitigated", "accepted", "deferred")
VERIFICATIONS = ("code", "manual")
MITIGATION_ID = re.compile(r"^MIT-\d{4}$")
MITIGATION_FIELDS = ("id", "title", "control", "verification", "vectors")
URL = re.compile(r"^[a-z][a-z0-9+.-]*://")
RETIRED_STATUSES = ("superseded", "deprecated", "withdrawn", "obsolete")

# Two tokens — "vector:" then "mitigates" — then one MIT id, optionally
# qualified by a register slug. Written so this line does not match itself.
ANNOTATION = re.compile(r"vector:\s*mitigates\s+((?:[A-Za-z0-9][\w.-]*)/)?(MIT-\d{4})\b")
ANNOTATION_GREP = r"vector:[[:space:]]*mitigates"

# An answer to a scanner finding, per ADR-0009. The key is what the person
# answered — a scanner, a rule, optionally a path scope — never anything the
# scanner hands out, because a fingerprint's failures suppress a question
# nobody knows was asked.
ANSWER_ID = re.compile(r"^ANS-\d{4}$")
ANSWERS = ("vector", "not_a_threat", "model_gap")
CONTRADICTIONS = ("disposition_revised", "false_positive")
ANSWER_FIELDS = ("id", "scanner", "rule", "answer", "reason", "answered")
PINNED_ANSWERS = ("not_a_threat", "model_gap")

REVIEW_FIELDS = ("path", "digest", "reviewed", "impact", "reason")
IMPACTS = ("none", "modelled")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|$)", re.S)
STATUS_ROW = re.compile(r"^\|\s*\*{0,2}status\*{0,2}\s*\|(.*?)\|", re.I | re.M)
SUPERSEDED_ROW = re.compile(r"^\|\s*\*{0,2}superseded[ _]by\*{0,2}\s*\|(.*?)\|", re.I | re.M)


class Report:
    def __init__(self):
        self.gaps = []

    def add(self, severity, code, element, message, field=None, source=None):
        self.gaps.append({
            "severity": severity, "code": code, "element": element,
            "field": field, "message": message, "source": source,
            "key": ":".join(p for p in (code, element, field) if p),
        })

    @property
    def blocking(self):
        return [g for g in self.gaps if g["severity"] == BLOCKING]

    @property
    def advisory(self):
        return [g for g in self.gaps if g["severity"] == ADVISORY]


# --- small shared helpers ----------------------------------------------------

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


def as_date(value):
    """A date, or None when the value is not one.

    YAML reads an unquoted 2026-06-30 as a date already; a quoted one arrives
    as text and has to be ISO. Anything else — a month, a milestone name — is
    not a date, whatever it means to a person.
    """
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def as_list(value):
    if value is None:
        return []
    return list(value) if isinstance(value, list) else [value]


def repository_root(start):
    """The nearest ancestor holding a .git, else the directory itself."""
    here = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return os.path.abspath(start)
        here = parent


def reference_path(reference, bases):
    """The file a specified_in reference names, or None.

    A URL is not a path and never fetched. A path is tried against each base in
    turn — the register's own directory first, then the repository root — and
    the anchor is dropped, not verified.
    """
    text = str(reference).strip()
    if URL.match(text):
        return None
    path = text.split("#", 1)[0]
    if not path:
        return None
    if os.path.isabs(path):
        return path if os.path.exists(path) else None
    for base in bases:
        candidate = os.path.join(base, path)
        if os.path.exists(candidate):
            return candidate
    return None


def resolves(reference, bases):
    return URL.match(str(reference).strip()) is not None or \
        reference_path(reference, bases) is not None


def read_status(path):
    """(status, superseded_by) for a design document, either None when absent.

    Frontmatter first, then a Status row in a header table, taking the first
    word of the value so that "Accepted — enforced since 0.8.0" reads as
    "Accepted". Neither is an error: a project is not obliged to carry a status
    it never agreed to write.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read(65536)
    except OSError:
        return None, None

    front = FRONTMATTER.match(text)
    if front:
        try:
            meta = yaml.safe_load(front.group(1))
        except yaml.YAMLError:
            meta = None
        if isinstance(meta, dict) and meta.get("status"):
            return str(meta["status"]).strip().split()[0], meta.get("superseded_by") or None

    row = STATUS_ROW.search(text)
    if row:
        words = row.group(1).replace("*", "").strip().split()
        if words:
            superseded = SUPERSEDED_ROW.search(text)
            by = superseded.group(1).replace("*", "").strip() if superseded else None
            return words[0], by or None
    return None, None


def retired_status(status):
    return status is not None and status.strip().lower().rstrip(".,") in RETIRED_STATUSES


# --- design documents, and who has read them ---------------------------------

def tracked_files(root):
    """Every file git knows about, repository-relative with forward slashes.

    The same reasoning as the annotation scan: build output, downloaded
    dependencies and somebody's local scratch file are invisible without
    reimplementing anybody's .gitignore.
    """
    try:
        # Dismissed rather than skipped in config, so the reason travels with
        # the call: argv is a list, so there is no shell and no metacharacter to
        # inject; every element but `root` is a constant, and `root` is consumed
        # by -C as a path rather than parsed as a flag. `git` is deliberately
        # not an absolute path — this file is copied into other people's
        # repositories, where git lives wherever their platform puts it, and a
        # hardcoded /usr/bin/git would be wrong far more often than PATH is
        # hostile.
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"],  # nosec B603 B607
                             capture_output=True, text=True)
    except (OSError, ValueError):
        return []
    if out.returncode != 0:
        return []
    return sorted(name for name in out.stdout.split("\0") if name)


def glob_match(path, pattern):
    """fnmatch, segment by segment, so `*` does not cross a directory.

    fnmatch on the whole path would make docs/*.md match docs/drafts/x.md,
    which is not what anybody writing that pattern meant. `**` spans any
    number of segments, as everywhere else that spells it that way.
    """
    def segments(parts, rest):
        if not rest:
            return not parts
        head, tail = rest[0], rest[1:]
        if head == "**":
            return any(segments(parts[index:], tail) for index in range(len(parts) + 1))
        if not parts or not fnmatch.fnmatch(parts[0], head):
            return False
        return segments(parts[1:], tail)
    return segments(path.split("/"), pattern.split("/"))


def covered_by(path, source):
    """Is this repository-relative path one of the documents a source names?"""
    entry = str(source).strip().replace(os.sep, "/")
    while entry.startswith("./"):
        entry = entry[2:]
    entry = entry.rstrip("/")
    if not entry:
        return False
    if any(character in entry for character in "*?["):
        return glob_match(path, entry)
    return path == entry or path.startswith(entry + "/")


def check_reviews(model, model_path, root, report, as_of, files=None):
    """Which design documents nobody has read against this model.

    The outermost link in the chain, and the only one whose input comes from
    outside the toolkit. Returns the pulse — how many documents, how many
    readings, and the oldest of them — which is reported whether or not
    anything failed.

    A model that declares no design_sources is opting out, so this reports
    nothing and fails nothing.
    """
    system = model.get("system") or {}
    sources = as_list(system.get("design_sources"))
    if not sources:
        return None

    shown = os.path.relpath(model_path, root)
    if files is None:
        files = tracked_files(root)

    cycle = system.get("review_cycle")
    if cycle is not None:
        if isinstance(cycle, bool) or not isinstance(cycle, int) or cycle < 1:
            report.add(BLOCKING, "BAD_FIELD", "system/review_cycle",
                       f"review_cycle is {cycle!r}; it must be a whole number of days, "
                       "or absent for no expiry at all", field="review_cycle", source=shown)
            cycle = None

    documents = set()
    for source in sources:
        matched = {name for name in files if covered_by(name, source)}
        if not matched:
            report.add(ADVISORY, "EMPTY_SOURCE", "system/design_sources",
                       f"{source} matches no tracked file; a source that names nothing "
                       "checks nothing, which usually means a typo or a moved directory",
                       field="design_sources", source=shown)
        documents |= matched

    # A decision that has retired itself does not describe the current system,
    # so asking somebody to read it against the model asks for a sentence about
    # nothing. An existing review of one is left alone rather than orphaned.
    live = set()
    for name in sorted(documents):
        status, _ = read_status(os.path.join(root, name))
        if not retired_status(status):
            live.add(name)

    reviews = {}
    for entry in as_list(system.get("reviewed")):
        if isinstance(entry, dict) and entry.get("path"):
            reviews[str(entry["path"]).strip().replace(os.sep, "/")] = entry

    unreviewed, changed = [], []
    for name in sorted(live):
        entry = reviews.get(name)
        if entry is None:
            unreviewed.append(name)
            continue
        stored = str(entry.get("digest") or "")
        if stored and stored != digest(os.path.join(root, name)):
            changed.append(name)

    orphans = [name for name in sorted(reviews) if name not in documents]

    # A moved document would otherwise be two findings for one edit. Pair them
    # by digest, and only where the pairing is unambiguous: a guess that looks
    # like a mechanism is worse than a little noise.
    renamed = []
    candidates_for = {name: digest(os.path.join(root, name)) for name in unreviewed}
    for name in list(unreviewed):
        here = candidates_for[name]
        candidates = [was for was in orphans if str(reviews[was].get("digest") or "") == here]
        twins = [other for other, other_digest in candidates_for.items() if other_digest == here]
        if len(candidates) == 1 and len(twins) == 1:
            renamed.append((name, candidates[0]))
            unreviewed.remove(name)
            orphans.remove(candidates[0])

    for name in unreviewed:
        report.add(BLOCKING, "UNREVIEWED_DOC", name,
                   "nobody has said what this document means for the model; read it and "
                   "record a reviewed entry — impact none is an answer, with a reason",
                   field="reviewed", source=shown)
    for name in changed:
        report.add(BLOCKING, "CHANGED_DOC", name,
                   "this has been edited since it was reviewed against the model; read the "
                   "change, then revise the model or record the new digest to say you have",
                   field="digest", source=shown)
    for name, was in renamed:
        report.add(ADVISORY, "RENAMED_DOC", name,
                   f"identical to the reviewed {was}, which no longer exists; this is a "
                   "rename, so correct the path rather than reading it again",
                   field="path", source=shown)
    for name in orphans:
        report.add(ADVISORY, "ORPHANED_REVIEW", name,
                   "reviewed, but no longer a design document under design_sources; "
                   "correct the path if it moved, otherwise drop the entry",
                   field="reviewed", source=shown)

    oldest = None
    for name, entry in sorted(reviews.items()):
        if name not in documents:
            continue
        when = as_date(entry.get("reviewed"))
        if when is None:
            continue
        if oldest is None or when < oldest[1]:
            oldest = (name, when)
        if cycle and (as_of - when).days > cycle:
            report.add(BLOCKING, "REVIEW_EXPIRED", name,
                       f"last read on {when.isoformat()}, which is more than the "
                       f"{cycle} days this model asks for; read it again and say what it "
                       "means now", field="reviewed", source=shown)

    return {
        "model": shown,
        "documents": len(live),
        "reviews": sum(1 for name in reviews if name in documents),
        "cycle": cycle,
        "oldest": None if oldest is None else {
            "path": oldest[0], "reviewed": oldest[1].isoformat(),
            "age_days": (as_of - oldest[1]).days,
        },
    }


# --- the register checks, shared with check_matrix.py ------------------------

def check_register(register, threats_path, as_of, bases=(), model_path=None):
    """Everything that must be true of a register on its own.

    Imported by check_matrix.py, which adds the guidance an interview needs.
    Currency against the documents above and below is check_currency's.
    """
    report = Report()

    for field in ("threats", "threats_digest"):
        if not answered(register, field):
            report.add(BLOCKING, "MISSING_FIELD", "<file>", f"{field} is missing or empty",
                       field=field)
    if answered(register, "threats_digest") and register["threats_digest"] != digest(threats_path):
        report.add(BLOCKING, "STALE_THREATS", "<file>",
                   "threats_digest does not match the enumeration's current bytes; the "
                   "vectors may have moved under this matrix, so reconcile the register first")

    vectors = [v for v in (register.get("vectors") or []) if isinstance(v, dict)]
    mitigations = register.get("mitigations") or []
    retired = [r for r in (register.get("retired") or []) if isinstance(r, dict)]
    retired_ids = {str(r.get("id")) for r in retired}

    live_vectors = {str(v.get("id")): v for v in vectors if v.get("id")}
    live_mitigations = {}
    for entry in mitigations:
        if isinstance(entry, dict) and entry.get("id"):
            live_mitigations.setdefault(str(entry["id"]), entry)

    # --- dispositions -----------------------------------------------------
    state_of = {}
    named_by_vector = {}
    for entry in vectors:
        ident = str(entry.get("id") or "<unnamed>")
        where = f"vectors/{ident}"
        disposition = entry.get("disposition")
        if not isinstance(disposition, dict) or not disposition:
            report.add(BLOCKING, "NO_DISPOSITION", where,
                       "no disposition; nothing says what is being done about this vector",
                       field="disposition")
            continue

        state = disposition.get("state")
        if state not in STATES:
            report.add(BLOCKING, "BAD_STATE", where,
                       f"{state!r} is not a disposition; expected one of {', '.join(STATES)}",
                       field="disposition.state")
            continue
        state_of[ident] = state

        if not answered(disposition, "decided"):
            report.add(BLOCKING, "MISSING_FIELD", where, "decided is unanswered; a decision "
                       "with no date cannot be asked 'since when'", field="disposition.decided")
        elif as_date(disposition["decided"]) is None:
            report.add(BLOCKING, "BAD_DATE", where,
                       f"decided {disposition['decided']!r} is not a YYYY-MM-DD date",
                       field="disposition.decided")

        named = [str(m) for m in as_list(disposition.get("mitigations"))]
        named_by_vector[ident] = named
        if state == "mitigated" and not named:
            report.add(BLOCKING, "MISSING_MITIGATION", where,
                       "mitigated by nothing; name the mitigation, or the state is a label",
                       field="disposition.mitigations")
        for mitigation in named:
            if mitigation not in live_mitigations:
                why = ("is retired; a retired mitigation protects nothing"
                       if mitigation in retired_ids else "does not exist in mitigations")
                report.add(BLOCKING, "UNRESOLVED_MITIGATION", where,
                           f"names {mitigation}, which {why}", field="disposition.mitigations")

        if state in ("accepted", "deferred"):
            if not answered(disposition, "owner"):
                report.add(BLOCKING, "MISSING_OWNER", where,
                           f"{state} by nobody; an acceptance without an owner is a shrug",
                           field="disposition.owner")
            if not answered(disposition, "reason"):
                report.add(BLOCKING, "MISSING_REASON", where,
                           f"{state} for no stated reason; a decision nobody can disagree "
                           "with is not a decision", field="disposition.reason")

        if state == "deferred":
            if not answered(disposition, "until"):
                report.add(BLOCKING, "MISSING_UNTIL", where,
                           "deferred with no until; a deferral that cannot expire is an "
                           "acceptance with nobody accountable", field="disposition.until")
            else:
                until = as_date(disposition["until"])
                if until is None:
                    report.add(BLOCKING, "BAD_UNTIL", where,
                               f"until {disposition['until']!r} is not a YYYY-MM-DD date; a "
                               "milestone goes in until_label, beside a date, never instead "
                               "of one", field="disposition.until")
                else:
                    if until < as_of:
                        report.add(BLOCKING, "EXPIRED", where,
                                   f"deferred until {until.isoformat()}, which has passed; "
                                   "decide it, or move the date with a reason in history",
                                   field="disposition.until")
                    earlier = [as_date(h.get("until")) for h in disposition.get("history") or []
                               if isinstance(h, dict) and h.get("state") == "deferred"]
                    pushes = [d for d in earlier if d is not None and d < until]
                    if len(pushes) >= 2:
                        report.add(ADVISORY, "PUSHED_UNTIL", where,
                                   f"until has been moved {len(pushes)} times "
                                   f"({', '.join(d.isoformat() for d in sorted(pushes))} → "
                                   f"{until.isoformat()}); a deferral pushed every quarter "
                                   "stays green forever", field="disposition.until")

    # --- mitigations ------------------------------------------------------
    served_by = {}
    seen_ids = set()
    for index, entry in enumerate(mitigations):
        if not isinstance(entry, dict):
            report.add(BLOCKING, "BAD_ITEM", "mitigations", "entries must be mappings")
            continue
        ident = str(entry.get("id") or f"<unnamed {index}>")
        where = f"mitigations/{ident}"
        if not MITIGATION_ID.match(str(entry.get("id") or "")):
            report.add(BLOCKING, "BAD_ID", where,
                       f"{entry.get('id')!r} is not of the form MIT-NNNN", field="id")
        if ident in seen_ids:
            report.add(BLOCKING, "DUPLICATE_ID", where,
                       "a second mitigation with this id — two branches took the same "
                       "number; renumber the later one", field="id")
        seen_ids.add(ident)
        if ident in retired_ids:
            report.add(BLOCKING, "REUSED_ID", where,
                       f"{ident} is both live and retired; a retired id is never reused",
                       field="id")
        for field in MITIGATION_FIELDS:
            if not answered(entry, field):
                report.add(BLOCKING, "MISSING_FIELD", where, f"{field} is unanswered",
                           field=field)

        verification = entry.get("verification")
        if answered(entry, "verification") and verification not in VERIFICATIONS:
            report.add(BLOCKING, "BAD_VERIFICATION", where,
                       f"{verification!r} is not a verification; expected one of "
                       f"{', '.join(VERIFICATIONS)}", field="verification")
        if verification == "manual" and not answered(entry, "evidence"):
            report.add(BLOCKING, "MISSING_EVIDENCE", where,
                       "verified by hand, with nowhere the evidence lives; a manual control "
                       "nobody can show is a claim", field="evidence")

        specified = answered(entry, "specified_in")
        implemented = answered(entry, "implemented_in")
        if not specified and not implemented:
            report.add(BLOCKING, "NO_PLACE", where,
                       "neither specified_in nor implemented_in; a mitigation that exists "
                       "only in this file is a wish, not a requirement")
        if specified and not resolves(entry["specified_in"], bases):
            report.add(BLOCKING, "UNRESOLVED_SPEC", where,
                       f"specified_in {entry['specified_in']!r} does not resolve to a file; "
                       "the requirement is claimed to be written somewhere it is not",
                       field="specified_in")

        listed = [str(v) for v in as_list(entry.get("vectors"))]
        live = []
        for vector in listed:
            if vector in live_vectors:
                live.append(vector)
                served_by.setdefault(vector, []).append(ident)
            elif vector not in retired_ids:
                report.add(BLOCKING, "UNRESOLVED_VECTOR", where,
                           f"serves {vector}, which does not exist", field="vectors")
        if listed and not live:
            report.add(BLOCKING, "ORPHAN_MITIGATION", where,
                       "serves no live vector; it may be real code protecting nothing anyone "
                       "tracks — retire it with a reason rather than deleting it",
                       field="vectors")

        states = {state_of.get(v) for v in live}
        if "deferred" in states and not specified:
            report.add(BLOCKING, "SPEC_REQUIRED", where,
                       "serves a deferred vector but names no specification; the requirement "
                       "has to reach the work before it is built", field="specified_in")
        if "mitigated" in states and not implemented and verification == "code":
            report.add(BLOCKING, "IMPL_REQUIRED", where,
                       "serves a mitigated vector but names nowhere the control lives; "
                       "mitigated means it exists, so say where", field="implemented_in")

        for vector in live:
            if ident not in named_by_vector.get(vector, []) and vector in state_of:
                report.add(BLOCKING, "DISAGREEING_LINK", f"vectors/{vector}",
                           f"{ident} serves this vector, but the disposition does not name it",
                           field="disposition.mitigations")

    for vector, named in named_by_vector.items():
        for mitigation in named:
            if mitigation in live_mitigations and mitigation not in served_by.get(vector, []):
                report.add(BLOCKING, "DISAGREEING_LINK", f"mitigations/{mitigation}",
                           f"named by {vector}'s disposition, but does not list it in vectors",
                           field="vectors")

    by_element = {}
    for entry in vectors:
        by_element.setdefault(str(entry.get("element")), []).append(str(entry.get("id")))
    for element, ids in by_element.items():
        if len(ids) >= 2 and all(state_of.get(i) == "accepted" for i in ids):
            report.add(ADVISORY, "ALL_ACCEPTED", element,
                       f"every one of its {len(ids)} vectors is accepted; sometimes right, "
                       "always worth a second look")

    check_answer_records(register, report, state_of, live_vectors, model_path)

    return report


def check_answer_records(register, report, state_of, live_vectors, model_path=None):
    """What must be true of the answers a register holds, without a scan.

    A broken answer is a broken register rather than a judgement about a
    finding, which is why this runs wherever a register is checked — CI
    included — while everything that needs a SARIF file lives in
    check_answers.py and runs only in a session.

    model_path is optional because the one check that needs it, a dismissal
    lapsing, is about the model rather than the register. check_matrix.py does
    not pass one: an interview deciding dispositions has no use for knowing
    that a scanner answer has to be re-argued.
    """
    answers = register.get("answers")
    if answers is None:
        return
    if not isinstance(answers, list):
        report.add(BLOCKING, "BAD_SECTION", "answers", "answers must be a list", field="answers")
        return

    seen = set()
    for index, entry in enumerate(answers):
        if not isinstance(entry, dict):
            report.add(BLOCKING, "BAD_ITEM", "answers", "entries must be mappings")
            continue

        ident = str(entry.get("id") or f"#{index + 1}")
        where = f"answers/{ident}"
        for field in ANSWER_FIELDS:
            if not answered(entry, field):
                report.add(BLOCKING, "MISSING_FIELD", where,
                           f"{field} is unanswered; an answer nobody can disagree with is "
                           "not an answer", field=field)
        if entry.get("id"):
            if not ANSWER_ID.match(str(entry["id"])):
                report.add(BLOCKING, "BAD_ID", where,
                           f"{entry['id']!r} is not an ANS-NNNN id", field="id")
            elif str(entry["id"]) in seen:
                report.add(BLOCKING, "DUPLICATE_ID", where, "answered twice under one id",
                           field="id")
            seen.add(str(entry["id"]))

        answer = entry.get("answer")
        if answer is not None and answer not in ANSWERS:
            report.add(BLOCKING, "BAD_ANSWER", where,
                       f"{answer!r} is not an answer; expected one of {', '.join(ANSWERS)}",
                       field="answer")
            continue

        if answer == "vector":
            named = str(entry.get("vector") or "")
            if not named:
                report.add(BLOCKING, "MISSING_FIELD", where,
                           "answers 'vector' but names none", field="vector")
            elif named not in live_vectors:
                report.add(BLOCKING, "UNKNOWN_VECTOR", where,
                           f"names {named}, which this register does not hold", field="vector")
            elif state_of.get(named) == "mitigated":
                # The case this capability is worth the most for: evidence
                # arguing with an attestation. Silence is not one of the ways
                # to close it.
                contradiction = entry.get("contradiction")
                if contradiction not in CONTRADICTIONS:
                    report.add(BLOCKING, "CONTRADICTION", where,
                               f"{named} is dispositioned mitigated and a scanner found this "
                               "anyway; say which — the control does not do what it claimed "
                               f"(contradiction: {CONTRADICTIONS[0]}), or the finding is wrong "
                               f"(contradiction: {CONTRADICTIONS[1]})", field="contradiction")
        elif answer in PINNED_ANSWERS:
            stored = str(entry.get("model_digest") or "")
            if not stored:
                report.add(BLOCKING, "MISSING_FIELD", where,
                           f"answers {answer!r} but records no model_digest; the argument was "
                           "made against a model, so say which one", field="model_digest")
            elif model_path and os.path.exists(model_path) and stored != digest(model_path):
                report.add(ADVISORY, "LAPSED_ANSWER", where,
                           "argued against a model that has since changed; read the change, "
                           "then re-argue it or record the new digest to say you have",
                           field="model_digest")

        if answer == "model_gap":
            report.add(ADVISORY, "MODEL_GAP", where,
                       "a scanner found something in a part of the system the model does not "
                       "describe; the repair is the diagram, not the register")

        if answered(entry, "answered") and as_date(entry["answered"]) is None:
            report.add(BLOCKING, "BAD_DATE", where,
                       f"answered {entry['answered']!r} is not a YYYY-MM-DD date",
                       field="answered")


# --- currency against the blueprint -----------------------------------------

def check_currency(register, report, bases, enumeration=None, model_path=None,
                   threats_path=None):
    """The hops a register cannot check on its own: the model above it, and the
    design documents its mitigations name.

    Returns the coverage of each mitigation, which is what the summary renders.
    """
    coverage = {}

    if enumeration is not None and model_path is not None:
        stored = enumeration.get("model_digest")
        if stored and os.path.exists(model_path) and stored != digest(model_path):
            where = f"<enumeration {os.path.basename(threats_path or '')}>"
            report.add(BLOCKING, "STALE_MODEL", where,
                       "model_digest does not match the model's current bytes; the enumeration "
                       "was run against a model that has since changed, so re-run it",
                       field="model_digest")

    vectors = [v for v in (register.get("vectors") or []) if isinstance(v, dict)]
    state_of = {}
    for entry in vectors:
        disposition = entry.get("disposition")
        if isinstance(disposition, dict):
            state_of[str(entry.get("id"))] = disposition.get("state")

    for entry in register.get("mitigations") or []:
        if not isinstance(entry, dict):
            continue
        ident = str(entry.get("id") or "<unnamed>")
        where = f"mitigations/{ident}"
        served = [str(v) for v in as_list(entry.get("vectors"))]

        if not answered(entry, "specified_in"):
            coverage[ident] = {"state": "uncovered", "document": None, "status": None}
            if not any(state_of.get(v) == "deferred" for v in served):
                report.add(ADVISORY, "UNCOVERED", where,
                           "no specified_in; nothing says where this control is required, so "
                           "nothing downstream can notice the requirement changing",
                           field="specified_in")
            continue

        reference = entry["specified_in"]
        path = reference_path(reference, bases)
        if path is None:
            if URL.match(str(reference).strip()):
                coverage[ident] = {"state": "covered", "document": str(reference),
                                   "status": None, "remote": True}
                report.add(ADVISORY, "STATUS_UNKNOWN", where,
                           f"{reference} is a URL; it is accepted as resolving and never "
                           "fetched, so neither its status nor its drift can be seen",
                           field="specified_in")
            else:
                coverage[ident] = {"state": "missing", "document": str(reference), "status": None}
            continue

        status, superseded_by = read_status(path)
        shown = os.path.relpath(path, bases[-1] if bases else ".")
        record = {"state": "covered", "document": shown, "status": status}

        if retired_status(status):
            record["state"] = "superseded"
            trailer = f"; superseded by {superseded_by}" if superseded_by else ""
            report.add(BLOCKING, "SUPERSEDED_SPEC", where,
                       f"{shown} is {status}{trailer}; this control answers a decision nobody "
                       "holds any more, so the mitigation needs re-deciding", field="specified_in")
        elif status is None:
            report.add(ADVISORY, "STATUS_UNKNOWN", where,
                       f"{shown} carries no status this can read, so a supersession would go "
                       "unnoticed; a frontmatter status, or a Status row, is enough",
                       field="specified_in")

        stored = entry.get("specified_digest")
        if not stored:
            report.add(ADVISORY, "NO_DIGEST", where,
                       f"no specified_digest recorded against {shown}, so an edit to the "
                       "requirement cannot be detected", field="specified_digest")
        elif stored != digest(path):
            record["state"] = "stale"
            report.add(BLOCKING, "STALE_SPEC", where,
                       f"{shown} has changed since this mitigation was decided against it; "
                       "read the change, then either revise the mitigation or record the new "
                       "digest to say you have", field="specified_digest")

        coverage[ident] = record

    return coverage


# --- annotations, where a project uses them ----------------------------------

def scan_annotations(root, excludes=()):
    """Every `vector: mitigates` line in tracked files.

    git is the file list, so ignored build output and downloaded dependencies
    are invisible without reimplementing anyone's .gitignore, and `git grep`
    does the reading in one pass.
    """
    found = []
    try:
        # As above, and ANNOTATION_GREP is a module constant, so the pattern is
        # not anybody's input either.
        out = subprocess.run(
            ["git", "-C", root, "grep", "-I", "-n", "-E", ANNOTATION_GREP],  # nosec B603 B607
            capture_output=True, text=True)
    except (OSError, ValueError):
        return found
    if out.returncode not in (0, 1):
        return found

    for line in out.stdout.splitlines():
        path, _, rest = line.partition(":")
        number, _, text = rest.partition(":")
        if not number.isdigit():
            continue
        if any(fnmatch.fnmatch(path, pattern) for pattern in excludes):
            continue
        for match in ANNOTATION.finditer(text):
            slug = match.group(1)[:-1] if match.group(1) else None
            found.append({"file": path, "line": int(number), "slug": slug,
                          "id": match.group(2)})
    return found


def check_annotations(annotations, registers, report):
    """Checked where present, never required.

    An annotation naming a mitigation no register has is wrong wherever it
    appears. A mitigation with no annotation is not a failure — the annotation
    was never evidence of anything — unless the register declared where the
    control belongs, which is a project opting into more.
    """
    known = {}
    for slug, register in registers.items():
        for entry in register.get("mitigations") or []:
            if isinstance(entry, dict) and entry.get("id"):
                known.setdefault(str(entry["id"]), set()).add(slug)

    seen = {}
    for note in annotations:
        where = f"{note['file']}:{note['line']}"
        registers_for = known.get(note["id"], set())
        if note["slug"] is not None:
            if note["slug"] not in registers:
                report.add(BLOCKING, "UNKNOWN_ANNOTATION", where,
                           f"names register {note['slug']!r}, which this repository does not have")
                continue
            if note["slug"] not in registers_for:
                report.add(BLOCKING, "UNKNOWN_ANNOTATION", where,
                           f"{note['id']} is not a mitigation in {note['slug']}")
                continue
            seen.setdefault((note["slug"], note["id"]), []).append(note)
            continue

        if not registers_for:
            report.add(BLOCKING, "UNKNOWN_ANNOTATION", where,
                       f"names {note['id']}, which no register in this repository has")
        elif len(registers) > 1:
            report.add(BLOCKING, "AMBIGUOUS_ANNOTATION", where,
                       f"a bare {note['id']} where this repository holds "
                       f"{len(registers)} registers ({', '.join(sorted(registers))}); "
                       f"qualify it as <slug>/{note['id']}")
        else:
            seen.setdefault((next(iter(registers_for)), note["id"]), []).append(note)

    for slug, register in registers.items():
        for entry in register.get("mitigations") or []:
            if not isinstance(entry, dict) or not entry.get("id"):
                continue
            locations = [str(p) for p in as_list(entry.get("implemented_in"))]
            if len(locations) < 1:
                continue
            here = seen.get((slug, str(entry["id"])), [])
            missing = [location for location in locations
                       if not any(note["file"] == location
                                  or note["file"].startswith(location.rstrip("/") + "/")
                                  for note in here)]
            if missing and len(missing) < len(locations):
                report.add(BLOCKING, "PARTIAL_COVERAGE", f"mitigations/{entry['id']}",
                           f"annotated in {len(locations) - len(missing)} of {len(locations)} "
                           f"declared locations; nothing claims it in "
                           f"{', '.join(missing)}", field="implemented_in")
    return seen


# --- the repository ----------------------------------------------------------

def find_models(root, excludes=()):
    paths = []
    for base, directories, files in os.walk(root):
        directories[:] = [d for d in directories if d not in (".git", "node_modules")]
        for name in sorted(files):
            if not name.endswith(".dfd.yaml"):
                continue
            path = os.path.join(base, name)
            shown = os.path.relpath(path, root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(shown, pattern) for pattern in excludes):
                continue
            paths.append(path)
    return sorted(paths)


def find_registers(root):
    paths = []
    for base, directories, files in os.walk(root):
        directories[:] = [d for d in directories if d not in (".git", "node_modules")]
        for name in sorted(files):
            if name.endswith(".vectors.yaml"):
                paths.append(os.path.join(base, name))
    return sorted(paths)


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


def check_repository(root, as_of, excludes=()):
    report = Report()
    registers, coverage, pulse = {}, {}, []

    paths = find_registers(root)
    models = find_models(root, excludes)
    if not paths and not models:
        raise SystemExit((2, f"no *.dfd.yaml or *.vectors.yaml found under {root}"))

    # Read the file list once: every model's design_sources is matched against
    # the same tracked set, and `git ls-files` on a large repository is not free.
    files = tracked_files(root) if models else []
    for path in models:
        model = load(path, "model")
        entry = check_reviews(model, path, root, report, as_of, files=files)
        if entry is not None:
            pulse.append(entry)

    for path in paths:
        slug = os.path.basename(path)[: -len(".vectors.yaml")]
        here = os.path.dirname(os.path.abspath(path))
        bases = (here, root)
        register = load(path, "register")
        registers[slug] = register

        reference = register.get("threats")
        threats_path = os.path.join(here, reference) if reference else None
        enumeration, model_path = None, None
        if threats_path and os.path.exists(threats_path):
            enumeration = load(threats_path, "enumeration")
            model = enumeration.get("model")
            if model:
                model_path = os.path.join(os.path.dirname(threats_path), model)
        elif reference:
            report.add(BLOCKING, "UNRESOLVED_SPEC", "<file>",
                       f"threats names {reference}, which is not beside the register",
                       field="threats", source=path)

        if threats_path and os.path.exists(threats_path):
            part = check_register(register, threats_path, as_of, bases=bases,
                                  model_path=model_path)
            for gap in part.gaps:
                gap["source"] = path
            report.gaps.extend(part.gaps)

        before = len(report.gaps)
        coverage[slug] = check_currency(register, report, bases, enumeration=enumeration,
                                        model_path=model_path, threats_path=threats_path)
        for gap in report.gaps[before:]:
            gap["source"] = path

    annotations = scan_annotations(root, excludes)
    before = len(report.gaps)
    check_annotations(annotations, registers, report)
    for gap in report.gaps[before:]:
        gap.setdefault("source", None)

    summary = {
        "registers": {slug: len(register.get("vectors") or [])
                      for slug, register in registers.items()},
        "annotations": len(annotations),
        "coverage": coverage,
        "by_specification": by_specification(coverage),
        "pulse": pulse,
    }
    return report, summary


def by_specification(coverage):
    grouped = {}
    for register in coverage.values():
        for ident, record in register.items():
            document = record.get("document") or "— no specification named —"
            grouped.setdefault(document, {"status": record.get("status"), "mitigations": []})
            grouped[document]["mitigations"].append(ident)
    for entry in grouped.values():
        entry["mitigations"].sort()
    return grouped


LIMIT = ("Coverage, not proof: this says the paperwork is consistent and current, "
         "never that any control works.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", metavar="DIR", default=".",
                        help="the repository to check (default: the working directory)")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD",
                        help="the date deferrals are judged against (default: today)")
    parser.add_argument("--exclude", metavar="GLOB", action="append", default=[],
                        help="skip matching files in the annotation scan; repeatable")
    parser.add_argument("--json", action="store_true", help="emit findings and summary as JSON")
    args = parser.parse_args(argv)

    as_of = datetime.date.today()
    if args.as_of:
        as_of = as_date(args.as_of)
        if as_of is None:
            print(f"--as-of {args.as_of!r} is not a YYYY-MM-DD date", file=sys.stderr)
            return 2

    root = repository_root(args.root) if args.root == "." else os.path.abspath(args.root)
    try:
        report, summary = check_repository(root, as_of, tuple(args.exclude))
    except SystemExit as exit_:
        if isinstance(exit_.code, tuple):
            print(exit_.code[1], file=sys.stderr)
            return exit_.code[0]
        raise

    if args.json:
        print(json.dumps({
            "vendored_from": VENDORED_FROM, "as_of": as_of.isoformat(),
            "blocking": len(report.blocking), "advisory": len(report.advisory),
            "current": not report.blocking, "gaps": report.gaps, **summary,
        }, indent=2, default=str))
        return 0 if not report.blocking else 1

    print(f"vector {VENDORED_FROM} — as of {as_of.isoformat()}")
    for severity, gaps in ((BLOCKING, report.blocking), (ADVISORY, report.advisory)):
        if not gaps:
            continue
        groups = {}
        for gap in gaps:
            groups.setdefault((gap["source"], gap["element"]), []).append(gap)
        print(f"\n{severity} — {len(gaps)} finding(s)")
        print("=" * 60)
        for (source, element), items in groups.items():
            where = f"{os.path.relpath(source, root)} · {element}" if source else element
            print(f"\n  {where}")
            for gap in items:
                field = f"{gap['field']}: " if gap["field"] else ""
                print(f"    - {field}{gap['message']}")

    print("\nCoverage by specification")
    print("=" * 60)
    for document, entry in sorted(summary["by_specification"].items()):
        status = entry["status"] or "status unknown"
        print(f"  {document} [{status}] — {', '.join(entry['mitigations'])}")
    if summary["annotations"]:
        print(f"\n{summary['annotations']} annotation(s) in tracked files.")

    for entry in summary["pulse"]:
        print(f"\nCurrency of {entry['model']}")
        print("=" * 60)
        cycle = (f"read again every {entry['cycle']} days" if entry["cycle"]
                 else "no review cycle set")
        print(f"  {entry['reviews']} of {entry['documents']} design document(s) "
              f"reviewed — {cycle}")
        if entry["oldest"]:
            print(f"  oldest reading: {entry['oldest']['path']} on "
                  f"{entry['oldest']['reviewed']}, {entry['oldest']['age_days']} days ago")

    print()
    if report.blocking:
        print(f"Not current: {len(report.blocking)} blocking, {len(report.advisory)} advisory.")
        print(LIMIT)
        return 1
    if report.advisory:
        print(f"Current. {len(report.advisory)} advisory item(s).")
    else:
        print("Current.")
    print(LIMIT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
