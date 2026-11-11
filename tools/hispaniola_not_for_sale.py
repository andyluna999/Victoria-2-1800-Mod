"""Hispaniola cannot be sold, because by 1803 France did not have it to sell.

The United States kept annexing Haiti at the Louisiana Purchase, and the fix we made
to our own purchase event did nothing -- because the event doing it is not ours. It is
the base game's. "Hispaniola Granted Statehood" appears nowhere in HPM; it is vanilla
Victoria II, and so is the purchase that preceded it. Those files are not in this mod
and cannot be edited from here.

So the defence has to be in the data rather than the event. Two things, both of which
are also true:

France's core on Saint-Domingue is removed at the start. The colony had been in open
revolt since 1791, the National Convention had abolished slavery there in 1794 and the
colony had governed itself ever since, and by 1800 the French claim was a legal
fiction maintained by a Republic that had no soldiers on the island. A purchase filter
that looks for French cores will not find one.

And when Toussaint takes Santo Domingo in 1801 -- which he did, in January, unifying
the island in defiance of Bonaparte's explicit orders -- the provinces pass out of
French ownership. After that there is nothing on Hispaniola for anyone to buy, which
is precisely the position the United States was in historically: Jefferson's
negotiators asked about the island and were told it was not on the table, because
Leclerc's expedition was already sailing to take it back by force.
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
HISP = [2213, 2214, 2215, 2216]
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid not in HISP: continue
    s = rd(f)
    if re.search(r"^\s*add_core\s*=\s*FRA\s*$", s, re.M):
        wr(f, re.sub(r"^\s*add_core\s*=\s*FRA\s*\n", "", s, flags=re.M))
        log["French cores removed from Hispaniola"] += 1

# and Toussaint's unification takes the island out of French hands
f = f"{MOD}/events/1800_Hispaniola.txt"
if os.path.exists(f):
    s = rd(f)
    m = re.search(r"id = 9101301\b", s)
    if m:
        i = s.find('name = "EVTOPTA9101301"', m.end())
        if i > 0:
            j = s.find("\n", i)
            add = ("".join(f"\n        {p} = {{ remove_core = FRA }}" for p in HISP))
            if "remove_core = FRA" not in s[i:i+600]:
                s = s[:j] + add + s[j:]
                wr(f, s)
                log["Toussaint's unification voids the French claim"] = 1

left = []
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid in HISP and re.search(r"^\s*add_core\s*=\s*FRA\s*$", rd(f), re.M):
        left.append(pid)
log["Hispaniola provinces still French-cored"] = len(left)
for k, v in sorted(log.items()): print(f"  {k:<46}{v}")
