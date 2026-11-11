"""Fleets for 1800.

Two problems with the inherited fleets.

**Twenty-nine steam transports.** The first steam warship of any kind is Fulton's
Demologos in 1814, and a steam transport fleet is a thing of the 1840s. These are
sailing navies: they become frigates.

**The fleets are 1836 peacetime establishments.** In 1836 the Royal Navy had most of
its ships laid up in ordinary; in 1800 it had something over a hundred ships of the
line in commission and roughly as many frigates, because it was blockading four
coastlines at once. France, Spain and the Netherlands likewise had far more hulls in
1800 than in 1836 -- Trafalgar and the long blockade were still ahead of them, and the
Dutch fleet had not yet been taken at the Texel.

Clipper transports are left alone. The name is anachronistic -- a clipper is a thing of
the 1840s -- but the unit is Victoria II's generic sailing transport and there is
nothing better to map it to, and the eight countries that hold `clipper_design` after
the technology rollback are exactly the eight that could keep a transport fleet at sea.
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

# the navies at war, and the ratio of 1800 hulls to 1836 ones
WAR_FLEET = {"ENG": 1.8, "FRA": 1.5, "SPA": 2.0, "NET": 1.6, "DEN": 1.4,
             "RUS": 1.3, "TUR": 1.2, "SWE": 1.3, "POR": 1.2, "SIC": 1.2}

for f in sorted(glob.glob(f"{MOD}/history/units/*.txt")):
    tag = os.path.basename(f)[:3]
    s = rd(f)
    if "navy" not in s: continue
    before = s

    # no steam at sea in 1800
    n = len(re.findall(r"type\s*=\s*steam_transport", s))
    if n:
        s = re.sub(r"type\s*=\s*steam_transport", "type = frigate", s)
        log["steam transports made sail"] += n

    mult = WAR_FLEET.get(tag)
    if mult:
        out, pos, added = [], 0, 0
        for m in re.finditer(r"[ \t]*navy[ \t]*=[ \t]*\{", s):
            i = m.end(); d = 1
            while i < len(s) and d:
                if s[i] == "{": d += 1
                elif s[i] == "}": d -= 1
                i += 1
            body = s[m.start():i]
            ships = []
            for sm in re.finditer(r"[ \t]*ship[ \t]*=[ \t]*\{", body):
                j = sm.end(); dd = 1
                while j < len(body) and dd:
                    if body[j] == "{": dd += 1
                    elif body[j] == "}": dd -= 1
                    j += 1
                ships.append(body[sm.start():j])
            if not ships:
                out.append(s[pos:i]); pos = i; continue
            extra = int(round(len(ships) * (mult - 1)))
            new = []
            for k in range(extra):
                sp = ships[k % len(ships)]
                sp = re.sub(r'name\s*=\s*"[^"]*"', f'name = "No. {k+1}"', sp, count=1)
                new.append(sp)
            added += extra
            grown = body.rstrip()
            grown = grown[:grown.rindex("}")] + "\n".join(new) + "\n}"
            out.append(s[pos:m.start()]); out.append(grown); pos = i
        out.append(s[pos:])
        if added:
            s = "".join(out); log["ships added for the war"] += added

    if s != before:
        wr(f, s); log["fleets adjusted"] += 1

counts = collections.Counter()
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    counts[os.path.basename(f)[:3]] = len(re.findall(r"ship\s*=\s*\{",
        re.sub(r"#.*", "", rd(f))))
for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
print(f"  ships afloat worldwide            {sum(counts.values())}")
print("    " + ", ".join(f"{t} {n}" for t, n in counts.most_common(8)))
