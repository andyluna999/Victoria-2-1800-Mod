"""
# Each of these now moves separatism, and they are all available from 1800. A viceroy
# who establishes the intendancies, endows the Seminario, admits the neutral traders
# and lets the Consolidacion die quietly arrives at Bayonne with about thirty points
# of credit -- which is the difference between the shock being survivable and the
# rising being decided before he could act.
Layer D: the decision shelf for Spanish America, 1800-1821.

The narrative plan builds three layers -- a date clock, a flag ledger, and map
effectors -- and every one of them fires *at* the player. The playtest found what that
leaves out: an empty decisions tab and nothing to chase. A date-gated event asks a
question once and moves on; a decision sits there, available for years, and the player
chooses when and whether.

So this adds three things the plan does not yet have.

**Decisions that stand open for a window.** Each has a `potential` window of several
years rather than a single date, so a viceroy can see the Consolidación sitting on his
desk and put it off.

**Reforms that are real levers, not flavour.** Every decision here changes a number
the player is already watching: revenue, militancy among a named culture, research,
leadership. The Bourbon reform programme was a set of trade-offs and it should read
like one.

**Modifiers with a cost on both sides.** None of these is free. The Consolidación
raises an enormous sum and poisons criollo credit for a generation; the militia makes
the colony defensible by arming the people who will later use it.

Everything here is a real policy of the Spanish empire between 1800 and 1821.
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
LOC = []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

COLONIES = "OR = { tag = NSP tag = VPE tag = VNG tag = RDP tag = CGC tag = CBA tag = PTR }"

# ---------------------------------------------------------------- modifiers
MODS = """
consolidacion_enforced = {
\ticon = 4
\ttax_efficiency = 0.15
\tfactory_owner_cost = 0.25
\tglobal_population_growth = -0.002
\tcore_pop_consciousness_modifier = 0.75
}

consolidacion_evaded = {
\ticon = 1
\ttax_efficiency = -0.08
\tglobal_population_growth = 0.001
\tcore_pop_militancy_modifier = -0.4
}

criollo_militia = {
\ticon = 2
\tsupply_consumption = -0.1
\tmobilisation_size = 0.04
\tland_organisation = 0.1
\tcore_pop_consciousness_modifier = 0.5
}

intendancy_system = {
\ticon = 3
\tadministrative_efficiency_modifier = 0.2
\ttax_efficiency = 0.1
\tcore_pop_militancy_modifier = 0.3
}

comercio_de_neutrales = {
\ticon = 5
\timport_cost = -0.25
\ttariff_efficiency_modifier = -0.15
\tglobal_immigrant_attract = 0.1
\tresearch_points_modifier = 0.05
}

estanco_del_tabaco = {
\ticon = 4
\ttax_efficiency = 0.12
\trgo_output = -0.05
\tcore_pop_militancy_modifier = 0.2
}

the_fortified_coast = {
\ticon = 2
\tland_defense_modifier = 0.15
\tsupply_consumption = -0.1
\torg_regain = 0.1
}

creole_university = {
\ticon = 8
\tresearch_points_modifier = 0.12
\teducation_efficiency_modifier = 0.15
\tcore_pop_consciousness_modifier = 0.6
}
"""
src = open(f"{MOD}/common/event_modifiers.txt", encoding="cp1252", errors="replace").read()
if "consolidacion_enforced" not in src:
    # Append at the end of the file. Inserting before the last closing brace nests
    # the new modifiers inside the last existing one, which silently strips that
    # modifier's brace and leaves the file malformed -- the game hangs on load with
    # nothing in the logs.
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers added"] = MODS.count(" = {")

# ---------------------------------------------------------------- decisions
D = []
# Each reform moves separatism, and they are all available from 1800. A viceroy who
# establishes the intendancies, endows the Seminario, admits the neutral traders and
# lets the Consolidacion die quietly arrives at Bayonne with about thirty points of
# credit banked -- which is the difference between the shock being survivable and the
# rising being settled before he had a chance to act. The old arrangement gave him
# nothing to bank and then decided the question for him.
SEPARATISM = {'establish_the_intendancies': -6, 'endow_the_royal_seminary': -5, 'open_the_neutral_trade': -8, 'expand_the_colonial_militia': -4, 'fortify_the_coast': -3, 'the_tobacco_estanco': 5, 'evade_the_consolidacion': -10}


def dec(name, title, desc, potential, allow, effect, ai=1):
    if name in SEPARATISM:
        effect = (effect.rstrip("\n") + "\n\t\t\tchange_variable = "
                  "{ which = separatism value = %d }" % SEPARATISM[name])
    D.append(f"""\t{name} = {{
\t\tpicture = administration
\t\tpotential = {{
{potential}
\t\t}}
\t\tallow = {{
{allow}
\t\t}}
\t\teffect = {{
{effect}
\t\t}}
\t\tai_will_do = {{ factor = {ai} }}
\t}}
""")
    loc(name + "_title", title); loc(name + "_desc", desc)
    log["decisions"] += 1

# --- the Consolidación de Vales Reales, 1804 ---------------------------------------
# The single most destructive act of Bourbon government in the Americas. Madrid,
# bankrupt from the British war, ordered the Church's colonial mortgages called in and
# the capital shipped to Spain. Church mortgages *were* the credit system of New Spain:
# almost every hacienda and mine ran on them. Some twelve million pesos left Mexico in
# five years and the criollo propertied class was ruined by it. It is the clearest
# single cause of why those same men backed Hidalgo six years later.
dec("enforce_the_consolidacion",
    "Enforce the Consolidación de Vales Reales",
    "Madrid is bankrupt and the royal decree is explicit: the Church's mortgages are to "
    "be called in and the capital remitted to Spain. Those mortgages are the credit of "
    "every hacienda and mine in the viceroyalty. The money will be found. So will the "
    "resentment.",
    f"\t\t\t{COLONIES}\n\t\t\tyear = 1804\n\t\t\tNOT = {{ year = 1810 }}\n"
    "\t\t\tNOT = { has_country_flag = consolidacion_settled }",
    "\t\t\twar = no",
    "\t\t\tset_country_flag = consolidacion_settled\n"
    "\t\t\tset_country_flag = consolidacion_enforced\n"
    "\t\t\tadd_country_modifier = { name = consolidacion_enforced duration = 5475 }\n"
    "\t\t\ttreasury = 40000\n\t\t\tSPA = { treasury = 60000 prestige = 5 }\n"
    "\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = 4 consciousness = 3 }\n"
    "\t\t\tany_pop = { limit = { has_pop_culture = mestizo } militancy = 2 }\n"
    "\t\t\tprestige = -5", ai=3)

dec("evade_the_consolidacion",
    "Delay the Consolidación",
    "The decree can be acknowledged, registered, and then administered so slowly that "
    "little of it is ever collected. Iturrigaray chose roughly this course, and Madrid "
    "noticed. The colony keeps its credit and the viceroy keeps the enmity of the "
    "peninsular party.",
    f"\t\t\t{COLONIES}\n\t\t\tyear = 1804\n\t\t\tNOT = {{ year = 1810 }}\n"
    "\t\t\tNOT = { has_country_flag = consolidacion_settled }",
    "\t\t\twar = no",
    "\t\t\tset_country_flag = consolidacion_settled\n"
    "\t\t\tset_country_flag = consolidacion_evaded\n"
    "\t\t\tadd_country_modifier = { name = consolidacion_evaded duration = 5475 }\n"
    "\t\t\tSPA = { relation = { who = THIS value = -40 } }\n"
    "\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = -2 }\n"
    "\t\t\tprestige = 5", ai=1)

# --- the colonial militia -----------------------------------------------------------
# After Havana fell to the British in 1762 the Crown accepted that Spain could not
# garrison the Americas from Europe and built a colonial militia instead -- officered
# by the criollo gentry, who thereby acquired rank, arms and the habit of command.
dec("expand_the_colonial_militia",
    "Expand the Colonial Militia",
    "Havana fell to a British fleet in eleven weeks because Spain cannot garrison the "
    "Americas from Europe. The answer is a militia raised here and officered by the "
    "creole gentry. It will make the viceroyalty defensible. It will also give the "
    "creoles rank, arms and the habit of command.",
    f"\t\t\t{COLONIES}\n\t\t\tNOT = {{ has_country_modifier = criollo_militia }}",
    "\t\t\tmoney = 5000",
    "\t\t\ttreasury = -5000\n"
    "\t\t\tadd_country_modifier = { name = criollo_militia duration = -1 }\n"
    "\t\t\tany_pop = { limit = { has_pop_culture = criollo } consciousness = 2 }\n"
    "\t\t\tprestige = 3", ai=2)

# --- the intendancy system -----------------------------------------------------------
dec("establish_the_intendancies",
    "Establish the Intendancies",
    "The Ordinance of Intendants replaces the old corregidores -- who bought their posts "
    "and recouped the price from the Indians -- with salaried professionals sent from "
    "Spain. It is honest government, and it strips a whole creole class of the offices "
    "they had treated as property.",
    f"\t\t\t{COLONIES}\n\t\t\tNOT = {{ has_country_modifier = intendancy_system }}",
    "\t\t\tmoney = 8000\n\t\t\twar = no",
    "\t\t\ttreasury = -8000\n"
    "\t\t\tadd_country_modifier = { name = intendancy_system duration = -1 }\n"
    "\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = 2 }\n"
    "\t\t\tSPA = { relation = { who = THIS value = 25 } }", ai=2)

# --- neutral trade ---------------------------------------------------------------------
# With the Royal Navy across the Atlantic trade routes, Madrid licensed neutral
# shipping in 1797 so the colonies would not starve of imports. It worked, and it
# ended the monopoly in practice years before anyone ended it in law.
dec("open_the_neutral_trade",
    "Admit the Neutral Traders",
    "The Royal Navy sits across every route to Cádiz and the warehouses are empty. "
    "Licensing neutral ships -- American, mostly -- will keep the colony supplied. It "
    "will also show every merchant here what trade looks like without Seville taking "
    "its cut, and they will not forget it.",
    f"\t\t\t{COLONIES}\n\t\t\tNOT = {{ has_country_modifier = comercio_de_neutrales }}\n"
    "\t\t\tSPA = { war = yes }",
    "\t\t\talways = yes",
    "\t\t\tadd_country_modifier = { name = comercio_de_neutrales duration = -1 }\n"
    "\t\t\tany_pop = { limit = { type = capitalists } consciousness = 3 }\n"
    "\t\t\tany_pop = { limit = { type = aristocrats } militancy = 1 }\n"
    "\t\t\tSPA = { relation = { who = THIS value = -20 } }", ai=2)

# --- the tobacco monopoly ---------------------------------------------------------------
dec("the_tobacco_estanco",
    "Extend the Tobacco Monopoly",
    "The estanco already licenses who may grow tobacco and at what price. Extending it "
    "is the quickest revenue in the Americas and the most hated: it reaches into the "
    "smallholding of every farmer who ever planted a row of it.",
    f"\t\t\t{COLONIES}\n\t\t\tNOT = {{ has_country_modifier = estanco_del_tabaco }}",
    "\t\t\twar = no",
    "\t\t\tadd_country_modifier = { name = estanco_del_tabaco duration = -1 }\n"
    "\t\t\ttreasury = 10000\n"
    "\t\t\tany_pop = { limit = { type = farmers } militancy = 2 }", ai=2)

# --- coastal defence ---------------------------------------------------------------------
dec("fortify_the_coast",
    "Fortify the Coast",
    "Veracruz, Cartagena, Havana and Callao are the locks on the empire, and the "
    "engineers have been asking for the money since the last war. British squadrons do "
    "not announce themselves.",
    f"\t\t\t{COLONIES}\n\t\t\tNOT = {{ has_country_modifier = the_fortified_coast }}",
    "\t\t\tmoney = 12000",
    "\t\t\ttreasury = -12000\n"
    "\t\t\tadd_country_modifier = { name = the_fortified_coast duration = -1 }\n"
    "\t\t\tprestige = 5", ai=2)

# --- the university ------------------------------------------------------------------------
# The Real Seminario de Minería opened in Mexico City in 1792 and was, by some way, the
# best scientific school in the Americas. Humboldt said so when he visited in 1803.
dec("endow_the_royal_seminary",
    "Endow the Royal Seminary of Mines",
    "The Seminario de Minería teaches chemistry and metallurgy to a standard Humboldt "
    "thought the equal of anything in Europe, and it teaches it to creoles. Endowing it "
    "will repay itself in the silver returns. What else it produces is harder to price.",
    f"\t\t\t{COLONIES}\n\t\t\tNOT = {{ has_country_modifier = creole_university }}",
    "\t\t\tmoney = 10000",
    "\t\t\ttreasury = -10000\n"
    "\t\t\tadd_country_modifier = { name = creole_university duration = -1 }\n"
    "\t\t\tany_pop = { limit = { has_pop_culture = criollo } consciousness = 2 literacy = 0.05 }\n"
    "\t\t\tprestige = 8", ai=2)

body = "political_decisions = {\n\n" + "\n".join(D) + "\n}\n"
wr(f"{MOD}/decisions/1800_Bourbon_Reforms.txt", body)

rows = ["" for _ in range(0)]
csv = "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC)
wr(f"{MOD}/localisation/11_bourbon.csv", csv + "\n")
log["localisation rows"] = len(LOC)

for k, v in sorted(log.items()): print(f"  {k:<28}{v}")
