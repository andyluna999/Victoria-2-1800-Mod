"""No chain may die because one roll was missed.

The Mutiny at Aranjuez had a window of exactly 1808 and a mean time of two months.
Fontainebleau fired on schedule in March 1807 and set its flag; Aranjuez then had
twelve months to come up and never did. The arithmetic says that should be near
impossible, and it happened anyway -- Victoria II's event pulse evaluates a bounded
number of candidates per country per tick, and with our ninety events sitting on top
of HPM's three thousand a narrow window can simply be skipped.

Everything downstream died with it. Bayonne never fired, so the colonies never learned
the King was a prisoner, so Iturrigaray was never asked who governs. The French
invasion of Spain had a window of 1808 to 1810 and was waiting on a flag that arrived
in 1811, by which time its own window had shut. One missed roll cost the entire
Spanish collapse and everything the colonies do in response to it.

So: any event another event waits on gets a window of at least six years, and a mean
time no slower than two months. The historical date is still when it wants to happen --
the mean time sees to that -- but a chain can now survive the engine losing interest
for a year. The same applies to the events that merely follow a date: they get four
years rather than one.

This is a general repair, applied by rewriting the year bounds in place, so it covers
every chain in the mod rather than the three I happen to have noticed.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections

MOD = _BUILD
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

CHAINED_WINDOW = 6     # years, for an event something else waits on
PLAIN_WINDOW = 4       # years, for an event that only waits on a date
SLOWEST_MEAN = 2       # months

# which flags are tested anywhere, so we know which events are load-bearing
all_text = "\n".join(rd(f) for f in glob.glob(f"{MOD}/events/1800_*.txt")) + \
           "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/1800_*.txt"))
tested = set(re.findall(r"has_(?:global|country)_flag\s*=\s*(\w+)", all_text))

for f in sorted(glob.glob(f"{MOD}/events/1800_*.txt")):
    s = rd(f)
    out, pos, n = [], 0, 0
    for m in re.finditer(r"^country_event\s*=\s*\{", s, re.M):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        b = s[m.end():i-1]
        if "is_triggered_only" in b:
            continue
        yrs = [int(y) for y in re.findall(r"year\s*=\s*(\d{4})", b)]
        if len(yrs) < 2:
            continue
        lo, hi = min(yrs), max(yrs)
        # does anything wait on a flag this event sets?
        sets = set(re.findall(r"set_(?:global|country)_flag\s*=\s*(\w+)", b))
        want = CHAINED_WINDOW if (sets & tested) else PLAIN_WINDOW
        new_hi = max(hi, lo + want)
        nb = b
        if new_hi != hi:
            nb = re.sub(rf"NOT\s*=\s*\{{\s*year\s*=\s*{hi}\s*\}}",
                        f"NOT = {{ year = {new_hi} }}", nb, count=1)
            log["windows widened"] += 1
        mt = re.search(r"mean_time_to_happen\s*=\s*\{([^}]*)\}", nb, re.S)
        if mt:
            mm = re.search(r"months\s*=\s*(\d+)", mt.group(1))
            if mm and int(mm.group(1)) > SLOWEST_MEAN:
                nb = nb[:mt.start(1)] + mt.group(1).replace(
                    f"months = {mm.group(1)}", f"months = {SLOWEST_MEAN}") + nb[mt.end(1):]
                log["mean times shortened"] += 1
        if nb != b:
            out.append(s[pos:m.end()]); out.append(nb); pos = i - 1; n += 1
    if n:
        out.append(s[pos:]); wr(f, "".join(out)); log["files rewritten"] += 1

for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
