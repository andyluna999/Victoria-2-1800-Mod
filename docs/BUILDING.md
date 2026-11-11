# Building HPM 1800

## What you need

- A copy of the **Historical Project Mod**, unmodified, at `hpm/HPM - Copy`
- Python 3.11 or later
- Pillow, for the flag and event art passes

## Running the build

```sh
bash tools/make.sh
```

This reads the pristine HPM and writes a complete mod to `build/HPM`. It does not
modify the source. Running it twice produces byte-identical output — if it does not,
something is wrong and the determinism check at the end will say so.

## How the build is organised

Each pass in `tools/` does one thing. The order in `make.sh` matters a great deal and
is commented where it is not obvious. Several passes rewrite files that earlier passes
produced, so a change inserted at the wrong point will be silently overwritten — this
has happened enough times to be worth stating plainly.

Rough order:

1. **World data** — provinces, owners, cores, pops, cultures, the 1800 political map
2. **Countries** — governments, parties, accepted cultures, technology, treasuries
3. **Military** — orders of battle, soldier pops, leaders, navies, unit types
4. **Content** — the event and decision chains, in rough chronological order
5. **Presentation** — flags, event art, picture mapping, window widths
6. **Audits** — five suites, all of which must pass

## The audits

Run individually:

```sh
python3 tools/lint.py
python3 tools/sweep.py
python3 tools/deep_audit.py
python3 tools/chain_audit.py
python3 tools/demographic_audit.py
```

`deep_audit.py` compares against a recorded baseline and reports only new defects. To
re-record the baseline after a deliberate change, see the file.

## Writing a new pass

Three rules, each learned the hard way:

**Check the idiom against HPM's own usage before writing it.** Victoria II accepts a
great deal of syntax that does nothing. `if = { limit = ... }` parses and never fires.
`move_pop` beside `reduce_pop` parses and moves nobody. `years` in a mean time parses
and is ignored. If HPM does not write it somewhere in its three thousand events, there
is probably a reason.

**A province takes `add_province_modifier`, not `add_country_modifier`.** The country
form aimed at a province is accepted and silently does nothing.

**Flags and modifiers are matched as whole names, not substrings.** A guard like
`if "the_liberator" not in src` matches `the_liberator_lives` and skips the write.
