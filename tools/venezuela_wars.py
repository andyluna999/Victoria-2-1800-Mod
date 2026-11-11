"""Venezuela, 1806 to 1823: two republics that fell, and the one that did not.

Written from an account by a Venezuelan player, which is far better sourced than
anything I would have assembled, and whose central point reshapes the whole chain:

**Venezuela was divided from the first day.** When Emparan was deposed on the
nineteenth of April 1810 and the Supreme Junta took Caracas, Maracaibo, Coro and
Guayana did not follow -- they declared for the Regency and stayed royalist. The
declaration of the fifth of July 1811 was made by seven provinces and not by a
country. Modelling this as "Venezuela rises" gets the war wrong at the start, because
the royalist bases that destroyed the first two republics were inside Venezuela the
whole time.

The sequence:

  **1806.** Miranda sails twice, funded in part by Rufus King, a Federalist senator
  whose government did not know. The first attempt fails at Ocumare, the second lands
  and is pushed back.

  **1810-12.** The junta, then the declaration by seven provinces, then Puerto Cabello
  betrayed and the capitulation at San Mateo. The First Republic lasts a year.

  **1813-14.** The Admirable Campaign retakes the west; Marino retakes the north-east.
  What this produces is two republics, not one -- Caracas in the west and Cumana in
  the east, separate armies and separate governments, nominally the same state. Then
  Boves, whose llanero cavalry destroyed both, and who died at Urica, by Zaraza's
  lance if the story is true.

  **1816-19.** The east again, San Felix, Angostura taken. In 1818 the llaneros change
  sides under Paez, which is the hinge of the whole war. In 1819 Bolivar crosses into
  New Granada and the Republic of Colombia is proclaimed at Angostura -- with most of
  Venezuela still Spanish.

  **1821-23.** Carabobo, with the British Legion in the line. Then Maracaibo and
  Puerto Cabello hold out another two years, and the war ends on the lake.
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

CARACAS, MARACAIBO, CORO, ANGOSTURA, CUMANA = 2264, 2270, 2272, 2275, 2267
# The seven that signed, as best the map allows: Caracas, Cumana, Barcelona,
# Margarita, Barinas, Merida and Trujillo.
PATRIOT = [CARACAS, CUMANA, 2274, 2271, 2273, 2268, 2269, 2265, 2266]

# The plains. Boves raised them in 1813 and they were never patriot again until Paez
# brought them over in 1818, so the Second Republic held materially less country than
# the First -- Barinas and the llanos were gone before it started. The reporter's
# second point, and it is the reason the Second Republic was weaker than the map
# suggests.
LLANOS = [2274, 2265, 2266]
# the three that declared for the Regency and never stopped
ROYALIST = [MARACAIBO, CORO, ANGOSTURA, 2276, 2277, 2278]

MODS = """
the_first_republic = {
\ticon = 2
\tcore_pop_consciousness_modifier = 2.0
\tland_organisation = -0.2
\tmobilisation_size = 0.08
}

the_plains_are_against_us = {
\ticon = 1
\tmobilisation_size = -0.12
\tsupply_consumption = 0.2
\tland_defense_modifier = -0.15
\tcore_pop_militancy_modifier = 1.0
}

the_two_republics = {
\ticon = 1
\tland_organisation = -0.25
\torg_regain = -0.2
\tadministrative_efficiency_modifier = -0.25
\tcore_pop_consciousness_modifier = 1.5
}

the_legions_of_hell = {
\ticon = 1
\tland_attack_modifier = 0.4
\tmobilisation_size = 0.2
\tmovement_cost = -0.25
\tcore_pop_militancy_modifier = 2.0
}

the_llaneros_turn = {
\ticon = 2
\tland_attack_modifier = 0.25
\tmobilisation_size = 0.15
\tmovement_cost = -0.2
\torg_regain = 0.2
}

the_british_legion = {
\ticon = 2
\tland_organisation = 0.2
\tland_attack_modifier = 0.15
\torg_regain = 0.15
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "\nthe_first_republic = {" not in src:
    wr(f"{MOD}/common/event_modifiers.txt", src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 5

def ev(eid, body, title, desc, opts):
    EV.append(body); loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    for k, v in opts.items(): loc(k, v)
    log["events"] += 1

# --- 1806: Miranda ------------------------------------------------------------------------
ev(9103400, """country_event = {
    id = 9103400
    title = "EVTNAME9103400"
    desc = "EVTDESC9103400"
    picture = "1819_bolivar"
    fire_only_once = yes

    trigger = {
        tag = VNZ
        year = 1806
        NOT = { year = 1810 }
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9103400"
        set_country_flag = h18v_miranda_came
        change_variable = { which = separatism value = 8 }
        prestige = -3
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 2 }
        USA = { relation = { who = THIS value = -25 } }
    }
}
""", "Miranda Lands at Coro",
"He has been trying to do this for twenty years and has finally found somebody to pay "
"for it -- a Federalist senator in New York, acting without his government and "
"possibly against it. The first attempt failed at Ocumare when the ships were "
"intercepted. This one got ashore at Coro, raised a flag nobody recognised, and "
"discovered that the people he had come to liberate had been told he was a French "
"agent and a heretic, and believed it. He has re-embarked. He will be back.",
{"EVTOPTA9103400": "He had no following here. That may not last."})

# --- 1810: the nineteenth of April, and the three provinces that refused ---------------------
ev(9103401, f"""country_event = {{
    id = 9103401
    title = "EVTNAME9103401"
    desc = "EVTDESC9103401"
    picture = "1808_iturrigaray"
    fire_only_once = yes

    trigger = {{
        tag = VNZ
        has_country_flag = h18c_bayonne_known
        year = 1810
        NOT = {{ year = 1815 }}
    }}
    mean_time_to_happen = {{ months = 4 }}

    option = {{
        name = "EVTOPTA9103401"
        set_country_flag = h18v_junta_of_caracas
        add_country_modifier = {{ name = the_first_republic duration = -1 }}
        change_variable = {{ which = separatism value = 20 }}
        remove_country_modifier = colonial_trade_monopoly
{"".join(f"        {p} = {{ add_core = CLM }}" + chr(10) for p in PATRIOT)}        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -3 consciousness = 4 }}
        ai_chance = {{ factor = 70 }}
    }}
    option = {{
        name = "EVTOPTB9103401"
        change_variable = {{ which = separatism value = 10 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 5 }}
        ai_chance = {{ factor = 30 }}
    }}
}}
""", "The Nineteenth of April",
"The cabildo of Caracas has deposed Vicente Emparan, who asked the crowd in the plaza "
"whether they wanted him to continue and was answered by a priest standing behind him "
"shaking his head. He resigned on the spot. The Supreme Junta governs in Ferdinand's "
"name, which is the formula everywhere this year. What is not the formula is the "
"reply from Maracaibo, Coro and Guayana, which have declared for the Regency at Cadiz "
"and will take orders from Caracas on no account whatever. This captaincy is now "
"three governments and one of them is ours.",
{"EVTOPTA9103401": "The Junta governs. The west and Guayana can be dealt with later.",
 "EVTOPTB9103401": "Emparan stays. The plaza can be cleared."})

# --- 1811: seven provinces, not a country ----------------------------------------------------
ev(9103402, """country_event = {
    id = 9103402
    title = "EVTNAME9103402"
    desc = "EVTDESC9103402"
    picture = "1812_cadiz_constitution"
    fire_only_once = yes

    trigger = {
        tag = VNZ
        has_country_flag = h18v_junta_of_caracas
        year = 1811
        NOT = { year = 1816 }
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9103402"
        set_country_flag = h18v_declared
        set_country_flag = h18c_independent
        government = presidential_dictatorship
        vote_franschise = landed_voting
        change_variable = { which = separatism value = 15 }
        prestige = 10
        SPA = { relation = { who = THIS value = -120 } }
        any_pop = { limit = { has_pop_culture = criollo } militancy = -4 consciousness = 5 }
        any_pop = { limit = { has_pop_culture = spanish } militancy = 6 }
    }
}
""", "The Fifth of July",
"Seven provinces have signed: Caracas, Cumana, Barcelona, Margarita, Barinas, Merida "
"and Trujillo. Maracaibo, Coro and Guayana have not, and the men who drafted the "
"document know perfectly well that a third of the country they have just declared "
"independent is garrisoned against them. It is the first such declaration anywhere in "
"Spanish America and it is made by a congress that does not control the coast it "
"would need to defend it.",
{"EVTOPTA9103402": "Seven provinces, then. It will have to be enough."})

# --- 1812: San Mateo ---------------------------------------------------------------------------
ev(9103403, f"""country_event = {{
    id = 9103403
    title = "EVTNAME9103403"
    desc = "EVTDESC9103403"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = VNZ
        has_country_flag = h18v_declared
        year = 1812
        NOT = {{ year = 1817 }}
    }}
    mean_time_to_happen = {{ months = 7 }}

    option = {{
        name = "EVTOPTA9103403"
        set_country_flag = h18v_first_republic_fell
        clr_country_flag = h18c_independent
        remove_country_modifier = the_first_republic
        government = absolute_monarchy
        prestige = -20
        change_variable = {{ which = separatism value = -10 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 7 consciousness = 2 }}
        ai_chance = {{ factor = 75 }}
    }}
    option = {{
        name = "EVTOPTB9103403"
        set_country_flag = h18v_held_at_san_mateo
        war_exhaustion = 15
        prestige = 10
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -3 }}
        ai_chance = {{ factor = 25 }}
    }}
}}
""", "The Capitulation of San Mateo",
"An earthquake levelled the patriot cities in March and spared the royalist ones, "
"which the clergy have explained at length and to great effect. Then Puerto Cabello "
"was handed over by the officer holding it -- Bolivar, as it happens -- when the "
"prisoners in the magazine broke out and turned the guns on the town. Miranda has "
"signed a capitulation at San Mateo, and the men who made him dictator four months "
"ago have decided that this is treason and handed him to the Spanish.",
{"EVTOPTA9103403": "It is over. The Republic lasted a year.",
 "EVTOPTB9103403": "The line holds at San Mateo."})

# --- 1813-14: two republics, and Boves -----------------------------------------------------------
ev(9103404, """country_event = {
    id = 9103404
    title = "EVTNAME9103404"
    desc = "EVTDESC9103404"
    picture = "1819_bolivar"
    fire_only_once = yes

    trigger = {
        tag = VNZ
        has_country_flag = h18v_first_republic_fell
        year = 1813
        NOT = { year = 1818 }
    }
    mean_time_to_happen = { months = 6 }

    option = {
        name = "EVTOPTA9103404"
        set_country_flag = h18v_second_republic
        set_country_flag = h18c_independent
        set_country_flag = h18v_llanos_lost
        add_country_modifier = { name = the_two_republics duration = -1 }
        add_country_modifier = { name = the_plains_are_against_us duration = -1 }
        government = presidential_dictatorship
        change_variable = { which = separatism value = 20 }
        prestige = 12
        any_pop = { limit = { has_pop_culture = criollo } militancy = -4 consciousness = 3 }
    }
}
""", "The Admirable Campaign",
"Bolivar has come down from New Granada and taken the west in three months, issuing a "
"decree at Trujillo promising death to any Spaniard who does not actively assist the "
"cause -- war to the death, in those words, and meant. Marino has taken the "
"north-east independently and shows no inclination to take orders from Caracas. What "
"exists now is two republics calling themselves one: Caracas in the west, Cumana in "
"the east, two armies, two governments, and no agreement on which of them is the "
"country.",
{"EVTOPTA9103404": "Two republics, then, and we will call them one."})

ev(9103405, f"""country_event = {{
    id = 9103405
    title = "EVTNAME9103405"
    desc = "EVTDESC9103405"
    picture = "ambush_army"
    fire_only_once = yes

    trigger = {{
        tag = VNZ
        has_country_flag = h18v_second_republic
        year = 1814
        NOT = {{ year = 1819 }}
    }}
    mean_time_to_happen = {{ months = 6 }}

    option = {{
        name = "EVTOPTA9103405"
        set_country_flag = h18v_boves
        clr_country_flag = h18c_independent
        remove_country_modifier = the_two_republics
        government = absolute_monarchy
        prestige = -25
        change_variable = {{ which = separatism value = -5 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 8 }}
        ai_chance = {{ factor = 80 }}
    }}
    option = {{
        name = "EVTOPTB9103405"
        set_country_flag = h18v_boves_beaten
        add_country_modifier = {{ name = the_llaneros_turn duration = -1 }}
        prestige = 20
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -5 }}
        ai_chance = {{ factor = 20 }}
    }}
}}
""", "The Legions of Hell",
"Boves is an Asturian shopkeeper who was jailed by the patriots and has raised the "
"plains against them, and the plainsmen have come because he lets them keep what they "
"take and because the republic in Caracas is a lawyers' republic that never offered "
"them anything. He has perhaps eight thousand horse. He does not take prisoners, he "
"moves faster than anything that can be sent after him, and he is a better general "
"than anyone the republic has. The whole of the centre has gone.",
{"EVTOPTA9103405": "Both republics are falling. The roads east are full of refugees.",
 "EVTOPTB9103405": "He is unhorsed at Urica, on Zaraza's lance if the story is true."})

# --- 1817-19: Angostura, the llaneros, and the Republic of Colombia ----------------------------
ev(9103406, f"""country_event = {{
    id = 9103406
    title = "EVTNAME9103406"
    desc = "EVTDESC9103406"
    picture = "1819_bolivar"
    fire_only_once = yes

    trigger = {{
        tag = VNZ
        has_country_flag = h18v_boves
        year = 1817
        NOT = {{ year = 1823 }}
    }}
    mean_time_to_happen = {{ months = 8 }}

    option = {{
        name = "EVTOPTA9103406"
        set_country_flag = h18v_angostura
        set_country_flag = h18c_independent
        # the plains stop being the enemy's and become ours
        clr_country_flag = h18v_llanos_lost
        remove_country_modifier = the_plains_are_against_us
        add_country_modifier = {{ name = the_llaneros_turn duration = -1 }}
        government = presidential_dictatorship
        capital = {ANGOSTURA}
        change_variable = {{ which = separatism value = 25 }}
        prestige = 15
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -4 consciousness = 4 }}
        any_pop = {{ limit = {{ has_pop_culture = mestizo }} militancy = -3 consciousness = 3 }}
    }}
}}
""", "San Felix, and the Plains Change Sides",
"The Guayana campaign has taken Angostura, which is on a river the Royal Navy cannot "
"reach and far enough from Caracas to be defensible, and the government has been "
"established there. More important than the town: Paez has brought the llaneros over. "
"The same horsemen who destroyed the second republic under Boves are now the best "
"cavalry the patriots have, for the same reason they fought for him -- somebody has "
"finally offered them the herds.",
{"EVTOPTA9103406": "Angostura, and the plains with us."})

ev(9103407, """country_event = {
    id = 9103407
    title = "EVTNAME9103407"
    desc = "EVTDESC9103407"
    picture = "map_of_colombia"
    fire_only_once = yes

    trigger = {
        OR = { tag = VNZ tag = GCO }
        has_country_flag = h18v_angostura
        year = 1821
        NOT = { year = 1828 }
    }
    mean_time_to_happen = { months = 7 }

    option = {
        name = "EVTOPTA9103407"
        set_country_flag = h18v_carabobo
        add_country_modifier = { name = the_british_legion duration = 1825 }
        prestige = 25
        SPA = { prestige = -15 war_exhaustion = 10 }
        any_pop = { militancy = -4 }
    }
}
""", "Carabobo",
"The British Legion held the ridge while the llaneros came round the flank, and the "
"Spanish line went in an hour. They are volunteers, veterans of the Peninsula with "
"nothing to do since Waterloo, recruited in London on promises the republic cannot "
"keep, and today they stood in square and took the fire that made the manoeuvre "
"possible. Caracas is open. What remains is Puerto Cabello and Maracaibo, and those "
"will take rather longer.",
{"EVTOPTA9103407": "Caracas is open."})

ev(9103408, f"""country_event = {{
    id = 9103408
    title = "EVTNAME9103408"
    desc = "EVTDESC9103408"
    picture = "crimean_war_ships"
    fire_only_once = yes

    trigger = {{
        OR = {{ tag = VNZ tag = GCO }}
        has_country_flag = h18v_carabobo
        year = 1823
        NOT = {{ year = 1830 }}
    }}
    mean_time_to_happen = {{ months = 8 }}

    option = {{
        name = "EVTOPTA9103408"
        set_country_flag = h18v_the_war_is_over
        set_country_flag = h18c_independence_won
{"".join(f"        {p} = {{ secede_province = THIS add_core = THIS }}" + chr(10) for p in ROYALIST)}        prestige = 20
        SPA = {{ prestige = -20 }}
        any_pop = {{ militancy = -5 consciousness = 2 }}
    }}
}}
""", "The Lake",
"Laborde's squadron was the last Spanish force in the country and it was beaten on "
"Lake Maracaibo by a fleet of schooners and gunboats that had no business winning. "
"Puerto Cabello fell in November to an assault across the shallows at night. Thirteen "
"years after the nineteenth of April there is no Spanish soldier left in Venezuela, "
"and Maracaibo -- which declared for the Regency in 1810 and never once wavered -- is "
"part of a republic whose capital is a river town in Guayana.",
{"EVTOPTA9103408": "There is no Spanish soldier left in Venezuela."})

wr(f"{MOD}/events/1800_Venezuela_Wars.txt", "\n".join(EV))
wr(f"{MOD}/localisation/46_venezuela.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
