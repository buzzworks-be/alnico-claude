"""Rewrite .claude-plugin/marketplace.json from plugins/*/.claude-plugin/plugin.json."""
import json
import pathlib

MARKETPLACE = pathlib.Path(".claude-plugin/marketplace.json")
SYNCED = ("description", "author", "license", "version")

market = json.loads(MARKETPLACE.read_text())
existing = {e["name"]: e for e in market["plugins"]}

plugins = []
for manifest_path in sorted(pathlib.Path("plugins").glob("*/.claude-plugin/plugin.json")):
    manifest = json.loads(manifest_path.read_text())
    name = manifest["name"]
    entry = existing.get(name, {"name": name})
    for key in SYNCED:
        if key in manifest:
            entry[key] = manifest[key]
    entry["source"] = f"./{manifest_path.parent.parent.as_posix()}"
    plugins.append(entry)

market["plugins"] = plugins
MARKETPLACE.write_text(json.dumps(market, indent=2, ensure_ascii=False) + "\n")
