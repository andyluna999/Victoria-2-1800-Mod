"""Hispaniola, 1800-1809.

**Who owns Santo Domingo on 1 January 1800 is a trick question.** Spain ceded the whole
eastern two-thirds of the island to France at Basel on 22 July 1795. France never came
to collect: it was busy, and the Spanish governor Joaquín García simply carried on
governing, collecting the taxes and flying the Spanish flag over a colony that was
legally French. He did so for five and a half years, until Toussaint Louverture marched
across the island in January 1801 and took possession on France's behalf without being
asked to.

So the map wants owner and controller to disagree -- France holds the title, Spain
holds the ground -- which is the same device as Austria standing in French Piedmont.

**And Saint-Domingue is not a colony in any ordinary sense.** On the start date it is
French in law and Toussaint's in fact: he is governor-general, he has just finished
beating Rigaud in the War of the South, and within eighteen months he will write a
constitution making himself governor for life and abolishing slavery for ever in a
colony that is still, technically, taking orders from Paris.

The chain:

  **1800** The War of the South ends. Toussaint holds the whole colony.
  **1801** He occupies Santo Domingo, frees the slaves there, and promulgates his
  constitution. Napoleon reads it as a declaration of independence, which it nearly is.
  **1802** Leclerc lands with the largest expedition France ever sent overseas.
  Toussaint is taken by a trick and dies in a cell in the Jura.
  **1803** Yellow fever kills Leclerc and most of his army. Rochambeau fights a war of
  extermination and loses it.
  **1804** Dessalines declares independence on the first of January and the colony
  takes back its Taíno name.
  **1809** In Santo Domingo the Spanish creoles rise against French rule and ask Madrid
  to take them back, beginning the twelve years they themselves called España Boba --
  foolish Spain -- because the Crown wanted the colony and would not pay for it.
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
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

# --- the map: France owns what Spain is standing on --------------------------------
SANTO_DOMINGO = (2214, 2216)
for pid in SANTO_DOMINGO:
    g = glob.glob(f"{MOD}/history/provinces/*/{pid} - *.txt")
    if not g: continue
    s = rd(g[0])
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^\s*owner\s*=.*$", "owner = FRA", head, count=1, flags=re.M)
    if re.search(r"^\s*controller\s*=", head, re.M):
        head = re.sub(r"^\s*controller\s*=.*$", "controller = SPA", head, count=1, flags=re.M)
    else:
        head = re.sub(r"(^owner\s*=.*\n)", r"\1controller = SPA\n", head, count=1, flags=re.M)
    open(g[0], "w", encoding="cp1252", errors="replace",
         newline="\n").write(head.rstrip("\n") + "\n" + tail)
    log["Santo Domingo provinces: France owns, Spain holds"] += 1

def ev(eid, tag, yr, until, title, desc, opt, effect, needs="", mtth=3, extra=""):
    gate = f"        has_global_flag = {needs}\n" if needs else ""
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        year = {yr}
        NOT = {{ year = {until} }}
{gate}{extra}    }}
    mean_time_to_happen = {{ months = {mtth} }}

    option = {{
        name = "EVTOPTA{eid}"
{effect}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["events"] += 1

ev(9101300, "FRA", 1800, 1802, "The War of the South Is Over",
   "Rigaud has sailed for France and Toussaint holds every parish from Môle-Saint-"
   "Nicolas to Jacmel. He governs in the Republic's name, keeps the forms scrupulously, "
   "signs himself governor-general, and has an army of twenty thousand men who have "
   "beaten the English and the Spanish and now each other. The commissioners Paris "
   "sends him are received with great courtesy and ignored.",
   "The colony is quiet, and it is his.",
   "        set_global_flag = h18_toussaint_supreme\n"
   "        2213 = { add_core = HAI }\n        2215 = { add_core = HAI }\n"
   "        prestige = 3", mtth=4)

ev(9101301, "FRA", 1801, 1803, "Toussaint Takes Santo Domingo",
   "He has crossed the island without orders and taken possession of the Spanish "
   "colony that Basel gave us six years ago and we never collected. Governor García "
   "handed over the keys. Toussaint has abolished slavery there, which was not in the "
   "treaty, and is now promulgating a constitution for the whole island that names "
   "himself governor for life with the right to choose his successor. He sends it to "
   "the First Consul for approval, as a courtesy.",
   "A gilded African in a general's coat.",
   "        set_global_flag = h18_toussaint_constitution\n"
   "        2214 = { secede_province = FRA add_core = HAI }\n"
   "        2216 = { secede_province = FRA add_core = HAI }\n"
   "        SPA = { relation = { who = FRA value = -30 } }",
   needs="h18_toussaint_supreme", mtth=4)

ev(9101302, "FRA", 1802, 1804, "The Leclerc Expedition",
   "Twenty-two thousand men under my brother-in-law, the largest force France has ever "
   "sent across an ocean, with orders to restore the authority of the Republic and, "
   "when the moment is right, the institution that made the colony worth having. "
   "Toussaint is to be invited aboard a ship to discuss terms. He is not to leave it.",
   "Rid us of these gilded Africans.",
   "        set_global_flag = h18_leclerc\n"
   "        treasury = -30000\n"
   "        2213 = { add_province_modifier = { name = the_fever_coast duration = 1095 } }\n"
   "        2215 = { add_province_modifier = { name = the_fever_coast duration = 1095 } }\n"
   "        badboy = 3",
   needs="h18_toussaint_constitution", mtth=4)

ev(9101303, "FRA", 1803, 1805, "The Fever and Rochambeau",
   "Leclerc is dead of the fever and so are fifty thousand others. Rochambeau has "
   "answered an insurrection with dogs imported from Cuba, drownings in the bay of Le "
   "Cap, and a gas chamber in a ship's hold, and the colony has answered him. The "
   "British are back in the Channel and there is no reinforcement coming. We have lost "
   "the richest colony in the world and most of an army to it.",
   "Damn sugar, damn coffee, damn colonies.",
   "        set_global_flag = h18_saint_domingue_lost\n"
   "        prestige = -15\n        badboy = 2",
   needs="h18_leclerc", mtth=6)

# --- independence ---------------------------------------------------------------------
EV.append("""country_event = {
    id = 9101304
    title = "EVTNAME9101304"
    desc = "EVTDESC9101304"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = FRA
        year = 1804
        NOT = { year = 1806 }
        has_global_flag = h18_saint_domingue_lost
    }
    mean_time_to_happen = { months = 2 }

    option = {
        name = "EVTOPTA9101304"
        set_global_flag = h18_haiti_independent
        prestige = -10
        2213 = { secede_province = HAI }
        2215 = { secede_province = HAI }
        HAI = {
            government = presidential_dictatorship
            prestige = 10
            treasury = 5000
            any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = -4 consciousness = 4 }
        }
    }
}
""")
loc("EVTNAME9101304", "The First of January, 1804")
loc("EVTDESC9101304",
    "Dessalines has declared the colony independent at Gonaïves and given it back the "
    "name the Taíno used for it: Ayiti. He has torn the white out of the tricolour and "
    "kept the rest. It is the second republic in the Americas and the only state "
    "anywhere ever made by a successful revolt of the enslaved, and not one government "
    "on earth intends to recognise it.")
loc("EVTOPTA9101304", "Then let no one trade with them.")

# --- España Boba --------------------------------------------------------------------
EV.append("""country_event = {
    id = 9101305
    title = "EVTNAME9101305"
    desc = "EVTDESC9101305"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = SPA
        year = 1809
        NOT = { year = 1812 }
        has_global_flag = h18_bayonne
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9101305"
        set_global_flag = h18_espana_boba
        2214 = { secede_province = THIS add_core = THIS }
        2216 = { secede_province = THIS add_core = THIS }
        prestige = 5
        FRA = { prestige = -3 }
    }
}
""")
loc("EVTNAME9101305", "España Boba")
loc("EVTDESC9101305",
    "The creoles of Santo Domingo have risen against French rule, beaten the garrison "
    "at Palo Hincado with British powder, and asked to be Spanish again. The Crown has "
    "accepted with enthusiasm and sent nothing: no money, no garrison, no governor worth "
    "the title. The colonists will spend the next twelve years calling the arrangement "
    "foolish Spain, and they will mean it affectionately for about two of them.")
loc("EVTOPTA9101305", "They may fly our flag at their own expense.")

MODS = """
the_fever_coast = {
\ticon = 1
\tland_attrition = 2.0
\tlocal_rgo_output = -0.25
\tlocal_ruling_party_support = -0.2
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_fever_coast" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 1

wr(f"{MOD}/events/1800_Hispaniola.txt", "\n".join(EV))
wr(f"{MOD}/localisation/18_hispaniola.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<46}{v}")
