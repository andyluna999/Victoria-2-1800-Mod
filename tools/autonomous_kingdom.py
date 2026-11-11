"""The road nobody models: independence without revolution.

Every version of Spanish American independence in this mod so far has been a republic
born out of a rising. That is Hidalgo, Buenos Aires and Caracas, and it is only half
of what happened. Mexico -- the largest, richest and most heavily garrisoned of the
viceroyalties -- became independent by the opposite route, and it is the route the
player is most likely to want.

**The Plan de Iguala, 24 February 1821.** Agustin de Iturbide was a royalist colonel
who had spent eleven years killing insurgents, and was sent south in 1820 to finish
Guerrero, the last of them. He negotiated with him instead. The Three Guarantees were
religion, independence and union: the Catholic Church untouched, Mexico sovereign, and
peninsular and creole equal before the law. The throne was offered to Ferdinand VII.

It worked because it was not a revolution. The royalist officer corps changed sides as
a body, bringing the army, the treasury and the administration with it, and almost
nobody was killed. A viceroyalty that had spent a decade crushing risings walked into
independence with its state intact -- which is precisely why the men of property
accepted it, having refused Hidalgo.

So there are four states now, not three:

  **Colony.** Remittances, monopoly, garrison.
  **Junta.** Governs for Ferdinand, keeps the revenue, no war.
  **Autonomous kingdom.** Renounces Madrid's authority while remaining the viceroyalty:
  the same army, the same treasury, the same officials, at war with Spain over who
  governs rather than over whether to exist. The peninsular officers resign.
  **Republic.** The enclave born of a rising, with six provinces and enthusiasm.

And the incentive inverts, which is the point. A viceroy who kept the kingdom quiet,
paid for garrisons and held separatism down arrives in 1820 with an intact army and a
solvent treasury -- and those are exactly the preconditions for Iguala. **The best
independence in the game is the reward for having been the best colonial governor.**
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, os, collections

MOD = _BUILD
log = collections.Counter()
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

VICE = ["NSP", "VPE", "VNG", "RDP", "CGC"]
ANY = "OR = { " + " ".join(f"tag = {t}" for t in VICE) + " }"

MODS = """
the_new_junta = {
\ticon = 8
\tadministrative_efficiency_modifier = -0.1
\tcore_pop_consciousness_modifier = 0.5
}

the_autonomous_kingdom = {
\ticon = 8
\ttax_efficiency = 0.2
\tadministrative_efficiency_modifier = 0.15
\tland_organisation = 0.1
\tmobilisation_size = 0.04
\tcore_pop_consciousness_modifier = 0.5
}

the_peninsular_officers_resign = {
\ticon = 1
\tland_organisation = -0.2
\torg_regain = -0.15
\tleadership = -1
}

the_three_guarantees = {
\ticon = 8
\tcore_pop_militancy_modifier = -3.0
\tcore_pop_consciousness_modifier = -1.0
\ttax_efficiency = 0.15
\tadministrative_efficiency_modifier = 0.2
\tglobal_assimilation_rate = 0.3
\tprestige = 0.5
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_autonomous_kingdom" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

# --- the autonomous kingdom --------------------------------------------------------
DEC.append(f"""\tdeclare_the_kingdom_autonomous = {{
\t\tpicture = administration
\t\tpotential = {{
\t\t\t{ANY}
\t\t\thas_country_flag = h18c_junta_governs
\t\t\tNOT = {{ has_country_flag = h18c_autonomous }}
\t\t\tNOT = {{ has_country_flag = h18c_independent }}
\t\t}}
\t\tallow = {{
\t\t\tmoney = 15000
\t\t\twar = no
\t\t\t# Three years of governing in the King's name before renouncing him, and
\t\t\t# only while Madrid has something else to attend to.
\t\t\tNOT = {{ has_country_modifier = the_new_junta }}
\t\t\tSPA = {{ war = yes }}
\t\t}}
\t\teffect = {{
\t\t\tset_country_flag = h18c_autonomous
\t\t\tset_global_flag = h18_an_autonomous_kingdom
\t\t\ttreasury = -15000
\t\t\tgovernment = prussian_constitutionalism
\t\t\tvote_franschise = landed_voting
\t\t\tadd_country_modifier = {{ name = the_autonomous_kingdom duration = -1 }}
\t\t\tadd_country_modifier = {{ name = the_peninsular_officers_resign duration = 3650 }}
\t\t\tremove_country_modifier = colonial_trade_monopoly
\t\t\tany_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -3 consciousness = 3 }}
\t\t\tany_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = 6 consciousness = 2 }}
\t\t\tSPA = {{
\t\t\t\trelation = {{ who = THIS value = -150 }}
\t\t\t\twar = {{
\t\t\t\t\ttarget = THIS
\t\t\t\t\tattacker_goal = {{ casus_belli = war_of_independence_cb }}
\t\t\t\t\tdefender_goal = {{ casus_belli = status_quo }}
\t\t\t\t\tcall_ally = yes
\t\t\t\t}}
\t\t\t}}
\t\t\tprestige = 15
\t\t}}
\t\tai_will_do = {{
\t\t\tfactor = 0.5
\t\t\tmodifier = {{ factor = 4 SPA = {{ war = yes }} }}
\t\t\tmodifier = {{ factor = 0 has_global_flag = h18_morillo_sails }}
\t\t}}
\t}}
""")
loc("declare_the_kingdom_autonomous_title", "III. Renounce the Authority of Madrid")
loc("declare_the_kingdom_autonomous_desc",
    "Not a republic and not a rebellion: this kingdom declares that it governs itself, "
    "under its own laws, with its own army and revenue, and will recognise no authority "
    "in Spain over its affairs. The Crown is not renounced -- the throne is simply "
    "declared to be here. Every peninsular officer in the service will resign or be "
    "removed, which costs us the best part of the staff, and Madrid will treat it as "
    "treason. What it does not cost us is the army, the treasury, the audiencia or the "
    "tax rolls. We go to war as a state, not as an insurrection.")
log["decisions"] += 1

# --- the Plan de Iguala ----------------------------------------------------------------
DEC.append("""\tthe_plan_of_iguala = {
\t\tpicture = administration
\t\tpotential = {
\t\t\ttag = NSP
\t\t\tyear = 1820
\t\t\tNOT = { exists = MEX }
\t\t\tNOT = { has_country_flag = h18c_independent }
\t\t}
\t\tallow = {
\t\t\tNOT = { check_variable = { which = separatism value = 60 } }
\t\t\tcheck_variable = { which = separatism value = 15 }
\t\t\twar = no
\t\t\tmoney = 10000
\t\t\t# Earned, not taken: Iguala is Iturbide bringing the royalist army over,
\t\t\t# which presupposes a kingdom that has already stopped obeying Madrid.
\t\t\tOR = {
\t\t\t\thas_country_flag = h18c_junta_governs
\t\t\t\thas_country_flag = h18c_autonomous
\t\t\t\thas_country_flag = h18c_civil_war
\t\t\t}
\t\t\tOR = {
\t\t\t\thas_global_flag = h18_riego_cancels_the_expedition
\t\t\t\tSPA = { war = yes }
\t\t\t}
\t\t\tNOT = { has_global_flag = h18_morillo_sails }
\t\t}
\t\teffect = {
\t\t\tset_country_flag = h18c_independent
\t\t\tset_global_flag = h18_plan_de_iguala
\t\t\ttreasury = -10000
\t\t\t# New Spain ceases to exist, and so do its claims
\t\t\tall_core = { remove_core = NSP }
\t\t\tchange_tag = MEX
\t\t\tgovernment = absolute_monarchy
\t\t\tvote_franschise = landed_voting
\t\t\tupper_house_composition = appointed
\t\t\tadd_country_modifier = { name = the_three_guarantees duration = -1 }
\t\t\tremove_country_modifier = colonial_trade_monopoly
\t\t\tremove_country_modifier = the_rising
\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = -5 consciousness = 2 }
\t\t\tany_pop = { limit = { has_pop_culture = mestizo } militancy = -4 }
\t\t\tany_pop = { limit = { has_pop_culture = spanish } militancy = 2 }
\t\t\tSPA = { relation = { who = THIS value = -80 } }
\t\t\tprestige = 25
\t\t}
\t\tai_will_do = {\n\t\t\tfactor = 0.4\n\t\t\tmodifier = { factor = 6 has_global_flag = h18_riego_cancels_the_expedition }\n\t\t\tmodifier = { factor = 3 SPA = { war = yes } }\n\t\t\tmodifier = { factor = 0 has_global_flag = h18_morillo_sails }\n\t\t}
\t}
""")
loc("the_plan_of_iguala_title", "IV. Independence as a Kingdom: the Plan of Iguala")
loc("the_plan_of_iguala_desc",
    "Colonel Iturbide was sent south to finish Guerrero and has come back with him "
    "instead. The plan has three guarantees and no more: the Catholic religion "
    "untouched, this kingdom independent, and peninsular and creole equal before the "
    "law. The throne is to be offered to Ferdinand VII, and if he will not take it, to "
    "whoever will. There is to be no republic, no confiscation and no settling of "
    "accounts for the last eleven years. The officer corps has already agreed, which "
    "means the army comes with us entire, and the men of property who would not hear "
    "of Hidalgo have been in the room all week.")
log["decisions"] += 1


# --- the negotiated road, one for each viceroyalty -------------------------------------
# Iguala is Mexico's. Every viceroyalty had a moment when independence could be had by
# agreement among the men already in charge rather than by a rising, and each of those
# moments has the same shape: late, conservative, expensive, and available only to a
# government that still has an army and a treasury. The reward is the same -- a country
# that arrives intact instead of an enclave that has to win itself one.
NEGOTIATED = [
 ("VPE", "PEU", 1821, "the_protectorate_of_san_martin",
  "Proclaim the Protectorate",
  "San Martin has landed at Paracas, taken Lima without a battle because the viceroy "
  "withdrew rather than fight in the streets, and declared himself Protector. He does "
  "not want a republic. He wants a throne with a European prince on it and the men who "
  "run this viceroyalty still running it, and he has said as much in writing. The "
  "creole landowners of the coast, who spent the last decade paying for armies to "
  "crush the sierra, find they can live with this. Abolition of Indian tribute is the "
  "price and they will pay it."),
 ("VNG", "CLM", 1820, "the_treaty_of_trujillo",
  "Sign the Treaty of Trujillo",
  "Morillo and Bolivar met at Santa Ana and embraced in front of both staffs, which "
  "nobody expected. Six months of armistice, and a convention regularising the war -- "
  "no more shooting of prisoners on either side, after ten years of exactly that. "
  "Morillo understands what he has signed: to treat with the republic as a belligerent "
  "is to concede that it exists. He has asked to be relieved of his command and is "
  "going home."),
 ("RDP", "ARG", 1816, "the_congress_of_tucuman",
  "Declare at Tucuman",
  "The congress has declared the United Provinces independent of Ferdinand VII and his "
  "successors -- and then spent a fortnight arguing about what to put in his place. "
  "Belgrano has proposed restoring the Inca monarchy with a descendant of the Tupac "
  "Amaru line on the throne at Cuzco, which is less absurd than it sounds and has "
  "serious support. Others want a European prince. Nobody of consequence wants a "
  "republic, and in twelve years they will have one anyway."),
 ("CGC", "CHL", 1818, "the_declaration_at_talca",
  "Declare Independence at Talca",
  "O'Higgins signed it at Talca and had it sworn in Santiago, four weeks after "
  "Chacabuco and a month before Maipu makes it true. The Supreme Director governs with "
  "a senate he appointed himself and no intention of consulting anyone, which the "
  "landowners of the central valley regard as the entire point. The old families keep "
  "their estates, their militia commissions and their monopoly of office."),
]

for vic, suc, yr, key, title, body in NEGOTIATED:
    DEC.append(f"""\t{key} = {{
\t\tpicture = administration
\t\tpotential = {{
\t\t\ttag = {vic}
\t\t\tyear = {yr}
\t\t\tNOT = {{ exists = {suc} }}
\t\t\tNOT = {{ has_country_flag = h18c_independent }}
\t\t}}
\t\tallow = {{
\t\t\tNOT = {{ check_variable = {{ which = separatism value = 60 }} }}
\t\t\tcheck_variable = {{ which = separatism value = 15 }}
\t\t\twar = no
\t\t\tmoney = 10000
\t\t\t# Earned, not taken. A viceroyalty negotiates its way out only after it has
\t\t\t# already stopped obeying Madrid -- a junta, an autonomous kingdom, or a
\t\t\t# civil war it is already fighting -- and only once Spain cannot answer.
\t\t\tOR = {{
\t\t\t\thas_country_flag = h18c_junta_governs
\t\t\t\thas_country_flag = h18c_autonomous
\t\t\t\thas_country_flag = h18c_civil_war
\t\t\t}}
\t\t\tOR = {{
\t\t\t\thas_global_flag = h18_riego_cancels_the_expedition
\t\t\t\tSPA = {{ war = yes }}
\t\t\t}}
\t\t\tNOT = {{ has_global_flag = h18_morillo_sails }}

\t\t}}
\t\teffect = {{
\t\t\tset_country_flag = h18c_independent
\t\t\tset_global_flag = h18_negotiated_independence
\t\t\ttreasury = -10000
\t\t\tall_core = {{ remove_core = {vic} }}
\t\t\tchange_tag = {suc}
\t\t\tgovernment = presidential_dictatorship
\t\t\tvote_franschise = landed_voting
\t\t\tupper_house_composition = appointed
\t\t\tadd_country_modifier = {{ name = the_three_guarantees duration = -1 }}
\t\t\tremove_country_modifier = colonial_trade_monopoly
\t\t\tremove_country_modifier = the_rising
\t\t\tany_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -5 consciousness = 2 }}
\t\t\tany_pop = {{ limit = {{ has_pop_culture = mestizo }} militancy = -3 }}
\t\t\tSPA = {{ relation = {{ who = THIS value = -80 }} }}
\t\t\tprestige = 25
\t\t}}
\t\tai_will_do = {{
\t\t\tfactor = 0.4
\t\t\t# only once Spain can no longer answer: the expedition cancelled, or the
\t\t\t# metropole already fighting at home. A viceroy does not negotiate his way
\t\t\t# out of an empire that still has an army and a fleet.
\t\t\tmodifier = {{ factor = 6 has_global_flag = h18_riego_cancels_the_expedition }}
\t\t\tmodifier = {{ factor = 3 SPA = {{ war = yes }} }}
\t\t\tmodifier = {{ factor = 0 has_global_flag = h18_morillo_sails }}
\t\t}}
\t}}
""")
    loc(f"{key}_title", "IV. " + title); loc(f"{key}_desc", body)
    log["negotiated roads"] += 1

# --- and somebody has to wear the crown ------------------------------------------------
# The Plan offered the throne to Ferdinand VII, who refused it and forbade any Bourbon
# to accept. That left a vacancy, an army, and the man who had arranged everything.
EV.append("""country_event = {
    id = 9101810
    title = "EVTNAME9101810"
    desc = "EVTDESC9101810"
    picture = "1822_iturbide_crowned"
    fire_only_once = yes

    trigger = {
        tag = MEX
        has_global_flag = h18_plan_de_iguala
        year = 1822
        NOT = { year = 1825 }
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9101810"
        set_global_flag = h18_the_mexican_empire
        government = absolute_monarchy
        prestige = 15
        any_pop = { limit = { has_pop_culture = criollo } militancy = -2 }
        any_pop = { limit = { has_pop_culture = mestizo } consciousness = 2 }
        ai_chance = { factor = 70 }
    }
    option = {
        name = "EVTOPTB9101810"
        set_global_flag = h18_the_mexican_republic
        government = presidential_dictatorship
        vote_franschise = landed_voting
        prestige = 5
        any_pop = { limit = { has_pop_culture = criollo } militancy = 2 consciousness = 3 }
        any_pop = { limit = { has_pop_culture = mestizo } militancy = -2 }
        ai_chance = { factor = 30 }
    }
}
""")
loc("EVTNAME9101810", "A Crown Without a King")
loc("EVTDESC9101810",
    "The throne was offered to Ferdinand VII, who refused it, and then to each of his "
    "brothers in turn, and the Cortes has forbidden any Bourbon to accept. So there is "
    "a monarchy with nobody in it, an army that has not been paid, and a congress that "
    "cannot agree on anything else. On the eighteenth of May a sergeant of the Celaya "
    "regiment began shouting for Iturbide outside his house and the rest of the "
    "garrison took it up, and by morning the thing had the look of a popular demand. "
    "He has said he does not want it. Nobody in the room believes him, and the "
    "alternative on the table is a republic that half the officer corps has spent "
    "eleven years shooting people for proposing.")
loc("EVTOPTA9101810", "Agustin the First, by divine providence.")
loc("EVTOPTB9101810", "No crowns. Let it be a republic.")
log["events"] += 1

# --- winning the autonomous war --------------------------------------------------------
EV.append("""country_event = {
    id = 9101800
    title = "EVTNAME9101800"
    desc = "EVTDESC9101800"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        has_country_flag = h18c_autonomous
        war = no
        NOT = { exists = SPA }
    }
    mean_time_to_happen = { months = 2 }

    option = {
        name = "EVTOPTA9101800"
        set_country_flag = h18c_independent
        remove_country_modifier = the_peninsular_officers_resign
        prestige = 30
        any_pop = { militancy = -4 }
    }
}

country_event = {
    id = 9101801
    title = "EVTNAME9101801"
    desc = "EVTDESC9101801"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        has_country_flag = h18c_autonomous
        war = no
        exists = SPA
        NOT = { vassal_of = SPA }
        year = 1823
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9101801"
        set_country_flag = h18c_independent
        remove_country_modifier = the_peninsular_officers_resign
        prestige = 20
        SPA = { relation = { who = THIS value = 25 } }
        any_pop = { militancy = -3 }
    }
}
""")
loc("EVTNAME9101800", "Madrid Has Nothing Left to Send")
loc("EVTDESC9101800",
    "There is no longer a Spain in any sense that concerns this kingdom. The war ends "
    "because the other party to it has ceased to exist, and the officials who have been "
    "governing in the King's name for fifteen years will go on governing, in their own.")
loc("EVTOPTA9101800", "The kingdom stands on its own account.")
loc("EVTNAME9101801", "Madrid Gives Up the Attempt")
loc("EVTDESC9101801",
    "No fleet has sailed, no army has landed, and the Cortes has stopped voting money "
    "for either. The war is over in the only way these wars end: Spain stops claiming "
    "and we stop having to deny it. There is no treaty. There will be one eventually, "
    "and it will concede what is already true.")
loc("EVTOPTA9101801", "Let them recognise it when they can bear to.")
log["events"] = 2

# --- the independence decisions become a progression, not a shortcut -------------------
# Declaring a republic out of nowhere skipped the junta entirely. It now requires the
# kingdom to have taken a step away from Madrid first, so the four states are a ladder.
f = f"{MOD}/decisions/1800_Latin_Independence.txt"
if os.path.exists(f):
    t = rd(f)
    t = t.replace("""\t\t\tOR = {
\t\t\t\thas_country_flag = h18c_junta_governs
\t\t\t\thas_country_flag = h18c_the_rising
\t\t\t}""",
"""\t\t\tOR = {
\t\t\t\thas_country_flag = h18c_junta_governs
\t\t\t\thas_country_flag = h18c_autonomous
\t\t\t\thas_country_flag = h18c_civil_war
\t\t\t}""")
    wr(f, t); log["independence made a progression"] = 1

wr(f"{MOD}/events/1800_Autonomy.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_Autonomy.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/24_autonomy.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<36}{v}")
