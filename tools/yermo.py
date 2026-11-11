"""Yermo's night was not a coin flip, and the mod should not make it one.

Three hundred armed men of the Parian came over the palace wall and took a viceroy out
of his bed, in a capital of a hundred and thirty thousand people, in the richest
kingdom Spain possessed. That worked because of a specific set of conditions, and every
one of them was something Iturrigaray had control over:

  **There was nothing in the capital to stop them.** The peninsular merchants brought
  three hundred men. The colonial militia -- twelve battalions officered by creoles,
  the only armed force in New Spain with reason to defend a creole junta -- was in its
  home provinces. Nobody had brought it in.

  **The merchants had a grievance and the money to act on it.** The Parian's wealth was
  the import monopoly. A viceroy who had licensed neutral traders had already taken the
  thing they cared about most, and they knew what a creole junta would do to the rest.

  **The viceroy was compromised.** Iturrigaray had profited personally from the
  Consolidacion, which gave the Audiencia a respectable reason to be rid of him and gave
  the creoles he was supposedly protecting a reason not to die for him.

  **The apparatus was already pointed at meetings.** A government that had spent four
  years arresting corresponding societies had the lists, the informers and the habit.

So the odds now follow from the record. A viceroy who brought the militia into the
capital, let the Consolidacion die quietly, kept the Parian's monopoly intact and did
not spend the decade hanging juntistas has done everything that was actually available
to him, and the night goes the other way. One who did none of it gets the history.

There is also a decision he can take with the thing in front of him -- garrisoning the
palace once the ayuntamiento is already sitting -- which is expensive, announces to
every peninsular in Mexico City exactly whose side he is on, and is the single largest
factor in the outcome.
"""
import re, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

# --- the preparation the player can make while there is still time -------------------
DEC.append("""\tgarrison_the_palace = {
\t\tpicture = administration
\t\tpotential = {
\t\t\ttag = NSP
\t\t\thas_country_flag = h18c_bayonne_known
\t\t\tNOT = { has_country_flag = h18c_palace_garrisoned }
\t\t\tNOT = { has_country_flag = h18c_viceroy_deposed }
\t\t\tNOT = { has_country_flag = h18c_junta_governs }
\t\t}
\t\tallow = { money = 6000 }
\t\teffect = {
\t\t\tset_country_flag = h18c_palace_garrisoned
\t\t\ttreasury = -6000
\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = -2 consciousness = 1 }
\t\t\tany_pop = { limit = { has_pop_culture = spanish } militancy = 4 consciousness = 2 }
\t\t\tchange_variable = { which = separatism value = 5 }
\t\t\tprestige = -3
\t\t}
\t\tai_will_do = { factor = 3 }
\t}
""")
loc("garrison_the_palace_title", "Bring the Militia into the Capital")
loc("garrison_the_palace_desc",
    "Three battalions of the provincial militia, quartered in the city itself, with "
    "creole officers who understand precisely what they are being asked to guard. It "
    "announces to every peninsular in Mexico City whose side the viceroy is on, which "
    "is why no viceroy has ever done it. It also means that if the Parian decides to "
    "settle the question with three hundred men and a ladder, there will be somebody "
    "in the courtyard.")

# --- the night, weighted by the record ------------------------------------------------
TITLES = {
 9101110: ("The Palace Is Held",
           "They came over the wall at one in the morning as everyone said they would, "
           "and found three battalions of provincial militia in the courtyard with "
           "creole officers who had been waiting up for them. The Parian has money and "
           "three hundred men. It does not have an army, and tonight that distinction "
           "is the whole of the matter."),
 9101111: ("A Near Thing at the Gate",
           "The militia was in the city but not in the palace, and the thing turned on "
           "which officers woke first and whose orders they took. It was decided in a "
           "corridor by perhaps forty men, and everyone who was there gives a "
           "different account of it afterwards."),
 9101112: ("The Garrison Is Divided",
           "Half the officers in this capital owe their commissions to the viceroy and "
           "the other half owe their fortunes to the men coming over the wall. Nobody "
           "knows which half the sentries belong to until the sentries decide."),
 9101113: ("Nothing Stands in the Way",
           "No militia in the capital, a viceroy the Audiencia has been collecting "
           "grievances against for four years, and a merchant community that has "
           "already settled who holds which office by morning. Three hundred men with "
           "a ladder will be sufficient, and everyone concerned knows it."),
}

def night(eid, odds, extra, note):
    """One branch of Yermo's night, as an ordinary event with a real trigger.

    These were `is_triggered_only` with triggers attached, on the assumption that a
    directly-fired event still tests its conditions. Victoria II does not: it fires
    what it is told to fire. All four branches went off in a row carrying the same
    title, which is exactly what the playtest saw -- the ayuntamiento sitting four
    times. An ordinary event with a trigger and a short mean time behaves the way the
    design intended.
    """
    title, desc = TITLES[eid]
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = NSP
        has_country_flag = h18c_the_night_comes
        NOT = {{ has_country_flag = h18c_the_night_resolved }}
{extra}    }}
    mean_time_to_happen = {{ days = 20 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_country_flag = h18c_the_night_resolved
        random_list = {{
            {100 - odds} = {{ country_event = {{ id = 9101101 days = 15 }} }}
            {odds} = {{ country_event = {{ id = 9101102 days = 15 }} }}
        }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title)
    loc(f"EVTDESC{eid}", desc)
    loc(f"EVTOPTA{eid}", "We shall see.")
    log[note] = f"{odds}% the junta holds"

# Mutually exclusive by construction: each branch excludes everything above it, so
# exactly one trigger can pass. Without this, "everything done" also satisfies "most"
# and "something", and three events fire on the same night.
_ALL3 = ("        has_country_flag = h18c_palace_garrisoned\n"
         "        has_country_modifier = criollo_militia\n"
         "        has_country_flag = consolidacion_evaded\n")
_ANY = ("        OR = {\n"
        "            has_country_flag = h18c_palace_garrisoned\n"
        "            has_country_modifier = criollo_militia\n"
        "            has_country_flag = consolidacion_evaded\n"
        "        }\n")
_NOT_ALL3 = ("        NOT = {\n            AND = {\n"
             "                has_country_flag = h18c_palace_garrisoned\n"
             "                has_country_modifier = criollo_militia\n"
             "                has_country_flag = consolidacion_evaded\n"
             "            }\n        }\n")
# two of the three, but not all three
_TWO = ("        OR = {\n"
        "            AND = {\n"
        "                has_country_flag = h18c_palace_garrisoned\n"
        "                has_country_modifier = criollo_militia\n"
        "            }\n"
        "            AND = {\n"
        "                has_country_flag = h18c_palace_garrisoned\n"
        "                has_country_flag = consolidacion_evaded\n"
        "            }\n"
        "            AND = {\n"
        "                has_country_modifier = criollo_militia\n"
        "                has_country_flag = consolidacion_evaded\n"
        "            }\n"
        "        }\n")
_NOT_TWO = ("        NOT = {\n            OR = {\n"
            "                AND = {\n"
            "                    has_country_flag = h18c_palace_garrisoned\n"
            "                    has_country_modifier = criollo_militia\n"
            "                }\n"
            "                AND = {\n"
            "                    has_country_flag = h18c_palace_garrisoned\n"
            "                    has_country_flag = consolidacion_evaded\n"
            "                }\n"
            "                AND = {\n"
            "                    has_country_modifier = criollo_militia\n"
            "                    has_country_flag = consolidacion_evaded\n"
            "                }\n"
            "            }\n        }\n")
_NONE = ("        NOT = {\n            OR = {\n"
         "                has_country_flag = h18c_palace_garrisoned\n"
         "                has_country_modifier = criollo_militia\n"
         "                has_country_flag = consolidacion_evaded\n"
         "            }\n        }\n")
STRONG = _ALL3
GOOD = _TWO + _NOT_ALL3
FAIR = _ANY + _NOT_TWO + _NOT_ALL3
night(9101110, 85, STRONG, "everything done")
night(9101111, 65, GOOD, "most done")
night(9101112, 45, FAIR, "something done")
night(9101113, 20, _NONE, "nothing done")

# The fork routes straight to 9101115. An earlier draft had a router event in
# front of it with the same title, which meant one country could see "The Night
# Is Decided by the Decade" twice.

EV.append("""country_event = {
    id = 9101115
    title = "EVTNAME9101115"
    desc = "EVTDESC9101115"
    picture = "administration"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9101115"
        set_country_flag = h18c_the_night_comes
    }
}
""")
loc("EVTNAME9101115", "They Are Counting Muskets in the Parian")
loc("EVTDESC9101115",
    "The merchants have stopped pretending the junta is a legal question. What happens "
    "in the palace over the next few weeks will be settled by who has armed men in "
    "this city and whose side they are on, and that was decided years ago by choices "
    "nobody thought were about this.")
loc("EVTOPTA9101115", "Then we shall see what we have built.")

# --- point the original fork at the router ----------------------------------------------
f = f"{MOD}/events/1800_Iturrigaray.txt"
s = rd(f)
s = s.replace("""        random_list = {
            70 = { country_event = { id = 9101101 days = 45 } }
            30 = { country_event = { id = 9101102 days = 45 } }
        }""",
"""        # Not a coin flip. The outcome is routed through what this government
        # actually did: whether the militia is in the capital, whether the viceroy is
        # compromised by the Consolidacion, and whether he has had the nerve to
        # garrison his own palace.
        country_event = { id = 9101115 days = 30 }""")
wr(f, s)

wr(f"{MOD}/events/1800_Yermo.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_Yermo.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/27_yermo.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<22}{v}")
