"""The army that beat three empires.

Haiti was fielding one irregular regiment, and the United States annexed it in every
playthrough. Two things were wrong and both were ours.

**Its soldiers were the wrong people.** Haiti's primary culture is afro_caribbean and
every soldier pop in its provinces was french_creole -- the planters, who by 1804 were
dead, gone or in Louisiana. The army of the revolution was the formerly enslaved, and
a country whose own population carries no arms cannot defend itself in this engine at
all.

**And it was sized like a colony.** The force that destroyed Leclerc's expedition was
around twenty thousand men under arms, and it had already beaten the Spanish and a
British expedition that lost more men in Saint-Domingue than Wellington lost in the
whole Peninsular War. One regiment is not a rounding error, it is the difference
between a country that exists and one that does not.

So the soldiers become Haitian, taken out of the planter pops that will not be there
much longer anyway, and the army is the one that actually fought: irregulars in
numbers, bad at everything except the one thing they were extraordinary at, which was
not being beaten on that island.
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

HAITI = [2213, 2215]          # Port-au-Prince and the north
# the soldiers of Saint-Domingue are the people who fought, not the people who owned
for f in sorted(glob.glob(f"{MOD}/history/pops/*/*.txt")):
    s = rd(f)
    out, pos, n = [], 0, 0
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1))
        if pid not in HAITI: continue
        i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[pm.end():i-1]
        if "soldiers = {\n\t\tculture = afro_caribbean" in body: continue
        nb = re.sub(r"(soldiers = \{\n\t\tculture = )french_creole",
                    r"\1afro_caribbean", body)
        if nb == body: continue
        out.append(s[pos:pm.end()]); out.append(nb); pos = i - 1; n += 1
        log["provinces whose soldiers became Haitian"] += 1
    if n:
        out.append(s[pos:]); wr(f, "".join(out))

body = """# L'Armee Indigene. The force that beat the Spanish, the British and Leclerc in
# succession -- around twenty thousand under arms at its height, almost all of it
# infantry raised from people who had been property eight years earlier. Read at the
# start of the game and handed over when Haiti comes into being.

leader = {
\tname = "Toussaint Louverture"
\tdate = 1804.1.1
\ttype = land
\tpersonality = au_fait
\tbackground = natural_born_leader
\tprestige = 0.9
}

leader = {
\tname = "Jean-Jacques Dessalines"
\tdate = 1804.1.1
\ttype = land
\tpersonality = merciless
\tbackground = exranker
\tprestige = 0.7
}

leader = {
\tname = "Henri Christophe"
\tdate = 1804.1.1
\ttype = land
\tpersonality = relentless
\tbackground = exranker
\tprestige = 0.5
}

leader = {
\tname = "Jean-Pierre Boyer"
\tdate = 1820.1.1
\ttype = land
\tpersonality = balanced_p
\tbackground = exranker
\tprestige = 0.4
}

army = {
\tname = "Armee du Nord"
\tlocation = 2213
"""
for i in range(6):
    body += (f'\tregiment = {{\n\t\tname = "{i+1}. Armee Indigene"\n'
             f'\t\ttype = irregular\n\t\thome = 2213\n\t}}\n')
body += "}\n\narmy = {\n\tname = \"Armee de l'Ouest\"\n\tlocation = 2215\n"
for i in range(5):
    body += (f'\tregiment = {{\n\t\tname = "{i+7}. Armee Indigene"\n'
             f'\t\ttype = irregular\n\t\thome = 2215\n\t}}\n')
body += "}\n"
wr(f"{MOD}/history/units/HAI_oob.txt", body)
log["Haitian regiments"] = 11

# and a nation that beat three empires is not a prestige-zero nonentity
g = glob.glob(f"{MOD}/history/countries/HAI - *.txt")
if g:
    s = rd(g[0])
    if re.search(r"^prestige\s*=\s*0\s*$", s, re.M):
        wr(g[0], re.sub(r"^prestige\s*=\s*0\s*$", "prestige = 8", s, count=1, flags=re.M))
        log["prestige given"] = 8
for k, v in sorted(log.items()): print(f"  {k:<40}{v}")
