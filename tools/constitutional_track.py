"""Layer E: the Spanish constitutional track, 1810-1833.

A reform is not a one-off purchase. Between 1810 and 1833 Spain and its colonies went
through the same constitution four times -- written, abolished, restored, abolished --
and the colonies' loyalty tracked it almost exactly. This is a state machine, and the
player should be able to feel it ratchet.

The historical arc:

  **1810** The Cortes meets at Cádiz with the French at the gates, and summons deputies
  from the Americas. Not subjects: deputies.

  **1812** The Constitution makes every free man in the empire a Spanish citizen with
  representation, and makes the viceroyalties provinces rather than possessions. It is
  the most generous offer Madrid ever made and it was made from desperation.

  **1814** Ferdinand VII returns, declares the Constitution void from the day it was
  written, and jails the men who wrote it. This is the hinge of the whole period. Up to
  1814 most criollo leaders wanted autonomy inside the empire; after it, the moderates
  had nothing to be moderate about. San Martín, Bolívar and Iturbide all hardened here.

  **1820** Riego's mutiny at Cádiz -- of an army assembled to sail against the colonies
  -- restores the Constitution. A second offer, three years too late.

  **1823** A French army, mandated by Verona, marches in and restores Ferdinand
  absolute. The Ominous Decade.

Each stage is a rail on Spain that reaches every colony, and at each stage the colony
gets a decision: take the offer or refuse it. Taking it moves real Victoria II reform
settings -- franchise, parties, press -- rather than adding a decorative modifier, so a
constitutional colony is visibly a different kind of state from an absolutist one.

The loyalty ledger: each colony carries `loyalty_credit`, raised by accepting an offer
and destroyed by a revocation. Section 8 of the plan keys the regency chain to it.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
# Event ids live in 9100800-9100599. The first draft used 9100400, which collides with
# the Porte events; the lint caught it, which is the whole point of the lint.
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

COLONY_LIST = "NSP VPE VNG RDP CGC CBA PTR"
def each_colony(effect):
    return "\n".join(f"        {t} = {{ {effect} }}" for t in COLONY_LIST.split())

# ---------------------------------------------------------------- modifiers
MODS = """
constitutional_province = {
\ticon = 8
\tglobal_immigrant_attract = 0.15
\tresearch_points_modifier = 0.1
\tcore_pop_militancy_modifier = -1.0
\ttax_efficiency = 0.08
}

the_broken_promise = {
\ticon = 1
\tcore_pop_militancy_modifier = 2.5
\tcore_pop_consciousness_modifier = 1.5
\ttax_efficiency = -0.12
\tglobal_assimilation_rate = -0.5
}

ominous_decade = {
\ticon = 4
\tadministrative_efficiency_modifier = -0.15
\tcore_pop_militancy_modifier = 1.0
\tresearch_points_modifier = -0.1
}
"""
src = open(f"{MOD}/common/event_modifiers.txt", encoding="cp1252", errors="replace").read()
if "constitutional_province" not in src:
    # Append at the end of the file. Inserting before the last closing brace nests
    # the new modifiers inside the last existing one, which silently strips that
    # modifier's brace and leaves the file malformed -- the game hangs on load with
    # nothing in the logs.
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = MODS.count(" = {")

def rail(eid, tag, year, until, title, desc, opt, effect, extra=""):
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        year = {year}
        NOT = {{ year = {until} }}
{extra}    }}
    mean_time_to_happen = {{ months = 2 }}

    option = {{
        name = "EVTOPTA{eid}"
{effect}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["rails"] += 1

# --- 1810: the Cortes summons the Americas -------------------------------------------
rail(9100800, "SPA", 1810, 1812,
 "The Cortes Meets at Cádiz",
 "The King is a prisoner in France, the French army holds everything but this one city, "
 "and what is left of Spain has summoned a Cortes behind the guns of the fleet. It has "
 "done something no Spanish government has done before: it has written to the Americas "
 "and asked them to send deputies. Not petitions. Deputies.",
 "Then let them come.",
 "        set_global_flag = h18_cortes_summoned\n"
 "        prestige = 5\n" + each_colony("country_event = 9100801"))

EV.append(f"""country_event = {{
    id = 9100801
    title = "EVTNAME9100801"
    desc = "EVTDESC9100801"
    picture = "administration"
    is_triggered_only = yes

    option = {{
        name = "EVTOPTA9100801"
        set_country_flag = h18c_sent_deputies
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -2 consciousness = 2 }}
        SPA = {{ relation = {{ who = THIS value = 30 }} }}
        prestige = 3
        ai_chance = {{ factor = 80 }}
    }}
    option = {{
        name = "EVTOPTB9100801"
        set_country_flag = h18c_declined_cortes
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 4 }}
        SPA = {{ relation = {{ who = THIS value = -30 }} }}
        ai_chance = {{ factor = 20 }}
    }}
}}
""")
loc("EVTNAME9100801", "A Summons from Cádiz")
loc("EVTDESC9100801",
    "The junta at Cádiz asks this viceroyalty to elect deputies to a Cortes that claims "
    "to speak for the whole monarchy. The peninsular party says it is a trap of liberals "
    "and lawyers. The creoles say it is the first time in three hundred years that "
    "anyone in Spain has asked us anything.")
loc("EVTOPTA9100801", "Elect the deputies.")
loc("EVTOPTB9100801", "Cádiz does not speak for the King.")
log["colony responses"] += 1

# --- 1812: the Constitution --------------------------------------------------------
rail(9100802, "SPA", 1812, 1814,
 "The Constitution of Cádiz",
 "Signed on the nineteenth of March. The monarchy is to be constitutional, the Cortes "
 "sovereign, the press free, and every free man in the empire -- on either side of the "
 "Atlantic -- a Spanish citizen. The viceroyalties are not possessions any more. They "
 "are provinces, with representation. It is the most generous thing Spain has ever "
 "offered the Americas, and it is offered because there is nothing left to offer.",
 "Sovereignty resides in the nation.",
 "        set_global_flag = h18_constitution_1812\n"
 "        government = prussian_constitutionalism\n"
 "        political_parties = harassment\n"
 "        press_rights = censored_press\n"
 "        vote_franschise = landed_voting\n"
 "        upper_house_composition = appointed\n"
 "        prestige = 10\n" + each_colony("country_event = 9100803"),
 extra="        has_global_flag = h18_cortes_summoned\n")

DEC.append("""\taccept_the_constitution_of_cadiz = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = { tag = NSP tag = VPE tag = VNG tag = RDP tag = CGC tag = CBA tag = PTR }
\t\t\thas_global_flag = h18_constitution_1812
\t\t\tNOT = { has_global_flag = h18_ferdinand_absolutist }
\t\t\tNOT = { has_country_modifier = constitutional_province }
\t\t\tNOT = { has_country_flag = h18c_refused_constitution }
\t\t}
\t\tallow = { war = no }
\t\teffect = {
\t\t\tset_country_flag = h18c_constitutional
\t\t\tadd_country_modifier = { name = constitutional_province duration = -1 }
\t\t\tgovernment = prussian_constitutionalism
\t\t\tpolitical_parties = harassment
\t\t\tpress_rights = censored_press
\t\t\tvote_franschise = landed_voting
\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = -3 consciousness = 2 }
\t\t\tany_pop = { limit = { has_pop_culture = mestizo } militancy = -1 }
\t\t\tSPA = { relation = { who = THIS value = 50 } }
\t\t\tprestige = 10
\t\t}
\t\tai_will_do = { factor = 4 }
\t}

\trefuse_the_constitution_of_cadiz = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = { tag = NSP tag = VPE tag = VNG tag = RDP tag = CGC tag = CBA tag = PTR }
\t\t\thas_global_flag = h18_constitution_1812
\t\t\tNOT = { has_country_modifier = constitutional_province }
\t\t\tNOT = { has_country_flag = h18c_constitutional }
\t\t\tNOT = { has_country_flag = h18c_refused_constitution }
\t\t}
\t\tallow = { always = yes }
\t\teffect = {
\t\t\tset_country_flag = h18c_refused_constitution
\t\t\tany_pop = { limit = { has_pop_culture = criollo } consciousness = 5 militancy = 3 }
\t\t\tSPA = { relation = { who = THIS value = -60 } }
\t\t\tprestige = -5
\t\t}
\t\tai_will_do = { factor = 1 }
\t}
""")
loc("accept_the_constitution_of_cadiz_title", "I. Swear the Constitution of Cádiz")
loc("accept_the_constitution_of_cadiz_desc",
    "To swear it is to become a province of a constitutional monarchy rather than a "
    "possession of a king: a Cortes, a limited franchise, a press that is merely "
    "censored rather than silent, and deputies of our own in Spain. The peninsular "
    "party will call it surrender to the lawyers. The creoles have wanted it for a "
    "century.")
loc("refuse_the_constitution_of_cadiz_title", "I. Refuse the Constitution")
loc("refuse_the_constitution_of_cadiz_desc",
    "The Cortes at Cádiz is a committee of liberals sheltering behind a British fleet, "
    "and it has no authority to remake the monarchy while the King is a prisoner. We "
    "hold this viceroyalty for Ferdinand, and we will hold it as it was.")

EV.append("""country_event = {
    id = 9100803
    title = "EVTNAME9100803"
    desc = "EVTDESC9100803"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100803"
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 3 }
    }
}
""")
loc("EVTNAME9100803", "Citizens of the Monarchy")
loc("EVTDESC9100803",
    "The text has arrived and is being read in the plazas. Men who were subjects this "
    "morning are citizens this afternoon, at least on paper, and the question of what "
    "the paper is worth is now the only question in the viceroyalty.")
loc("EVTOPTA9100803", "Let it be read out.")

# --- 1814: the revocation, the hinge of the period -----------------------------------
rail(9100804, "SPA", 1814, 1816,
 "Ferdinand Tears Up the Constitution",
 "The King has come home and his first act is a decree declaring the Constitution void "
 "from the day it was written, as though it had never existed. The men who wrote it, "
 "who held Cádiz for him while he was a guest at Valençay, are going to prison. "
 "Everything the Americas were promised in 1812 is withdrawn in a sentence.",
 "Nothing was ever conceded.",
 "        set_global_flag = h18_ferdinand_absolutist\n"
 "        clr_global_flag = h18_constitution_1812\n"
 "        government = absolute_monarchy\n"
 "        political_parties = underground_parties\n"
 "        press_rights = state_press\n"
 "        vote_franschise = none_voting\n"
 "        prestige = -10\n" + each_colony("country_event = 9100805"),
 extra="        has_global_flag = h18_constitution_1812\n")

EV.append("""country_event = {
    id = 9100805
    title = "EVTNAME9100805"
    desc = "EVTDESC9100805"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100805"
        remove_country_modifier = constitutional_province
        add_country_modifier = { name = the_broken_promise duration = -1 }
        government = absolute_monarchy
        political_parties = underground_parties
        press_rights = state_press
        vote_franschise = none_voting
        any_pop = { limit = { has_pop_culture = criollo } militancy = 6 consciousness = 4 }
        any_pop = { limit = { has_pop_culture = mestizo } militancy = 3 }
        SPA = { relation = { who = THIS value = -50 } }
    }
}
""")
loc("EVTNAME9100805", "The Promise Withdrawn")
loc("EVTDESC9100805",
    "Two years ago we were made citizens. The decree arriving today says we never were. "
    "The men who argued for patience, for autonomy inside the monarchy, for working "
    "through the Cortes -- those men have just been proved fools in public, and they "
    "will not make the argument twice.")
loc("EVTOPTA9100805", "There is nothing left to be moderate about.")

# --- 1820: Riego, and the second offer ------------------------------------------------
rail(9100806, "SPA", 1820, 1822,
 "Riego Proclaims the Constitution",
 "The army gathered at Cádiz to sail against the colonies has mutinied rather than "
 "embark, and its commander has proclaimed the Constitution of 1812. Ferdinand, with no "
 "army left that will obey him, has sworn to it. The expedition that was to reconquer "
 "the Americas will not sail.",
 "Let us march, and I the first.",
 "        set_global_flag = h18_trienio\n"
 "        clr_global_flag = h18_ferdinand_absolutist\n"
 "        government = prussian_constitutionalism\n"
 "        political_parties = harassment\n"
 "        press_rights = censored_press\n"
 "        vote_franschise = landed_voting\n" + each_colony("country_event = 9100807"),
 extra="        has_global_flag = h18_ferdinand_absolutist\n")

EV.append("""country_event = {
    id = 9100807
    title = "EVTNAME9100807"
    desc = "EVTDESC9100807"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100807"
        set_country_flag = h18c_second_offer
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 3 }
        ai_chance = { factor = 100 }
    }
}
""")
loc("EVTNAME9100807", "The Second Offer")
loc("EVTDESC9100807",
    "The Constitution is law again and the army that was to be sent against us has "
    "refused to sail. Madrid offers in 1820 what it offered in 1812 and withdrew in "
    "1814. The offer may even be sincere this time. Whether anyone here still wants it "
    "is a different question, and in Mexico the answer is being written by a colonel of "
    "royalist cavalry named Iturbide.")
loc("EVTOPTA9100807", "Eight years too late.")

# --- 1823: the Hundred Thousand Sons -------------------------------------------------
rail(9100808, "SPA", 1823, 1825,
 "The Hundred Thousand Sons of Saint Louis",
 "A French army has crossed the Bidasoa with the blessing of the Congress of Verona, "
 "brushed aside the constitutional government, and restored Ferdinand absolute. The "
 "liberals who have not fled are being hanged. Spain enters what will be remembered as "
 "the Ominous Decade.",
 "The King has his throne and France has the bill.",
 "        set_global_flag = h18_ominous_decade\n"
 "        clr_global_flag = h18_trienio\n"
 "        government = absolute_monarchy\n"
 "        political_parties = underground_parties\n"
 "        press_rights = state_press\n"
 "        vote_franschise = none_voting\n"
 "        add_country_modifier = { name = ominous_decade duration = 3650 }\n"
 "        prestige = -5\n"
 "        FRA = { prestige = 10 }",
 extra="        has_global_flag = h18_trienio\n")

wr(f"{MOD}/events/1800_Constitutional.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_Constitutional.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/12_constitutional.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
log["decisions"] = 2

for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
