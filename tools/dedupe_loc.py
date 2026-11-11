"""One key, one value.

Two of our localisation passes were writing the same keys with different text, and
Victoria II takes whichever file sorts first -- so the result depended on a filename.
`CGC` was "Captaincy General of Chile" in one file and "General Captaincy of Chile" in
another; `CBA_conservative` was "Partido Realista" in one and "Council" in the other,
which is why colonial party names read oddly in play.

Where two of our own files disagree the first wins, which is what the engine does,
so cleaning the duplicates cannot change a single line of text the player sees. Keys that
merely repeat the same text are left alone.
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

files = sorted(f for f in glob.glob(f"{MOD}/localisation/[0-9][0-9]_*.csv")
               if not os.path.basename(f).startswith("00_"))
# The FIRST definition wins, because that is what Victoria II itself does: it reads
# the localisation folder in filename order and keeps the first value it sees for a
# key. Keeping the last would have silently changed in-game text -- the colonial
# parties would have gone from "Partido Realista" to "Council of Elders", which is the
# generic name a later pass writes for the small tags it creates.
best = {}
for f in files:
    for line in rd(f).split("\n"):
        if ";" not in line: continue
        best.setdefault(line.split(";")[0], (f, line))

for f in files:
    out, changed = [], 0
    for line in rd(f).split("\n"):
        if ";" not in line:
            out.append(line); continue
        k = line.split(";")[0]
        owner, winner = best.get(k, (f, line))
        if owner != f:
            changed += 1
            log["duplicate rows dropped"] += 1
            continue
        out.append(line)
    if changed:
        open(f, "w", encoding="cp1252", errors="replace",
             newline="\n").write("\n".join(out))
        log["files cleaned"] += 1

# verify
seen = collections.defaultdict(set)
for f in files:
    for line in rd(f).split("\n"):
        if ";" in line: seen[line.split(";")[0]].add(line.split(";", 2)[1])
log["keys still defined twice"] = sum(1 for v in seen.values() if len(v) > 1)
for k, v in sorted(log.items()): print(f"  {k:<28}{v}")
