"""Armies for the countries this project created, and a wartime scale for the rest.

Twenty-three tags held territory and no soldiers. The Viceroyalty of New Spain had
ninety-five provinces and no garrison; the Maratha Confederacy, the strongest land
power in India, had nothing at all. Both are free conquests for anyone who notices.

Sizes are historical rather than proportional. The colonial armies of Spanish America
were small, badly paid and mostly militia -- about thirty thousand men of all kinds in
New Spain, which is why a few thousand insurgents could paralyse it in 1810. The
Maratha establishment was the opposite: Sindhia alone kept tens of thousands of
regular infantry drilled by European officers, and the Company took it seriously enough
to fight two wars over it. The Barbary regencies kept janissary corps and corsair
squadrons rather than field armies.

The existing orders of battle are 1836 peacetime establishments. The powers at war on
the start date are scaled to a war footing, because France in 1800 had something like
four hundred thousand men under arms and the file gave it sixty-four regiments.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, sys, collections

MOD = _BUILD; W = _WORK
L = json.load(open(f"{W}/world_live.json"))
P = {int(k): v for k, v in L["prov"].items()}
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# ownership from the mod, never from world_live.json: that file is written after the
# build, so reading it here means acting on the previous run's map
sys.path.insert(0, _TOOLS)
from livestate import province_state, population
OWNER, _CTRL, _CORES, _PATH = province_state()
owned = collections.defaultdict(list)
for pid, o in OWNER.items():
    if o: owned[o].append(pid)
ports = {t: [p for p in ps if (P.get(p, {}).get("nb") or 0) > 0] for t, ps in owned.items()}
caps = {}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    m = re.search(r"^\s*capital\s*=\s*(\d+)", rd(f), re.M)
    if m: caps[b.split(" - ")[0].strip()] = int(m.group(1))

# tag: (army name, infantry, irregular, cavalry, artillery, frigates, manowar, fleet name)
NEW = {
 "NSP": ("Ejercito de Nueva Espana",   5, 6, 2, 1, 2, 0, "Armada de Barlovento"),
 "VPE": ("Ejercito del Peru",          3, 4, 1, 1, 1, 0, "Escuadra del Mar del Sur"),
 "VNG": ("Ejercito de Nueva Granada",  2, 3, 1, 0, 1, 0, "Escuadra de Cartagena"),
 "RDP": ("Ejercito del Rio de la Plata",2, 3, 2, 0, 1, 0, "Apostadero del Plata"),
 "CGC": ("Ejercito de Chile",          1, 3, 1, 0, 0, 0, ""),
 "CBA": ("Ejercito de Cuba",           3, 2, 1, 1, 2, 1, "Escuadra de La Habana"),
 "PTR": ("Guarnicion de Puerto Rico",  1, 1, 0, 0, 1, 0, ""),
 "EBR": ("Exercito do Brasil",         3, 5, 2, 1, 2, 1, "Esquadra do Brasil"),
 # the Confederacy: Sindhia's regular brigades plus the Peshwa's horse
 "MAR": ("Maratha Confederacy",       12, 8, 10, 4, 0, 0, ""),
 "CRN": ("Nawab's Army",               1, 2, 1, 0, 0, 0, ""),
 "TYS": ("Tay Son Army",               4, 6, 1, 1, 2, 0, "Tay Son Fleet"),
 "IRE": ("Irish Establishment",        5, 2, 2, 1, 0, 0, ""),
 # the Barbary regencies: janissaries ashore, corsairs afloat
 "RGA": ("Odjak of Algiers",           2, 4, 2, 1, 4, 0, "Corsairs of Algiers"),
 "BTN": ("Beylical Guard",             1, 3, 1, 0, 2, 0, "Corsairs of Tunis"),
 "KRM": ("Karamanli Guard",            1, 3, 1, 0, 2, 0, "Corsairs of Tripoli"),
 "RAG": ("Ragusan Guard",              1, 0, 0, 0, 0, 0, "Ragusan Marine"),
 "LIG": ("Guardia Ligure",             2, 1, 0, 1, 1, 0, "Squadra Ligure"),
 "HAU": ("Hausa Levies",               1, 6, 3, 0, 0, 0, ""),
 "GEO": ("Royal Georgian Army",        1, 2, 1, 0, 0, 0, ""),
 "IME": ("Imeretian Levy",             0, 2, 1, 0, 0, 0, ""),
 "YER": ("Yerevan Khanate",            0, 2, 2, 0, 0, 0, ""),
 "GAN": ("Ganja Khanate",              0, 2, 1, 0, 0, 0, ""),
 "BAK": ("Baku Khanate",               0, 2, 1, 0, 0, 0, ""),
}
for tag, (nm, inf, irr, cav, art, frig, mow, fleet) in NEW.items():
    ps = owned.get(tag) or []
    if not ps: continue
    loc = caps.get(tag) if caps.get(tag) in ps else ps[0]
    homes = (ps * 40)[:max(1, inf + irr + cav + art)]
    out = [f"# {nm}", ""]
    regs, k = [], 0
    for ty, n in (("infantry", inf), ("irregular", irr), ("cavalry", cav), ("artillery", art)):
        for i in range(n):
            regs.append(f'\tregiment = {{\n\t\tname = "{i+1}. {ty.title()}"\n'
                        f'\t\ttype = {ty}\n\t\thome = {homes[k % len(homes)]}\n\t}}')
            k += 1
    if regs:
        out.append(f'army = {{\n\tname = "{nm}"\n\tlocation = {loc}\n' + "\n".join(regs) + "\n}")
        log["armies created"] += 1; log["regiments created"] += len(regs)
    if fleet and (frig or mow):
        port = (ports.get(tag) or ps)[0]
        ships = []
        for ty, n in (("frigate", frig), ("manowar", mow)):
            for i in range(n):
                ships.append(f'\tship = {{\n\t\tname = "{i+1}. {ty.title()}"\n\t\ttype = {ty}\n\t}}')
        out.append(f'\nnavy = {{\n\tname = "{fleet}"\n\tlocation = {port}\n' + "\n".join(ships) + "\n}")
        log["fleets created"] += 1; log["ships created"] += len(ships)
    wr(f"{MOD}/history/units/{tag}_oob.txt", "\n".join(out) + "\n")

# --- every other country that holds land and has no soldiers ----------------------
# The sweep found forty-five, among them the Qing: HPM keeps China's order of battle
# on the formable CHI tag, which holds nothing, so the empire with a third of the
# world's population had no army at all. Sizes scale with population, with horse
# nations and tribal confederacies weighted up because a far larger share of them
# fought -- the Comanche fielded warriors in a proportion no European state matched.
# population from the mod's own pop files, for the same reason
PROVPOP = population()
pop = collections.Counter()
for pid, o in OWNER.items():
    if o: pop[o] += PROVPOP.get(pid, 0)
civ = {}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    m = re.search(r"^\s*civilized\s*=\s*(\w+)", rd(f), re.M)
    civ[b.split(" - ")[0].strip()] = (m.group(1) if m else "yes") == "yes"
have = {os.path.basename(f)[:3] for f in glob.glob(f"{MOD}/history/units/*.txt")
        if "regiment" in rd(f)}
for tag in sorted(k for k in pop if pop[k] and k not in have):
    ps = owned.get(tag) or []
    if not ps: continue
    real = pop[tag] / 0.25
    if civ.get(tag, True) and real > 400_000:
        n = max(2, min(200, round(real / 1_500_000)))
        mix = [("infantry", round(n * .55)), ("irregular", round(n * .20)),
               ("cavalry", round(n * .17)), ("artillery", n - round(n*.55) - round(n*.20) - round(n*.17))]
    else:
        n = max(1, min(10, round(real / 6_000)))
        mix = [("irregular", round(n * .65)), ("cavalry", n - round(n * .65))]
    loc = caps.get(tag) if caps.get(tag) in ps else ps[0]
    homes = (ps * 60)[:max(1, n)]
    regs, k = [], 0
    for ty, cnt in mix:
        for i in range(max(0, cnt)):
            regs.append(f'\tregiment = {{\n\t\tname = "{i+1}. {ty.title()}"\n'
                        f'\t\ttype = {ty}\n\t\thome = {homes[k % len(homes)]}\n\t}}')
            k += 1
    if not regs: continue
    nm = (L["countries"].get(tag, {}).get("name") or tag)
    wr(f"{MOD}/history/units/{tag}_oob.txt",
       f"# {nm}\n\narmy = {{\n\tname = \"{nm} Army\"\n\tlocation = {loc}\n"
       + "\n".join(regs) + "\n}\n")
    log["armies for countries that had none"] += 1
    log["regiments for countries that had none"] += len(regs)

# --- a war footing for the powers already fighting ---------------------------------
# Multiplying the 1836 peacetime establishment. France fielded roughly four hundred
# thousand men in 1800 and the file gave it sixty-four regiments.
# France conscripted on a scale nobody matched until the 1860s. Double was
# not enough: it lost Jena.
WAR = {"FRA": 3.5, "AUS": 1.8, "ENG": 1.4, "RUS": 1.3, "SPA": 1.3,
       "TUR": 1.4, "PRU": 1.3, "SIC": 1.3, "NET": 1.2}
for tag, mult in WAR.items():
    f = f"{MOD}/history/units/{tag}_oob.txt"
    if not os.path.exists(f): continue
    s_ = rd(f); out, pos, added = [], 0, 0
    # Brace counting, not a regex. A non-greedy match for the army's closing brace
    # stops at the first regiment's closing brace instead, which is why the first
    # attempt grew seven regiments where it should have grown sixty-four.
    for m in re.finditer(r"[ \t]*army[ \t]*=[ \t]*\{", s_):
        i = m.end(); d = 1
        while i < len(s_) and d:
            if s_[i] == "{": d += 1
            elif s_[i] == "}": d -= 1
            i += 1
        body = s_[m.start():i]
        regs = []
        for rm in re.finditer(r"[ \t]*regiment[ \t]*=[ \t]*\{", body):
            j = rm.end(); dd = 1
            while j < len(body) and dd:
                if body[j] == "{": dd += 1
                elif body[j] == "}": dd -= 1
                j += 1
            regs.append(body[rm.start():j])
        if not regs:
            out.append(s_[pos:i]); pos = i; continue
        extra = int(round(len(regs) * (mult - 1)))
        new = []
        for k2 in range(extra):
            r = regs[k2 % len(regs)]
            r = re.sub(r'name\s*=\s*"[^"]*"', f'name = "Levy {k2+1}"', r, count=1)
            new.append(r)
        added += extra
        grown = body.rstrip()
        grown = grown[:grown.rindex("}")] + "\n".join(new) + "\n}"
        out.append(s_[pos:m.start()]); out.append(grown); pos = i
    out.append(s_[pos:])
    if added:
        wr(f, "".join(out)); log["regiments added for the war"] += added

for k, v in sorted(log.items()): print(f"  {k:<34}{v}")
