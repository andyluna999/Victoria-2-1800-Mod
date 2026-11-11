"""Spheres of influence and diplomatic relations on 1 January 1800.

The relation blocks at the top of every order-of-battle file are 1836's and describe a
world that has not happened. Britain spheres Belgium, which will not exist for thirty
years, and the Ionian Islands, which belong to the Porte. Russia spheres Finland, which
is Swedish until 1809, and Transcaucasia, which this project has just broken into five
states. Austria spheres the German Confederation and Prussia the Zollverein, neither of
which has been founded.

Victoria II gives a sphere only to a Great Power, so the 1800 list follows from the
prestige work: Britain, France, Russia, Austria, Spain, the Ottomans and Prussia. Each
one's clients are the ones it actually had.

Relations are set to match the war. The thing most worth getting right is Paul I, who
is in nobody's camp on this date: he pulled Russia out of the coalition in October 1799
in a fury over Switzerland and Malta, and within a year he will be arming against
Britain rather than France. His relations are poor with everyone.
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

# Great Power -> the states in its sphere. Vassals are already bound by
# history/diplomacy and are not repeated here.
SPHERE = {
 # Portugal by the oldest alliance in Europe; Naples because British bayonets put
 # Ferdinand back on his throne six months ago
 "ENG": ["POR", "SIC"],
 # the Habsburg secundogenitures in Italy, whichever army is standing in them
 "AUS": ["TUS", "MOD", "PAR", "LUC"],
 # the north German neutrality zone Prussia has guaranteed since Basel in 1795
 "PRU": ["MEC", "OLD", "ANH", "LIP", "BRU", "HAM", "BRE", "LUB"],
 # Russia has patronised the Montenegrin prince-bishops since Peter the Great
 "RUS": ["MON"],
 # France rules its clients outright rather than sphering them; the Batavian,
 # Helvetic and Ligurian Republics are vassals in history/diplomacy
 "FRA": [],
 "SPA": [], "TUR": [],
}
# relation values. Negative is hostile; 200 is the practical maximum.
REL = {
 ("FRA","ENG"): -200, ("FRA","AUS"): -200, ("FRA","TUR"): -175, ("FRA","SIC"): -175,
 ("FRA","POR"): -125, ("FRA","SPA"):  150, ("FRA","PRU"):   50, ("FRA","USA"):  -75,
 ("ENG","AUS"):  150, ("ENG","POR"):  200, ("ENG","SIC"):  150, ("ENG","TUR"):  125,
 ("ENG","SPA"): -200, ("ENG","PRU"):   25, ("ENG","USA"):  -50, ("ENG","DEN"):  -75,
 ("AUS","TUR"):   75, ("AUS","PRU"):  -50, ("AUS","SIC"):  100,
 # Paul I, out of the coalition and in nobody's camp
 ("RUS","ENG"):  -75, ("RUS","AUS"): -100, ("RUS","FRA"):  -50, ("RUS","TUR"):   50,
 ("RUS","PRU"):   50, ("RUS","SWE"):  -50, ("RUS","DEN"):   50,
 # the armed neutrality forming in the Baltic against British search of neutral ships
 ("DEN","SWE"):   75, ("DEN","PRU"):   50,
 ("SPA","POR"):  -75, ("SPA","USA"):  -25,
}

# --- strip every 1836 relation block ---------------------------------------------
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    s = rd(f)
    out, pos, n = [], 0, 0
    for m in re.finditer(r"^[A-Z]{3}[ \t]*=[ \t]*\{", s, re.M):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        while i < len(s) and s[i] in "\r\n": i += 1
        out.append(s[pos:m.start()]); pos = i; n += 1
    if n:
        out.append(s[pos:])
        wr(f, "".join(out).lstrip("\n")); log["1836 relation blocks removed"] += n
        log["files cleaned"] += 1

# --- write the 1800 picture --------------------------------------------------------
# Spheres first. A country that is both a sphere member and a relation -- Portugal and
# Naples are both -- must take the sphere, and the dedupe below keeps whichever came
# first, so putting relations first silently demoted every British client to friendly.
byholder = collections.defaultdict(list)
for gp, clients in SPHERE.items():
    for c in clients:
        byholder[gp].append((c, 175, 5))
        log["spheres"] += 1
for (a, b), v in REL.items():
    byholder[a].append((b, v, 0))

for tag, entries in byholder.items():
    f = f"{MOD}/history/units/{tag}_oob.txt"
    body = rd(f) if os.path.exists(f) else ""
    seen, block = set(), []
    for other, value, level in entries:
        if other in seen: continue
        seen.add(other)
        lvl = level if level else (1 if value <= -100 else 2 if value < 0 else
                                   4 if value >= 150 else 3)
        block.append(f"{other} = {{\n\tvalue = {value}\n\tlevel = {lvl}\n"
                     f"\tinfluence_value = {25 if level == 5 else 0}\n}}")
        log["relations written"] += 1
    head = ("# Relations and spheres on 1 January 1800.\n"
            "# level 5 is a sphere, 4 friendly, 3 cordial, 2 cool, 1 hostile.\n\n"
            + "\n".join(block) + "\n\n")
    wr(f, head + body.lstrip("\n"))

for k, v in sorted(log.items()): print(f"  {k:<34}{v}")
