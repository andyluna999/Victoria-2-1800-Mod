"""No country may field a unit it has not got the technology for.

France began the game with no armies on the map at all, which is why it lost every war
after 1806. Two hundred and twenty-six regiments sat in FRA_oob.txt and none of them
appeared, because almost all of them were types France could not field.

The Garde Royale is the clearest case. HPM gives it the `guard` type, which Victoria II
unlocks with `breech_loaded_rifles` -- a technology of the 1860s. At a 1836 start that
is a minor anachronism nobody notices. At 1800, after the technology rollback stripped
1,227 anachronistic grants, it means the unit does not exist. Same for the hussars,
dragoons and cuirassiers, which each need their own activation invention, and for the
commerce raiders at sea.

243 units across 39 countries. Every one of them silently missing.

The fix is to write the order of battle in the units the period actually had. Infantry,
cavalry, irregulars, artillery, frigates and men-of-war need no technology and are what
these armies were made of. A cuirassier regiment becomes cavalry; it is still heavy
horse, it is simply described in a vocabulary the engine will accept in 1800. Where a
country lacks even flintlocks -- several of the non-European states do -- its infantry
becomes irregulars, which is accurate rather than a demotion.
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

# which technology or invention unlocks each unit type
act = {}
for f in glob.glob(f"{MOD}/technologies/*.txt") + glob.glob(f"{MOD}/inventions/*.txt"):
    s = re.sub(r"#.*", "", rd(f))
    for m in re.finditer(r"^([a-z_0-9]+)\s*=\s*\{", s, re.M):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        for u in re.findall(r"activate_unit\s*=\s*(\w+)", s[m.end():i]):
            act[u] = m.group(1)

start = {}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    head = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    start[b.split(" - ")[0].strip()] = set(
        re.findall(r"^\s*([a-z_]+)\s*=\s*1\s*$", head, re.M))

# what each type falls back to, in order of preference
FALLBACK = {
    "guard":        ["infantry", "irregular"],
    "engineer":     ["infantry", "irregular"],
    "infantry":     ["irregular"],
    "cuirassier":   ["cavalry", "irregular"],
    "dragoon":      ["cavalry", "irregular"],
    "hussar":       ["cavalry", "irregular"],
    "artillery":    ["infantry", "irregular"],
    "tank":         ["cavalry"],
    "plane":        ["infantry"],
    "commerce_raider": ["frigate"],
    "ironclad":     ["manowar"],
    "monitor":      ["frigate"],
    "cruiser":      ["frigate"],
    "battleship":   ["manowar"],
    "steam_transport": ["clipper_transport", "frigate"],
    "dreadnought":  ["manowar"],
}

def usable(tag, u):
    need = act.get(u)
    return need is None or need in start.get(tag, set())

changed_types = collections.Counter()
for f in sorted(glob.glob(f"{MOD}/history/units/*.txt")):
    tag = os.path.basename(f)[:3]
    s = rd(f)
    if "type" not in s: continue
    out = []
    def swap(m):
        u = m.group(1)
        if u in ("land", "sea") or usable(tag, u): return m.group(0)
        for alt in FALLBACK.get(u, []):
            if usable(tag, alt):
                changed_types[f"{u} -> {alt}"] += 1
                return m.group(0).replace(u, alt)
        # nothing it can field: irregulars need no technology anywhere
        changed_types[f"{u} -> irregular"] += 1
        return m.group(0).replace(u, "irregular")
    ns = re.sub(r"type\s*=\s*(\w+)", swap, s)
    if ns != s:
        wr(f, ns); log["order-of-battle files corrected"] += 1

log["units retyped"] = sum(changed_types.values())
for k, v in sorted(log.items()): print(f"  {k:<36}{v}")
for k, v in changed_types.most_common():
    print(f"    {k:<28}{v}")
