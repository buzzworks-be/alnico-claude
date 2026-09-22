#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Report every gap in a DFD model.

The interview is over when this exits 0. Gaps are BLOCKING (the model is not
usable for threat modelling yet) or ADVISORY (a judgement call the user should
make on the record). Suppress an advisory or a blocking gap you have discussed
and deliberately accepted by listing its key under system.accepted_gaps.
"""

import argparse
import json
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

BLOCKING, ADVISORY = "BLOCKING", "ADVISORY"

ENUMS = {
    "trust_zones.controlled_by": {"us", "end_user", "cloud_provider", "third_party", "unknown"},
    "actors.type": {"human", "external_system", "third_party_service", "ai_agent"},
    "processes.kind": {"service", "job", "lambda", "manual", "llm", "agent"},
    "stores.kind": {"database", "object_store", "queue", "cache", "file", "log",
                    "third_party", "paper"},
    "data.classification": {"public", "internal", "confidential", "restricted"},
    "data.personal_data": {"none", "pseudonymous", "personal", "special_category"},
    "flows.trigger": {"user_action", "scheduled", "event", "manual"},
}

PERSONAL = {"pseudonymous", "personal", "special_category"}

# A currency review, per UC-0003. The model says where its design lives and what
# it has been read against; whether anything is unread is check_traceability's,
# because that question is about a repository rather than about this file.
REVIEW_FIELDS = ("path", "digest", "reviewed", "impact", "reason")
IMPACTS = ("none", "modelled")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

RIGHTS_WORDS = ("access request", "subject request", "dsar", "erasure", "delete",
                "deletion", "export", "download my", "right to")


class Report:
    def __init__(self, accepted):
        self.gaps = []
        self.accepted = set(accepted or [])

    def add(self, severity, code, element, message, question=None, field=None):
        key = ":".join(p for p in (code, element, field) if p)
        if key in self.accepted:
            return
        self.gaps.append({
            "severity": severity, "code": code, "element": element,
            "field": field, "message": message, "question": question, "key": key,
        })

    @property
    def blocking(self):
        return [g for g in self.gaps if g["severity"] == BLOCKING]

    @property
    def advisory(self):
        return [g for g in self.gaps if g["severity"] == ADVISORY]


def answered(item, field):
    """A field counts as answered when it holds something other than null.

    Omitting a key and setting it to null both mean 'not asked yet'. Writing
    "n/a" with a reason means asked and answered, which is why that passes.
    """
    if not isinstance(item, dict) or field not in item:
        return False
    value = item[field]
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and not value:
        return False
    return True


def require(report, severity, section, item, fields, question_map, ident=None):
    if ident is None:
        ident = item.get("id") or item.get("name") or "<unnamed>"
    element = f"{section}/{ident}" if ident else section
    for field in fields:
        if not answered(item, field):
            report.add(severity, "MISSING_FIELD", element,
                       f"{field} is unanswered",
                       question_map.get(field), field=field)


# Every section named in ENUMS must be passed to check_enums somewhere below.
# processes.kind was added with no such call and every value passed silently, so
# this is asserted at import rather than left to be noticed.
def check_enums(report, section, items):
    for item in items:
        ident = item.get("id") or "<unnamed>"
        for field, allowed in ((f.split(".")[1], v) for f, v in ENUMS.items()
                               if f.startswith(section + ".")):
            if answered(item, field) and item[field] not in allowed:
                report.add(BLOCKING, "BAD_ENUM", f"{section}/{ident}",
                           f"{field} is {item[field]!r}; expected one of "
                           f"{', '.join(sorted(allowed))}", field=field)


ACTOR_Q = {
    "type": "Is this a person, another system of yours, or a third-party service?",
    "description": "What does this actor do with the system?",
    "trust_zone": "Which trust zone does this actor sit in? A user's own device is its own zone.",
    "authenticates_how": "How does the system know this actor is who it claims to be? "
                         "If it is anonymous, say so explicitly.",
    "is_data_subject": "Is this actor a person whose personal data the system holds, "
                       "as opposed to someone who handles other people's data?",
}

# The kinds that are a model rather than ordinary code. What differs about them
# is not which threat categories apply — ADR-0004 — but which questions have an
# answer worth having, so they are conditional requirements rather than a type.
MODEL_KINDS = {"llm", "agent"}

PROCESS_Q = {
    "kind": "What kind of process is this — a service, a scheduled job, a lambda, "
            "a manual step someone performs, a language model, or an agent that "
            "acts on its own?",
    "untrusted_input": "Does anything from outside the trust boundary reach this "
                       "model's prompt or context — user text, a fetched page, a "
                       "document, a tool's output? If none of it does, say so and "
                       "say what stops it.",
    "system_prompt": "Where do this model's instructions live, and who can change "
                     "them? A prompt in a config a deploy can edit is a different "
                     "thing from one in source review.",
    "output_handling": "What consumes this model's output, and does it treat it as "
                       "data or as instruction — rendered as markup, executed, "
                       "passed to a tool, written to a store?",
    "authority": "What can this agent do without a human approving it first? "
                 "\"Nothing without approval\" is a complete answer.",
    "description": "What does this process actually do to the data, not just move it?",
    "trust_zone": "Which trust zone does this run in?",
    "owner": "Which team is accountable for this?",
    "authn": "How does this process authenticate the things that call it?",
    "authz": "Once a caller is authenticated, what decides what it is allowed to do?",
    "logging": "What does this process log, and where does that go? "
               "Model the log destination as a store.",
}

STORE_Q = {
    "description": "What is in this store, at the field level?",
    "trust_zone": "Which trust zone does this sit in?",
    "kind": "What kind of store is this — database, object store, queue, cache, file, log?",
    "data": "Which data items from the dictionary live here?",
    "encryption_at_rest": "Is this encrypted at rest, and who holds the key?",
    "access_control": "Who can read this directly, bypassing the application?",
    "retention": "How long is this kept, and what enforces that?",
    "backups": "Where do backups go, and does the retention policy reach them?",
}

FLOW_Q = {
    "from": "Where does this flow start?",
    "to": "Where does it end?",
    "data": "What data specifically travels over this flow?",
    "protocol": "Over what protocol?",
    "encryption_in_transit": "Is it encrypted in transit, and how?",
    # Two framings, because the same missing field means different things
    # depending on whether the flow leaves its trust zone. Telling someone a
    # purely internal flow "crosses a trust boundary" is simply false, and
    # false reasons train people to stop reading the gaps.
    "authn": "What authenticates this flow, if anything? Both ends sit in the "
             "same trust zone, so 'nothing, it is internal' is a real answer — "
             "worth recording rather than leaving blank.",
    "authn_crossing": "What authenticates this flow? It crosses a trust "
                      "boundary, which is where spoofing and tampering "
                      "threats live.",
    "trigger": "What triggers this — a user action, a schedule, an event, a manual step?",
}

DATA_Q = {
    "classification": "How sensitive is this — public, internal, confidential, restricted?",
    "personal_data": "Is this personal data? none, pseudonymous, personal, or special_category "
                     "(health, biometrics, sexuality, religion, politics, union membership, race).",
    "subjects": "Whose data is this?",
    "retention": "How long is this kept, and what enforces that?",
    "lawful_basis": "What is the lawful basis for processing this?",
}


REVIEW_Q = {
    "path": "Which document was read? A repository-relative path.",
    "digest": "What were its bytes when it was read? sha256: and the hex digest.",
    "reviewed": "On what date did somebody read it?",
    "impact": "Did it change the model — modelled — or not — none?",
    "reason": "Why? A no-impact reading needs the sentence a later reader can disagree with.",
}


def check_reviews(report, system):
    """The shape of a currency review, and only its shape.

    Whether a document is unreviewed is a question about a repository, not
    about this file, so it belongs to check_traceability.py. Keeping it there
    is what lets this script stay a pure function of one model: no working
    directory, no git, and no way to fail on a model that is well formed.
    """
    for field in ("design_sources", "reviewed"):
        if field in system and system[field] is not None and not isinstance(system[field], list):
            report.add(BLOCKING, "BAD_SECTION", "system", f"{field} must be a list", field=field)

    for entry in system.get("design_sources") or []:
        if not isinstance(entry, str) or not entry.strip():
            report.add(BLOCKING, "BAD_ITEM", "system",
                       f"design_sources entries are paths or globs; {entry!r} is not one",
                       field="design_sources")

    cycle = system.get("review_cycle")
    if cycle is not None and (isinstance(cycle, bool) or not isinstance(cycle, int) or cycle < 1):
        report.add(BLOCKING, "BAD_FIELD", "system",
                   f"review_cycle is {cycle!r}; it must be a whole number of days, or "
                   "absent for no expiry at all",
                   "How many days may pass before a reading has to be repeated? Leave it "
                   "out unless an obligation actually requires one.", field="review_cycle")

    reviewed = system.get("reviewed")
    if not isinstance(reviewed, list):
        return
    for index, entry in enumerate(reviewed):
        if not isinstance(entry, dict):
            report.add(BLOCKING, "BAD_ITEM", "system", "reviewed entries must be mappings",
                       field="reviewed")
            continue
        ident = str(entry.get("path") or f"#{index + 1}")
        require(report, BLOCKING, "system/reviewed", entry, REVIEW_FIELDS, REVIEW_Q, ident=ident)
        if answered(entry, "impact") and entry["impact"] not in IMPACTS:
            report.add(BLOCKING, "BAD_ENUM", f"system/reviewed/{ident}",
                       f"impact is {entry['impact']!r}; expected one of "
                       f"{', '.join(IMPACTS)}", field="impact")
        if answered(entry, "digest") and not DIGEST.match(str(entry["digest"])):
            report.add(BLOCKING, "BAD_FIELD", f"system/reviewed/{ident}",
                       f"digest is {entry['digest']!r}; expected sha256: and sixty-four "
                       "hex characters, which is what makes an edit count", field="digest")


def validate(model):
    system = model.get("system") or {}
    report = Report(system.get("accepted_gaps"))

    analysis = system.get("analysis") or []
    if isinstance(analysis, str):
        analysis = [analysis]
    privacy = "linddun" in analysis
    privacy_sev = BLOCKING if privacy else ADVISORY

    sections = {name: (model.get(name) or []) for name in
                ("trust_zones", "actors", "processes", "stores", "data", "flows")}
    for name, items in sections.items():
        if not isinstance(items, list):
            report.add(BLOCKING, "BAD_SECTION", name, f"{name} must be a list")
            sections[name] = []
            continue
        # Drop entries that are not mappings here, rather than skipping them in
        # each loop below. One malformed entry used to survive as far as
        # require(), which crashed on item.get() — so a hand-edited model with a
        # stray list item got a traceback instead of the gap that explains it.
        mappings = [item for item in items if isinstance(item, dict)]
        if len(mappings) != len(items):
            report.add(BLOCKING, "BAD_ITEM", name, "entries must be mappings")
        sections[name] = mappings

    # --- system ---------------------------------------------------------
    require(report, BLOCKING, "system", system,
            ["name", "slug", "description", "analysis"], ident="", question_map={
        "name": "What is this system called?",
        "slug": "What short kebab-case name should the files use?",
        "description": "What does it do, and for whom?",
        "analysis": "Is this for a security review (stride), a privacy review (linddun), or both?",
    })
    if analysis and not set(analysis) <= {"stride", "linddun"}:
        report.add(BLOCKING, "BAD_ENUM", "system", "analysis may only contain stride and linddun",
                   field="analysis")
    scope = system.get("scope") or {}
    require(report, BLOCKING, "system", scope, ["in_scope", "out_of_scope"], ident="",
            question_map={
        "in_scope": "What is inside this diagram?",
        "out_of_scope": "What is deliberately outside it? An empty answer is rarely true.",
    })
    check_reviews(report, system)

    # --- ids ------------------------------------------------------------
    seen, index = {}, {}
    for name, items in sections.items():
        for item in items:
            ident = item.get("id")
            if not ident:
                report.add(BLOCKING, "MISSING_FIELD", f"{name}/<unnamed>",
                           "id is unanswered", "Every element needs a unique kebab-case id.",
                           field="id")
                continue
            if ident in seen:
                report.add(BLOCKING, "DUPLICATE_ID", f"{name}/{ident}",
                           f"id {ident!r} is already used by {seen[ident]}")
            else:
                seen[ident] = name
                index[ident] = (name, item)

    def ref_ok(report, ident, owner, field, allowed):
        if ident is None:
            return False
        if ident not in index:
            report.add(BLOCKING, "UNRESOLVED_REF", owner,
                       f"{field} points at {ident!r}, which is not defined", field=field)
            return False
        if index[ident][0] not in allowed:
            report.add(BLOCKING, "UNRESOLVED_REF", owner,
                       f"{field} points at {ident!r}, which is a "
                       f"{index[ident][0][:-1]}; expected {' or '.join(a[:-1] for a in allowed)}",
                       field=field)
            return False
        return True

    # --- minimum viable diagram ------------------------------------------
    for name, why in (("actors", "someone has to be outside the system talking to it"),
                      ("processes", "a DFD with no process has nothing doing the work"),
                      ("flows", "a DFD with no flows is a list, not a diagram")):
        if not sections[name]:
            report.add(BLOCKING, "EMPTY_SECTION", name, f"no {name} defined — {why}")

    # --- per-section fields ----------------------------------------------
    for zone in sections["trust_zones"]:
        require(report, BLOCKING, "trust_zones", zone, ["name", "description", "controlled_by"], {
            "description": "What does being inside this zone mean — who controls it?",
            "controlled_by": "Who controls this zone: us, end_user, cloud_provider, "
                             "third_party, or unknown?",
        })
    check_enums(report, "trust_zones", sections["trust_zones"])

    for actor in sections["actors"]:
        fields = ["name", "type", "description", "trust_zone", "authenticates_how"]
        require(report, BLOCKING, "actors", actor, fields, ACTOR_Q)
        if privacy:
            require(report, BLOCKING, "actors", actor, ["is_data_subject"], ACTOR_Q)
        if answered(actor, "is_data_subject") and not isinstance(actor["is_data_subject"], bool):
            report.add(BLOCKING, "BAD_BOOL", f"actors/{actor.get('id')}",
                       f"is_data_subject is {actor['is_data_subject']!r}; "
                       "expected true or false", field="is_data_subject")
        ref_ok(report, actor.get("trust_zone"), f"actors/{actor.get('id')}",
               "trust_zone", {"trust_zones"})
    check_enums(report, "actors", sections["actors"])

    for proc in sections["processes"]:
        require(report, BLOCKING, "processes", proc,
                ["name", "description", "trust_zone", "owner", "kind",
                 "authn", "authz", "logging"],
                PROCESS_Q)
        # A model whose prompt untrusted text can reach, or which acts without
        # supervision, has answers no other process has. Asked only of the kinds
        # that have them, so an ordinary service is not made to answer about a
        # system prompt it does not have.
        if proc.get("kind") in MODEL_KINDS:
            fields = ["untrusted_input", "system_prompt", "output_handling"]
            if proc.get("kind") == "agent":
                fields.append("authority")
            require(report, BLOCKING, "processes", proc, fields, PROCESS_Q)
        ref_ok(report, proc.get("trust_zone"), f"processes/{proc.get('id')}",
               "trust_zone", {"trust_zones"})

    check_enums(report, "processes", sections["processes"])

    for store in sections["stores"]:
        require(report, BLOCKING, "stores", store,
                ["name", "description", "trust_zone", "kind", "data",
                 "encryption_at_rest", "access_control"], STORE_Q)
        require(report, privacy_sev, "stores", store, ["retention", "backups"], STORE_Q)
        ref_ok(report, store.get("trust_zone"), f"stores/{store.get('id')}",
               "trust_zone", {"trust_zones"})
        for ref in store.get("data") or []:
            ref_ok(report, ref, f"stores/{store.get('id')}", "data", {"data"})
    check_enums(report, "stores", sections["stores"])

    for datum in sections["data"]:
        require(report, BLOCKING, "data", datum,
                ["name", "classification", "personal_data"], DATA_Q)
        if datum.get("personal_data") in PERSONAL:
            require(report, privacy_sev, "data", datum, ["subjects", "retention"], DATA_Q)
            if privacy:
                require(report, ADVISORY, "data", datum, ["lawful_basis"], DATA_Q)
        if datum.get("personal_data") == "special_category" and privacy:
            report.add(ADVISORY, "SPECIAL_CATEGORY", f"data/{datum.get('id')}",
                       "special category data raises the bar on every element that touches it",
                       "Confirm the lawful basis and whether this data is genuinely needed.")
    check_enums(report, "data", sections["data"])

    zone_of = {}
    for name in ("actors", "processes", "stores"):
        for item in sections[name]:
            zone_of[item.get("id")] = item.get("trust_zone")

    for flow in sections["flows"]:
        fid = flow.get("id")
        require(report, BLOCKING, "flows", flow,
                ["name", "from", "to", "data", "protocol",
                 "encryption_in_transit", "trigger"], FLOW_Q)
        endpoints = {"actors", "processes", "stores"}
        ref_ok(report, flow.get("from"), f"flows/{fid}", "from", endpoints)
        ref_ok(report, flow.get("to"), f"flows/{fid}", "to", endpoints)
        for ref in flow.get("data") or []:
            ref_ok(report, ref, f"flows/{fid}", "data", {"data"})
        if flow.get("from") and flow.get("from") == flow.get("to"):
            report.add(ADVISORY, "SELF_LOOP", f"flows/{fid}",
                       "this flow starts and ends at the same element",
                       "Is this really a loop, or is one end a different element?")
        src, dst = zone_of.get(flow.get("from")), zone_of.get(flow.get("to"))
        crosses = src and dst and src != dst
        if crosses and not answered(flow, "authn"):
            report.add(BLOCKING, "UNAUTH_CROSSING", f"flows/{fid}",
                       f"crosses from {src} into {dst} with no authn recorded",
                       FLOW_Q["authn_crossing"], field="authn")
        elif not answered(flow, "authn"):
            report.add(ADVISORY, "MISSING_FIELD", f"flows/{fid}",
                       "authn is unanswered", FLOW_Q["authn"], field="authn")
    check_enums(report, "flows", sections["flows"])

    # --- graph shape ------------------------------------------------------
    inbound, outbound = {}, {}
    for flow in sections["flows"]:
        if flow.get("from") in index:
            outbound.setdefault(flow["from"], []).append(flow)
        if flow.get("to") in index:
            inbound.setdefault(flow["to"], []).append(flow)

    for name in ("actors", "processes", "stores"):
        for item in sections[name]:
            ident = item.get("id")
            if not ident:
                continue
            if ident not in inbound and ident not in outbound:
                report.add(BLOCKING, "ORPHAN", f"{name}/{ident}",
                           "no flow touches this element",
                           "Either something connects to this, or it does not belong "
                           "in the diagram. Which is it?")

    for proc in sections["processes"]:
        ident = proc.get("id")
        if not ident or (ident not in inbound and ident not in outbound):
            continue
        if ident in inbound and ident not in outbound:
            report.add(BLOCKING, "BLACK_HOLE", f"processes/{ident}",
                       "data goes in and nothing comes out",
                       "What does this produce? If it only stores things, the destination "
                       "is a data store and there is a flow to it. If it genuinely "
                       "discards everything, that is worth saying out loud.")
        if ident in outbound and ident not in inbound:
            report.add(BLOCKING, "MIRACLE", f"processes/{ident}",
                       "data comes out with nothing going in",
                       "Where does this get its data? There is usually an unmentioned "
                       "source — a config store, a third-party feed, a scheduled trigger "
                       "reading from somewhere.")

    # --- reachability ------------------------------------------------------
    nodes = [i for n in ("actors", "processes", "stores") for i in
             (x.get("id") for x in sections[n]) if i]
    if nodes and sections["flows"]:
        adjacency = {n: set() for n in nodes}
        for flow in sections["flows"]:
            a, b = flow.get("from"), flow.get("to")
            if a in adjacency and b in adjacency:
                adjacency[a].add(b)
                adjacency[b].add(a)
        # Every piece, not one flood from nodes[0]: whichever element happened
        # to be declared first was treated as the main diagram, so a single
        # stranded actor at the top of the file reported every other element as
        # the stranded one. The largest piece is the main diagram instead, ties
        # broken by declaration order, which is a property of the graph.
        pieces, placed = [], set()
        for start in nodes:
            if start in placed:
                continue
            seen_nodes, stack = set(), [start]
            while stack:
                node = stack.pop()
                if node in seen_nodes:
                    continue
                seen_nodes.add(node)
                stack.extend(adjacency[node] - seen_nodes)
            placed |= seen_nodes
            pieces.append(sorted(seen_nodes))
        if len(pieces) > 1:
            main = max(pieces, key=len)
            detached = [p for p in pieces if p is not main]
            loose = [n for p in detached for n in p]
            report.add(ADVISORY, "DISCONNECTED", "graph",
                       f"the diagram is in {len(pieces)} pieces: "
                       + "; ".join(", ".join(p) for p in detached)
                       + (" does" if len(loose) == 1 else " do")
                       + f" not connect to the other {len(main)} element"
                       + ("" if len(main) == 1 else "s"),
                       "Is there a missing flow, or are these genuinely separate systems "
                       "that belong in their own diagram?")

    # --- unused declarations ------------------------------------------------
    used_data = {r for s in sections["stores"] for r in (s.get("data") or [])}
    used_data |= {r for f in sections["flows"] for r in (f.get("data") or [])}
    for datum in sections["data"]:
        if datum.get("id") and datum["id"] not in used_data:
            report.add(ADVISORY, "UNUSED_DATA", f"data/{datum['id']}",
                       "declared but no store or flow references it",
                       "Where does this data live and how does it move?")
    used_zones = {z for z in zone_of.values() if z}
    for zone in sections["trust_zones"]:
        if zone.get("id") and zone["id"] not in used_zones:
            report.add(ADVISORY, "UNUSED_ZONE", f"trust_zones/{zone['id']}",
                       "no element sits in this zone",
                       "Does something belong here that has not been modelled yet?")

    # --- privacy shape ------------------------------------------------------
    has_personal = any(d.get("personal_data") in PERSONAL for d in sections["data"])
    # A flag we could not read already has its own gap, and reporting
    # NO_DATA_SUBJECT on top of it would be a second, misleading finding about a
    # question the model may well have answered.
    flags = [a.get("is_data_subject") for a in sections["actors"]]
    unreadable = any(f is not None and not isinstance(f, bool) for f in flags)
    subjects = [a for a in sections["actors"] if a.get("is_data_subject") is True]

    if privacy and has_personal:
        if not unreadable and not subjects:
            report.add(BLOCKING, "NO_DATA_SUBJECT", "actors",
                       "the model holds personal data but no actor is marked as its subject",
                       "Whose personal data is this? That person is an actor, even if they "
                       "never interact with the system directly.")
        haystack = " ".join(
            str(f.get(k) or "") for f in sections["flows"] for k in ("name", "notes", "id")
        ).lower()
        if not any(word in haystack for word in RIGHTS_WORDS):
            report.add(ADVISORY, "NO_RIGHTS_FLOW", "flows",
                       "no flow looks like a data subject access, export, or deletion request",
                       "How does someone get a copy of their data, or have it deleted? "
                       "If that is a manual process, model the human step. If it does not "
                       "exist, that absence is itself the finding.")

    # The mirror of NO_DATA_SUBJECT, and it exists for the same reason: both
    # statements are answered and they contradict each other. LINDDUN
    # applicability reads the actor's flag, so left alone this model produces a
    # privacy analysis of a system that holds no personal data — questions about
    # linking and identifying asked of a person the data dictionary says is not
    # in there.
    #
    # Unlike its mirror this does not stand down for an unreadable flag, because
    # `subjects` counts only definite trues: one actor confirmed as a subject
    # contradicts an empty data dictionary whatever a second actor's flag says.
    if privacy and not has_personal and subjects:
        named = ", ".join(a.get("id") or "<unnamed>" for a in subjects)
        report.add(BLOCKING, "NO_PERSONAL_DATA", "data",
                   f"{named} is marked as a data subject, but no data entry is personal",
                   "Which of these data entries is this person's personal data? If none of "
                   "it is — if the model really holds nothing personal — then nobody is a "
                   "data subject of this system and the flag should be false.")

    if system.get("open_questions"):
        report.add(ADVISORY, "OPEN_QUESTIONS", "system",
                   f"{len(system['open_questions'])} question(s) the team could not answer",
                   "Carry these into the threat enumeration — an unanswerable question is "
                   "usually a finding in waiting.")

    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model", help="path to the .dfd.yaml model")
    parser.add_argument("--json", action="store_true", help="emit gaps as JSON")
    args = parser.parse_args()

    # Exit 2, not 1, and the distinction is the whole point: 1 means the model
    # has blocking gaps, which is what the interview loops on. `sys.exit(str)`
    # exits 1, so a mistyped filename used to be indistinguishable from an
    # unfinished model — the skill would keep interviewing against a file that
    # was never there. Every other check in the toolkit already separates the
    # two this way.
    def usage(message):
        print(message, file=sys.stderr)
        sys.exit(2)

    try:
        with open(args.model) as handle:
            model = yaml.safe_load(handle)
    except FileNotFoundError:
        usage(f"no such model: {args.model}")
    except yaml.YAMLError as exc:
        usage(f"{args.model} is not valid YAML: {exc}")

    if not isinstance(model, dict):
        usage(f"{args.model} should be a mapping with system/actors/processes/... keys")

    report = validate(model)

    if args.json:
        print(json.dumps({
            "blocking": len(report.blocking),
            "advisory": len(report.advisory),
            "complete": not report.blocking,
            "gaps": report.gaps,
        }, indent=2))
        return 0 if not report.blocking else 1

    # Grouped by element, because that is the unit the interview asks in: one
    # element's gaps are one coherent question for the person answering, and a
    # flat list by check type scatters them.
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
                print(f"    - {gap['message']}")
                if gap["question"]:
                    print(f"      ask: {gap['question']}")
                print(f"      key: {gap['key']}")

    print()
    if report.blocking:
        print(f"Not complete: {len(report.blocking)} blocking, "
              f"{len(report.advisory)} advisory.")
        return 1
    if report.advisory:
        print(f"No blocking gaps. {len(report.advisory)} advisory item(s) left to walk "
              "through with the user; record each decision in system.assumptions and "
              "add its key to system.accepted_gaps to retire it.")
    else:
        print("Complete: no blocking or advisory gaps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
