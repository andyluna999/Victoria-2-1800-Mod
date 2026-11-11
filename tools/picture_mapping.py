"""Give every event a face.

A hundred and sixty of our events shipped on `administration` -- a generic clerk at a
desk -- which makes a chain of forty events in a playthrough indistinguishable from
one another. HPM already carries three hundred and seventy-five pictures, so no new
art is needed: the job is matching.

The matching is by subject, not by country. A treaty gets a treaty picture, a battle
gets a battle, a coronation gets a throne, a rising gets a crowd. Where a picture
exists for the actual place it is used for the actual place. Where nothing fits, the
fallback is a period-appropriate generic rather than the clerk.
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

have = {os.path.basename(f)[:-4] for f in glob.glob(f"{MOD}/gfx/pictures/events/*.tga")}

def pick(*names):
    for n in names:
        if n in have: return n
    return None

# subject -> candidate pictures, best first. Only ones present on disk are used.
# Matched on the event's TITLE, which is specific, rather than its description, which
# is prose and mentions "the King" in half our events. First match wins, so the list
# runs from the most specific subject to the most general.
BY_WORD = [
 (("grito", "dolores"), ("1810_grito_de_dolores", "gritoasencio")),
 (("three guarantees", "iguala"), ("1821_three_guarantees",)),
 (("crown for the kingdom", "crown without a king", "coronation", "crowned"),
  ("1822_iturbide_crowned", "BRZ_pedro_coronation")),
 (("austerlitz", "jena", "wagram", "bailen", "medina", "second of may"),
  ("ambush_army", "big_parade", "battle_pavon")),
 (("tilsit", "pressburg", "schonbrunn", "frankfurt", "trujillo", "ildefonso",
   "fontainebleau", "armistice", "treaty"),
  ("treaty_of_paris_1856", "pact_of_piombieres", "league_of_three_emperors")),
 (("congress of vienna", "congress of paris", "peace of exhaustion", "congress"),
  ("berlin_congress_htm", "treaty_of_paris_1856")),
 (("expedition", "sails", "sailed", "fleet", "squadron", "morillo", "will not sail"),
  ("crimean_war_ships", "first_barbary_war", "usa_ship")),
 (("cortes", "constitution", "deputies", "assembly", "congress sits", "ayuntamiento",
   "junta", "cabildo"),
  ("senate_debate", "national_congress", "deliberation", "prussian_constitution")),
 (("rising", "revolt", "revolution", "insurrection", "mutiny", "aranjuez", "riot",
   "pont-rouge", "coup", "massacre", "colonists who stayed", "alhondiga"),
  # MEX_revolution is the 1910 revolution: Villa and Zapata, a century out
  # of period and instantly recognisable as wrong.
  ("streetriot", "storming_palace", "failed_revolution", "krakow_uprising")),
 (("viceroy", "audiencia", "intendanc", "governs", "government dissolves",
   "conspiracy", "suppress", "juntistas", "gallows", "repression"),
  ("asian_administration", "autocracy", "regency")),
 (("consolidacion", "treasury", "remittance", "monopoly", "customs", "tarif",
   "indemnity", "capital", "credit", "mines", "silver", "trade"),
  ("chilean_silver_rush", "bazaar", "stock_crash", "welcome_stranger_nugget")),
 (("militia", "army", "regiment", "garrison", "soldiers", "officers", "corps",
   "republic in arms", "cost of the americas", "fifteen years", "retaken",
   "foothold", "half a kingdom"),
  ("mexico_soldiers", "conscription_marching", "ethiopian_soldiers_marching")),
 (("slave", "slavery", "colonists", "plantation"),
  ("carta_esclavitud_ecu", "cotton_fields", "fugitive_slave")),
 (("seminary", "church", "bishop", "clergy", "university"),
  ("orthodox_priests", "missionaries")),
 (("louisiana", "new orleans", "mississippi", "deposit", "purchase", "frontier"),
  ("pioneer_wagons", "1843_GreatMigration", "homesteading")),
 (("haiti", "toussaint", "ennery", "hispaniola", "santo domingo", "les cayes",
   "silver bullet", "island"),
  ("haiti_debts", "dominican_revolution", "la_trinitaria")),
 (("tucuman", "talca", "protectorate", "declare", "independence", "republic",
   "kingdom", "autonomous", "madrid"),
  ("sucre", "map_of_colombia", "paraguay_independence", "montevideo_uruguay")),
 (("restless", "disaffected", "open revolt", "question", "year without"),
  ("streetriot", "nationalists", "failed_revolution")),
 (("smolensk", "moscow", "russia"), ("vacation_on_siberia", "assault_on_russian_lands")),
 (("absolutism", "settled order", "bourbon army", "grande armee", "army of the"),
  ("autocracy", "big_parade", "conscription_marching")),
]

loc_all = "".join(rd(f) for f in glob.glob(f"{MOD}/localisation/*.csv"))
titles = dict(re.findall(r"^(EVTNAME\d+);([^;]*)", loc_all, re.M))
descs = dict(re.findall(r"^(EVTDESC\d+);([^;]*)", loc_all, re.M))

# Decisions write `picture = administration` without quotes, so the first version of
# this pass skipped every one of them -- forty-one decisions still showing the clerk.
for f in (sorted(glob.glob(f"{MOD}/events/1800_*.txt"))
          + sorted(glob.glob(f"{MOD}/decisions/1800_*.txt"))):
    s = rd(f); out, pos, n = [], 0, 0
    for m in re.finditer(r'picture\s*=\s*"?administration"?', s):
        back = s[:m.start()]
        eid = re.findall(r"id = (\d+)", back)
        if eid and "/events/" in f:
            text = titles.get(f"EVTNAME{eid[-1]}", "").lower()
        else:
            # a decision: its own name is the most descriptive thing available
            names = re.findall(r"^\t([a-z_0-9]+)\s*=\s*\{", back, re.M)
            text = (names[-1].replace("_", " ") if names else "").lower()
        chosen = None
        for words, cands in BY_WORD:
            if any(w in text for w in words):
                chosen = pick(*cands)
                if chosen: break
        if not chosen:
            continue
        out.append(s[pos:m.start()]); out.append(f'picture = "{chosen}"')
        pos = m.end(); n += 1
        log[f"-> {chosen}"] += 1
    if n:
        out.append(s[pos:]); wr(f, "".join(out)); log["events repictured"] += n

left = sum(len(re.findall(r'picture\s*=\s*"administration"', rd(f)))
           for f in glob.glob(f"{MOD}/events/1800_*.txt"))
log["still on the clerk"] = left
for k, v in sorted(log.items(), key=lambda x: -x[1] if isinstance(x[1], int) else 0):
    print(f"  {k:<34}{v}")
