"""The Plata: a revolution that went abroad, and a union that would not hold.

Written from a request by an Argentine player, which is the right way to build this
part of the map.

Two things make the Rio de la Plata different from every other viceroyalty. The first
is that its revolution did not stay home. Buenos Aires deposed its viceroy in a week
and then spent fifteen years exporting the result: San Martin took an army over the
Andes to free Chile and sailed it to Peru, and Hipolito Bouchard took a single frigate
around the world under the flag of a country four years old, burning Spanish shipping
from the Philippines to California. In November 1818 he took Monterey and held it for
six days, which is the only time Argentina has governed California and is not in most
English-language histories at all.

The second is that it did not hold together. Independence was declared at Tucuman in
1816 by a congress that Artigas and the Liga Federal refused to attend, because the
question of whether the interior provinces were partners or possessions had already
turned into a war. Paraguay left in 1811 and was never brought back. Uruguay was
fought over with Brazil for three years until Britain, which wanted neither of them
holding both banks of the estuary, mediated it into existence in 1828. And the
unitarios and the federales went on killing each other until 1861.

So: the revolution can be carried outward, at a cost, and the union can be held
together or lost, and neither is free. The country that comes out of it is called the
United Provinces until somebody decides otherwise, because that is what it called
itself.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import os, collections

MOD = _BUILD
log = collections.Counter()
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

MODS = """
the_army_of_the_andes = {
\ticon = 2
\tland_attack_modifier = 0.2
\tsupply_consumption = -0.4
\tmovement_cost = -0.2
\torg_regain = 0.2
}

the_liga_federal = {
\ticon = 1
\tcore_pop_militancy_modifier = 3.0
\ttax_efficiency = -0.25
\tadministrative_efficiency_modifier = -0.2
\tland_organisation = -0.1
}

the_union_preserved = {
\ticon = 8
\tcore_pop_militancy_modifier = -1.5
\ttax_efficiency = 0.15
\tprestige = 0.4
\tglobal_assimilation_rate = 0.25
}

the_corsair_cruise = {
\ticon = 4
\tnaval_organisation = 0.2
\tleadership_modifier = 0.15
\ttariff_efficiency_modifier = 0.2
}

the_unitarian_quarrel = {
\ticon = 1
\tcore_pop_consciousness_modifier = 1.5
\tcore_pop_militancy_modifier = 2.0
\tadministrative_efficiency_modifier = -0.15
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "\nthe_army_of_the_andes = {" not in src:
    wr(f"{MOD}/common/event_modifiers.txt", src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 5

PL = "OR = { tag = RDP tag = ARG }"

def ev(eid, body, title, desc, opts):
    EV.append(body); loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    for k, v in opts.items(): loc(k, v)
    log["events"] += 1

# --- 1816: Tucuman, and the congress Artigas would not attend ---------------------------
ev(9103000, f"""country_event = {{
    id = 9103000
    title = "EVTNAME9103000"
    desc = "EVTDESC9103000"
    picture = "1817_san_martin"
    fire_only_once = yes

    trigger = {{
        {PL}
        year = 1816
        NOT = {{ year = 1824 }}
        OR = {{
            has_country_flag = h18c_junta_governs
            has_country_flag = h18c_independent
        }}
    }}
    mean_time_to_happen = {{ months = 6 }}

    option = {{
        name = "EVTOPTA9103000"
        set_country_flag = h18p_tucuman
        set_country_flag = h18p_centralist
        add_country_modifier = {{ name = the_liga_federal duration = -1 }}
        prestige = 10
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 3 consciousness = 3 }}
        ai_chance = {{ factor = 55 }}
    }}
    option = {{
        name = "EVTOPTB9103000"
        set_country_flag = h18p_tucuman
        set_country_flag = h18p_federalist
        add_country_modifier = {{ name = the_union_preserved duration = -1 }}
        political_reform = federalism
        prestige = 5
        any_pop = {{ militancy = -3 }}
        ai_chance = {{ factor = 45 }}
    }}
}}
""", "The Congress of Tucuman",
"Deputies from the provinces have declared these United Provinces free of Ferdinand "
"and of every other foreign domination, which is the easy part. The hard part is in "
"the empty chairs: Artigas and the Liga Federal are not here, because the question of "
"whether the interior is a partner of Buenos Aires or a possession of it has already "
"been settled by force in Entre Rios and settled the other way in Santa Fe. The "
"congress can govern from the port and treat the provinces as provinces, or it can "
"concede that a federation of this size is the only thing fourteen governors will "
"ever agree to obey.",
{"EVTOPTA9103000": "One nation, governed from Buenos Aires.",
 "EVTOPTB9103000": "A federation, or nothing at all."})

# --- 1817: the Army of the Andes --------------------------------------------------------
ev(9103001, f"""country_event = {{
    id = 9103001
    title = "EVTNAME9103001"
    desc = "EVTDESC9103001"
    picture = "1817_san_martin"
    fire_only_once = yes

    trigger = {{
        {PL}
        year = 1817
        NOT = {{ year = 1826 }}
        has_country_flag = h18p_tucuman
    }}
    mean_time_to_happen = {{ months = 8 }}

    option = {{
        name = "EVTOPTA9103001"
        set_country_flag = h18p_the_andes
        add_country_modifier = {{ name = the_army_of_the_andes duration = -1 }}
        treasury = -20000
        prestige = 15
        CGC = {{ country_event = {{ id = 9103002 days = 30 }} }}
        ai_chance = {{ factor = 70 }}
    }}
    option = {{
        name = "EVTOPTB9103001"
        treasury = 10000
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 1 }}
        ai_chance = {{ factor = 30 }}
    }}
}}
""", "The Army of the Andes",
"San Martin has spent three years in Mendoza building an army nobody asked him to "
"build, out of a province with eight thousand people in it, and he intends to take it "
"over the cordillera at twelve thousand feet. The argument is that this revolution "
"cannot be safe while Lima is a Spanish arsenal, and that the road to Lima runs "
"through Chile and not through Upper Peru, where four armies have already been "
"destroyed trying. It will cost more than the treasury has. He has been selling his "
"own furniture.",
{"EVTOPTA9103001": "Over the cordillera, then. Chile first, and Lima after.",
 "EVTOPTB9103001": "We have a revolution of our own to finish."})

ev(9103002, """country_event = {
    id = 9103002
    title = "EVTNAME9103002"
    desc = "EVTDESC9103002"
    picture = "1817_san_martin"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9103002"
        change_variable = { which = separatism value = 30 }
        any_pop = { limit = { has_pop_culture = criollo } militancy = 5 consciousness = 4 }
        FROM = { relation = { who = THIS value = 60 } }
    }
}
""", "An Army Has Crossed the Cordillera",
"Three thousand men came over the Los Patos and Uspallata passes in five days, which "
"the governor had been assured was impossible at this time of year by everyone he "
"asked. A third of the mules died. The army that arrived is still an army, it is "
"already across the Aconcagua, and the only force between it and Santiago is the one "
"that has spent six years failing to pacify the south.",
{"EVTOPTA9103002": "They are over. God help us."})

# --- 1818: Bouchard, the frigate, and California ----------------------------------------
DEC.append("""\tthe_corsair_cruise = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = { tag = RDP tag = ARG }
\t\t\tyear = 1817
\t\t\tNOT = { year = 1830 }
\t\t\thas_country_flag = h18p_tucuman
\t\t\tNOT = { has_country_flag = h18p_corsair }
\t\t}
\t\tallow = { money = 9000 }
\t\teffect = {
\t\t\tset_country_flag = h18p_corsair
\t\t\ttreasury = -9000
\t\t\tadd_country_modifier = { name = the_corsair_cruise duration = -1 }
\t\t\tprestige = 8
\t\t\tcountry_event = { id = 9103010 days = 400 }
\t\t}
\t\tai_will_do = { factor = 3 }
\t}
""")
loc("the_corsair_cruise_title", "Commission the Corsair Cruise")
loc("the_corsair_cruise_desc",
    "A letter of marque for Hipolito Bouchard and the frigate La Argentina, to take "
    "Spanish shipping wherever Spanish shipping can be found. He proposes to find it "
    "in the Philippines. The government cannot afford a navy and this is the next best "
    "thing: one ship, a crew of every nationality on the waterfront, and the flag of a "
    "country four years old flying in oceans that have never seen it.")
log["decisions"] = 1

ev(9103010, """country_event = {
    id = 9103010
    title = "EVTNAME9103010"
    desc = "EVTDESC9103010"
    picture = "1817_san_martin"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9103010"
        set_country_flag = h18p_monterey
        prestige = 25
        treasury = 24000
        NSP = { relation = { who = THIS value = -60 } }
        MEX = { relation = { who = THIS value = -30 } }
        87 = { add_core = THIS }
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 2 }
    }
    option = {
        name = "EVTOPTB9103010"
        prestige = 15
        treasury = 30000
        NSP = { relation = { who = THIS value = -40 } }
    }
}
""", "La Argentina at Monterey",
"Bouchard has gone round the world. He took Spanish prizes off Luzon, burned the "
"settlement at Hawaii's expense after a disagreement with Kamehameha's people, and on "
"the twentieth of November put two hundred men ashore in Alta California and took "
"Monterey, the capital, which he held for six days and left burning. The flag of the "
"United Provinces has flown over California. Whether that is a claim or an anecdote "
"depends entirely on what this government decides to do about it.",
{"EVTOPTA9103010": "It is a claim. Enter it on the map.",
 "EVTOPTB9103010": "It was a raid. Take the prize money and say nothing."})

# --- the revolution carried to Central America -------------------------------------------
ev(9103011, """country_event = {
    id = 9103011
    title = "EVTNAME9103011"
    desc = "EVTDESC9103011"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        OR = { tag = RDP tag = ARG }
        has_country_flag = h18p_corsair
        year = 1819
        NOT = { year = 1832 }
    }
    mean_time_to_happen = { months = 14 }

    option = {
        name = "EVTOPTA9103011"
        set_global_flag = h18p_the_isthmus_rises
        prestige = 12
        NSP = { change_variable = { which = separatism value = 18 } }
        MEX = { change_variable = { which = separatism value = 12 } }
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 2 }
    }
    option = {
        name = "EVTOPTB9103011"
        prestige = -3
    }
}
""", "The Coast of the Isthmus",
"The cruise took prizes at San Blas, Sonsonate and El Realejo, and the reports coming "
"back are less about the prizes than about what the shore parties found: a captaincy "
"general governed by perhaps four hundred Spaniards, no garrison worth the name, and "
"creoles who asked the boat crews when the ships were coming back. A commission or "
"two and some powder landed in the right bay would do more damage to Spain in the "
"Americas than another year off Peru.",
{"EVTOPTA9103011": "Land the powder. Let them find out they can.",
 "EVTOPTB9103011": "We have no business there and no ships to spare."})

# --- 1828: Britain mediates Uruguay into existence ----------------------------------------
ev(9103020, """country_event = {
    id = 9103020
    title = "EVTNAME9103020"
    desc = "EVTDESC9103020"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        OR = { tag = RDP tag = ARG }
        year = 1828
        NOT = { year = 1840 }
        owns = 2344
        NOT = { exists = URU }
    }
    mean_time_to_happen = { months = 10 }

    option = {
        name = "EVTOPTA9103020"
        set_global_flag = h18p_banda_oriental_lost
        URU = {
            all_core = { secede_province = THIS }
            add_country_modifier = { name = the_union_preserved duration = 3650 }
        }
        2344 = { remove_core = THIS }
        ENG = { relation = { who = THIS value = 50 } }
        prestige = -10
        any_pop = { limit = { has_pop_culture = criollo } militancy = 4 }
        ai_chance = { factor = 70 }
    }
    option = {
        name = "EVTOPTB9103020"
        set_country_flag = h18p_defied_london
        add_country_modifier = { name = the_unitarian_quarrel duration = -1 }
        ENG = { relation = { who = THIS value = -90 } }
        prestige = 10
        war_exhaustion = 15
        any_pop = { militancy = 5 }
        ai_chance = { factor = 30 }
    }
}
""", "London Will Have a Buffer",
"Three years of war with Brazil over the Banda Oriental and neither side can finish "
"it, which suits the third party at the table exactly. Britain does not want Buenos "
"Aires holding both banks of the estuary and does not want Rio holding them either; "
"what it wants is a small state in between that can be relied upon to let everybody's "
"shipping through. Lord Ponsonby has put it to both governments in terms that are "
"polite and not negotiable, and the Royal Navy is the reason they are not negotiable.",
{"EVTOPTA9103020": "Let there be a Uruguay. We have no fleet to argue with.",
 "EVTOPTB9103020": "The Banda Oriental is a province of these United Provinces."})

# --- the unitarian quarrel ----------------------------------------------------------------
ev(9103021, """country_event = {
    id = 9103021
    title = "EVTNAME9103021"
    desc = "EVTDESC9103021"
    picture = "administration"

    trigger = {
        OR = { tag = RDP tag = ARG }
        has_country_flag = h18p_centralist
        year = 1820
        NOT = { year = 1862 }
        NOT = { has_country_flag = h18p_quarrel_settled }
    }
    mean_time_to_happen = { months = 60 }

    option = {
        name = "EVTOPTA9103021"
        set_country_flag = h18p_quarrel_settled
        political_reform = federalism
        remove_country_modifier = the_liga_federal
        add_country_modifier = { name = the_union_preserved duration = -1 }
        any_pop = { militancy = -4 }
        prestige = 5
        ai_chance = { factor = 45 }
    }
    option = {
        name = "EVTOPTB9103021"
        add_country_modifier = { name = the_unitarian_quarrel duration = 3650 }
        any_pop = { limit = { has_pop_culture = criollo } militancy = 5 consciousness = 3 }
        ai_chance = { factor = 55 }
    }
}
""", "Unitarios and Federales",
"It has been going on since Tucuman and it is not an argument about theory. The port "
"collects the customs revenue of the whole country and spends it on the port; the "
"provinces want it shared and a constitution that says so; and every few years "
"somebody shoots a governor over it. Dorrego has just been shot. The question is "
"whether this is settled by conceding the federation that fourteen provinces have been "
"demanding for twelve years, or by whoever has the most cavalry.",
{"EVTOPTA9103021": "Concede the federation. The country is worth more than the customs house.",
 "EVTOPTB9103021": "The country is governed from Buenos Aires or it is not governed."})

wr(f"{MOD}/events/1800_La_Plata.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_La_Plata.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/40_la_plata.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
# Argentina did not call itself Argentina until 1860. The country that declared at
# Tucuman and fought the war was the United Provinces of the Rio de la Plata.
extra = [("ARG", "United Provinces of the Rio de la Plata"),
         ("ARG_ADJ", "Rioplatense"),
         ("ARG_absolute_monarchy", "United Provinces of the Rio de la Plata"),
         ("ARG_presidential_dictatorship", "United Provinces of the Rio de la Plata"),
         ("ARG_prussian_constitutionalism", "United Provinces of the Rio de la Plata")]
wr(f"{MOD}/localisation/41_united_provinces.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in extra) + "\n")
log["the United Provinces named"] = len(extra)
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
