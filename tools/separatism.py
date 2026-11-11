"""Separatism: a pressure you can see, feed and fight.

Independence is not scripted. Each viceroyalty carries a `separatism` figure that its
own government moves, and what happens at the thresholds follows from it. A New Spain
that swears the Constitution, stalls the Consolidación and pays for garrisons can be
sitting below the line in 1814 and survive Ferdinand's revocation. One that enforces
the Consolidación and pockets the remittances is past it before Morillo sails.

**Why there are two gauges and not one.** Victoria II already shows the right bar in
the right place: New Spain's primary culture is Spanish, it accepts only the criollos,
and its largest population by far is two and a third million mestizos who are not
accepted -- while Mexico's primary culture is mestizo and Mexico holds cores on a
hundred and four of its provinces. That is exactly the engine's condition for a
national independence movement, so one appears in the movements tab on its own and
grows on mestizo consciousness and militancy. It is real, it is native, and the player
can watch it.

What the engine will not do is let a trigger read that bar. So there is a second,
scripted figure moved by the same choices, and the two track each other because both
answer to what the player does. The scripted one is surfaced as a named modifier --
Restless, Disaffected, In Open Revolt -- rather than a number, so you always know which
side of a threshold you are on without being handed a spreadsheet.

**The asymmetry is the point.** Mexico and Peru are not Argentina and Chile.

In Mexico a parish priest raised the Indians and mestizos of the Bajío, stormed the
granary at Guanajuato and killed everyone inside it, and the creoles who had wanted
autonomy the week before went over to the viceroy in a body. Independence there, when
it came in 1821, came from Iturbide -- a royalist colonel -- precisely because the
creoles would not accept the alternative. So a rising in New Spain and Peru drives
mestizo militancy up and criollo militancy *down*: the elite is frightened into
loyalty, and separatism climbs more slowly but far more violently.

In Buenos Aires and Santiago the creole merchants and landowners took the government
themselves, in a cabildo abierto, with very little blood. Separatism there climbs fast
and cheap, and the state it produces is weak, factional and immediately at war with
its own provinces.
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

VICE = ["NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR"]
SUC = {"NSP": "MEX", "VPE": "PEU", "VNG": "CLM", "RDP": "ARG",
       "CGC": "CHL", "CBA": "CUB", "PTR": "PRI"}
# the two kinds of revolution
POPULAR = ("NSP", "VPE")              # mestizo rising, criollos frightened into loyalty
CREOLE  = ("RDP", "CGC", "VNG")       # cabildo abierto, merchants and landowners
ANY = "OR = { " + " ".join(f"tag = {t}" for t in VICE) + " }"

# --- modifiers: the visible face of the figure ------------------------------------
MODS = """
restless_kingdom = {
\ticon = 1
\tcore_pop_militancy_modifier = 0.5
\ttax_efficiency = -0.05
}

disaffected_kingdom = {
\ticon = 1
\tcore_pop_militancy_modifier = 1.5
\tcore_pop_consciousness_modifier = 1.0
\ttax_efficiency = -0.15
\tglobal_immigrant_attract = -0.2
}

in_open_revolt = {
\ticon = 1
\tcore_pop_militancy_modifier = 3.0
\tcore_pop_consciousness_modifier = 2.0
\ttax_efficiency = -0.3
\tland_organisation = -0.1
}

the_loyal_kingdom = {
\ticon = 8
\tcore_pop_militancy_modifier = -1.5
\ttax_efficiency = 0.15
\tglobal_immigrant_attract = 0.2
\tadministrative_efficiency_modifier = 0.1
}

the_recent_repression = {
\ticon = 1
\tcore_pop_militancy_modifier = -2.0
\tadministrative_efficiency_modifier = 0.1
}

the_memory_of_the_gallows = {
\ticon = 1
\tcore_pop_consciousness_modifier = 1.5
\tglobal_assimilation_rate = -0.3
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "restless_kingdom" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 6

# --- the figure starts at zero -------------------------------------------------------
EV.append(f"""country_event = {{
    id = 9101600
    title = "EVTNAME9101600"
    desc = "EVTDESC9101600"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        {ANY}
        year = 1800
    }}
    mean_time_to_happen = {{ days = 3 }}

    option = {{
        name = "EVTOPTA9101600"
        set_variable = {{ which = separatism value = 0 }}
    }}
}}
""")
loc("EVTNAME9101600", "The Kingdom at Peace")
loc("EVTDESC9101600",
    "Three hundred years of it, and nobody here has seriously proposed otherwise. The "
    "audiencia sits, the silver sails, the Church owns the mortgages, and the creoles "
    "complain about the peninsulars getting every office worth having. That is the "
    "normal condition of this kingdom and it has survived a great deal.")
loc("EVTOPTA9101600", "And will survive a great deal more.")

# --- the reader: every six months, show where we stand -------------------------------
def tier(eid, lo, hi, mod, others, title, desc, opt):
    bounds = f"        check_variable = {{ which = separatism value = {lo} }}\n"
    if hi is not None:
        bounds += f"        NOT = {{ check_variable = {{ which = separatism value = {hi} }} }}\n"
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"

    trigger = {{
        {ANY}
{bounds}        NOT = {{ has_country_modifier = {mod} }}
        NOT = {{ has_country_flag = h18c_independent }}
    }}
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA{eid}"
{''.join(f"        remove_country_modifier = {o}" + chr(10) for o in others)}        add_country_modifier = {{ name = {mod} duration = -1 }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["tiers"] += 1

tier(9101601, 25, 50, "restless_kingdom",
     ["disaffected_kingdom", "in_open_revolt", "the_loyal_kingdom"],
     "A Restless Kingdom",
     "Pasquinades on the cathedral door, a tertulia in every provincial capital where "
     "men read Raynal aloud and then burn the copy, and a corregidor in Querétaro "
     "reporting that he can no longer say with confidence who in his district would "
     "turn out for the King. Nothing that cannot be managed. Nothing that was true "
     "twenty years ago either.",
     "Watch the printers.")

tier(9101602, 50, 75, "disaffected_kingdom",
     ["restless_kingdom", "in_open_revolt", "the_loyal_kingdom"],
     "A Disaffected Kingdom",
     "The militia officers are creoles and the creoles have stopped pretending the "
     "arrangement suits them. Juntas are being discussed openly in houses where the "
     "audiencia cannot follow, the mails are being opened and found to be worth "
     "opening, and two regiments have had to be moved inland because the coast could "
     "not be trusted to hold them.",
     "It is no longer a question of printers.")

tier(9101603, 75, None, "in_open_revolt",
     ["restless_kingdom", "disaffected_kingdom", "the_loyal_kingdom"],
     "In Open Revolt",
     "There are two governments in this kingdom and only one of them is ours. Whole "
     "provinces remit nothing, the garrison holds the capital and the road to the port "
     "and very little else, and every man of property has decided which way he will "
     "jump and is waiting to see who moves first.",
     "Then it will be settled by force.")

# --- what moves it ---------------------------------------------------------------------
# Each is a small event that listens for a flag the existing chains already set.
def driver(eid, amount, flagtest, title, desc, opt, extra=""):
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        {ANY}
{flagtest}    }}
    mean_time_to_happen = {{ months = 2 }}

    option = {{
        name = "EVTOPTA{eid}"
        change_variable = {{ which = separatism value = {amount} }}
{extra}    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["drivers"] += 1

driver(9101610, 15, "        has_country_flag = h18c_bayonne_known\n",
       "No King to Be Loyal To",
       "The commission every official in this kingdom holds runs from a man who is a "
       "prisoner in France, and the body that claims to govern in his name is a "
       "committee in a besieged port. Loyalty has not stopped. It has merely become a "
       "question with more than one answer.",
       "To whom, exactly?")

driver(9101611, 20, "        has_country_flag = consolidacion_enforced\n",
       "The Credit of the Kingdom Is Gone",
       "The mortgages have been called in and the money shipped to Spain, and every "
       "hacienda and mine that ran on Church credit -- which is to say all of them -- "
       "has had its working capital taken by royal decree. The men ruined by this are "
       "not the poor.",
       "They will remember who did it.")

driver(9101612, -20, "        has_country_flag = h18c_constitutional\n",
       "Citizens of the Monarchy",
       "Deputies in the Cortes, a limited franchise, a press that is merely censored "
       "rather than silent, and the viceroyalty a province rather than a possession. "
       "Whatever else it is, it is the first answer Madrid has ever given.",
       "Let it be sworn in every parish.")

driver(9101613, 25, "        has_global_flag = h18_ferdinand_absolutist\n"
                    "        has_country_flag = h18c_constitutional\n",
       "Everything Conceded Is Withdrawn",
       "We swore the Constitution. We held elections, we sent deputies, we argued our "
       "case in Cádiz and we won some of it. The decree that arrived this morning says "
       "none of it ever happened. The men here who argued for patience have been made "
       "fools of in public, and they are the men who kept this kingdom quiet.",
       "There is nothing left to be patient for.")

driver(9101614, -15, "        has_country_flag = h18c_junta_governs\n",
       "The Junta Holds the Kingdom",
       "It governs in the King's name, it keeps the revenue here, and it has given the "
       "creoles the thing they actually wanted, which was to be the ones deciding. "
       "Whether that is loyalty or its opposite is a question nobody present wishes to "
       "put to a vote.",
       "For Ferdinand, and for ourselves.")

driver(9101615, -10, "        has_country_modifier = criollo_militia\n",
       "The Militia Is Raised",
       "Twelve battalions officered by the sons of this kingdom's best families, which "
       "makes the coast defensible and gives the creoles rank, arms, and the habit of "
       "being obeyed.",
       "A loyal militia is still a militia.",
       extra="        change_variable = { which = separatism_debt value = 10 }\n")

# A kingdom with no King and no answer to the question does not stay where it is.
EV.append(f"""country_event = {{
    id = 9101616
    title = "EVTNAME9101616"
    desc = "EVTDESC9101616"
    picture = "administration"

    trigger = {{
        {ANY}
        has_country_flag = h18c_bayonne_known
        NOT = {{ has_country_flag = h18c_independent }}
        NOT = {{ has_country_flag = h18c_junta_governs }}
        NOT = {{ has_country_modifier = the_recent_repression }}
        NOT = {{ check_variable = {{ which = separatism value = 70 }} }}
    }}
    mean_time_to_happen = {{ months = 24 }}

    option = {{
        name = "EVTOPTA9101616"
        change_variable = {{ which = separatism value = 8 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 1 }}
    }}
}}
""")
loc("EVTNAME9101616", "Another Year Without an Answer")
loc("EVTDESC9101616",
    "The audiencia governs because it has always governed, in the name of a king who "
    "is in France, on the authority of a junta in Cadiz that half the kingdom does not "
    "recognise. Nothing has been decided and nothing is going to be, and every month "
    "that passes makes the question of who governs here a little less theoretical.")
loc("EVTOPTA9101616", "The question will not keep.")
log["drivers"] += 1

# --- the asymmetry: what a rising does, and to whom ------------------------------------
for tag in POPULAR:
    eid = 9101620 + VICE.index(tag)
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        has_country_flag = h18c_the_rising
    }}
    mean_time_to_happen = {{ months = 2 }}

    option = {{
        name = "EVTOPTA{eid}"
        change_variable = {{ which = separatism value = 10 }}
        any_pop = {{
            limit = {{ has_pop_culture = mestizo }}
            militancy = 5 consciousness = 3
        }}
        any_pop = {{
            limit = {{ has_pop_culture = criollo }}
            militancy = -4 consciousness = 2
        }}
        add_country_modifier = {{ name = the_fear_of_the_many duration = -1 }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", "The Creoles Discover What a Rising Is")
    loc(f"EVTDESC{eid}",
        "Eighty thousand Indians and mestizos came over the wall at the granary and "
        "killed everyone sheltering inside it, peninsular and creole alike, and then "
        "went through the town. The men of property in this kingdom spent last year "
        "demanding autonomy and have spent this week riding to the viceroy to offer "
        "him their militia. Whatever is coming here, it is not what Buenos Aires is "
        "having.")
    loc(f"EVTOPTA{eid}", "Better the gachupines than this.")
    log["asymmetry"] += 1

for tag in CREOLE:
    eid = 9101630 + VICE.index(tag)
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        has_country_flag = h18c_the_rising
    }}
    mean_time_to_happen = {{ months = 2 }}

    option = {{
        name = "EVTOPTA{eid}"
        change_variable = {{ which = separatism value = 25 }}
        any_pop = {{
            limit = {{ has_pop_culture = criollo }}
            militancy = 3 consciousness = 5
        }}
        add_country_modifier = {{ name = the_cabildo_abierto duration = -1 }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", "The Cabildo Abierto")
    loc(f"EVTDESC{eid}",
        "The merchants and the landowners and the militia colonels met in open session, "
        "voted that authority returns to the people of the viceroyalty in the absence "
        "of the King, and appointed themselves. Almost nobody was killed. The men now "
        "governing are the same men who governed last month, which is the point, and "
        "the provinces that were not consulted have already begun to object.")
    loc(f"EVTOPTA{eid}", "The same men, in their own name.")
    log["asymmetry"] += 1

MODS2 = """
the_fear_of_the_many = {
\ticon = 4
\tcore_pop_militancy_modifier = -0.5
\tmobilisation_size = 0.04
\tglobal_assimilation_rate = -0.2
\ttax_efficiency = 0.05
}

the_cabildo_abierto = {
\ticon = 8
\tcore_pop_consciousness_modifier = 1.0
\tadministrative_efficiency_modifier = -0.1
\ttax_efficiency = -0.1
\tmobilisation_size = -0.02
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_fear_of_the_many" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS2 + "\n")
    log["modifiers"] += 2

# --- repression ---------------------------------------------------------------------------
DEC.append(f"""\tsuppress_the_juntistas = {{
\t\tpicture = administration
\t\tpotential = {{
\t\t\t{ANY}
\t\t\tcheck_variable = {{ which = separatism value = 20 }}
\t\t\tNOT = {{ has_country_modifier = the_recent_repression }}
\t\t\tNOT = {{ has_country_flag = h18c_independent }}
\t\t}}
\t\tallow = {{ money = 8000 }}
\t\teffect = {{
\t\t\ttreasury = -8000
\t\t\tchange_variable = {{ which = separatism value = -20 }}
\t\t\tchange_variable = {{ which = separatism_debt value = 10 }}
\t\t\tadd_country_modifier = {{ name = the_recent_repression duration = 1825 }}
\t\t\tadd_country_modifier = {{ name = the_memory_of_the_gallows duration = -1 }}
\t\t\tany_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -4 consciousness = 2 }}
\t\t\tany_pop = {{ limit = {{ has_pop_culture = mestizo }} militancy = -2 consciousness = 1 }}
\t\t\tprestige = -3
\t\t\tbadboy = 1
\t\t}}
\t\tai_will_do = {{ factor = 3 }}
\t}}
""")
loc("suppress_the_juntistas_title", "Suppress the Juntistas")
loc("suppress_the_juntistas_desc",
    "Arrest the corresponding societies, garrison the provincial capitals, hang the "
    "ringleaders where the town can see it and transport the rest to the presidios in "
    "Africa. It works. It worked in Quito in 1809, where the junta's members were "
    "killed in their cells, and it bought four years. What it does not do is change "
    "any man's mind, and the sons of the men hanged this year will be of age in 1820.")

# the debt coming due
EV.append(f"""country_event = {{
    id = 9101650
    title = "EVTNAME9101650"
    desc = "EVTDESC9101650"
    picture = "administration"

    trigger = {{
        {ANY}
        check_variable = {{ which = separatism_debt value = 10 }}
        NOT = {{ has_country_flag = h18c_independent }}
    }}
    mean_time_to_happen = {{ months = 36 }}

    option = {{
        name = "EVTOPTA9101650"
        change_variable = {{ which = separatism value = 10 }}
        change_variable = {{ which = separatism_debt value = -10 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 2 }}
    }}
}}
""")
loc("EVTNAME9101650", "The Sons of the Men We Hanged")
loc("EVTDESC9101650",
    "Of age now, and in the militia, and perfectly clear about which side of the square "
    "their fathers stood on. Every crackdown this government has ordered bought it a "
    "few quiet years and produced a cohort that cannot be reconciled on any terms we "
    "are able to offer.")
loc("EVTOPTA9101650", "We bought the time. This is the price.")

wr(f"{MOD}/events/1800_Separatism.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_Separatism.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/22_separatism.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<22}{v}")
