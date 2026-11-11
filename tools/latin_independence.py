"""The Spanish American wars of independence, 1809-1826.

Nothing of this existed. The colonies had decisions and flavour and no way to stop
being colonies: Mexico, Colombia, Argentina, Peru, Chile and Venezuela each had zero
regiments, so there was nothing to fight with and nothing to fight.

**How it works.** Independence runs through Victoria II's own rebel system rather than
through spawned armies, because the engine arms, supplies and commands rebels properly
and would do none of that for regiments conjured by an event. Each historical rising
drives militancy and consciousness up sharply in its viceroyalty; `independence_rebels`
form out of that and fight a real war with real armies. The player sits on one side of
it and chooses.

**The three states.** Every viceroyalty is a colony, a junta, or a republic, and the
decisions to move between them say what they cost:

  * **Colony.** Spanish subsidy, Spanish garrison, no war -- and the remittances, the
    trade monopoly, and criollo militancy climbing every year after 1814.
  * **Junta.** Keeps the revenue, avoids the war, governs "for Ferdinand". Spain treats
    it as rebellion from 1814, and you have armed your creoles to get there.
  * **Republic.** The money is yours. So is the blockade, the lack of recognition, and
    Morillo.

**The clock that makes it a gamble.** Morillo's expedition sails in 1815: ten thousand
five hundred men, the largest force Spain ever sent to the Americas. Riego's mutiny in
1820 cancels the second one -- the army assembled at Cádiz *to reconquer you* refuses
to embark. Survive 1815 to 1820 and you have won. Declare in 1810 and fold before
Morillo arrives and you have not.

**The liberators** arrive with the countries they make: Bolívar, San Martín, Sucre,
O'Higgins, Hidalgo, Morelos, Artigas, Páez, Santander, Iturbide. Bolívar's entry is
earlier and stronger if Pétion armed him at Les Cayes, which is a link the Haitian
chain already builds.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections

MOD = _BUILD
log = collections.Counter()
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

# viceroyalty -> (successor, year of its rising, name of the rising, flavour)
RISINGS = [
 ("NSP", "MEX", 1810, "The Grito de Dolores",
  "A parish priest at Dolores rang his church bell before dawn, told the Indians and "
  "mestizos of the Bajío that the gachupines had sold the kingdom to the French, and "
  "marched on Guanajuato under the banner of the Virgin of Guadalupe with eighty "
  "thousand people behind him and almost no muskets. The granary at Guanajuato was "
  "stormed and everyone inside it killed. The creoles who wanted autonomy are "
  "discovering what a rising in New Spain actually looks like, and most of them are "
  "going over to the viceroy.", 6, 4),
 ("VNG", "CLM", 1810, "The Twentieth of July",
  "A borrowed flower vase, a staged insult, and a crowd in the square at Bogotá that "
  "had been waiting for a reason. The cabildo has deposed the viceroy and constituted "
  "itself a junta of government. Cartagena has done the same, and will not take orders "
  "from Bogotá; nor will Socorro, nor Tunja. There are now several New Granadas and "
  "they have begun arguing before the Spanish have even left.", 5, 4),
 ("RDP", "ARG", 1810, "The May Revolution",
  "The cabildo abierto of Buenos Aires has voted that with the King a prisoner, "
  "authority returns to the people of the viceroyalty, and appointed a junta. It is "
  "careful to govern in Ferdinand's name. Nobody believes this, including the men who "
  "wrote it. Montevideo refuses to recognise them, Paraguay refuses, Upper Peru "
  "refuses, and the junta has sent armies to all three.", 5, 5),
 ("CGC", "CHL", 1810, "The First Junta at Santiago",
  "The cabildo abierto has taken the government from the captain-general and promised "
  "to hold it for the King. Within two years it will have a congress, a flag and a "
  "newspaper, and Carrera and O'Higgins will be fighting each other over which of them "
  "is the revolution.", 4, 4),
 ("VPE", "PEU", 1814, "The Rising at Cuzco",
  "The brothers Angulo and the cacique Pumacahua have taken Cuzco and proclaimed the "
  "Constitution of Cádiz -- which Ferdinand has just abolished -- against a viceroy who "
  "refuses to apply it. Peru is the loyal viceroyalty: it has the silver, the army and "
  "the bureaucracy, and the memory of Túpac Amaru is thirty years old and still fresh "
  "enough to frighten every creole landowner into the King's arms.", 3, 3),
]

# The risings used to be separate events that raised militancy and nothing else, and
# they carried the same titles as the civil wars that follow them -- two Grito de
# Dolores in one playthrough, one with the painting and one without. The civil war does
# both jobs now; these are gone.

# --- the three states, as decisions ----------------------------------------------------
COLONIES = "OR = { tag = NSP tag = VPE tag = VNG tag = RDP tag = CGC tag = CBA tag = PTR }"
SUCCESSOR = {"NSP": "MEX", "VPE": "PEU", "VNG": "CLM", "RDP": "ARG",
             "CGC": "CHL", "CBA": "CUB", "PTR": "PRI"}

DEC.append(f"""\tproclaim_the_junta = {{
\t\tpicture = administration
\t\tpotential = {{
\t\t\t{COLONIES}
\t\t\thas_country_flag = h18c_bayonne_known
\t\t\tNOT = {{ has_country_flag = h18c_junta_governs }}
\t\t\tNOT = {{ has_country_flag = h18c_independent }}
\t\t}}
\t\tallow = {{
\t\t\t# No militancy requirement. Convening a junta to get ahead of trouble is the
\t\t\t# historically interesting move and the old gate made it impossible: a viceroy
\t\t\t# who kept the public calm could not reach the one lever that would have saved
\t\t\t# him.
\t\t\talways = yes
\t\t}}
\t\teffect = {{
\t\t\tset_country_flag = h18c_junta_governs
\t\t\t# still the King's government, run by other men
\t\t\tvote_franschise = landed_voting
\t\t\tadd_country_modifier = {{ name = the_junta_governs duration = -1 }}
\t\t\t# A junta has to settle before it can become anything else. This runs for
\t\t\t# three years and the autonomous kingdom is barred while it does.
\t\t\tadd_country_modifier = {{ name = the_new_junta duration = 1095 }}
\t\t\tremove_country_modifier = colonial_trade_monopoly
\t\t\tSPA = {{ relation = {{ who = THIS value = -60 }} }}
\t\t\tany_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -3 consciousness = 3 }}
\t\t\tany_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = 4 }}
\t\t\tprestige = 5
\t\t}}
\t\tai_will_do = {{ factor = 2 }}
\t}}
""")
loc("proclaim_the_junta_title", "II. Proclaim a Junta of Government")
loc("proclaim_the_junta_desc",
    "To govern this kingdom in Ferdinand's name until he is restored, which is what "
    "Caracas said, and Buenos Aires, and Bogotá, and what every one of them meant "
    "something else by. The remittances to Madrid stop and the trade monopoly with "
    "them. So does any pretence that the Audiencia governs here. Spain will call it "
    "rebellion the moment it has an army to spare, and the creoles we arm to defend "
    "the junta are the men who will decide what comes after it.")

for vic, suc in SUCCESSOR.items():
    DEC.append(f"""\tdeclare_independence_{suc.lower()} = {{
\t\tpicture = administration
\t\tpotential = {{
\t\t\ttag = {vic}
\t\t\tNOT = {{ exists = {suc} }}
\t\t\tOR = {{
\t\t\t\thas_country_flag = h18c_junta_governs
\t\t\t\thas_country_flag = h18c_the_rising
\t\t\t}}
\t\t}}
\t\tallow = {{
\t\t\tyear = 1810
\t\t\taverage_consciousness = 3
\t\t}}
\t\teffect = {{
\t\t\tset_country_flag = h18c_independent
\t\t\tset_global_flag = h18_an_american_republic
\t\t\t# the viceroyalty ceases to exist, and so do its claims
\t\t\tall_core = {{ remove_core = {vic} }}
\t\t\tchange_tag = {suc}
\t\t\tgovernment = presidential_dictatorship
\t\t\tvote_franschise = landed_voting
\t\t\tadd_country_modifier = {{ name = the_war_of_independence duration = -1 }}
\t\t\tremove_country_modifier = colonial_trade_monopoly
\t\t\tSPA = {{
\t\t\t\trelation = {{ who = THIS value = -200 }}
\t\t\t\twar = {{
\t\t\t\t\ttarget = THIS
\t\t\t\t\tattacker_goal = {{ casus_belli = war_of_independence_cb }}
\t\t\t\t\tdefender_goal = {{ casus_belli = status_quo }}
\t\t\t\t\tcall_ally = yes
\t\t\t\t}}
\t\t\t}}
\t\t\tany_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -4 consciousness = 4 }}
\t\t\tprestige = 10
\t\t}}
\t\t# The player only. This decision converts the entire viceroyalty at a stroke:
\t\t# it is the viceroy himself declaring for the republic, which is a legitimate
\t\t# thing for a player to choose and a nonsense for the AI to do, because it
\t\t# skips the civil war and hands over the whole territory with no fighting --
\t\t# whole viceroyalties converting at once, which is what the playtest kept
\t\t# seeing. The AI's roads to independence are the civil war, which produces an
\t\t# enclave that has to win, and the negotiated settlements, which have to be
\t\t# earned.
\t\tai_will_do = {{ factor = 0 }}
\t}}
""")
    loc(f"declare_independence_{suc.lower()}_title", "IV. Independence as a Republic")
    loc(f"declare_independence_{suc.lower()}_desc",
        "No more juntas in the King's name. The remittances, the monopoly and the "
        "Audiencia go together, and so does the protection of the Spanish fleet: there "
        "will be a blockade, there will be no recognition from any court in Europe, and "
        "Spain will send an army as soon as the French are out of the peninsula. What "
        "we have instead is our own revenue, our own ports, and the men already under "
        "arms.")
log["decisions"] = len(DEC)

# --- Morillo, and Riego ---------------------------------------------------------------
EV.append("""country_event = {
    id = 9101560
    title = "EVTNAME9101560"
    desc = "EVTDESC9101560"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = SPA
        year = 1815
        NOT = { year = 1819 }
        # Morillo sailed because the colonies were in arms, not because anybody had
        # proclaimed a republic: Venezuela and New Granada were in open war and Madrid
        # sent ten thousand men to end it. Waiting on a republic meant the expedition
        # could never sail at all once the crisis was floored at 1820.
        OR = {
            has_global_flag = h18_spanish_america_in_arms
            has_global_flag = h18_an_american_republic
        }
        # Morillo sails under Ferdinand restored. The Trienio is what stops him, and
        # it has its own flag in the constitutional track.
        NOT = { has_global_flag = h18_trienio }
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9101560"
        set_global_flag = h18_morillo_sails
        add_country_modifier = { name = the_expeditionary_army duration = 2555 }
        treasury = -40000
        prestige = 10
        badboy = 2
    }
}
""")
loc("EVTNAME9101560", "Morillo's Expedition")
loc("EVTDESC9101560",
    "Ten thousand five hundred men and sixty transports, the largest force Spain has "
    "ever sent to the Americas, sailing for Cumaná under a general who learned his "
    "trade fighting the French in the mountains. His orders are to pacify Venezuela and "
    "New Granada and then go on to Buenos Aires. He has asked what he is to do about "
    "the creoles who merely wanted the Constitution, and has not been answered.")
loc("EVTOPTA9101560", "Pacify the Americas.")

EV.append("""country_event = {
    id = 9101561
    title = "EVTNAME9101561"
    desc = "EVTDESC9101561"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = SPA
        year = 1820
        NOT = { year = 1823 }
        has_global_flag = h18_trienio
    }
    mean_time_to_happen = { months = 3 }

    option = {
        name = "EVTOPTA9101561"
        set_global_flag = h18_riego_cancels_the_expedition
        remove_country_modifier = the_expeditionary_army
        prestige = -15
        any_country = {
            limit = { has_country_flag = h18c_independent }
            prestige = 10
            any_pop = { militancy = -3 }
        }
    }
}
""")
loc("EVTNAME9101561", "The Expedition Will Not Sail")
loc("EVTDESC9101561",
    "The second army for the Americas was assembled at Cádiz and has mutinied rather "
    "than embark. Riego proclaimed the Constitution to it on the parade ground at Las "
    "Cabezas and it cheered him. There will be no reconquest: there is no longer an "
    "army willing to attempt one, and the men who were to have sailed are marching on "
    "Madrid instead. Everything west of the Atlantic is lost, and it was lost in "
    "Andalusia.")
loc("EVTOPTA9101561", "Then the Americas are gone.")

# --- modifiers ---------------------------------------------------------------------------
MODS = """
the_rising = {
\ticon = 1
\tcore_pop_militancy_modifier = 1.5
\tcore_pop_consciousness_modifier = 1.0
\ttax_efficiency = -0.1
\tsupply_consumption = 0.1
}

the_junta_governs = {
\ticon = 8
\ttax_efficiency = 0.25
\tadministrative_efficiency_modifier = 0.15
\tcore_pop_consciousness_modifier = 1.0
\tmobilisation_size = 0.03
}

the_war_of_independence = {
\ticon = 1
\tmobilisation_size = 0.08
\tland_organisation = 0.1
\ttariff_efficiency_modifier = 0.3
\tglobal_immigrant_attract = -0.3
\twar_exhaustion = 0.5
}

the_expeditionary_army = {
\ticon = 2
\tmobilisation_size = 0.06
\tland_attack_modifier = 0.15
\tsupply_consumption = 0.2
\tmobilisation_economy_impact = 0.3
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_war_of_independence" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 4

# --- the liberators ------------------------------------------------------------------------
LIBERATORS = {
 "CLM": [("Simon Bolivar", 1819, "audacious", "natural_born_leader", 1.0),
         ("Francisco de Paula Santander", 1819, "expert", "gifted_administrator", 0.5),
         ("Antonio Jose de Sucre", 1821, "au_fait", "school_of_offense", 0.8)],
 "VNZ": [("Jose Antonio Paez", 1830, "implacable", "cavalry_school", 0.7)],
 "ARG": [("Jose de San Martin", 1816, "au_fait", "school_of_the_bayonet", 0.9),
         ("Manuel Belgrano", 1816, "earnest", "amateur", 0.4)],
 "CHL": [("Bernardo O'Higgins", 1818, "defiant", "exranker", 0.7),
         ("Jose Miguel Carrera", 1818, "vainglorious", "aristocrat", 0.4)],
 "MEX": [("Jose Maria Morelos", 1821, "relentless", "exranker", 0.8),
         ("Agustin de Iturbide", 1821, "arrogant", "war_college", 0.6),
         ("Vicente Guerrero", 1821, "persistant", "exranker", 0.6)],
 "PEU": [("Ramon Castilla", 1821, "balanced_p", "exranker", 0.5)],
 "URU": [("Jose Gervasio Artigas", 1828, "defiant", "cavalry_school", 0.7)],
}
for tag, rows in LIBERATORS.items():
    f = f"{MOD}/history/units/{tag}_oob.txt"
    body = rd(f) if os.path.exists(f) else ""
    have = set(re.findall(r'leader\s*=\s*\{[^}]*?name\s*=\s*"([^"]*)"', body, re.S))
    block = []
    for nm, yr, per, bak, pr in rows:
        if nm in have: continue
        block.append(f'leader = {{\n\tname = "{nm}"\n\tdate = {yr}.1.1\n\ttype = land\n'
                     f'\tpersonality = {per}\n\tbackground = {bak}\n\tprestige = {pr}\n}}')
        log["liberators"] += 1
    if block:
        wr(f, "# The men who made these countries, arriving with them.\n\n"
              + "\n".join(block) + "\n\n" + body.lstrip("\n"))

wr(f"{MOD}/events/1800_Latin_Independence.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_Latin_Independence.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/21_latin.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
