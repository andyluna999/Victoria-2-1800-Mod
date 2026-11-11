"""Spain: strong, stable, and overextended.

Three complaints from the runs, and they are the same complaint.

**Spain is in permanent rebellion.** Every run produces risings in the peninsula from
the first decade. Bourbon Spain in 1800 was many things -- bankrupt, badly governed,
run by the queen's favourite -- but it was not seething. The absolutism modifier holds
consciousness and militancy down until 1815, and then expires, so unrest arrives
exactly when the Restoration does and the liberal risings of 1820 and 1830 have
somewhere to come from.

**Spain cannot reach the Americas.** Fifty-four hulls and no transports is not a fleet
that reconquers anything. Spain in 1800 had the third navy in the world, roughly sixty
ships of the line, and the whole argument about the colonies turned on whether it could
get an army across the Atlantic faster than the Royal Navy could stop it.

**Spain cannot beat a colony.** Thirty-nine regiments for a country with an empire on
two continents. The Bourbon army was small by French standards and professional by
colonial ones: the peninsular regiments that went to the Americas beat militia
consistently, and lost only when there were too many places to be at once.

So Spain gets the army and navy it had, and a modifier that makes it exactly what it
was: better than any single colony, and unable to be in five places. Supply consumption
and mobilisation cost are punishing, so the second and third simultaneous war hurt far
more than the first.

**And the colonies get garrisons.** Fourteen regiments for New Spain was a token. The
viceregal armies were real -- some thirty thousand men of all kinds in New Spain alone,
mostly militia with creole officers -- and they are what the player commands as viceroy
and fights as a republic. They are numerous and bad: irregulars and cavalry, few
regulars, no organisation bonus. Quantity against Spain's quality, which is the
historical shape of every one of these wars.
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

MODS = """
age_of_absolutism = {
\ticon = 4
\tcore_pop_militancy_modifier = -3.0
\tcore_pop_consciousness_modifier = -2.0
\tglobal_pop_militancy_modifier = -0.03
\tglobal_pop_consciousness_modifier = -0.02
\tadministrative_efficiency_modifier = 0.1
\truling_party_support = 0.2
}

the_bourbon_army = {
\ticon = 2
\tland_attack_modifier = 0.2
\tland_defense_modifier = 0.15
\tland_organisation = 0.15
\tland_unit_start_experience = 10
\tsupply_consumption = 0.35
\tmobilisation_economy_impact = 0.4
\torg_regain = -0.1
}

the_colonial_levy = {
\ticon = 1
\tmobilisation_size = 0.12
\tland_organisation = -0.2
\tland_attack_modifier = -0.15
\torg_regain = -0.2
\tsupply_consumption = -0.2
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "age_of_absolutism" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

# --- the army and the navy ------------------------------------------------------------
# Spain's order of battle is multiplied; the colonies get a bigger, worse one.
SCALE = {"SPA": 1.9}
# Halved from the first pass. Thirty-six regiments made New Spain the eighth power in
# the world; eighteen makes it a garrison force that can hold its own provinces and
# lose a straight fight with Spain, which is what a viceroyalty was.
COLONIAL = {"NSP": 1.3, "VPE": 1.3, "VNG": 1.2, "RDP": 1.2, "CGC": 1.2,
            "CBA": 1.2, "PTR": 1.1, "EBR": 1.3}
FLEET = {"SPA": 1.5}

for tag, mult in list(SCALE.items()) + list(COLONIAL.items()):
    f = f"{MOD}/history/units/{tag}_oob.txt"
    if not os.path.exists(f): continue
    s = rd(f); out, pos, added = [], 0, 0
    for m in re.finditer(r"[ \t]*army[ \t]*=[ \t]*\{", s):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[m.start():i]
        regs = []
        for rm in re.finditer(r"[ \t]*regiment[ \t]*=[ \t]*\{", body):
            j = rm.end(); dd = 1
            while j < len(body) and dd:
                if body[j] == "{": dd += 1
                elif body[j] == "}": dd -= 1
                j += 1
            regs.append(body[rm.start():j])
        if not regs:
            out.append(s[pos:i]); pos = i; continue
        extra = int(round(len(regs) * (mult - 1)))
        new = []
        for k in range(extra):
            r = regs[k % len(regs)]
            # the colonies raise militia, not regulars
            if tag in COLONIAL:
                r = re.sub(r"type\s*=\s*\w+", "type = irregular", r, count=1)
            r = re.sub(r'name\s*=\s*"[^"]*"', f'name = "{k+1}. Levy"', r, count=1)
            new.append(r)
        added += extra
        grown = body.rstrip()
        grown = grown[:grown.rindex("}")] + "\n".join(new) + "\n}"
        out.append(s[pos:m.start()]); out.append(grown); pos = i
    out.append(s[pos:])
    if added:
        wr(f, "".join(out)); log[f"regiments added"] += added

for tag, mult in FLEET.items():
    f = f"{MOD}/history/units/{tag}_oob.txt"
    if not os.path.exists(f): continue
    s = rd(f); out, pos, added = [], 0, 0
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
            # an army that cannot be carried is not a threat to anyone overseas
            if k % 3 == 2:
                sp = re.sub(r"type\s*=\s*\w+", "type = clipper_transport", sp, count=1)
            sp = re.sub(r'name\s*=\s*"[^"]*"', f'name = "No. {k+1}"', sp, count=1)
            new.append(sp)
        added += extra
        grown = body.rstrip()
        grown = grown[:grown.rindex("}")] + "\n".join(new) + "\n}"
        out.append(s[pos:m.start()]); out.append(grown); pos = i
    out.append(s[pos:])
    if added:
        wr(f, "".join(out)); log["ships added"] += added

# --- the modifiers, granted by event because history files will not take them ----------
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))

ABSOLUTIST = ["SPA", "AUS", "RUS", "PRU", "POR", "SIC", "SAR", "TUS", "PAP",
              "BAV", "WUR", "BAD", "SAX", "DEN", "SWE", "TUR"]
EV.append(f"""country_event = {{
    id = 9101900
    title = "EVTNAME9101900"
    desc = "EVTDESC9101900"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        OR = {{ {' '.join(f'tag = {t}' for t in ABSOLUTIST)} }}
        year = 1800
    }}
    mean_time_to_happen = {{ days = 4 }}

    option = {{
        name = "EVTOPTA9101900"
        add_country_modifier = {{ name = age_of_absolutism duration = 5475 }}
    }}
}}

country_event = {{
    id = 9101901
    title = "EVTNAME9101901"
    desc = "EVTDESC9101901"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = SPA
        year = 1800
    }}
    mean_time_to_happen = {{ days = 4 }}

    option = {{
        name = "EVTOPTA9101901"
        add_country_modifier = {{ name = the_bourbon_army duration = -1 }}
    }}
}}

country_event = {{
    id = 9101902
    title = "EVTNAME9101902"
    desc = "EVTDESC9101902"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        OR = {{ tag = NSP tag = VPE tag = VNG tag = RDP tag = CGC tag = CBA tag = PTR tag = EBR }}
        year = 1800
    }}
    mean_time_to_happen = {{ days = 4 }}

    option = {{
        name = "EVTOPTA9101902"
        add_country_modifier = {{ name = the_colonial_levy duration = -1 }}
    }}
}}
""")
loc("EVTNAME9101900", "The Settled Order of Things")
loc("EVTDESC9101900",
    "Kings govern because they are kings, the Church teaches that this is how God "
    "arranged matters, and the men who think otherwise publish in Amsterdam and are "
    "read by perhaps four thousand people on the continent. There was a revolution in "
    "France and the answer to it has been censorship, the Index and the police, which "
    "will hold for about fifteen years.")
loc("EVTOPTA9101900", "Nothing is to be discussed.")
loc("EVTNAME9101901", "The Army of the Bourbons")
loc("EVTDESC9101901",
    "Small, professional, and the best thing the Spanish state produces. The peninsular "
    "regiments beat colonial militia whenever they meet it, and the difficulty has "
    "never been winning a battle in the Americas -- it has been that there are five "
    "places that need an army and only enough money for one.")
loc("EVTOPTA9101901", "Quality, and not enough of it.")
loc("EVTNAME9101902", "The Militia of the Kingdom")
loc("EVTDESC9101902",
    "Twelve battalions on paper and rather fewer in the field, officered by the sons of "
    "the best families and armed with whatever the arsenal at Veracruz has not sold. "
    "What it has is numbers and the ability to be raised again after being beaten, "
    "which over ten years turns out to matter more than winning.")
loc("EVTOPTA9101902", "Numbers, and the time to use them.")

def wr2(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
wr2(f"{MOD}/events/1800_Balance.txt", "\n".join(EV))
wr2(f"{MOD}/localisation/25_balance.csv",
    "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
