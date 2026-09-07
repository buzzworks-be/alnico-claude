---
name: close-case
description: "Close the case: final leak sweep, then detach. Invoke by name."
---

# Close case

Detach the target and return Heimdall to the state the leak rules assume:
target-agnostic, and shareable because it is.

## Where the scripts are

Resolve it once, at the top of your shell work:

```sh
H="${CLAUDE_PLUGIN_ROOT:-.}"    # plugin cache when installed, this directory otherwise
```

Then invoke everything as `"$H"/bin/<name>`. The variable is set in the
environment when Heimdall is installed, so the expansion is correct without the
skill needing to know where it is running from.

## Why this exists

The gitignore keeps the target out of Heimdall's *history* — not out of
backups, archives, or anything else that reads the filesystem. An attached
`.heimdall/` and the case files under `cases/` are the two places the target
lives on this machine, and closing the case deals with both deliberately.

## Procedure

1. **Confirm the case files were handed over.** They are handoff artifacts and
   live only here; once the case closes, this machine may be the last copy.
   If any case file was never delivered, deliver it now.
2. **Run the closer:**

   ```sh
   "$H"/bin/detach-target.sh                      # sweep, list case files, detach
   "$H"/bin/detach-target.sh --purge-case-files   # additionally delete them
   ```

   It runs `"$H"/bin/check-no-leak` **before** detaching — the guard reads its
   search terms from the attachment's own metadata, so the sweep must happen
   while it still knows what to look for. A failed or inconsistent sweep
   blocks detachment (exit 7); resolve the leak first, never force past it.

   It also refuses (exit 8) when readings are held with nothing
   attached. There the guard has no identifiers to search for, so it would
   exit 0 without having looked — and a close reported from that state is a
   claim about a sweep that never ran. Re-attach the target those readings
   are about and close properly, or hand them over and delete them by hand.
   Do not report a clean close over an exit 8.
3. **Report the outcome**: swept clean, target detached, which case files remain
   on this machine (or that they were purged). If the script refused, report
   the refusal and its reason — never paraphrase it as a close.

Never purge case files on your own initiative — deleting the possibly-last copy
of a reading is the user's call. Default is to keep and say so.

## After

Heimdall is cold again: `/open-case` opens the next one. Nothing about the previous target remains outside any case files
deliberately kept.

## Shells

A case directory with bookkeeping and no reading — an attach that never
profiled, or readings handed over and deleted by hand — is an empty shell.
It carries nothing about any target, but it holds a codename out of the
wordlist for ever and is listed as held at every close. The closer removes
every such shell at every close and names what it removed; nothing with a
case file in it is ever touched this way. Say what was tidied.
