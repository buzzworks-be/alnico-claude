---
name: recap
description: >-
  One screen: what this toolkit is, the capabilities in the order a chain runs,
  and where this repository currently stands — every model it holds, how far
  each has got, and the first thing that would move it. Use when somebody asks
  what vector is, what the order is, which command comes next, "where were we",
  "what state is this in", "what do I run first" — or at the start of a session
  in a repository whose chain nobody in the room has seen before. Reports only:
  it writes nothing, decides nothing, and always exits 0.
---

# The recap: what this is, and where this repository stands

A chain is seven commands in an order nothing tells you, over four artefacts
that derive from one another by digest. This is the one command that does not
need you to know any of that first.

## Run it

```sh
python3 "${CLAUDE_PLUGIN_ROOT}"/skills/dfd/scripts/recap.py $ARGUMENTS
```

`$ARGUMENTS` is an optional slug — `recap.py acme-checkout` reports on that one
model rather than every model in the tree. `--root` chooses the directory,
`--as-of` the date deferrals are judged against, and `--exclude` a glob to leave
out, repeatably.

## Then paste what it printed, into the reply

**Reproduce the output verbatim in your reply, inside a fenced code block, and
stop.** Do not summarise it, re-order it, rank it, or soften any line of it.

Not "the output is above". Not "as shown". In most clients the block holding a
command's output is **collapsed by default**, so a reply that points at it
leaves the reader looking at one sentence *about* the recap instead of the
recap — which is the summary this skill exists to prevent, arrived at by
gesture rather than by paraphrase. The person asked for a screen. Give them
the screen.

The fence is not decoration either: the chain table and the per-model block are
aligned in columns, and Markdown outside a fence collapses the runs of spaces
that hold them apart.

That is the whole of this skill, and it is not a style preference. Every state
the script prints is a sentence some other check wrote about its own subject,
relayed rather than interpreted — which is the only protection a recap has.
Everything else in this toolkit derives from something and breaks loudly when
that something moves; a recap derives from a repository at one instant and has
nothing to break against. A summary of a summary is where a confident falsehood
gets in, and nothing downstream would catch it.

Afterwards you may add something the script could not know — that a version
just shipped, that a path moved — as long as it is plainly your own and comes
after the block rather than instead of a line in it.

If a line looks wrong, the answer is to run the check it came from and read the
whole thing, not to adjust the wording.

## What it will not tell you

That anybody read any of it. The script closes by saying so, and that closing
line is the difference between a screen of green and coverage — leave it in.

## When the repository has no model

The script says so and names `/vector:dfd`. That is the right answer and not an
empty result: a chain that has not started is the normal state of a repository
that has just installed this.
