"""A regiment needs soldiers to put in it.

The colonies had orders of battle and no divisions on the map, through four patches of
looking in the wrong place. The files were valid, the unit types fieldable, the home
provinces owned, the braces balanced. What was missing was people.

Victoria II fills a regiment from the soldier pop of its home province. New Spain's
soldier pops were seven, fifteen, twenty-nine and sixty-five, against Spain's seven
hundred to fourteen hundred and France's twelve to fifteen hundred. Thirty-six
regiments drawing on a hundredth of the manpower they needed produced nothing at all,
silently, which is how every other bug in this project has behaved.

The cause is in our own demographic work. The occupational pass gave the colonies the
soldier share of a quiet agrarian province, which is defensible as social history and
useless as an order of battle: the viceregal armies were real, some thirty thousand men
under arms in New Spain, mostly militia but mustered and counted.

So every province that a regiment calls home gets a soldier pop large enough to supply
the regiments drawing on it. The people are moved out of farmers and labourers in the
same province rather than invented, so the province total, the national total and the
world total are all unchanged -- the demographic audit still has to pass, and it does.
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
PER_REGIMENT = 900      # soldier pop units needed to field one regiment at our scale
# The plains and woodland nations are small, and a bar set for European states left
# almost all of them with a single token regiment. Their warriors are irregulars drawn
# from a whole people rather than a professional soldier class, so they field one for
# every three hundred -- which still leaves the Comanche with four and the Sioux with
# three, and nobody able to fight the United States for long.
SMALL_NATIONS = {"SIO", "COM", "PAW", "OSA", "APA", "NAV", "CRA", "BLA", "ARI", "CHE",
                 "CRK", "CHA", "SEM", "CCY", "CAW", "NEZ", "AAA", "ANI", "IRO", "COA",
                 "COK", "SAL", "BCY", "MAP", "TLI", "YUP", "CHY", "ARA", "KAN", "OTO"}
PER_WARRIOR = 300
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# how many regiments call each province home
need = collections.Counter()
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    for m in re.finditer(r"home\s*=\s*(\d+)", re.sub(r"#.*", "", rd(f))):
        need[int(m.group(1))] += 1


# Victoria II fills a regiment only from a soldier pop of an ACCEPTED culture. New
# Spain's soldier pops were 87% mestizo, Maya, Nahua and Miskito against a country
# that accepted only Spanish and criollo, so its army existed on paper and could not
# be manned at all. Mustering has to put the men into a pop the owner can recruit.
accepted = {}
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(_f))[0]
    _p = re.search(r"^\s*primary_culture\s*=\s*(\w+)", _h, re.M)
    _s = set(re.findall(r"^\s*culture\s*=\s*(\w+)", _h, re.M))
    if _p: _s.add(_p.group(1))
    accepted[_b.split(" - ")[0].strip()] = _s

solcul = collections.defaultdict(dict)
for _f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    _t = re.sub(r"#.*", "", rd(_f))
    for _pm in re.finditer(r"^(\d+)\s*=\s*\{", _t, re.M):
        _pid = int(_pm.group(1)); _i = _pm.end(); _d = 1
        while _i < len(_t) and _d:
            if _t[_i] == "{": _d += 1
            elif _t[_i] == "}": _d -= 1
            _i += 1
        for _m in re.finditer(r"\bsoldiers = \{\n\t\tculture = (\w+)\n\t\t"
                              r"religion = \w+\n\t\tsize = (\d+)", _t[_pm.end():_i-1]):
            solcul[_pid][_m.group(1)] = solcul[_pid].get(_m.group(1), 0) + int(_m.group(2))

owner_of = {}
for _f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    _pid = int(re.match(r"(\d+)", os.path.basename(_f)).group(1))
    _h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(_f))[0]
    _m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", _h, re.M)
    owner_of[_pid] = _m.group(1) if _m else ""

POPRE = re.compile(r"(\t([a-z_]+) = \{\n\t\tculture = ([a-z_0-9]+)\n\t\t"
                   r"religion = ([a-z_0-9]+)\n\t\tsize = (\d+)\n\t\}\n)")
DONOR = ("farmers", "labourers", "artisans", "slaves")

for f in sorted(glob.glob(f"{MOD}/history/pops/*/*.txt")):
    s = rd(f)
    out, pos, touched = [], 0, 0
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        if pid not in need:
            continue
        body = s[pm.end():i-1]
        rows = [(m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5)))
                for m in POPRE.finditer(body)]
        if not rows: continue
        have = sum(sz for _, ty, _, _, sz in rows if ty == "soldiers")
        want = need[pid] * PER_REGIMENT
        if have >= want: continue
        short = want - have
        # take it from the largest civilian pops in the same province, in order
        donors = sorted([r for r in rows if r[1] in DONOR], key=lambda r: -r[4])
        pool = sum(r[4] for r in donors)
        if pool < short * 1.4:          # never strip a province bare
            short = int(pool * 0.6)
        if short < 10: continue
        new_body = body
        taken = 0
        for raw, ty, cu, rl, sz in donors:
            if taken >= short: break
            give = min(sz - 10, int(round(short * sz / pool)) + 1, short - taken)
            if give <= 0: continue
            new_body = new_body.replace(
                raw, raw.replace(f"size = {sz}", f"size = {sz - give}"), 1)
            taken += give
        if taken <= 0: continue
        # put them into the existing soldier pop, or make one of the majority culture
        # muster into a soldier pop the owner can actually recruit from
        _own = owner_of.get(pid, "")
        _acc = accepted.get(_own, set())
        sold = [r for r in rows if r[1] == "soldiers" and (not _acc or r[2] in _acc)]
        if not sold:
            sold = [r for r in rows if r[1] == "soldiers"]
        if sold:
            raw, ty, cu, rl, sz = sold[0]
            new_body = new_body.replace(
                raw, raw.replace(f"size = {sz}", f"size = {sz + taken}"), 1)
        else:
            _cands = [r for r in rows if not _acc or r[2] in _acc] or rows
            big = max(_cands, key=lambda r: r[4])
            new_body = new_body.rstrip("\n") + (
                f"\n\tsoldiers = {{\n\t\tculture = {big[2]}\n\t\t"
                f"religion = {big[3]}\n\t\tsize = {taken}\n\t}}\n")
        out.append(s[pos:pm.end()]); out.append(new_body); pos = i - 1
        touched += 1
        log["provinces reinforced"] += 1
        log["soldiers mustered"] += taken
    if touched:
        out.append(s[pos:]); wr(f, "".join(out)); log["pop files rewritten"] += 1

# --- second pass: a regiment whose parish cannot fill it recruits somewhere else -----
# Some provinces are simply too small to supply three regiments however much is moved
# into them, and stripping a village bare to raise a brigade is worse history than
# recruiting from the next town. So any regiment still short is re-homed onto its own
# country's best-supplied province.
sol = collections.Counter()
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s_ = re.sub(r"#.*", "", rd(f))
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s_, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(s_) and d:
            if s_[i] == "{": d += 1
            elif s_[i] == "}": d -= 1
            i += 1
        for m in re.finditer(r"\bsoldiers = \{\n\t\tculture = \w+\n\t\t"
                             r"religion = \w+\n\t\tsize = (\d+)", s_[pm.end():i-1]):
            sol[pid] += int(m.group(1))

owner = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    owner[pid] = m.group(1) if m else ""

for f in sorted(glob.glob(f"{MOD}/history/units/*.txt")):
    tag = os.path.basename(f)[:3]
    if tag in {"MEX", "CLM", "ARG", "CHL", "PEU", "VNZ", "ECU", "BOL", "URU", "PRG",
           "CUB", "PRI", "BRZ", "TEX", "CAL", "HAI", "ALD", "TUN", "TRI"}: continue
    t = rd(f)
    homes = [int(x) for x in re.findall(r"home = (\d+)", t)]
    if not homes: continue
    # rank a country's provinces by soldiers it can ACTUALLY recruit, not by soldiers
    _acc = accepted.get(tag, set())
    def _usable(p):
        return sum(v for c, v in solcul.get(p, {}).items() if not _acc or c in _acc)
    mine = sorted((p for p, o in owner.items() if o == tag), key=lambda p: -_usable(p))
    if not mine: continue
    _per = PER_WARRIOR if tag in SMALL_NATIONS else PER_REGIMENT
    capacity = {p: _usable(p) // _per for p in mine}
    used = collections.Counter()
    moved = 0
    def place(m):
        global moved
        pid = int(m.group(1))
        used[pid] += 1
        if used[pid] <= capacity.get(pid, 0):
            return m.group(0)
        for q in mine:
            if used[q] < capacity.get(q, 0):
                used[q] += 1; used[pid] -= 1; moved += 1
                return f"home = {q}"
        return m.group(0)
    nt = re.sub(r"home = (\d+)", place, t)
    if moved:
        wr(f, nt); log["regiments re-homed"] += moved

# --- third pass: an army nobody can man is not an army --------------------------------
# The Comanche were given eight regiments by population and have twenty thousand people.
# Putting half a nation in uniform to fill an order of battle is worse than having a
# smaller one, so a country that cannot man its regiments loses the surplus instead of
# conscripting its own children.
# A country that does not exist yet owns nothing, so its capacity reads zero and its
# army would be disbanded entirely. These are armed for the day they appear.
SPAWNS_LATER = {"MEX", "CLM", "ARG", "CHL", "PEU", "VNZ", "ECU", "BOL", "URU", "PRG",
           "CUB", "PRI", "BRZ", "TEX", "CAL", "HAI", "ALD", "TUN", "TRI"}
for f in sorted(glob.glob(f"{MOD}/history/units/*.txt")):
    tag = os.path.basename(f)[:3]
    if tag in SPAWNS_LATER: continue
    t = rd(f)
    homes = [int(x) for x in re.findall(r"home = (\d+)", t)]
    if not homes: continue
    mine = [p for p, o in owner.items() if o == tag]
    _acc2 = accepted.get(tag, set())
    capacity = sum(sum(v for c, v in solcul.get(p, {}).items() if not _acc2 or c in _acc2)
                   for p in mine) // (PER_WARRIOR if tag in SMALL_NATIONS else PER_REGIMENT)
    if capacity >= len(homes): continue
    drop = len(homes) - capacity
    out2, pos2, dropped = [], 0, 0
    for am in re.finditer(r"[ \t]*army[ \t]*=[ \t]*\{", t):
        i = am.end(); d = 1
        while i < len(t) and d:
            if t[i] == "{": d += 1
            elif t[i] == "}": d -= 1
            i += 1
        body = t[am.start():i]
        regs = []
        for rm in re.finditer(r"[ \t]*regiment[ \t]*=[ \t]*\{", body):
            j = rm.end(); dd = 1
            while j < len(body) and dd:
                if body[j] == "{": dd += 1
                elif body[j] == "}": dd -= 1
                j += 1
            regs.append(body[rm.start():j])
        nb = body
        # never leave a country with no army at all
        keep_at_least = 1
        for r in reversed(regs):
            if dropped >= drop or len(regs) - dropped <= keep_at_least: break
            nb = nb.replace(r, "", 1); dropped += 1
        out2.append(t[pos2:am.start()]); out2.append(nb); pos2 = i
    out2.append(t[pos2:])
    if dropped:
        wr(f, "".join(out2)); log["regiments disbanded as unmannable"] += dropped

for k, v in sorted(log.items()): print(f"  {k:<34}{v}")
