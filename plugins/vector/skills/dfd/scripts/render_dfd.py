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
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

SHAPES = {
    # External entities are squared off, processes rounded, stores are
    # cylinders — the same visual vocabulary as a hand-drawn DFD, so anyone
    # who has seen one before can read this without the legend.
    "actors": ('["', '"]'),
    "processes": ('("', '")'),
    "stores": ('[("', '")]'),
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


def mermaid(model):
    sections = {n: (model.get(n) or []) for n in
                ("trust_zones", "actors", "processes", "stores", "flows")}
    zone_of, node_line = {}, {}

    for section, (open_shape, close_shape) in SHAPES.items():
        for item in sections[section]:
            ident = item.get("id")
            if not ident:
                continue
            zone_of[ident] = item.get("trust_zone")
            name = label(item.get("name") or ident)
            node_line[ident] = f'{mid(ident)}{open_shape}{name}{close_shape}'

    lines = ["flowchart LR"]

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

    for flow in sections["flows"]:
        src, dst = flow.get("from"), flow.get("to")
        if src not in node_line or dst not in node_line:
            continue
        carried = [str(data_names.get(r, r)) for r in (flow.get("data") or [])]
        text = label(", ".join(carried) if carried else (flow.get("name") or ""))
        crosses = zone_of.get(src) and zone_of.get(dst) and zone_of[src] != zone_of[dst]
        arrow = "==>" if crosses else "-->"
        lines.append(f'  {mid(src)} {arrow}|"{text}"| {mid(dst)}' if text
                     else f"  {mid(src)} {arrow} {mid(dst)}")

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

    out.append("\n## Diagram\n")
    out.append("```mermaid\n" + mermaid(model) + "\n```\n")
    out.append("Rectangles are external entities, rounded boxes are processes, cylinders "
               "are data stores, and boxed groups are trust zones. A thick arrow crosses "
               "a trust boundary.\n")

    out.append("\n## Trust zones\n")
    out.append(table(["Zone", "Controlled by", "Description"],
                     [[cell(z.get("name") or z.get("id")), cell(z.get("controlled_by")),
                       cell(z.get("description"))] for z in (model.get("trust_zones") or [])]))

    out.append("\n## External entities\n")
    out.append(table(["Actor", "Type", "Zone", "Authenticated by", "Data subject"],
                     [[cell(a.get("name")), cell(a.get("type")), zone(a.get("trust_zone")),
                       cell(a.get("authenticates_how")), cell(a.get("is_data_subject"))]
                      for a in (model.get("actors") or [])]))

    out.append("\n## Processes\n")
    out.append(table(["Process", "Zone", "Owner", "Authn", "Authz", "Logging"],
                     [[cell(p.get("name")), zone(p.get("trust_zone")), cell(p.get("owner")),
                       cell(p.get("authn")), cell(p.get("authz")), cell(p.get("logging"))]
                      for p in (model.get("processes") or [])]))

    out.append("\n## Data stores\n")
    out.append(table(["Store", "Kind", "Zone", "Holds", "At rest", "Access", "Retention",
                      "Backups"],
                     [[cell(s.get("name")), cell(s.get("kind")), zone(s.get("trust_zone")),
                       data_list(s.get("data")), cell(s.get("encryption_at_rest")),
                       cell(s.get("access_control")), cell(s.get("retention")),
                       cell(s.get("backups"))]
                      for s in (model.get("stores") or [])]))

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

    text = mermaid(model) + "\n" if args.mermaid_only else render(model)

    if args.output:
        with open(args.output, "w") as handle:
            handle.write(text)
        print(f"wrote {args.output}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
