"""American claims follow the Purchase; they do not precede it.

Thirty provinces west of the Mississippi carry a United States core on the start date
while belonging to New Spain, the Sioux, the Pawnee, the Osage, the Comanche and the
Arikara. Omaha, Topeka, Minneapolis, Sioux City, Cedar Rapids. In 1800 the United
States has no claim to any of it, legal or otherwise: the territory is Spanish by the
Treaty of San Lorenzo and inhabited by nations the United States has treaties with.

The claim is created in April 1803, and by a specific act -- France selling what it had
acquired from Spain three years earlier and never administered. That is the moment the
American right to the Mississippi valley comes into existence, and the map should say
so rather than assuming it from the start.

So the cores come off, and the Purchase puts them on. A player who keeps Louisiana
Spanish, or a France that refuses Monroe, produces a United States with no claim west
of the river at all -- which is the correct consequence and currently impossible.

The eastern bank is left alone. Those cores predate the Purchase and are not in
question.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, json, collections

MOD = _BUILD; W = _WORK
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# Everything the United States claims but does not own, outside the thirteen states
# and the Northwest Territory it already held.
stripped = []
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    s = rd(f)
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)[0]
    o = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    owner = o.group(1) if o else ""
    if owner == "USA" or not owner: continue
    if not re.search(r"^\s*add_core\s*=\s*USA\s*$", head, re.M): continue
    # only the trans-Mississippi west: everything a native nation or New Spain holds
    if owner not in ("NSP", "SIO", "PAW", "OSA", "COM", "ARI", "CRA", "BLA", "BCY",
                     "APA", "NAV", "AAA", "NEZ", "SAL", "CRK", "CCY", "CHA", "CAW",
                     "SEM", "ANI", "IRO", "COK", "COA", "TLI", "YUP", "MAP"):
        continue
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head2 = re.sub(r"^\s*add_core\s*=\s*USA\s*\n", "", parts[0], flags=re.M)
    tail = ("\n" + "\n".join(parts[1:])) if len(parts) > 1 else ""
    wr(f, head2.rstrip("\n") + "\n" + tail)
    stripped.append(pid)
    log["USA cores removed"] += 1
stripped.sort()

# The Purchase grants them. Written into the existing event rather than a new one.
f = f"{MOD}/events/1800_Louisiana.txt"
s = rd(f)
grant = "".join(f"        {p} = {{ add_core = USA }}\n" for p in stripped)
if grant and "add_core = USA" not in s:
    s = s.replace("""        any_owned = {
            limit = { is_core = FRA continent = north_america }
            secede_province = USA
        }""",
"""        any_owned = {
            limit = { is_core = FRA continent = north_america }
            secede_province = USA
        }
        # France renouncing its claim is what creates the American one. Until this
        # moment the United States has no title west of the Mississippi, and if this
        # sale never happens it never acquires one.
""" + grant.rstrip("\n"))
    wr(f, s); log["provinces the Purchase now claims"] = len(stripped)

print(f"  USA cores removed                {log['USA cores removed']}")
print(f"  granted by the Purchase instead  {log.get('provinces the Purchase now claims', 0)}")
print(f"  provinces: {stripped[:12]}{' ...' if len(stripped) > 12 else ''}")
