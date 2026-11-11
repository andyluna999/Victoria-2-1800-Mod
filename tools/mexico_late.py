"""Three things the Mexican republic needed and did not have.

**The war names.** `become_independent` and the base game's core casus belli name their
wars with keys the base game localises and HPM does not override -- except that
something in this stack is not finding them, so a war of independence shows as
INDEPENDENCE_NAME. They are defined here, which costs nothing and settles it.

**The reconquest.** Mexico cores a hundred and four provinces and eight of them are
Comanche. Beating the Comanche produced nothing, because the claim only pays out
through the war-goal system: the casus belli has to be selected at the declaration and
survive to the peace, and an AI-mediated war on the frontier rarely does either. A
republic that has beaten the people on its own cored land should get the land. So
there is a decision that does it directly, against any neighbour too weak to hold it,
at a price in infamy and militancy.

**The immigrants.** This is the one that decides the century. Victoria II sends
emigrants where literacy, jobs and `immigrant_attract` are highest, and the United
States starts with every one of those advantages and compounds them -- so Mexico can
pass universal suffrage, pensions and public schools and still watch the north fill
with people who are not its own. That is not a bad model of history, but it is a
model with no lever in it, and a player who has done everything right deserves one.

Mexico had real attractions and used them: free land to anyone who would farm it, no
tithe for settlers, and after 1824 a federal republic that advertised itself in Europe
as the liberal alternative to a continent of restored monarchies. The colonisation law
of 1824 offered a league and a labour of land to any head of household who came. What
it never had was peace long enough for anyone to believe the offer, which is exactly
the thing a player can supply.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

# --- 1. the war names the base game is not supplying -------------------------------------
for k, v in [("WAR_INDEPENDENCE_NAME", "$COUNTRY_ADJ$ War of Independence"),
             ("WAR_TAKE_CORE_NAME", "$ATTACKER_ADJ$ Reclamation of $STATE$"),
             ("WAR_ALL_CORES_NAME", "$ATTACKER_ADJ$ Unification War"),
             ("WAR_RESTORE_ORDER_NAME", "$ATTACKER_ADJ$ Restoration of Order"),
             ("WAR_LIBERATE_COUNTRY_NAME", "Liberation of $COUNTRY$")]:
    loc(k, v)
log["war names supplied"] = 5

AMER = ("MEX", "PEU", "CLM", "ARG", "CHL", "BRZ")

# --- 2. the reconquest, done directly -----------------------------------------------------
DEC.append("""\tunify_the_republic = {
\t\tpicture = conquest_of_the_desert
\t\tpotential = {
\t\t\tOR = {
				tag = MEX tag = PEU tag = CLM tag = ARG tag = CHL
				tag = URU tag = PRG tag = BOL tag = GCO tag = CBA tag = PTR
				tag = DOM tag = HAI tag = TEX tag = CAL
			}
\t\t\thas_country_flag = h18c_the_claim_stands
\t\t\tany_neighbor_country = {
\t\t\t\tcivilized = no
\t\t\t\tany_owned_province = { is_core = THIS }
\t\t\t}
\t\t}
\t\tallow = {
\t\t\twar = no
\t\t\tmoney = 20000
\t\t\tany_neighbor_country = {
\t\t\t\tcivilized = no
\t\t\t\tany_owned_province = { is_core = THIS }
\t\t\t}
\t\t}
\t\teffect = {
\t\t\ttreasury = -20000
\t\t\tbadboy = 4
\t\t\tprestige = 8
\t\t\tany_country = {
\t\t\t\tlimit = {
\t\t\t\t\tcivilized = no
\t\t\t\t\tneighbour = THIS
\t\t\t\t\tany_owned_province = { is_core = THIS }
\t\t\t\t}
\t\t\t\tany_owned = {
\t\t\t\t\tlimit = { is_core = THIS }
\t\t\t\t\tsecede_province = THIS
\t\t\t\t}
\t\t\t}
\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = -2 consciousness = 1 }
\t\t}
\t\tai_will_do = { factor = 6 }
\t}
""")
loc("unify_the_republic_title", "Unify the Republic")
loc("unify_the_republic_desc",
    "The map taught in the schools runs to the Sabine and the Arkansas and a great "
    "deal of what it covers is governed by people who have never heard of this "
    "congress. Occupying it is not a war in any sense the chancelleries would "
    "recognise -- there is no government to declare on and no capital to take -- it is "
    "the slow business of garrisons, land titles and presidios, and it is expensive "
    "and it is not quick. What it produces is a country whose borders match its claim "
    "for the first time since it stopped being a viceroyalty.")
log["decisions"] += 1

# --- 3. why anyone would come to Mexico ----------------------------------------------------
MODS = """
the_colonisation_law = {
\ticon = 8
\tglobal_immigrant_attract = 1.8
\tfarm_RGO_size = 0.15
\ttax_efficiency = -0.05
}

the_liberal_republic_advertised = {
\ticon = 8
\tglobal_immigrant_attract = 1.2
\tprestige = 0.3
\tglobal_assimilation_rate = 0.2
}

the_open_republic = {
\ticon = 8
\tglobal_immigrant_attract = 1.0
\tglobal_assimilation_rate = 0.5
\tnon_accepted_pop_militancy_modifier = -1.5
}

a_generation_of_peace = {
\ticon = 8
\tglobal_immigrant_attract = 1.5
\tcore_pop_militancy_modifier = -1.0
\tglobal_population_growth = 0.003
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "\nthe_colonisation_law = {" not in src:
    wr(f"{MOD}/common/event_modifiers.txt", src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

DEC.append("""\tthe_colonisation_law = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = {
				tag = MEX tag = PEU tag = CLM tag = ARG tag = CHL tag = BRZ
				tag = URU tag = PRG tag = BOL tag = GCO tag = CBA tag = PTR
				tag = DOM tag = HAI tag = TEX tag = CAL
			}
\t\t\thas_country_flag = h18c_independent
\t\t\tNOT = { has_country_modifier = the_colonisation_law }
\t\t}
\t\tallow = { war = no money = 10000 }
\t\teffect = {
\t\t\ttreasury = -10000
\t\t\tadd_country_modifier = { name = the_colonisation_law duration = -1 }
\t\t\tany_pop = { limit = { has_pop_culture = criollo } consciousness = 1 }
\t\t}
\t\tai_will_do = { factor = 5 }
\t}

\tadvertise_the_republic = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = {
				tag = MEX tag = PEU tag = CLM tag = ARG tag = CHL
				tag = URU tag = PRG tag = BOL tag = GCO tag = CBA tag = PTR
				tag = DOM tag = HAI tag = TEX tag = CAL
			}
\t\t\thas_country_modifier = the_colonisation_law
\t\t\tNOT = { has_country_modifier = the_liberal_republic_advertised }
\t\t\tOR = {
\t\t\t\tvote_franschise = wealth_voting
\t\t\t\tvote_franschise = universal_voting
\t\t\t}
\t\t}
\t\tallow = { war = no money = 15000 }
\t\teffect = {
\t\t\ttreasury = -15000
\t\t\tadd_country_modifier = { name = the_liberal_republic_advertised duration = -1 }
\t\t\tprestige = 5
\t\t}
\t\tai_will_do = { factor = 4 }
\t}
""")
loc("the_colonisation_law_title", "The Colonisation Law")
loc("the_colonisation_law_desc",
    "A league and a labour of land to any head of household who comes and farms it, "
    "free of tithe for ten years and free of customs on what he brings with him. The "
    "terms are better than anything on offer north of the river and they always have "
    "been; what the republic has never been able to offer alongside them is the "
    "reasonable expectation that the government granting the title will still exist "
    "when the title is challenged.")
loc("advertise_the_republic_title", "Advertise the Republic in Europe")
loc("advertise_the_republic_desc",
    "Agents in Hamburg, Le Havre and the Irish ports, with pamphlets, maps and the "
    "constitution translated into four languages. The argument writes itself: a "
    "federal republic with a wider franchise than any monarchy in Europe, land for the "
    "asking, and no conscription into anyone's dynastic quarrel. The competition is a "
    "country to the north making the same offer with more ships and better harbours, "
    "so the pamphlets had better be good.")
log["decisions"] += 2

EV.append("""country_event = {
    id = 9103201
    title = "EVTNAME9103201"
    desc = "EVTDESC9103201"
    picture = "homesteading"
    fire_only_once = yes

    trigger = {
        OR = {
				tag = MEX tag = PEU tag = CLM tag = ARG tag = CHL tag = BRZ
				tag = URU tag = PRG tag = BOL tag = GCO tag = CBA tag = PTR
				tag = DOM tag = HAI tag = TEX tag = CAL
			}
        has_country_modifier = the_colonisation_law
        citizens_rights = all_voting_pops
        NOT = { has_country_modifier = the_open_republic }
    }
    mean_time_to_happen = { months = 8 }

    option = {
        name = "EVTOPTA9103201"
        add_country_modifier = { name = the_open_republic duration = -1 }
        prestige = 10
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 1 }
    }
}

country_event = {
    id = 9103200
    title = "EVTNAME9103200"
    desc = "EVTDESC9103200"
    picture = "homesteading"
    fire_only_once = yes

    trigger = {
        OR = {
				tag = MEX tag = PEU tag = CLM tag = ARG tag = CHL tag = BRZ
				tag = URU tag = PRG tag = BOL tag = GCO tag = CBA tag = PTR
				tag = DOM tag = HAI tag = TEX tag = CAL
			}
        has_country_modifier = the_colonisation_law
        war = no
        NOT = { war = yes }
        average_militancy = 2
        NOT = { has_country_modifier = a_generation_of_peace }
    }
    mean_time_to_happen = { months = 90 }

    option = {
        name = "EVTOPTA9103200"
        add_country_modifier = { name = a_generation_of_peace duration = -1 }
        prestige = 15
        any_pop = { militancy = -2 consciousness = 1 }
    }
}
""")
loc("EVTNAME9103200", "A Generation Without a War")
loc("EVTDESC9103200",
    "No foreign army on the soil, no pronunciamiento in the capital and no province in "
    "revolt, for long enough that a man who was born at the beginning of it is old "
    "enough to farm. It is the first time this has happened here since the viceroys, "
    "and the people who notice first are the shipping agents in Hamburg and Le Havre, "
    "who have been telling enquirers for twenty years that the land is excellent and "
    "the government is a lottery. They have stopped saying the second half.")
loc("EVTOPTA9103200", "Peace, long enough to be believed.")
loc("EVTNAME9103201", "A Country They Can Belong To")
loc("EVTDESC9103201",
    "A German who lands at Veracruz and takes the land grant becomes a citizen of this "
    "republic with the same rights as a man born in Guanajuato, which is more than the "
    "country to the north offers the Irish and a great deal more than the one he left "
    "offered him. The newspapers in Hamburg have begun printing the terms beside the "
    "American ones, in the same column, and the comparison does not go the way the "
    "consul in New Orleans expected.")
loc("EVTOPTA9103201", "Citizens, not guests.")
log["events"] += 1

wr(f"{MOD}/events/1800_Mexico_Late.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_Mexico_Late.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/44_mexico_late.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
