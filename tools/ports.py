"""Every port the period had, and every port HPM shipped.

Two faults. Our province passes rewrite a file's head to change owners, cores and
trade goods, and somewhere in that rewriting they were dropping the `naval_base` line:
thirty-nine harbours that HPM ships were simply gone from our build, including
Charleston, Bordeaux, Rotterdam, La Coruna, San Francisco and Mobile. A country whose
ports have quietly vanished cannot build a fleet, repair one, or land an army.

And the Spanish Americas were short of the harbours that actually mattered. Veracruz
is the single most important port in the empire -- every ounce of silver leaving New
Spain and every regiment arriving went through it, and the fleet system was built
around it -- and it had no naval base in either HPM or ours. The same for Tampico,
Maracaibo, Guayaquil, Valdivia and Santo Domingo.

So: whatever HPM had is restored, and the ports the period ran on are added at the
level the period warranted. Veracruz and Havana take level 2 because they were
fortified naval stations with squadrons based on them; the rest take level 1, which
is a harbour that works rather than a fortress.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections

SRC = _SRC
MOD = _BUILD
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# what HPM itself shipped
pristine = {}
for f in glob.glob(f"{SRC}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    m = re.search(r"^\s*naval_base\s*=\s*([1-9])", rd(f), re.M)
    if m: pristine[pid] = int(m.group(1))

# and the ports the period ran on, by name, at the level it warranted
PERIOD = {
 2162: 2,   # Veracruz -- the silver and every regiment that ever arrived
 2209: 2,   # Havana -- the fortified station of the Caribbean squadron
 2163: 1,   # Tampico
 2184: 1,   # Campeche
 2149: 1,   # Acapulco, the Manila galleon
 2270: 1,   # Maracaibo
 2280: 1,   # Guayaquil, where the Pacific squadron was built
 2214: 1,   # Santo Domingo
 2328: 1,   # Valdivia, the southern bastion
 2432: 1,   # Recife
 2387: 1,   # San Juan
}

want = dict(pristine)
for pid, lvl in PERIOD.items():
    want[pid] = max(want.get(pid, 0), lvl)

for f in sorted(glob.glob(f"{MOD}/history/provinces/*/*.txt")):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid not in want: continue
    s = rd(f)
    have = re.search(r"^\s*naval_base\s*=\s*([0-9])", s, re.M)
    if have and int(have.group(1)) >= want[pid]: continue
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    if have:
        head = re.sub(r"^\s*naval_base\s*=\s*[0-9]\s*$",
                      f"naval_base = {want[pid]}", head, count=1, flags=re.M)
        log["harbours deepened"] += 1
    else:
        head = head.rstrip("\n") + f"\nnaval_base = {want[pid]}\n"
        log["harbours restored or added"] += 1
    wr(f, head.rstrip("\n") + "\n" + tail)

now = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    m = re.search(r"^\s*naval_base\s*=\s*([1-9])", rd(f), re.M)
    if m: now[pid] = int(m.group(1))
log["naval bases in the build"] = len(now)
log["still missing from HPM's own list"] = len(set(pristine) - set(now))
for k, v in sorted(log.items()): print(f"  {k:<36}{v}")
