"""Put every unit somewhere its country actually holds.

The 1836 order of battle stations armies and recruits regiments in provinces that the
1800 map has given to somebody else. Swiss troops stand in French Geneva, Prussian
troops in French Cologne and Swedish Stralsund, Greek troops in Ottoman Athens, and
Belgium fields an army for a country that does not exist.

Two fields matter and only one of them is obvious. `location` is where a formation
stands; `home` is the province a regiment recruits from, and a regiment whose home is
foreign cannot reinforce. Both are fixed here.

Formations belonging to a country that holds nothing at all are removed outright,
keeping the file so the tag still has somewhere to put an army later.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, sys, collections, math

MOD = _BUILD; W = _WORK
L = json.load(open(f"{W}/world_live.json"))
P = {int(k): v for k, v in L["prov"].items()}
ST = {int(k): v for k, v in json.load(open(f"{W}/prov_stats.json")).items()}
SEA = set(L["sea"])
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# ownership from the mod, never from world_live.json: that file is written after the
# build, so reading it here means acting on the previous run's map
sys.path.insert(0, _TOOLS)
from livestate import province_state, population
OWNER, _CTRL, _CORES, _PATH = province_state()
SPAWNS_LATER = {"MEX", "CLM", "ARG", "CHL", "PEU", "VNZ", "ECU", "BOL", "URU", "PRG",
           "CUB", "PRI", "BRZ", "TEX", "CAL", "HAI", "ALD", "TUN", "TRI"}
owned = collections.defaultdict(list)
for pid, o in OWNER.items():
    if o: owned[o].append(pid)
caps = {}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    m = re.search(r"^\s*capital\s*=\s*(\d+)", rd(f), re.M)
    if m: caps[b.split(" - ")[0].strip()] = int(m.group(1))

def nearest(tag, pid):
    """The closest province this country holds, so a unit moves as little as possible."""
    opts = owned.get(tag) or []
    if not opts: return None
    if pid in opts: return pid
    here = ST.get(pid)
    if not here:
        return caps.get(tag) if caps.get(tag) in opts else opts[0]
    best, bd = None, 1e18
    for q in opts:
        s = ST.get(q)
        if not s: continue
        d = (s["lx"] - here["lx"]) ** 2 + (s["ly"] - here["ly"]) ** 2
        if d < bd: best, bd = q, d
    return best or opts[0]

def coastal(tag, pid):
    """A navy has to sit in a port: an owned province that touches our sea list."""
    opts = [q for q in owned.get(tag, []) if (P.get(q, {}).get("nb") or 0) > 0]
    if not opts: opts = owned.get(tag, [])
    if not opts: return None
    if pid in opts: return pid
    here = ST.get(pid)
    if not here: return opts[0]
    return min(opts, key=lambda q: ((ST[q]["lx"] - here["lx"]) ** 2 +
                                    (ST[q]["ly"] - here["ly"]) ** 2) if q in ST else 1e18)

for f in sorted(glob.glob(f"{MOD}/history/units/*.txt")):
    tag = os.path.basename(f)[:3]
    s = rd(f)
    if not re.search(r"\b(army|navy)\s*=\s*\{", s): continue
    # Countries our own content brings into being later keep their orders of battle.
    # Victoria II reads these at the start of the game and hands them over when the
    # country appears; clearing them as "landless" left every republic born into a war
    # with nothing to fight it with.
    SPAWNS_LATER_LOCAL = {"MEX", "CLM", "ARG", "CHL", "PEU", "VNZ", "ECU", "BOL", "URU",
                    "PRG", "CUB", "PRI", "BRZ", "TEX", "CAL", "HAI", "ALD", "TUN", "TRI"}
    if not owned.get(tag) and tag not in SPAWNS_LATER_LOCAL:
        # the country holds nothing on this map; strip its formations and leave the file
        out, pos = [], 0
        for m in re.finditer(r"[ \t]*(army|navy)[ \t]*=[ \t]*\{", s):
            i = m.end(); d = 1
            while i < len(s) and d:
                if s[i] == "{": d += 1
                elif s[i] == "}": d -= 1
                i += 1
            while i < len(s) and s[i] in "\r\n": i += 1
            out.append(s[pos:m.start()]); pos = i
            log["formations removed from landless countries"] += 1
        out.append(s[pos:])
        wr(f, "".join(out)); log["landless country files cleared"] += 1
        continue

    if tag in SPAWNS_LATER:
        continue          # armed for a country that does not hold land yet
    changed = False
    pieces, pos = [], 0
    for m in re.finditer(r"[ \t]*(army|navy)[ \t]*=[ \t]*\{", s):
        kind = m.group(1); i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[m.start():i]
        def fix_loc(mm):
            global changed
            pid = int(mm.group(1))
            if OWNER.get(pid) == tag: return mm.group(0)
            new = coastal(tag, pid) if kind == "navy" else nearest(tag, pid)
            if new is None or new == pid: return mm.group(0)
            changed = True; log[f"{kind} locations moved"] += 1
            return mm.group(0).replace(str(pid), str(new))
        body = re.sub(r"location\s*=\s*(\d+)", fix_loc, body)
        def fix_home(mm):
            global changed
            pid = int(mm.group(1))
            # Owned, not merely held: a regiment recruits from its own country's
            # population. Spain administers Santo Domingo but France owns it, so a
            # Spanish regiment cannot take its drafts from there.
            if OWNER.get(pid) == tag: return mm.group(0)
            new = nearest(tag, pid)
            if new is None or new == pid: return mm.group(0)
            changed = True; log["regiment homes remapped"] += 1
            return mm.group(0).replace(str(pid), str(new))
        body = re.sub(r"home\s*=\s*(\d+)", fix_home, body)
        pieces.append(s[pos:m.start()]); pieces.append(body); pos = i
    pieces.append(s[pos:])
    if changed:
        wr(f, "".join(pieces)); log["country files corrected"] += 1

for k, v in sorted(log.items()): print(f"  {k:<44}{v}")
