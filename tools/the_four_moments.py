"""The junta, the rupture and the crown: four questions that arrive.

These are the last four that sat in the decisions tab pretending to be policy. A
viceroy did not select "proclaim a junta" from a list at a time of his choosing -- the
King was taken, the cabildo abierto convened itself whether he liked it or not, and
the question was put to him in a room full of men who had already decided. Nor did
anyone choose to "renounce the authority of Madrid" on a quiet Tuesday: the rupture
came when the alternative ran out.

So each arrives at its hour, in the words the moment actually used, and each carries
exactly the flags its decision carried -- `h18c_junta_governs` is read nineteen times
and `h18c_independent` thirty-four, so the chains downstream never notice the change.

Every viceroyalty gets its own, because they are not the same question. Buenos Aires
deposed its viceroy in a week and never restored him. Lima never deposed anybody and
had to be invaded twice before it would separate. Bogota and Santiago convened juntas
in the King's name and spent a decade arguing about what that meant. And New Spain's
junta ended at two in the morning with three hundred armed men in the palace.

**Waiting is always an option**, and the question comes back. That is the one thing a
decision did better than an event and it is worth keeping: a viceroy who is not ready
to answer should be able to not answer, and live with what that costs.
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

# tag, successor, the junta's own name, the kingdom road, the republic's name
V = [
 ("NSP", "MEX", "the Junta of New Spain", "the Plan of Iguala",
  "the Mexican Republic", "Mexico City"),
 ("VPE", "PEU", "the Junta of Lima", "the Protectorate",
  "the Peruvian Republic", "Lima"),
 ("VNG", "CLM", "the Supreme Junta of Santa Fe", "the Congress of Angostura",
  "the Republic of Colombia", "Bogota"),
 ("RDP", "ARG", "the Primera Junta", "the Congress of Tucuman",
  "the United Provinces", "Buenos Aires"),
 ("CGC", "CHL", "the Junta of Santiago", "the Declaration at Talca",
  "the Republic of Chile", "Santiago"),
]

for n, (vic, suc, junta, road, repub, cap) in enumerate(V):
    base = 9102920 + n * 4

    # --- the junta question -------------------------------------------------------------
    EV.append(f"""country_event = {{
    id = {base}
    title = "EVTNAME{base}"
    desc = "EVTDESC{base}"
    picture = "1808_iturrigaray"

    trigger = {{
        tag = {vic}
        has_country_flag = h18c_bayonne_known
        NOT = {{ has_country_flag = h18c_junta_governs }}
        NOT = {{ has_country_flag = h18c_independent }}
        NOT = {{ has_country_flag = h18c_junta_refused_twice }}
    }}
    mean_time_to_happen = {{ months = 7 }}

    option = {{
        name = "EVTOPTA{base}"
        set_country_flag = h18c_junta_governs
        add_country_modifier = {{ name = the_new_junta duration = 1095 }}
        change_variable = {{ which = separatism value = -15 }}
        remove_country_modifier = colonial_trade_monopoly
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -4 consciousness = 3 }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = 3 }}
        ai_chance = {{ factor = 60 }}
    }}
    option = {{
        name = "EVTOPTB{base}"
        set_country_flag = h18c_junta_deferred
        add_country_modifier = {{ name = the_loyal_kingdom duration = 1825 }}
        change_variable = {{ which = separatism value = 6 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 2 militancy = 2 }}
        SPA = {{ relation = {{ who = THIS value = 25 }} }}
        ai_chance = {{ factor = 40 }}
    }}
}}
""")
    loc(f"EVTNAME{base}", f"Who Shall Govern: {junta}")
    loc(f"EVTDESC{base}",
        f"The cabildo of {cap} has convened itself without being summoned and the "
        "room is full of men who have already worked out what they want to say. The "
        "argument is not for independence and nobody in it would admit to wanting "
        "any: it is that sovereignty reverts to the people when the King is taken, "
        "that this kingdom is not a possession of Spain but a realm of the same crown, "
        "and that a junta here is no more rebellious than the one sitting in Seville. "
        "Every word of that is good Spanish law and the peninsulars in the room know "
        "it, which is why they are so frightened.")
    loc(f"EVTOPTA{base}", f"Let {junta} sit, in the King's name.")
    loc(f"EVTOPTB{base}", "There is a government here already. It is mine.")
    log["moments"] += 1

    # --- the rupture ---------------------------------------------------------------------
    EV.append(f"""country_event = {{
    id = {base + 1}
    title = "EVTNAME{base + 1}"
    desc = "EVTDESC{base + 1}"
    picture = "administration"

    trigger = {{
        tag = {vic}
        has_country_flag = h18c_junta_governs
        NOT = {{ has_country_modifier = the_new_junta }}
        NOT = {{ has_country_flag = h18c_autonomous }}
        NOT = {{ has_country_flag = h18c_independent }}
        SPA = {{ war = yes }}
    }}
    mean_time_to_happen = {{ months = 20 }}

    option = {{
        name = "EVTOPTA{base + 1}"
        set_country_flag = h18c_autonomous
        add_country_modifier = {{ name = the_peninsular_officers_resign duration = 3650 }}
        change_variable = {{ which = separatism value = 10 }}
        government = prussian_constitutionalism
        vote_franschise = landed_voting
        prestige = 10
        SPA = {{ relation = {{ who = THIS value = -70 }} }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -3 consciousness = 4 }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = 5 }}
        ai_chance = {{ factor = 45 }}
    }}
    option = {{
        name = "EVTOPTB{base + 1}"
        change_variable = {{ which = separatism value = 5 }}
        SPA = {{ relation = {{ who = THIS value = 40 }} }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 3 }}
        ai_chance = {{ factor = 55 }}
    }}
}}
""")
    loc(f"EVTNAME{base + 1}", "The Authority of Madrid")
    loc(f"EVTDESC{base + 1}",
        "Three years of governing in the King's name, and the King is still a prisoner "
        "in a chateau in France while a committee in Cadiz issues orders to a kingdom "
        "it has never seen. The junta has been obeying those orders out of courtesy "
        "for some time now. The question in front of it is whether to keep pretending "
        "that is obedience, or to say out loud what everyone here has understood for "
        "two years: that this kingdom is governed from this room.")
    loc(f"EVTOPTA{base + 1}", "We govern ourselves. We have been doing it for three years.")
    loc(f"EVTOPTB{base + 1}", "We are the King's, and we will wait for the King.")
    log["moments"] += 1

    # --- the crisis: crown or republic ----------------------------------------------------
    EV.append(f"""country_event = {{
    id = {base + 2}
    title = "EVTNAME{base + 2}"
    desc = "EVTDESC{base + 2}"
    picture = "1822_iturbide_crowned"

    trigger = {{
        tag = {vic}
        # Iguala is 1821 and the Trienio 1820. Nothing here is proclaimed before the
        # Riego mutiny, because historically nothing was -- and firing early would
        # change the tag out from under the risings.
        year = 1820
        OR = {{
            has_country_flag = h18c_autonomous
            check_variable = {{ which = separatism value = 35 }}
            has_global_flag = h18_trienio
        }}
        NOT = {{ has_country_flag = h18c_independent }}
        war = no
    }}
    mean_time_to_happen = {{ months = 24 }}

    option = {{
        name = "EVTOPTA{base + 2}"
        set_country_flag = h18c_independent
        set_global_flag = h18_plan_de_iguala
        all_core = {{ remove_core = {vic} }}
        change_tag = {suc}
        government = absolute_monarchy
        vote_franschise = landed_voting
        upper_house_composition = appointed
        prestige = 20
        any_pop = {{ militancy = -3 }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = -2 }}
        ai_chance = {{ factor = 40 }}
    }}
    option = {{
        name = "EVTOPTB{base + 2}"
        set_country_flag = h18c_independent
        set_global_flag = h18_an_american_republic
        all_core = {{ remove_core = {vic} }}
        change_tag = {suc}
        government = presidential_dictatorship
        vote_franschise = landed_voting
        political_reform = wealth_voting
        prestige = 15
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -4 consciousness = 4 }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = 6 }}
        ai_chance = {{ factor = 45 }}
    }}
    option = {{
        name = "EVTOPTC{base + 2}"
        change_variable = {{ which = separatism value = 8 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 3 consciousness = 2 }}
        ai_chance = {{ factor = 15 }}
    }}
}}
""")
    loc(f"EVTNAME{base + 2}", f"The Question of the Crown: {road}")
    loc(f"EVTDESC{base + 2}",
        "It can be settled two ways and both have been argued in this room for a "
        "decade. A kingdom: our own crown, offered first to a Bourbon so that nobody "
        "can call it a revolution, with the Church established, the army intact and "
        "the men who govern now governing after. Or a republic: a congress, a "
        "constitution, no king at all, and the understanding that the gachupines will "
        "fight it and the Holy Alliance will never recognise it. The first is safer "
        "and asks a European prince to accept a throne no European prince has yet "
        "accepted. The second is cleaner and has worked exactly once, in a country to "
        "the north that had no viceroy to depose.")
    loc(f"EVTOPTA{base + 2}", f"A kingdom of our own. Proclaim {road}.")
    loc(f"EVTOPTB{base + 2}", f"No king at all. Proclaim {repub}.")
    loc(f"EVTOPTC{base + 2}", "Not this year.")
    log["moments"] += 1

# a viceroy who twice refuses a junta stops being asked
EV.append("""country_event = {
    id = 9102919
    title = "EVTNAME9102919"
    desc = "EVTDESC9102919"
    picture = "administration"

    trigger = {
        has_country_flag = h18c_junta_deferred
        NOT = { has_country_flag = h18c_junta_governs }
        NOT = { has_country_flag = h18c_junta_refused_twice }
    }
    mean_time_to_happen = { months = 30 }

    option = {
        name = "EVTOPTA9102919"
        set_country_flag = h18c_junta_refused_twice
        change_variable = { which = separatism value = 12 }
        any_pop = { limit = { has_pop_culture = criollo } militancy = 4 consciousness = 3 }
    }
}
""")
loc("EVTNAME9102919", "The Cabildo Stops Asking")
loc("EVTDESC9102919",
    "The question was put twice and answered the same way twice, and the men who put "
    "it have drawn the obvious conclusion: there is no road to a government of their "
    "own through this palace. They have stopped petitioning. Some of them have stopped "
    "coming to the city. What they are doing instead is not yet known, which is itself "
    "the most alarming thing about it.")
loc("EVTOPTA9102919", "The petitions have stopped. That is not good news.")
log["moments"] += 1

# --- retire the four decisions these replace ---------------------------------------------
import re, glob
RETIRE = ["proclaim_the_junta", "declare_the_kingdom_autonomous", "the_plan_of_iguala"]
RETIRE += [f"declare_independence_{s.lower()}" for _, s, _, _, _, _ in V]
RETIRE += ["the_protectorate_of_san_martin", "the_treaty_of_trujillo",
           "the_congress_of_tucuman", "the_declaration_at_talca"]
for f in sorted(glob.glob(f"{MOD}/decisions/1800_*.txt")):
    s = rd(f); n = 0
    for name in RETIRE:
        m = re.search(rf"\n\t{name} = \{{", s)
        if not m: continue
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        s = s[:m.start()] + s[i:]
        n += 1; log["decisions retired"] += 1
    if n: wr(f, s)

wr(f"{MOD}/events/1800_Four_Moments.txt", "\n".join(EV))
wr(f"{MOD}/localisation/38_moments.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")

left = 0
for f in glob.glob(f"{MOD}/decisions/1800_*.txt"):
    t = re.sub(r"#.*", "", rd(f))
    for m in re.finditer(r"^\t([a-z_0-9]+) = \{", t, re.M):
        i = m.end(); d = 1
        while i < len(t) and d:
            if t[i] == "{": d += 1
            elif t[i] == "}": d -= 1
            i += 1
        if re.search(r"\btag = NSP\b", t[m.end():i]): left += 1
log["decisions a New Spain player now sees"] = left
for k, v in sorted(log.items()): print(f"  {k:<42}{v}")
