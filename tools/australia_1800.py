"""Australia and New Zealand in 1800.

The inherited figures are 1836's and wrong in three directions at once:

  * **120,544 Europeans.** The New South Wales muster of 1800 counted 5,217 people in
    the whole colony. We were out by a factor of twenty-three.
  * **254,828 Aboriginal people**, against estimates for 1788 that run from 750,000 up.
    Out by a factor of three the other way.
  * **Distributed by where 1836 colonists lived.** Perth with 20,000 people in 1800,
    thirty years before it was founded; Tasmania with 32,000, three years before
    Risdon Cove. Aboriginal population followed water and coast, not British charters.

In 1800 the British presence is Sydney, Parramatta, Norfolk Island and the Hawkesbury,
and nothing else. There is no settlement in Tasmania, Victoria, Queensland, South
Australia, Western Australia or the Northern Territory, and none in New Zealand --
only sealers and a handful of missionaries who are not a colony.

Carrying capacity, not charters: the Murray-Darling, the eastern seaboard, Arnhem Land,
Cape York and the southwest corner carried dense populations; the Western Desert,
Nullarbor, Simpson and Tanami carried almost nobody.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, collections

MOD = _BUILD; W = _WORK
L = json.load(open(f"{W}/world_live.json"))
SCALE = 0.25
NAME = {int(k): v["n"] for k, v in L["prov"].items()}
log = collections.Counter()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# real people in 1800
TOTAL = {"aborigine": 750_000, "maori": 110_000,
         "british": 3_300, "irish": 1_900, "melanesian": 6_000}

# relative carrying capacity. The wet tropics, the big river systems and the temperate
# southeast and southwest fed the most people; the deserts fed the fewest.
CAP = {
 # the southeast: the Murray-Darling and the coast
 2468: 34, 2469: 30, 2470: 26, 2471: 14, 2472: 20, 2473: 18, 2474: 14, 2475: 7,
 2476: 28, 2477: 20, 2478: 16, 2479: 20, 2480: 14, 2481: 12, 2482: 26,
 # Queensland: the wet tropics and Cape York were among the densest country anywhere
 2483: 30, 2484: 22, 2485: 12, 2486: 18, 2487: 26, 2488: 30, 2489: 7, 2490: 7, 2604: 16,
 # South Australia: the Adelaide plains and the lower Murray, then desert
 2491: 20, 2492: 12, 2493: 14, 2494: 9, 2495: 3, 2496: 2,
 # the southwest corner is rich; everything north and east of it is not
 2497: 24, 2498: 16, 2499: 12, 2500: 3, 2501: 16, 2502: 7, 2503: 2, 2504: 8,
 2601: 1, 2602: 7, 2605: 1,
 # the Top End: Arnhem Land and the Daly carried real numbers
 2505: 24, 2506: 5, 2507: 5, 2603: 1,
 # New Zealand: the North Island warm enough for kumara, the South Island much less so
 2509: 30, 2510: 22, 2511: 18, 2512: 16, 2571: 24,
 2513: 6, 2514: 4, 2515: 8, 2516: 7,
 2508: 2, 2524: 1,
}
AU = {p for p in CAP if p < 2509 or p in (2601, 2602, 2603, 2604, 2605)}
NZ = {2509, 2510, 2511, 2512, 2571, 2513, 2514, 2515, 2516}

# the colony in 1800: Sydney, the Hawkesbury, Parramatta, Norfolk Island. That is all.
SETTLER = {2468: 0.72, 2469: 0.17, 2508: 0.08, 2470: 0.03}

ARCH = {
 "aborigine":  {"farmers": .88, "soldiers": .065, "clergymen": .03, "aristocrats": .025},
 "maori":      {"farmers": .84, "soldiers": .09,  "aristocrats": .04, "clergymen": .03},
 "melanesian": {"farmers": .88, "soldiers": .07,  "aristocrats": .03, "clergymen": .02},
 # a penal colony: soldiers, convict labour, a few officials and a chaplain
 "british":    {"labourers": .46, "soldiers": .18, "farmers": .14, "artisans": .10,
                "bureaucrats": .05, "officers": .03, "clergymen": .02, "aristocrats": .02},
 "irish":      {"labourers": .72, "farmers": .16, "artisans": .08, "soldiers": .04},
}
REL = {"aborigine": "animist", "maori": "animist", "melanesian": "animist",
       "british": "protestant", "irish": "catholic"}

alloc = collections.defaultdict(dict)
aucap = sum(CAP[p] for p in AU)
nzcap = sum(CAP[p] for p in NZ)
for p in AU: alloc[p]["aborigine"] = TOTAL["aborigine"] * SCALE * CAP[p] / aucap
for p in NZ: alloc[p]["maori"] = TOTAL["maori"] * SCALE * CAP[p] / nzcap
for p, share in SETTLER.items():
    for c in ("british", "irish"):
        alloc[p][c] = TOTAL[c] * SCALE * share
alloc[2508]["melanesian"] = TOTAL["melanesian"] * SCALE * 0.15
alloc[2524]["melanesian"] = TOTAL["melanesian"] * SCALE * 0.85

rows = []
summary = collections.Counter()
for p, mix in alloc.items():
    for c, v in mix.items():
        n = int(round(v))
        if n < 10: continue
        arch = ARCH[c]; placed = 0; items = sorted(arch.items(), key=lambda x: (-x[1], x[0]))
        for i, (ty, fr) in enumerate(items):
            sz = int(round(n * fr)) if i < len(items) - 1 else n - placed
            placed += sz
            if sz < 5: continue
            rows.append((p, ty, c, REL[c], sz)); summary[c] += sz

files = {}
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    files[f] = open(f, encoding="cp1252", errors="replace").read()

# Norfolk Island and Wake are also defined in the Pacific file. A province may only
# appear once, so strip them there before writing them here.
for f, s_ in list(files.items()):
    if not re.search(r"^(2508|2524)\s*=\s*\{", s_, re.M): continue
    out, pos = [], 0
    for pm in re.finditer(r"^(2508|2524)\s*=\s*\{", s_, re.M):
        i = pm.end(); d = 1
        while i < len(s_) and d:
            if s_[i] == "{": d += 1
            elif s_[i] == "}": d -= 1
            i += 1
        out.append(s_[pos:pm.start()]); pos = i
    out.append(s_[pos:])
    files[f] = "".join(out)
    wr(f, files[f]); log["duplicates removed from the Pacific file"] += 1

# rewrite only the Australian pop file
target = None
for f, s in files.items():
    if os.path.basename(f) != "australia.txt": continue
    target = f; break
if target is None:
    for f, s in files.items():
        if {int(m.group(1)) for m in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M)} & set(CAP):
            target = f; break
keep = []
s = files[target]
for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
    pid = int(pm.group(1)); i = pm.end(); d = 1
    while i < len(s) and d:
        if s[i] == "{": d += 1
        elif s[i] == "}": d -= 1
        i += 1
    if pid not in CAP: keep.append(s[pm.start():i])
by = collections.defaultdict(list)
for p, ty, c, rl, sz in rows: by[p].append((ty, c, rl, sz))
txt = ""
for p in sorted(by):
    txt += f"{p} = {{\n"
    for ty, c, rl, sz in by[p]:
        txt += f"\t{ty} = {{\n\t\tculture = {c}\n\t\treligion = {rl}\n\t\tsize = {sz}\n\t}}\n"
    txt += "}\n"
wr(target, ("\n".join(keep) + "\n\n" if keep else "") + txt)

tot = sum(summary.values())
print(f"  provinces written                 {len(by)}")
print(f"  Australia and New Zealand         {tot:,} pops = {int(tot/SCALE):,} real")
for c, v in summary.most_common():
    print(f"    {c:<12}{v:>8,} = {int(v/SCALE):>9,} real   (target {TOTAL[c]:,})")
print(f"  Europeans in the colony           {int((summary['british']+summary['irish'])/SCALE):,}"
      f"   (the 1800 muster counted 5,217)")
