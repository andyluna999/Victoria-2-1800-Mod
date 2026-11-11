"""The republic a settler rises for has to be one whose primary culture is his.

`nationalist_rebels` carries `independence = culture`: the rebels release the nation
whose PRIMARY culture matches their own. Texas was modelled as a Mexican successor --
primary culture mestizo -- so Anglo settlers in Houston and San Antonio had no nation
to rise for and the entire filibuster chain ended in nothing at all.

That is the wrong Texas for this system. Austin's colonists came from Missouri,
Louisiana and Tennessee; the republic they made joined the Confederacy twenty-five
years later; HPM's own CSA already accepts `texan`. So Texas is dixie, still accepting
the Tejanos who were there first and the Yankees who came with the Southerners.

California was already yankee and needed only dixie alongside it, since the overland
parties were mixed.

New Mexico produces no republic and should not: the Gila and the Rio Grande were taken
by the United States Army in 1846, not by settlers declaring anything. That band still
fills, still raises pressure and still makes the north expensive to hold -- it simply
ends in a war rather than a flag. Rio Grande stays what it historically was, a Mexican
federalist breakaway, and has no business in a chain about Anglo settlement.
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

WANT = {
 "TEX": ("dixie", ["mestizo", "yankee", "comanche"]),
 "CAL": ("yankee", ["dixie", "mestizo"]),
}
for tag, (prim, acc) in WANT.items():
    g = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s = rd(g[0])
    parts = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^primary_culture\s*=\s*\w+", f"primary_culture = {prim}",
                  head, count=1, flags=re.M)
    have = set(re.findall(r"^\s*culture\s*=\s*(\w+)", head, re.M))
    add = "".join(f"culture = {c}\n" for c in acc if c not in have)
    if add:
        head = re.sub(r"(^primary_culture\s*=.*\n)", r"\1" + add, head,
                      count=1, flags=re.M)
    wr(g[0], head.rstrip("\n") + "\n" + tail)
    log["republics retuned"] += 1

# and the New Mexico band stops producing one
f = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(f):
    s = rd(f)
    m = re.search(r"country_event = \{\n    id = 9102592.*?\n\}\n", s, re.S)
    if m:
        wr(f, s[:m.start()] + s[m.end():])
        log["Rio Grande republic removed"] = 1

# verify: every republic this chain can produce is reachable by its settlers
bad = []
for tag in ("TEX", "CAL"):
    g = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(g[0]))[0]
    p = re.search(r"^primary_culture\s*=\s*(\w+)", h, re.M)
    if not p or p.group(1) not in ("yankee", "dixie"):
        bad.append(f"{tag} primary is {p.group(1) if p else '?'}")
log["republics unreachable by settlers"] = len(bad)
for k, v in sorted(log.items()): print(f"  {k:<36}{v}")
