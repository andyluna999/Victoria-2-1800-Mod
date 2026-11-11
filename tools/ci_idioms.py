"""Guard against the idioms that have silently broken this mod.

Victoria II accepts a great deal of syntax that does nothing at all. Every one of
these parsed cleanly, passed every audit, and produced no effect in play until a
playthrough caught it -- which took weeks each time.

This runs without a copy of HPM, so it can live in CI.
"""
import re, sys, glob, pathlib

BANNED = [
    (r"\bif\s*=\s*\{\s*limit\s*=",
     "`if = { limit = ... }` is EU4 syntax. Victoria II has no `if` effect; the "
     "block parses and every branch fires."),
    (r"mean_time_to_happen\s*=\s*\{[^}]*\byears\s*=",
     "`years` in a mean time is ignored. HPM uses months and days only."),
    (r"reduce_pop[^{}]*move_pop|move_pop[^{}]*reduce_pop",
     "`reduce_pop` beside `move_pop` appears nowhere in HPM's three thousand "
     "events. The waves fire and nobody moves."),
    (r"random_pop\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*move_pop",
     "`move_pop` inside `random_pop` is not an idiom HPM uses. Use `any_pop`."),
    (r"\b\d{1,4}\s*=\s*\{[^{}]*add_country_modifier",
     "A province takes `add_province_modifier`. The country form aimed at a "
     "province is accepted and does nothing."),
]

# The audit files describe these idioms in order to detect them, so they match
# themselves. They are not generating anything.
SKIP = ("ci_idioms.py", "lint.py", "sweep.py", "deep_audit.py", "chain_audit.py",
        "demographic_audit.py", "event_audit.py")

fails = 0
for f in sorted(glob.glob("tools/*.py")):
    if any(f.endswith(x) for x in SKIP):
        continue
    text = pathlib.Path(f).read_text(encoding="utf-8", errors="replace")
    # `70 = { ... }` inside a random_list is a probability weight, not a province id.
    # The bodies nest, so strip them by counting braces rather than by regex.
    out, i = [], 0
    while True:
        m = re.search(r"random_list\s*=\s*\{", text[i:])
        if not m:
            out.append(text[i:]); break
        start = i + m.start(); j = i + m.end(); d = 1
        while j < len(text) and d:
            if text[j] == "{": d += 1
            elif text[j] == "}": d -= 1
            j += 1
        out.append(text[i:start]); i = j
    text = "".join(out)
    for pat, why in BANNED:
        for m in re.finditer(pat, text, re.S):
            line = text[:m.start()].count("\n") + 1
            print(f"{f}:{line}: {why}")
            fails += 1

print(f"\n{'FAILED: ' + str(fails) + ' occurrence(s)' if fails else 'no invented idioms found'}")
sys.exit(1 if fails else 0)
