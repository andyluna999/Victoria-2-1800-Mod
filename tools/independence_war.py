"""How a war of independence is actually won.

The playtest reached the right crisis and had no way out of it: New Spain beat Mexico,
declared for itself, and then found there was no mechanism by which Spain would ever
stop. The run ended in a console command. Four things were missing.

**The rebels were fighting for nothing.** Their war goal was `status_quo`, which means
survive. A war of independence is fought to take the viceroyalty, and Mexico holds
cores on all of it, so the goal is `annex_core_country`. Until now even total victory
changed nothing on the map.

**Madrid was not in the war.** The republic fought the viceroyalty alone, while every
one of these wars was against Spain -- the viceroyalty was an administration, not a
belligerent. `call_ally = yes` pulls the overlord in, which is what overlords are for.

**The viceroyalty could not fall.** Take Mexico City and the viceregal government
should cease to exist, its territory passing to the republic, with Spain fighting on
from overseas against a country it refuses to recognise. That is exactly what happened
between 1821 and 1836: fifteen years of formal war with nobody left to fight it.

**And Spain never gave up.** Victoria II does not expose war score to a trigger, so
commitment is measured by the thing that actually matters -- how much of the republic's
territory Spain is holding. A Spain that has landed nothing quits in four years, which
is Riego's mutiny. A Spain that has retaken three quarters of Mexico stays fifteen.
Between those the cliff is deliberate: Madrid digs in only when it is close.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

# viceroyalty -> (successor, the places it must take to have won, what to call it)
# None of these may be a province the republic is born holding.
SUCC = {
 "NSP": ("MEX", [2172, 2159], "Mexico City"),      # the capital and Veracruz
 "VPE": ("PEU", [2295, 2300], "Lima"),             # Lima and the coast
 "VNG": ("CLM", [2251, 1723], "Cartagena"),        # the port and Panama
 "RDP": ("ARG", [2344, 2343], "Montevideo"),       # Montevideo and the Paraguay
 "CGC": ("CHL", [2328, 2329], "Valdivia"),         # Valdivia and Temuco, which stayed royal
}

MODS = """
the_long_war_in_the_americas = {
\ticon = 1
\twar_exhaustion = 1.5
\ttax_efficiency = -0.15
\tcore_pop_militancy_modifier = 1.5
\tmobilisation_economy_impact = 0.3
\tprestige = -0.5
}

the_long_insurgency = {
\ticon = 2
\tland_defense_modifier = 0.4
\torg_regain = 0.3
\tmobilisation_size = 0.15
\twar_exhaustion = -1.0
\tsupply_consumption = -0.3
\tcore_pop_militancy_modifier = -1.5
}

the_war_against_our_own = {
\ticon = 1
\twar_exhaustion = 1.5
\tland_organisation = -0.15
\torg_regain = -0.2
\ttax_efficiency = -0.2
\tmobilisation_economy_impact = 0.4
\tcore_pop_militancy_modifier = 1.5
}

the_republic_victorious = {
\ticon = 8
\tprestige = 1.0
\tcore_pop_militancy_modifier = -2.0
\tglobal_immigrant_attract = 0.3
\ttax_efficiency = 0.1
}

the_viceroyalty_has_fallen = {
\ticon = 1
\tcore_pop_militancy_modifier = 2.0
\tprestige = -1.0
\tdiplomatic_points_modifier = -0.2
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_long_war_in_the_americas" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

# --- Spain bleeds for every year of it --------------------------------------------
EV.append("""country_event = {
    id = 9102100
    title = "EVTNAME9102100"
    desc = "EVTDESC9102100"
    picture = "administration"

    trigger = {
        tag = SPA
        has_global_flag = h18_spanish_america_in_arms
        NOT = { has_country_modifier = the_long_war_in_the_americas }
        OR = {
            war_with = MEX
            war_with = PEU
            war_with = CLM
            war_with = ARG
            war_with = CHL
        }
    }
    mean_time_to_happen = { months = 10 }

    option = {
        name = "EVTOPTA9102100"
        add_country_modifier = { name = the_long_war_in_the_americas duration = 1460 }
        treasury = -12000
        prestige = -5
        any_pop = { limit = { has_pop_culture = spanish } militancy = 1 consciousness = 1 }
    }
}
""")
loc("EVTNAME9102100", "The Cost of the Americas")
loc("EVTDESC9102100",
    "Every regiment sent across the Atlantic has to be raised, paid, shipped and fed, "
    "and a third of them die of fever before they see an insurgent. The silver that "
    "used to come the other way has stopped, because the mines are in the hands of the "
    "people we are fighting. The Cortes has begun asking what the Americas are worth, "
    "which is a question no minister wants debated in public.")
loc("EVTOPTA9102100", "They are worth whatever they cost.")
log["events"] += 1

# --- the viceroyalty falls --------------------------------------------------------
for vic, (suc, caps, capname) in SUCC.items():
    eid = 9102110 + list(SUCC).index(vic)
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {suc}
        exists = {vic}
        war_with = {vic}
{"".join(f"        {c} = {{ controlled_by = THIS }}" + chr(10) for c in caps)}    }}
    mean_time_to_happen = {{ months = 10 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_country_flag = h18c_viceroyalty_fallen
        {vic} = {{
            country_event = {eid + 10}
            all_core = {{ remove_core = {vic} }}
        }}
        prestige = 25
        any_pop = {{ militancy = -4 consciousness = 2 }}
    }}
}}

country_event = {{
    id = {eid + 10}
    title = "EVTNAME{eid + 10}"
    desc = "EVTDESC{eid + 10}"
    picture = "administration"
    is_triggered_only = yes

    option = {{
        name = "EVTOPTA{eid + 10}"
        add_country_modifier = {{ name = the_viceroyalty_has_fallen duration = -1 }}
        annex_to = {suc}
    }}
}}
""")
    loc(f"EVTNAME{eid}", f"{capname} Has Fallen")
    loc(f"EVTDESC{eid}",
        "The audiencia has dispersed, the viceroy is on a ship or in a cell, and the "
        "machinery that governed this kingdom for three centuries has simply stopped. "
        "There is nothing left to negotiate with. Spain has not conceded anything and "
        "will not for a long time -- but there is no longer a royal government here to "
        "concede it to, and the war from this point is against an ocean.")
    loc(f"EVTOPTA{eid}", "The kingdom is ours. Madrid remains.")
    loc(f"EVTNAME{eid + 10}", "The Government Dissolves")
    loc(f"EVTDESC{eid + 10}",
        "No order was given and none was needed. The clerks stopped coming, the "
        "treasury was found to be empty, and the men who held commissions from the "
        "King discovered they held nothing at all.")
    loc(f"EVTOPTA{eid + 10}", "It is finished.")
    log["events"] += 2

# --- Spain gives up, on a clock set by how well it is doing -------------------------
TIERS = [
    (9102130, 4, "        NOT = { any_owned_province = { controlled_by = SPA } }\n",
     "Nothing Has Been Retaken",
     "Four years, three expeditions and a fleet, and the flag does not fly over one "
     "square mile of the mainland that it did not fly over at the start. The soldiers "
     "who sailed are dead of fever or deserted into the country they were sent to "
     "subdue. There is no army at Cadiz that will embark and no money to pay one if "
     "there were."),
    (9102131, 6, "        any_owned_province = { controlled_by = SPA }\n",
     "A Foothold and Nothing More",
     "Six years, and the King's writ runs in the ports and nowhere behind them. Every "
     "column sent inland comes back smaller or does not come back. The generals write "
     "that with twenty thousand more men the thing could be finished, which is what "
     "they wrote before the last twenty thousand."),
    (9102132, 8, "        any_owned_province = { controlled_by = SPA }\n"
                 "        war_exhaustion = 25\n",
     "Half a Kingdom, and the Cost of It",
     "Eight years. Half the country is held and the other half cannot be reached, and "
     "holding what we have costs more each year than the whole viceroyalty ever "
     "remitted. The Cortes has voted the money twice and will not vote it again."),
    # And the backstop. A Spain holding three quarters of the country has a real
    # argument for staying, so it stays -- but fifteen years is the outer limit of
    # what any government can spend on a war it is not finishing, and the period has
    # to end whatever happened in it.
    (9102133, 15, "",
     "Fifteen Years",
     "Fifteen years. Two kings, three constitutions, a French occupation and a mutiny "
     "at Cadiz, and the Americas are still not pacified. The men who voted the first "
     "expedition are dead or in exile. Nobody in this room believes any longer that "
     "the thing can be finished, and nobody is willing to be the minister who says so "
     "first, so it will be settled by simply ceasing to pay for it."),
]
for eid, yrs, cond, title, desc in TIERS:
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = SPA
        has_country_modifier = the_long_war_in_the_americas
        war_exhaustion = {10 + yrs * 2}
        # a floor, not an average: Madrid does not give up the Americas in three years
        year = {1814 + yrs}
{cond}    }}
    mean_time_to_happen = {{ months = {yrs * 12} }}

    option = {{
        name = "EVTOPTA{eid}"
        set_global_flag = h18_madrid_gives_up
        prestige = -25
        badboy = -5
        any_country = {{
            limit = {{ has_country_flag = h18c_viceroyalty_fallen }}
            country_event = 9102140
        }}
        any_country = {{
            limit = {{ has_country_flag = h18c_independent }}
            country_event = 9102140
        }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    loc(f"EVTOPTA{eid}", "Let them go.")
    log["events"] += 1

EV.append("""country_event = {
    id = 9102140
    title = "EVTNAME9102140"
    desc = "EVTDESC9102140"
    picture = "administration"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9102140"
        set_country_flag = h18c_independence_won
        add_country_modifier = { name = the_republic_victorious duration = -1 }
        end_war = SPA
        prestige = 40
        any_pop = { militancy = -6 consciousness = 3 }
        SPA = { relation = { who = THIS value = 20 } }
    }
}
""")
loc("EVTNAME9102140", "Spain Lets Go")
loc("EVTDESC9102140",
    "No treaty, no ceremony and no apology: the expeditions simply stop coming. "
    "Recognition will take another decade and will arrive as a formality long after "
    "everyone has stopped waiting for it. What ends today is the possibility that "
    "somebody will arrive from across the Atlantic and take this country back.")
loc("EVTOPTA9102140", "Nobody is coming. We are a country.")
log["events"] += 1

wr(f"{MOD}/events/1800_Independence_War.txt", "\n".join(EV))
wr(f"{MOD}/localisation/28_independence_war.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<22}{v}")
