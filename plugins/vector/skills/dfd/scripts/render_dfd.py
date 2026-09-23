#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Render a DFD model as Markdown with a Mermaid diagram and element tables.

The diagram is a view, not the source of truth. Regenerate it after every edit
to the model rather than hand-editing the output.
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


def sibling(name):
    """A sibling script, imported rather than reimplemented.

    The provenance marker is written here and read by check_traceability.py, so
    it is spelled once, there, where the check that depends on it lives.
    """
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

SHAPES = {
    # External entities are squared off, processes rounded, stores are
    # cylinders — the same visual vocabulary as a hand-drawn DFD, so anyone
    # who has seen one before can read this without the legend.
    "actors": ('["', '"]'),
    "processes": ('("', '")'),
    "stores": ('[("', '")]'),
    # A subsystem is not one of those things. It is a name for a group of them,
    # so it gets the subroutine shape: a box that reads as standing for
    # something rather than being it.
    "subsystems": ('[["', '"]]'),
}


def cell(value):
    """Flatten a value into something safe for a Markdown table cell."""
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "—"
    text = str(value).strip()
    return text.replace("|", "\\|").replace("\n", "<br>") if text else "—"


# Mermaid parses these as syntax, so an element whose id collides with one
# would silently break the whole diagram rather than one node.
RESERVED = {"end", "graph", "subgraph", "class", "classdef", "click", "style",
            "linkstyle", "direction", "o", "x"}


def label(text):
    """Mermaid labels are quoted and pipe-delimited, so both characters go."""
    return str(text).replace('"', "'").replace("|", "/").replace("\n", " ")


def mid(ident):
    """A Mermaid-safe node id. Trailing underscore keeps it readable."""
    return f"{ident}_" if str(ident).lower() in RESERVED else str(ident)


def parents_of(model):
    """{element_id: subsystem_id}, for the elements that name one."""
    return {item["id"]: item["parent"]
            for name in ("processes", "stores")
            for item in (model.get(name) or [])
            if isinstance(item, dict) and item.get("id") and item.get("parent")}


def project(model, scope=None):
    """Which node stands for each element, in the diagram named by `scope`.

    There are two levels, so this is one hop and never a walk up a chain.
    Inside the scope an element stands for itself; outside it, its subsystem
    stands for it; an element in no subsystem always stands for itself.
    `scope=None` is the overview, where every element stands for its subsystem.

    A model that declares no subsystems maps every element to itself, which is
    what keeps the rest of this file producing exactly what it produced before
    the field existed.
    """
    parent = parents_of(model)
    stands_for = {}
    for name in ("actors", "processes", "stores"):
        for item in (model.get(name) or []):
            if not isinstance(item, dict) or not item.get("id"):
                continue
            owner = parent.get(item["id"])
            stands_for[item["id"]] = (item["id"] if owner in (None, scope)
                                      else owner)
    return stands_for


def mermaid(model, scope=None):
    sections = {n: (model.get(n) or []) for n in
                ("trust_zones", "subsystems", "actors", "processes", "stores",
                 "flows")}
    stands_for = project(model, scope)
    parent = parents_of(model)
    zone_of, node_line, element_zone = {}, {}, {}

    for section, (open_shape, close_shape) in SHAPES.items():
        if section == "subsystems":
            continue
        for item in sections[section]:
            ident = item.get("id")
            if not ident:
                continue
            element_zone[ident] = item.get("trust_zone")
            if stands_for.get(ident) != ident:
                continue
            zone_of[ident] = item.get("trust_zone")
            name = label(item.get("name") or ident)
            node_line[ident] = f'{mid(ident)}{open_shape}{name}{close_shape}'

    # A subsystem standing in for several elements takes their trust zone only
    # when every one of them is in it. One that straddles a boundary is drawn
    # outside the zones, which is the more useful of the two things it could
    # say: a part reaching across a boundary is the part to look at first.
    stood_for = {}
    for ident, stands in stands_for.items():
        if stands != ident:
            stood_for.setdefault(stands, []).append(ident)
    open_shape, close_shape = SHAPES["subsystems"]
    for sub in sections["subsystems"]:
        ident = sub.get("id")
        if not ident or ident not in stood_for:
            continue
        zones = {element_zone.get(i) for i in stood_for[ident]}
        zone_of[ident] = zones.pop() if len(zones) == 1 else None
        name = label(sub.get("name") or ident)
        node_line[ident] = f'{mid(ident)}{open_shape}{name}{close_shape}'

    # A subsystem's own diagram holds its elements and whatever they touch,
    # rather than the whole model with one part expanded.
    if scope is not None:
        inside = {i for i in stands_for if parent.get(i) == scope}
        keep = set(inside)
        for flow in sections["flows"]:
            ends = (stands_for.get(flow.get("from")), stands_for.get(flow.get("to")))
            if any(e in inside for e in ends):
                keep |= {e for e in ends if e}
        node_line = {i: line for i, line in node_line.items() if i in keep}
        zone_of = {i: z for i, z in zone_of.items() if i in keep}

    # Top-to-bottom, because a real model is wider than a screen otherwise.
    # Measured with mermaid-cli over the four models in this repository: LR
    # rendered 2874, 2398, 4094 and 2897 pixels wide; TB rendered 2317, 1389,
    # 1823 and 1982. The largest halves. Height grows in exchange, and that is
    # the right trade where these are read — a Markdown column scales a wide
    # diagram down until the labels are unreadable, and scrolls a tall one.
    #
    # `direction` inside a subgraph is not the lever it looks like: Mermaid
    # ignores it once edges cross between subgraphs, which every data flow
    # diagram has. Both LR and TB measured byte-identical with and without it.
    lines = ["flowchart TB"]

    for zone in sections["trust_zones"]:
        members = [i for i, z in zone_of.items() if z == zone.get("id")]
        if not members:
            continue
        lines.append(f'  subgraph {mid(zone["id"])}'
                     f'["{label(zone.get("name") or zone["id"])}"]')
        for ident in members:
            lines.append(f"    {node_line[ident]}")
        lines.append("  end")

    for ident, line in node_line.items():
        if not zone_of.get(ident):
            lines.append(f"  {line}")

    data_names = {d.get("id"): (d.get("name") or d.get("id"))
                  for d in (model.get("data") or [])}

    # Flows that land on the same pair of nodes become one arrow — but only
    # where a subsystem stood in for an end of them. Two flows drawn between
    # the same two elements are two facts about the model and are still drawn
    # twice, which is what keeps an unlayered model rendering exactly as it
    # did before any of this existed.
    grouped = {}
    for flow in sections["flows"]:
        src = stands_for.get(flow.get("from"), flow.get("from"))
        dst = stands_for.get(flow.get("to"), flow.get("to"))
        if src not in node_line or dst not in node_line or src == dst:
            continue
        grouped.setdefault((src, dst), []).append(flow)
    merged = {pair for pair, group in grouped.items()
              if any(f.get("from") != pair[0] or f.get("to") != pair[1] for f in group)}

    def arrow_for(src, dst, group):
        carried = []
        for flow in group:
            for ref in (flow.get("data") or []):
                name = str(data_names.get(ref, ref))
                if name not in carried:
                    carried.append(name)
        if not carried:
            carried = [f.get("name") for f in group if f.get("name")]
        seen, names = set(), []
        for name in carried:
            if name and name not in seen:
                seen.add(name)
                names.append(name)
        text = label(", ".join(names))
        # Read from the elements the flow actually connects, not from the nodes
        # drawn for them. A subsystem spanning two zones has no zone of its own,
        # so asking the drawn nodes would call every arrow touching it internal
        # — including the ones that leave the system altogether.
        crosses = any(element_zone.get(f.get("from")) and element_zone.get(f.get("to"))
                      and element_zone[f["from"]] != element_zone[f["to"]]
                      for f in group)
        arrow = "==>" if crosses else "-->"
        return (f'  {mid(src)} {arrow}|"{text}"| {mid(dst)}' if text
                else f"  {mid(src)} {arrow} {mid(dst)}")

    drawn = set()
    for flow in sections["flows"]:
        src = stands_for.get(flow.get("from"), flow.get("from"))
        dst = stands_for.get(flow.get("to"), flow.get("to"))
        if (src, dst) not in grouped:
            continue
        if (src, dst) in merged:
            if (src, dst) in drawn:
                continue
            drawn.add((src, dst))
            lines.append(arrow_for(src, dst, grouped[(src, dst)]))
        else:
            lines.append(arrow_for(src, dst, [flow]))

    return "\n".join(lines)


def table(headers, rows):
    if not rows:
        return "_None recorded._\n"
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(out) + "\n"


def bullets(items):
    if not items:
        return "_None recorded._\n"
    return "\n".join(f"- {i}" for i in items) + "\n"


def render(model):
    system = model.get("system") or {}
    scope = system.get("scope") or {}
    data_names = {d.get("id"): (d.get("name") or d.get("id"))
                  for d in (model.get("data") or [])}
    zone_names = {z.get("id"): (z.get("name") or z.get("id"))
                  for z in (model.get("trust_zones") or [])}

    def zone(ident):
        return cell(zone_names.get(ident, ident))

    def data_list(refs):
        return cell([data_names.get(r, r) for r in (refs or [])])

    out = [f"# {system.get('name') or 'Untitled system'} — data flow diagram\n"]
    if system.get("description"):
        out.append(f"{system['description']}\n")

    analysis = system.get("analysis") or []
    if analysis:
        pretty = {"stride": "STRIDE (security)", "linddun": "LINDDUN (privacy)"}
        out.append("**Scoped for:** " + ", ".join(pretty.get(a, a) for a in analysis) + "\n")

    out.append("## Scope\n")
    out.append("**In scope**\n\n" + bullets(scope.get("in_scope")))
    out.append("\n**Out of scope**\n\n" + bullets(scope.get("out_of_scope")))

    subsystems = [s for s in (model.get("subsystems") or []) if isinstance(s, dict)]
    parent = parents_of(model)
    subsystems = [s for s in subsystems if s.get("id") in set(parent.values())]

    legend = ("Rectangles are external entities, rounded boxes are processes, cylinders "
              "are data stores, and boxed groups are trust zones. A thick arrow crosses "
              "a trust boundary.")
    if subsystems:
        legend = legend.replace(
            "cylinders are data stores,",
            "cylinders are data stores, double-edged boxes stand for a whole "
            "subsystem,")
        out.append("\n## Overview\n")
        out.append("```mermaid\n" + mermaid(model, None) + "\n```\n")
        out.append(legend + " Each subsystem is drawn in full in its own section "
                   "below; a subsystem drawn outside every zone spans more than "
                   "one of them.\n")
    else:
        out.append("\n## Diagram\n")
        out.append("```mermaid\n" + mermaid(model) + "\n```\n")
        out.append(legend + "\n")

    out.append("\n## Trust zones\n")
    out.append(table(["Zone", "Controlled by", "Description"],
                     [[cell(z.get("name") or z.get("id")), cell(z.get("controlled_by")),
                       cell(z.get("description"))] for z in (model.get("trust_zones") or [])]))

    out.append("\n## External entities\n")
    out.append(table(["Actor", "Type", "Zone", "Authenticated by", "Data subject"],
                     [[cell(a.get("name")), cell(a.get("type")), zone(a.get("trust_zone")),
                       cell(a.get("authenticates_how")), cell(a.get("is_data_subject"))]
                      for a in (model.get("actors") or [])]))

    def process_table(items):
        return table(["Process", "Zone", "Owner", "Authn", "Authz", "Logging"],
                     [[cell(p.get("name")), zone(p.get("trust_zone")), cell(p.get("owner")),
                       cell(p.get("authn")), cell(p.get("authz")), cell(p.get("logging"))]
                      for p in items])

    def store_table(items):
        return table(["Store", "Kind", "Zone", "Holds", "At rest", "Access", "Retention",
                      "Backups"],
                     [[cell(s.get("name")), cell(s.get("kind")), zone(s.get("trust_zone")),
                       data_list(s.get("data")), cell(s.get("encryption_at_rest")),
                       cell(s.get("access_control")), cell(s.get("retention")),
                       cell(s.get("backups"))]
                      for s in items])

    processes = [p for p in (model.get("processes") or []) if isinstance(p, dict)]
    stores = [t for t in (model.get("stores") or []) if isinstance(t, dict)]

    if subsystems:
        # One part at a time: its diagram and its own elements together, rather
        # than one picture of everything and two flat tables under it.
        for sub in subsystems:
            ident = sub.get("id")
            out.append(f"\n## {sub.get('name') or ident}\n")
            if sub.get("description"):
                out.append(f"{sub['description']}\n")
            out.append("```mermaid\n" + mermaid(model, ident) + "\n```\n")
            mine = [p for p in processes if p.get("parent") == ident]
            held = [t for t in stores if t.get("parent") == ident]
            if mine:
                out.append("\n**Processes**\n\n" + process_table(mine))
            if held:
                out.append("\n**Data stores**\n\n" + store_table(held))
        # Named to read as a question. An element both parts read and write is
        # honestly at level 0; a model where most of them are here is one
        # somebody should look at again, and nothing reports that.
        loose_p = [p for p in processes if not p.get("parent")]
        loose_s = [t for t in stores if not t.get("parent")]
        if loose_p or loose_s:
            out.append("\n## Not in a subsystem\n")
            if loose_p:
                out.append("\n**Processes**\n\n" + process_table(loose_p))
            if loose_s:
                out.append("\n**Data stores**\n\n" + store_table(loose_s))
    else:
        out.append("\n## Processes\n")
        out.append(process_table(processes))
        out.append("\n## Data stores\n")
        out.append(store_table(stores))

    out.append("\n## Data dictionary\n")
    out.append(table(["Data", "Classification", "Personal data", "Subjects", "Retention",
                      "Lawful basis"],
                     [[cell(d.get("name")), cell(d.get("classification")),
                       cell(d.get("personal_data")), cell(d.get("subjects")),
                       cell(d.get("retention")), cell(d.get("lawful_basis"))]
                      for d in (model.get("data") or [])]))

    zone_of = {i.get("id"): i.get("trust_zone") for n in ("actors", "processes", "stores")
               for i in (model.get(n) or [])}
    element_names = {i.get("id"): (i.get("name") or i.get("id"))
                     for n in ("actors", "processes", "stores")
                     for i in (model.get(n) or [])}
    flow_rows = []
    for f in (model.get("flows") or []):
        src, dst = f.get("from"), f.get("to")
        crosses = (zone_of.get(src) and zone_of.get(dst)
                   and zone_of[src] != zone_of[dst])
        flow_rows.append([cell(f.get("name")), cell(element_names.get(src, src)),
                          cell(element_names.get(dst, dst)), data_list(f.get("data")),
                          cell(f.get("protocol")), cell(f.get("encryption_in_transit")),
                          cell(f.get("authn")), cell(f.get("trigger")),
                          "yes" if crosses else "no"])
    out.append("\n## Data flows\n")
    out.append(table(["Flow", "From", "To", "Carries", "Protocol", "In transit",
                      "Authn", "Trigger", "Crosses boundary"], flow_rows))

    out.append("\n## Assumptions\n")
    out.append(bullets(system.get("assumptions")))
    out.append("\n## Open questions\n")
    out.append(bullets(system.get("open_questions")))

    reviewed = [r for r in (system.get("reviewed") or []) if isinstance(r, dict)]
    if reviewed:
        # Sorted by the recorded date, newest first, with an unparseable or
        # missing one last rather than dropped: a reader should see the entry
        # and the fact that it does not say when.
        def when(entry):
            return str(entry.get("reviewed") or "")
        reviewed = sorted(reviewed, key=when, reverse=True)
        out.append("\n## Reviewed against\n")
        oldest = min((when(r) for r in reviewed if when(r)), default=None)
        claim = ("This model has been read against the documents below. It is a claim "
                 "about documents, never about the system: a design change made without "
                 "one is invisible here.")
        if oldest:
            claim += f" The oldest reading here is from {oldest}."
        if system.get("review_cycle"):
            claim += f" This model asks to be read again every {system['review_cycle']} days."
        out.append(claim + "\n")
        out.append(table(["Document", "Read on", "Impact", "Why"],
                         [[cell(r.get("path")), cell(r.get("reviewed")),
                           cell(r.get("impact")), cell(r.get("reason"))]
                          for r in reviewed]))

    out.append("\n---\n")
    out.append("_Generated from the model by `render_dfd.py`. Edit the `.dfd.yaml` "
               "and regenerate; changes made here will be lost._\n")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model", help="path to the .dfd.yaml model")
    parser.add_argument("-o", "--output", help="write here instead of stdout")
    parser.add_argument("--mermaid-only", action="store_true",
                        help="emit just the diagram, for pasting elsewhere")
    args = parser.parse_args()

    try:
        with open(args.model) as handle:
            model = yaml.safe_load(handle)
    except FileNotFoundError:
        sys.exit(f"no such model: {args.model}")
    except yaml.YAMLError as exc:
        sys.exit(f"{args.model} is not valid YAML: {exc}")

    if not isinstance(model, dict):
        sys.exit(f"{args.model} should be a mapping with system/actors/processes/... keys")

    if args.mermaid_only:
        text = mermaid(model) + "\n"
    else:
        text = sibling("check_traceability").stamp(render(model), args.model)

    if args.output:
        with open(args.output, "w") as handle:
            handle.write(text)
        print(f"wrote {args.output}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
