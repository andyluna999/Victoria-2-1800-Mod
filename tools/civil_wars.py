"""Independence as a civil war, which the viceroy can prevent and the player can join.

The first full run produced forty-two Jacobin risings and six independence rebellions
in New Spain and no Mexico at all. Leaving independence to Victoria II's rebel system
meant it never arrived: liberal rebels agitating for a constitution swamped the
national question, and the two never resolved into a country.

So independence is a civil war now, built the way HPM builds the American one --
`release_vassal`, a treasury and leadership for the new state, a declaration of war --
and the player picks a side at the moment it happens.

**It is preventable, and that is the whole game.** The Grito fires on 16 September 1810
only if separatism has reached thirty. A viceroy who swore the Constitution, stalled
the Consolidación, raised the militia and paid for garrisons can be sitting at twenty
when the date arrives, and the priest at Dolores rings his bell to a parish that does
not rise. Below the threshold a milder event fires instead: a conspiracy discovered, a
few men hanged, and the kingdom holds.

That is the incentive the viceroy should feel. Militarise, suppress, reform just enough
-- and the republic never happens. Let it slide and you are fighting your own
population with an army raised from it.

**The asymmetry carries through.** In New Spain and Peru the republic is born out of a
popular rising: it starts with more men and less money, the creoles mostly side with
the King, and it is a long bloody war. In Buenos Aires, Santiago and Bogotá the
cabildo takes the government: the republic starts solvent and organised, with the
creoles in it, and its problem is that its own provinces do not accept it either.
"""
import re, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

# What each rising actually held. This is the whole difference between a civil war and
# a handover: `release_vassal = MEX` gives Mexico every province it has a core on --
# seventy-nine of them, including Mexico City, Veracruz, California and Guatemala --
# and the war is over before it starts.
#
# Hidalgo held the Bajio: Guanajuato, Guadalajara, Zacatecas, Valladolid. He turned
# back from Mexico City at Las Cruces and never saw Veracruz. Buenos Aires held the
# city and the littoral; Upper Peru, Paraguay and Montevideo all refused it to its
# face. Santiago held the central valley and not Valdivia. Bogota held Cundinamarca
# while Cartagena ran its own junta and Popayan stayed royal. Cuzco held the southern
# sierra and Lima never wavered.
#
# So the republic is born as an enclave that has to win, which is what it was.
HELD = {
 "MEX": [2167, 2166, 2158, 2170, 2160, 2169],   # the Bajio and Guadalajara
 "ARG": [2348, 2361, 2362, 2360, 2379],         # Buenos Aires, the littoral, Cordoba
 "CHL": [2324, 2325, 2326, 2327, 2331],         # the central valley
 "CLM": [2247, 2249, 2248, 2250],               # Cundinamarca
 "PEU": [2302, 2303, 2304, 2299],               # Cuzco, Puno, Arequipa, Ayacucho
}

# viceroyalty, successor, year, kind, the rising's name
WARS = [
 ("NSP", "MEX", 1810, "popular", "The Grito de Dolores",
  "The priest at Dolores rang his church bell before dawn and told the Indians and "
  "mestizos of the Bajio that the gachupines had sold the kingdom to the French. "
  "Eighty thousand came, with machetes and slings and perhaps a thousand muskets "
  "between them, and the granary at Guanajuato was stormed and everyone inside it "
  "killed. This is not a cabildo voting itself into office. This is the thing every "
  "man of property in New Spain has been afraid of since Tupac Amaru, and it is here."),
 ("VPE", "PEU", 1814, "popular", "The Rising at Cuzco",
  "The Angulo brothers and the cacique Pumacahua hold Cuzco and have raised the "
  "southern sierra with them -- Indians, mestizos and a good many creoles who wanted "
  "the Constitution applied and have been told it no longer exists. Peru is the loyal "
  "viceroyalty. It has the silver, the army, the bureaucracy and the memory of 1780, "
  "and it has just discovered that none of those are the same as consent."),
 ("RDP", "ARG", 1810, "creole", "The May Revolution",
  "The cabildo abierto of Buenos Aires voted that authority returns to the people of "
  "the viceroyalty while the King is a prisoner, and appointed itself the government. "
  "Almost nobody has been killed. The men now in office are the merchants and militia "
  "colonels who were in office last month, which is precisely the point, and "
  "Montevideo, Asuncion and Upper Peru have all refused to take orders from them."),
 ("CGC", "CHL", 1810, "creole", "The First Junta at Santiago",
  "The cabildo has taken the government from the captain-general and promised to hold "
  "it for the King, which fooled nobody for very long. Within two years there will be "
  "a congress, a flag and a newspaper, and Carrera and O'Higgins will be fighting each "
  "other over which of them is the revolution."),
 ("VNG", "CLM", 1810, "creole", "The Twentieth of July",
  "A borrowed flower vase, a staged insult and a crowd in the square at Bogota that "
  "had been waiting for a reason. The cabildo has deposed the viceroy and made itself "
  "a junta. Cartagena has done the same and will not take orders from Bogota; nor will "
  "Socorro, nor Tunja. There are several New Granadas now and they began arguing "
  "before the Spanish had finished leaving."),
]

# Twenty, not thirty. Bayonne alone is worth twenty-five now, so a viceroyalty that
# learns the King is a prisoner and does nothing to calm itself crosses the line. One
# that swears the Constitution and proclaims a junta does not, which is the whole
# point: the civil war is the default and peace is the thing you have to buy.
# Twenty-five, against a Bayonne worth fifteen. The old pair -- Bayonne +25 against a
# threshold of 20 -- meant the rising was decided the moment the King was taken, and
# every lever that could have prevented it waited on a flag Bayonne itself set. A
# viceroy who had governed well for eight years arrived at the crisis with nothing
# banked. The reforms carry weight before 1808 now, so good government is a buffer the
# shock lands against instead of a thing that happens too late to matter.
THRESHOLD = 25

def civil_war(vic, suc, yr, kind, title, body):
    eid = 9101700 + len(EV) * 3
    popular = kind == "popular"
    # the men who actually led it, granted at the moment of proclamation
    GENERALS = {'MEX': [('Miguel Hidalgo', 'inspiring', 'priest'), ('Jose Maria Morelos', 'au_fait', 'natural_born_leader'), ('Vicente Guerrero', 'resourceful', 'guerilla_fighter')], 'PEU': [('Mateo Pumacahua', 'audacious', 'guerilla_fighter'), ('Ramon Castilla', 'balanced_p', 'exranker')], 'CLM': [('Simon Bolivar', 'audacious', 'natural_born_leader'), ('Francisco de Paula Santander', 'expert', 'gifted_administrator'), ('Antonio Jose de Sucre', 'au_fait', 'school_of_offense')], 'ARG': [('Jose de San Martin', 'au_fait', 'natural_born_leader'), ('Manuel Belgrano', 'inspiring', 'politician')], 'CHL': [("Bernardo O'Higgins", 'resourceful', 'exranker'), ('Jose Miguel Carrera', 'audacious', 'aristocrat')]}
    generals = "".join(
        f'        define_general = {{ name = "{n}" personality = {pe} '
        f'background = {bg} }}\n' for n, pe, bg in GENERALS.get(suc, []))
    # a popular rising wrecks the economy it rises in; a cabildo coup does not
    popular_flag = ("        set_country_flag = popular_insurrection\n"
                    if popular else "")
    # what the new republic starts with
    # seceding to a tag that does not yet exist brings it into being holding exactly
    # these provinces, and nothing else
    held = "".join(f"        {p} = {{ secede_province = {suc} add_core = {suc} }}\n"
                   for p in HELD[suc])
    money = 8000 if popular else 25000
    lead = 2 if popular else 4
    mob = "0.10" if popular else "0.05"
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {vic}
        year = {yr}
        NOT = {{ year = {yr + 3} }}
        check_variable = {{ which = separatism value = {THRESHOLD} }}
        NOT = {{ has_country_flag = h18c_independent }}
        NOT = {{ exists = {suc} }}
    }}
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_country_flag = h18c_civil_war
        set_country_flag = h18c_the_rising
{popular_flag}
        set_global_flag = h18_spanish_america_in_arms
{held}        {suc} = {{
            country_event = {eid + 1}
            treasury = {money}
            leadership = {lead}
            # the insurgent's advantage: ground it knows, a cause it believes, and
            # nowhere else to go. Every one of these wars was won by the side that
            # could keep losing battles and still be there the following spring.
            add_country_modifier = {{ name = the_long_insurgency duration = -1 }}
        }}
        # and the viceroyalty pays for fighting its own people
        add_country_modifier = {{ name = the_war_against_our_own duration = -1 }}
        war = {{
            target = {suc}
            attacker_goal = {{ casus_belli = war_of_independence_cb }}
            # The republic is not fighting to survive; it is fighting to take the
            # viceroyalty, every province of which it holds a core on.
            defender_goal = {{ casus_belli = status_quo }}
            # and the overlord comes in, because these wars were against Spain
            call_ally = yes
        }}
        # and only now: Spain is already a belligerent, so it stays in, but the
        # viceroyalty is no longer a satellite it can shelter behind after peace
        SPA = {{ release_vassal = THIS }}
        change_variable = {{ which = separatism value = 20 }}
        ai_chance = {{ factor = 100 }}
    }}
    option = {{
        name = "EVTOPTB{eid}"
        set_country_flag = h18c_went_over
        set_country_flag = h18c_the_rising
        set_global_flag = h18_spanish_america_in_arms
{held}        {suc} = {{
            country_event = {eid + 1}
            treasury = {money}
            leadership = {lead}
            add_country_modifier = {{ name = the_long_insurgency duration = -1 }}
        }}
        # the viceroyalty ceases to exist, and so do its claims
        all_core = {{ remove_core = {vic} }}
        change_tag = {suc}
        SPA = {{
            relation = {{ who = THIS value = -200 }}
            war = {{
                target = THIS
                attacker_goal = {{ casus_belli = war_of_independence_cb }}
                defender_goal = {{ casus_belli = status_quo }}
                call_ally = yes
            }}
        }}
        SPA = {{ release_vassal = THIS }}
        ai_chance = {{ factor = 0 }}
    }}
}}

country_event = {{
    id = {eid + 1}
    title = "EVTNAME{eid + 1}"
    desc = "EVTDESC{eid + 1}"
    picture = "administration"
    is_triggered_only = yes

    option = {{
        name = "EVTOPTA{eid + 1}"
{generals}        set_country_flag = h18c_independent
        set_country_flag = h18c_the_republic_declared
        government = presidential_dictatorship
        vote_franschise = landed_voting
        political_parties = harassment
        # It has no standing army -- orders of battle are read at the start of the
        # game and this country did not exist then -- so it has to raise one out of
        # the provinces it holds. Jingoism and the mobilisation bonus are what let it.
        war_policy = jingoism
        add_country_modifier = {{ name = {'the_army_of_the_people' if popular else 'the_republic_of_the_cabildo'} duration = -1 }}
        any_pop = {{ limit = {{ has_pop_culture = {'mestizo' if popular else 'criollo'} }} militancy = -4 consciousness = 4 }}
        prestige = 10
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", body)
    loc(f"EVTOPTA{eid}", "The kingdom will be held for the King.")
    loc(f"EVTOPTB{eid}", "Then we are no longer the King's.")
    loc(f"EVTNAME{eid + 1}", "A Republic in Arms")
    loc(f"EVTDESC{eid + 1}",
        "A government, a flag, a treasury of sorts and an army that is mostly "
        "enthusiasm. What it does not have is recognition from any court in Europe, a "
        "navy, or the faintest guarantee that it will exist in two years."
        if popular else
        "A government of the men who were already governing, with the revenue of the "
        "port, the militia already raised and the account books in order. What it does "
        "not have is agreement from a single province that was not consulted.")
    loc(f"EVTOPTA{eid + 1}", "Then it must be won.")
    log["civil wars"] += 1

    # the version where the viceroy has kept the kingdom quiet
    q = eid + 2
    EV.append(f"""country_event = {{
    id = {q}
    title = "EVTNAME{q}"
    desc = "EVTDESC{q}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {vic}
        year = {yr}
        NOT = {{ year = {yr + 3} }}
        NOT = {{ check_variable = {{ which = separatism value = {THRESHOLD} }} }}
    }}
    mean_time_to_happen = {{ months = 4 }}

    option = {{
        name = "EVTOPTA{q}"
        set_country_flag = h18c_conspiracy_broken
        set_country_flag = h18c_the_rising
        change_variable = {{ which = separatism value = 5 }}
        change_variable = {{ which = separatism_debt value = 5 }}
        prestige = 5
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 1 }}
    }}
}}
""")
    loc(f"EVTNAME{q}", "A Conspiracy Discovered")
    loc(f"EVTDESC{q}",
        "The corresponding society met in a house in Queretaro and one of its members "
        "went to the audiencia the same night. The priest who was to have raised the "
        "parishes is in a cell, the muskets have been found, and the thing is over "
        "before it began. It was closer than the proclamation posted this morning "
        "admits, and everyone who matters knows it.")
    loc(f"EVTOPTA{q}", "The kingdom holds.")
    log["conspiracies"] += 1

for vic, suc, yr, kind, title, body in WARS:
    civil_war(vic, suc, yr, kind, title, body)

MODS = """
the_army_of_the_people = {
\ticon = 1
\tmobilisation_size = 0.3
\tland_organisation = -0.15
\tsupply_consumption = 0.2
\ttax_efficiency = -0.2
\tcore_pop_militancy_modifier = -1.0
}

the_republic_of_the_cabildo = {
\ticon = 8
\tmobilisation_size = 0.2
\ttax_efficiency = 0.15
\tadministrative_efficiency_modifier = 0.1
\tcore_pop_consciousness_modifier = 1.5
\tland_organisation = -0.05
}

the_national_question = {
\ticon = 4
\tcore_pop_militancy_modifier = -1.0
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_army_of_the_people" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

# --- quiet the constitutional rebels while the national war is on ---------------------
# Forty-two Jacobin risings in New Spain drowned the national question. A colony
# fighting for its existence is not also fighting about the franchise.
s = rd(f"{MOD}/common/rebel_types.txt")
m = re.search(r"^liberal_rebels\s*=\s*\{", s, re.M)
if m and "the national question" not in s:
    i = m.end(); d = 1
    while i < len(s) and d:
        if s[i] == "{": d += 1
        elif s[i] == "}": d -= 1
        i += 1
    body = s[m.end():i-1]
    sp = re.search(r"spawn_chance\s*=\s*\{", body)
    add = ("\n        # the national question crowds out the constitutional one\n"
           "        modifier = {\n            factor = 0.05\n"
           "            country = { has_global_flag = h18_spanish_america_in_arms }\n"
           "            country = { OR = { tag = NSP tag = VPE tag = VNG tag = RDP\n"
           "                               tag = CGC tag = MEX tag = PEU tag = CLM\n"
           "                               tag = ARG tag = CHL } }\n        }\n")
    nb = body[:sp.end()] + add + body[sp.end():]
    wr(f"{MOD}/common/rebel_types.txt", s[:m.end()] + nb + s[i-1:])
    log["liberal rebels quieted in the Americas"] = 1

# Victoria II builds a war's name from its casus belli, substituting the defender's
# adjective. "$DEFENDER_ADJ$ War of Independence" gives the Mexican War of
# Independence, the Peruvian, the Chilean, and so on.
LOC.append(("WAR_OF_INDEPENDENCE_NAME", "$DEFENDER_ADJ$ War of Independence"))

wr(f"{MOD}/events/1800_Civil_Wars.txt", "\n".join(EV))
wr(f"{MOD}/localisation/23_civil_wars.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<40}{v}")
