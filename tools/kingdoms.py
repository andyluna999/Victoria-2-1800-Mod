"""Reyno de Mexico: a country whose name follows its constitution.

A viceroyalty that wins its independence while still a monarchy is not a republic, and
calling it one erased the most interesting thing about how Mexican independence
actually went. The Plan of Iguala produced an empire that offered its throne to
Ferdinand VII; the coats of arms of the period read REYNO DE MEXICO, and the men who
made it had spent eleven years shooting people for proposing a republic.

Victoria II supports this directly. A localisation key of the form TAG_government
overrides a country's name under that form of government -- HPM already carries a
hundred and eighty-nine of them. So the name follows the constitution: win as a
monarchy and you are the Kingdom of Mexico, become a republic later and the name
changes with you, without a second tag or a second flag.

And somebody has to wear it. When a viceroyalty wins independence as a monarchy, the
crown is offered: to the sitting viceroy, who is whoever survived 1808; to a Bourbon
prince, which is what Iguala actually proposed and what Madrid refused; or to nobody,
by convening a congress and becoming a republic after all. The three roads lead to
three different countries, and all three happened somewhere in Spanish America.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# the monarchical names, under every government that is one
KINGDOMS = {
 "MEX": ("Reyno de Mexico", "Mexican Empire"),
 "PEU": ("Reino del Peru", "Kingdom of Peru"),
 "CLM": ("Reino de Nueva Granada", "Kingdom of New Granada"),
 "ARG": ("Reino del Plata", "Kingdom of the Plate"),
 "CHL": ("Reino de Chile", "Kingdom of Chile"),
}
MONARCHIES = ("absolute_monarchy", "prussian_constitutionalism",
              "hms_government", "constitutional_monarchy")
for tag, (name, _) in KINGDOMS.items():
    for g in MONARCHIES:
        loc(f"{tag}_{g}", name)
        log["names"] += 1

# --- the crown -----------------------------------------------------------------------
for tag, (name, imperial) in KINGDOMS.items():
    eid = 9102200 + list(KINGDOMS).index(tag) * 2
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "1822_iturbide_crowned"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        OR = {{
            has_country_flag = h18c_independence_won
            has_country_flag = h18c_viceroyalty_fallen
            has_global_flag = h18_plan_de_iguala
        }}
        OR = {{
            government = absolute_monarchy
            government = prussian_constitutionalism
        }}
        NOT = {{ has_country_flag = h18c_crowned }}
    }}
    mean_time_to_happen = {{ months = 6 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_country_flag = h18c_crowned
        set_country_flag = h18c_native_dynasty
        government = absolute_monarchy
        prestige = 20
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -3 consciousness = 1 }}
        any_pop = {{ limit = {{ has_pop_culture = mestizo }} consciousness = 2 }}
        ai_chance = {{ factor = 55 }}
    }}
    option = {{
        name = "EVTOPTB{eid}"
        set_country_flag = h18c_crowned
        set_country_flag = h18c_bourbon_offered
        government = prussian_constitutionalism
        prestige = 10
        SPA = {{ relation = {{ who = THIS value = 40 }} }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = -4 }}
        any_pop = {{ limit = {{ has_pop_culture = mestizo }} militancy = 2 consciousness = 2 }}
        ai_chance = {{ factor = 25 }}
    }}
    option = {{
        name = "EVTOPTC{eid}"
        set_country_flag = h18c_crowned
        set_country_flag = h18c_chose_the_republic
        government = presidential_dictatorship
        vote_franschise = landed_voting
        prestige = 5
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 3 consciousness = 4 }}
        any_pop = {{ limit = {{ has_pop_culture = mestizo }} militancy = -3 consciousness = 3 }}
        ai_chance = {{ factor = 20 }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", "A Crown for the Kingdom")
    loc(f"EVTDESC{eid}",
        "Independence is won and the throne is empty. It can be offered to the man who "
        "has been governing here -- which makes a dynasty out of an administrator and "
        "will be resented by everyone who did the fighting. It can be offered to a "
        "Bourbon prince, which is what the Plan promised and what reconciles the "
        "peninsulars and the Church, and which Madrid will almost certainly refuse "
        "while being flattered to have been asked. Or the congress can be convened and "
        "the whole question abolished, which is cheap, popular with the men who carried "
        "muskets, and the beginning of forty years of generals.")
    loc(f"EVTOPTA{eid}", "The crown to the man who holds the country.")
    loc(f"EVTOPTB{eid}", "Offer it to a prince of Spain.")
    loc(f"EVTOPTC{eid}", "Convene the congress. No crowns.")
    log["coronations"] += 1

wr(f"{MOD}/events/1800_Kingdoms.txt", "\n".join(EV))
wr(f"{MOD}/localisation/29_kingdoms.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<22}{v}")
