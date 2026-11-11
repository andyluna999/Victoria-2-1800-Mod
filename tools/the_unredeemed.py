"""A republic that wins its freedom still wants its country.

The wars of independence are fought for `status_quo` -- to be let go -- because a
defender goal applies against the war leader and anything acquisitive there made the
republics try to annex Spain. But winning the right to exist is not the same as
holding the country, and every one of these republics spent the decades afterwards
trying to make its map match its claim.

Mexico is born in the Bajio with cores on a hundred and four provinces. Colombia is
born in Cundinamarca with Cartagena, Panama and Quito outside it. Argentina holds the
littoral and claims Upper Peru, Paraguay and the Banda Oriental, and spent the 1810s
and 1820s failing to take any of them.

So once a republic is independent and short of its cores it gets the same instrument
Victoria II gives the United States for Manifest Destiny: the exclusive
`acquire_all_cores` casus belli, which costs no infamy at all, plus a standing
modifier that makes the recovery the national project. The claim is not a grievance
and not a grudge -- it is the official map, taught in the schools, and no government
there could survive abandoning it.
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

MODS = """
the_unredeemed_provinces = {
\ticon = 4
\tcore_pop_consciousness_modifier = 1.0
\tmobilisation_size = 0.05
\tland_attack_modifier = 0.1
\tprestige = -0.2
\tdiplomatic_points_modifier = 0.15
}

the_map_is_the_country = {
\ticon = 8
\tcore_pop_militancy_modifier = -1.0
\tglobal_assimilation_rate = 0.3
\tprestige = 0.5
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_unredeemed_provinces" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 2

REPUBLICS = {
 "MEX": ("Mexico", "the provinces of the north and the Isthmus"),
 "PEU": ("Peru", "Upper Peru and the Guayaquil coast"),
 "CLM": ("Colombia", "Cartagena, Panama and Quito"),
 "ARG": ("Argentina", "Upper Peru, Paraguay and the Banda Oriental"),
 "CHL": ("Chile", "the south and the Araucania"),
 "TEX": ("Texas", "the country between the Nueces and the Rio Grande"),
}

for n, (tag, (name, what)) in enumerate(REPUBLICS.items()):
    eid = 9102700 + n * 2
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "map_of_colombia"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        OR = {{
            has_country_flag = h18c_independence_won
            has_country_flag = h18c_independent
            has_country_flag = h18c_viceroyalty_fallen
        }}
        any_core = {{ NOT = {{ owned_by = THIS }} }}
    }}
    mean_time_to_happen = {{ months = 10 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_country_flag = h18c_the_claim_stands
        set_country_flag = exclusive_acquire_all_cores_CB
        set_country_flag = h18c_reclaim_cb
        add_country_modifier = {{ name = the_unredeemed_provinces duration = -1 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 2 }}
        prestige = 5
        ai_chance = {{ factor = 85 }}
    }}
    option = {{
        name = "EVTOPTB{eid}"
        set_country_flag = h18c_the_claim_abandoned
        add_country_modifier = {{ name = the_map_is_the_country duration = -1 }}
        prestige = -10
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 3 }}
        ai_chance = {{ factor = 15 }}
    }}
}}

country_event = {{
    id = {eid + 1}
    title = "EVTNAME{eid + 1}"
    desc = "EVTDESC{eid + 1}"
    picture = "map_of_colombia"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        has_country_flag = h18c_the_claim_stands
        NOT = {{ any_core = {{ NOT = {{ owned_by = THIS }} }} }}
    }}
    mean_time_to_happen = {{ months = 6 }}

    option = {{
        name = "EVTOPTA{eid + 1}"
        clr_country_flag = exclusive_acquire_all_cores_CB
        remove_country_modifier = the_unredeemed_provinces
        add_country_modifier = {{ name = the_map_is_the_country duration = -1 }}
        prestige = 25
        any_pop = {{ militancy = -3 consciousness = 1 }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", "The Provinces Not Yet Ours")
    loc(f"EVTDESC{eid}",
        f"The republic exists and is a third of the country the schools teach. {what.capitalize()} "
        "are on every map printed here, in the same colour as the capital, and are "
        "governed by somebody else. No minister can propose giving them up and "
        "survive the week, and no minister has the army to take them either. So the "
        "claim stands, on paper, for as long as it takes -- which is how these things "
        "are done everywhere and how they poison a border for a century.")
    loc(f"EVTOPTA{eid}", "The map is not negotiable.")
    loc(f"EVTOPTB{eid}", "We will govern what we hold.")
    loc(f"EVTNAME{eid + 1}", "The Map and the Country Agree")
    loc(f"EVTDESC{eid + 1}",
        "Every province the schools taught as ours is ours, and the generation that "
        "grew up on that map has lived to see it true. It is a rarer thing than anyone "
        "here appreciates: most countries that make such a claim are still making it a "
        "century later.")
    loc(f"EVTOPTA{eid + 1}", "The country is whole.")
    log["republics given the claim"] += 1

wr(f"{MOD}/events/1800_Unredeemed.txt", "\n".join(EV))
LOC.append(("RECLAIM_REPUBLIC_NAME", "$DEFENDER_ADJ$ Reclamation"))
wr(f"{MOD}/localisation/35_unredeemed.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<30}{v}")
