"""Settlers have to be on the ground at the start, because they cannot be put there later.

Victoria II has no effect that creates a pop. `add_pop`, `create_pop` and
`change_pop_culture` appear zero times in HPM's three thousand events; only
`reduce_pop` exists, and it only shrinks. So an event that opens a frontier band can
raise its attractiveness and nothing else -- and raising the attractiveness of an
empty province attracts nobody.

The band provinces as shipped have almost no Americans in them. The Lower Mississippi
carries 285 dixie against six thousand french_creole; Arkansas and the Osage country
have none at all. The American tide had no Americans in it.

So they are seeded at 1800, at sizes that are true for 1800: a few thousand around
Natchez and the Missouri bootheel, where they really were, and nothing at all west of
the Mississippi, where they really were not. Everything after that is growth and
migration working on a seed that exists, which is what the band modifiers are for.

Dixie outnumbers yankee two to one. The road into Texas runs up from Louisiana and
Tennessee rather than across from New England, and Texas is a dixie-primary republic:
a tide of Yankees would raise no Texan nationalists at all.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# province -> total American settlers in 1800, at our 0.25 scale
SEED = {
 139: 900, 140: 700, 141: 300, 142: 400,      # the lower Mississippi
 146: 1100, 144: 500,                          # St Louis and the Arkansas bottom
 143: 200, 167: 900,                           # Little Rock, Springfield
}
DIXIE, YANKEE = 0.67, 0.33

for f in sorted(glob.glob(f"{MOD}/history/pops/*/*.txt")):
    s = rd(f)
    out, pos, n = [], 0, 0
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1))
        if pid not in SEED: continue
        i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[pm.end():i-1]
        if "culture = dixie" in body and "culture = yankee" in body:
            continue
        tot = SEED[pid]
        add = ""
        for cul, share in (("dixie", DIXIE), ("yankee", YANKEE)):
            if f"culture = {cul}" in body: continue
            sz = int(round(tot * share))
            if sz < 10: continue
            add += (f"\tfarmers = {{\n\t\tculture = {cul}\n\t\treligion = protestant\n"
                    f"\t\tsize = {sz}\n\t}}\n")
            log["settler pops seeded"] += 1
            log["settlers"] += sz
        if not add: continue
        # taken out of the province's existing farmers, so the total does not move
        take = sum(int(x) for x in re.findall(
            r"farmers = \{\n\t\tculture = \w+\n\t\treligion = \w+\n\t\tsize = (\d+)", body))
        nb = body
        if take:
            want = min(tot, int(take * 0.5))
            drop = re.search(r"(farmers = \{\n\t\tculture = \w+\n\t\treligion = \w+\n"
                             r"\t\tsize = )(\d+)", nb)
            if drop and want:
                nb = nb[:drop.start(2)] + str(max(10, int(drop.group(2)) - want)) + nb[drop.end(2):]
        out.append(s[pos:pm.end()]); out.append(nb.rstrip("\n") + "\n" + add)
        pos = i - 1; n += 1
    if n:
        out.append(s[pos:]); wr(f, "".join(out)); log["pop files rewritten"] += 1

# verify
got = collections.Counter()
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    t = re.sub(r"#.*", "", rd(f))
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", t, re.M):
        pid = int(pm.group(1))
        if pid not in SEED: continue
        i = pm.end(); d = 1
        while i < len(t) and d:
            if t[i] == "{": d += 1
            elif t[i] == "}": d -= 1
            i += 1
        for m in re.finditer(r"culture = (dixie|yankee)\n\t\treligion = \w+\n\t\tsize = (\d+)",
                             t[pm.end():i-1]):
            got[m.group(1)] += int(m.group(2))
log["dixie on the frontier"] = got["dixie"]
log["yankee on the frontier"] = got["yankee"]
for k, v in sorted(log.items()): print(f"  {k:<28}{v}")
