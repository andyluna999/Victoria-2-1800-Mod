"""A fleet has to be in a port.

Six navies sat in provinces Victoria II has no harbour in -- including New Granada's,
one of the colonial tags whose order of battle only became live when we started
declaring them. The game builds every country's units when a game begins, not just the
player's, so one bad fleet anywhere crashes the start for everybody.

Ports are not ours to invent either: a `naval_base = 1` written into a province file
means nothing unless the map has that province on a coast. So the authority here is
HPM's own list of harbours, and a fleet that is not in one is moved to the nearest
harbour its owner actually holds. A country with no port at all loses its fleet, which
is the correct answer for a landlocked one.
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
SRC = _SRC
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# Harbours HPM itself recognises, plus the ones the period ran on that HPM omits.
# Veracruz is the clearest: every ounce of silver leaving New Spain and every
# regiment arriving went through it, and neither HPM nor our build gave it a port.
# Treating pristine HPM as the sole authority meant this pass kept deleting them
# again a few lines after ports.py added them.
PORTS = set()
for f in glob.glob(f"{SRC}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if re.search(r"^\s*naval_base\s*=\s*[1-9]", rd(f), re.M):
        PORTS.add(pid)
PERIOD_PORTS = {2162, 2209, 2163, 2184, 2149, 2270, 2280, 2214, 2328, 2432, 2387}
PORTS |= PERIOD_PORTS

owner = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", h, re.M)
    owner[pid] = m.group(1) if m else ""

# naval bases we invented that the map will not support
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid in PORTS: continue
    s = rd(f)
    if re.search(r"^\s*naval_base\s*=\s*[1-9]", s, re.M):
        wr(f, re.sub(r"^\s*naval_base\s*=\s*[1-9]\s*\n", "", s, flags=re.M))
        log["invented harbours removed"] += 1

for f in sorted(glob.glob(f"{MOD}/history/units/*.txt")):
    tag = os.path.basename(f)[:3]
    s = rd(f)
    mine = sorted(p for p in PORTS if owner.get(p) == tag)
    out, pos, moved, dropped = [], 0, 0, 0
    for m in re.finditer(r"[ \t]*navy[ \t]*=[ \t]*\{", s):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[m.start():i]
        loc = re.search(r"location\s*=\s*(\d+)", body)
        if not loc or int(loc.group(1)) in PORTS:
            continue
        if mine:
            nb = body.replace(f"location = {loc.group(1)}", f"location = {mine[0]}", 1)
            out.append(s[pos:m.start()]); out.append(nb); pos = i; moved += 1
        else:
            out.append(s[pos:m.start()]); pos = i; dropped += 1
    if moved or dropped:
        out.append(s[pos:]); wr(f, "".join(out))
        log["fleets moved to a real port"] += moved
        log["fleets disbanded, no port"] += dropped

left = []
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    for m in re.finditer(r"navy\s*=\s*\{[^}]*?location\s*=\s*(\d+)", rd(f), re.S):
        if int(m.group(1)) not in PORTS:
            left.append(os.path.basename(f)[:3])
log["fleets still out of port"] = len(left)
for k, v in sorted(log.items()): print(f"  {k:<30}{v}")
