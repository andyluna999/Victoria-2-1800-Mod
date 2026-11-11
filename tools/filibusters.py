"""The American tide: a frontier that fills from the east, one band at a time.

**The settlers are moved, not hoped for.** Victoria II cannot create a pop -- there is
no `add_pop` anywhere in three thousand events -- but it can move one, and HPM moves
pops constantly: the Trail of Tears, the Boer trek, the Polish and Ottoman population
exchanges all use `move_pop`. So each band, when it opens, physically walks American
farmers out of the band behind it into the new country, in waves, over years.

That makes the tide deterministic and culture-controlled. Raising a province's
attraction and trusting the engine's migration would have delivered Englishmen,
Germans or nobody at all, and would never have crossed the Mexican border, because
Victoria II sends emigrants only to countries that accept their culture -- which New
Spain does not. Dixie moves west because we walk it west.

Nothing here reuses the civil war machinery. The Spanish American risings are a
national question settled by armies; this is demography, and it ends in rebellion only
because people who are already living somewhere decide they would rather govern it.

**The chain.** Victoria II moves pops by its own rules and has no notion of geography,
so left alone it will put a Yankee in Monterey in 1808. The frontier is therefore
opened in bands, each shut until its year, and a province that is shut attracts
nobody:

    1805  Louisiana and the lower Mississippi
    1812  Arkansas, the Osage country, the Red River
    1820  east Texas -- the Brazos and the Trinity
    1828  San Antonio and the Nueces
    1836  New Mexico, the Gila, the Paso del Norte
    1845  California

**The curve is logistic, not exponential.** Each band pulls hard when it opens and
stops pulling once it has filled, so growth flattens between bands and steepens only
when the next one opens. That is a staircase approximating a logistic and it is what
westward settlement actually looked like: Missouri fills, nothing happens for a
decade, then Texas starts.

**And the dates are not fixed.** They are the latest a band can open. A viceroyalty
that admits the neutral traders, invites the empresarios, or lets the presidio line
rot opens the next band years early, and one that garrisons the north and keeps the
border closed can hold a band shut past its date. California at 1845 is the reward for
governing the north well; California at 1835 is the consequence of not.

**What the settlers do.** Nothing, for a long time. They farm, they outnumber the
people who were there, and when enough of them are in one place and the garrison is
thin, `nationalist_rebels` of their own culture rise with an occupation multiplier of
five. Hold a province past the threshold and the republic forms -- Texas, California,
the Rio Grande, Deseret -- with Mexico keeping its cores, because Mexico never
conceded any of it.
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

# where each band draws its settlers from: the band immediately behind it
SOURCE = {1812: [139, 140, 142, 146], 1820: [143, 167, 146, 144],
          1828: [132, 133], 1836: [137, 138, 133], 1845: [137, 102, 2143],
          # the northern road
          1810: [163, 167, 146], 1818: [150, 151, 153], 1830: [123, 126, 154],
          1840: [120, 155, 121], 1848: [106, 112, 116]}

# Which culture walks which road. The southern road out of Louisiana is Dixie; the
# northern one out of Ohio and Illinois is Yankee. That division is the reason Texas
# joined the Confederacy and Kansas bled over the question.
ROAD = {1812: "dixie", 1820: "dixie", 1828: "dixie", 1836: "dixie", 1845: "dixie",
        1810: "yankee", 1818: "yankee", 1830: "yankee", 1840: "yankee", 1848: "yankee"}

# band year -> (provinces, name, the republic it can produce)
BANDS = [
 (1805, [139, 140, 141, 142, 146, 144], "the Lower Mississippi", None),
 (1812, [143, 167, 128, 129],           "the Arkansas and the Osage country", None),
 (1820, [132, 133],                     "the Brazos and the Trinity", "TEX"),
 (1828, [137, 138],                     "San Antonio and the Nueces", "TEX"),
 (1836, [103, 104, 102, 2143],          "New Mexico and the Gila", "RGR"),
 (1845, [90, 89, 87, 84],               "California", "CAL"),
 # the northern road, up the Ohio and out along the Platte
 (1810, [150, 151, 153],                "Missouri and the Iowa country", None),
 (1818, [123, 126, 154],                "the Platte and the Kansas", None),
 (1830, [120, 155, 121, 122],           "the Dakota country", None),
 (1840, [106, 112, 116, 113],           "the high plains and the Powder River", None),
 (1848, [97, 91, 81, 78],               "Oregon and the Great Basin", None),
]

MODS = """
the_frontier_is_open = {
\ticon = 4
\timmigrant_attract = 3.0
\tlocal_RGO_output = 0.1
\tpopulation_growth = 0.002
}

the_frontier_has_filled = {
\ticon = 4
\timmigrant_attract = 0.2
}

the_presidio_line = {
\ticon = 2
\timmigrant_attract = -1.5
\timmigrant_push = 0.3
\tlocal_rgo_output = -0.05
}

the_empresario_grants = {
\ticon = 8
\ttax_efficiency = 0.1
\tglobal_immigrant_attract = 0.4
\tcore_pop_consciousness_modifier = 0.5
}

the_border_arranged = {
\ticon = 8
\tglobal_immigrant_attract = -0.3
\tdiplomatic_points_modifier = 0.2
\tcore_pop_militancy_modifier = -0.5
}

the_filibusters = {
\ticon = 1
\tcore_pop_militancy_modifier = 1.0
\tglobal_immigrant_attract = 0.3
\tsupply_consumption = 0.1
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_frontier_is_open" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 6

HOLDERS = ("NSP", "MEX", "COM", "OSA", "APA", "NAV", "ARI", "SIO", "PAW", "CRA")
ANY = "OR = { " + " ".join(f"tag = {t}" for t in HOLDERS) + " }"

# --- a band opens -------------------------------------------------------------------
for n, (yr, provs, name, rep) in enumerate(BANDS):
    # two ids per band, eleven bands: 9102500-9102521
    eid = 9102500 + n * 2
    # a band opens early if the border has been left open; late if the presidios hold
    early = ("        OR = {\n"
             f"            year = {yr}\n"
             "            AND = {\n"
             f"                year = {yr - 8}\n"
             "                has_global_flag = h18_the_border_is_open\n"
             "            }\n"
             "        }\n")
    grant = "".join(f"        {p} = {{ add_province_modifier = "
                    f"{{ name = the_frontier_is_open duration = 5475 }} }}\n"
                    for p in provs)
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "pioneer_wagons"
    fire_only_once = yes

    trigger = {{
        tag = USA
        # No Purchase, no road. The staging ground is the lower Mississippi and the
        # Missouri, and if those are still Spanish or French the tide never starts.
        has_global_flag = h18_louisiana_purchase
        owns = 146
{early}        NOT = {{ has_global_flag = h18_band_{yr} }}
    }}
    mean_time_to_happen = {{ months = 6 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_global_flag = h18_band_{yr}
{grant}        any_pop = {{
            limit = {{ OR = {{ has_pop_culture = yankee has_pop_culture = dixie }} }}
            consciousness = 1
        }}
    }}
}}

country_event = {{
    id = {eid + 1}
    title = "EVTNAME{eid + 1}"
    desc = "EVTDESC{eid + 1}"
    picture = "homesteading"
    fire_only_once = yes

    trigger = {{
        tag = USA
        has_global_flag = h18_band_{yr}
    }}
    mean_time_to_happen = {{ months = 150 }}

    option = {{
        name = "EVTOPTA{eid + 1}"
{"".join(f"        {p} = {{ remove_province_modifier = the_frontier_is_open }}" + chr(10) for p in provs)}{"".join(f"        {p} = {{ add_province_modifier = {{ name = the_frontier_has_filled duration = -1 }} }}" + chr(10) for p in provs)}    }}
}}
""")
    loc(f"EVTNAME{eid}", f"The Road Opens: {name}")
    loc(f"EVTDESC{eid}",
        "The wagons have reached country nobody from the States had any business in "
        "ten years ago. They are not an expedition and nobody sent them: they are "
        "families, with ploughs and children and an unshakeable conviction that empty "
        "land belongs to whoever works it. Whose flag flies over it is a question they "
        "expect to be settled later and in their favour.")
    loc(f"EVTOPTA{eid}", "Let them go west.")

    # the waves: American farmers walked out of the band behind this one, a few at a
    # time over a decade, which is how a frontier actually fills
    src = SOURCE.get(yr)
    if src:
        for w in range(3):
            wid = 9102600 + n * 4 + w
            # one source province per wave, emptied the way HPM empties one
            sp = src[w % len(src)]
            moves = (f"        {sp} = {{\n"
                     f"            any_pop = {{\n"
                     f"                limit = {{ has_pop_culture = {ROAD.get(yr, 'dixie')} }}\n"
                     f"                move_pop = {provs[w % len(provs)]}\n"
                     f"            }}\n"
                     f"        }}\n")
            EV.append(f"""country_event = {{
    id = {wid}
    title = "EVTNAME{wid}"
    desc = "EVTDESC{wid}"
    picture = "pioneer_wagons"
    fire_only_once = yes

    trigger = {{
        tag = USA
        has_global_flag = h18_band_{yr}
    }}
    mean_time_to_happen = {{ months = {28 + w * 34} }}

    option = {{
        name = "EVTOPTA{wid}"
{moves}    }}
}}
""")
            loc(f"EVTNAME{wid}", f"Wagons West: {name}")
            loc(f"EVTDESC{wid}",
                "Another season, another few hundred families off the end of the road, "
                "selling up in country that was the frontier ten years ago to buy "
                "country that is the frontier now. They take the seed corn, the plough "
                "and the family Bible, and they leave behind a farm somebody else will "
                "buy for the same reason.")
            loc(f"EVTOPTA{wid}", "West, and west again.")
            log["migration waves"] += 1
    loc(f"EVTNAME{eid + 1}", f"The Country Fills: {name}")
    loc(f"EVTDESC{eid + 1}",
        "The good land is taken, the prices have risen, and the men arriving now find "
        "the choice bottoms already fenced. The traffic does not stop so much as turn: "
        "whoever is still coming will keep going, past this, to wherever the next "
        "unfenced country is.")
    loc(f"EVTOPTA{eid + 1}", "They will move on.")
    log["bands"] += 1

# --- what opens a band early --------------------------------------------------------
DEC.append("""\tinvite_the_empresarios = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = { tag = NSP tag = MEX }
\t\t\tyear = 1820
\t\t\tNOT = { has_country_modifier = the_empresario_grants }
\t\t\tNOT = { has_global_flag = h18_the_border_is_open }
\t\t}
\t\tallow = { war = no }
\t\teffect = {
\t\t\tset_global_flag = h18_the_border_is_open
\t\t\tadd_country_modifier = { name = the_empresario_grants duration = -1 }
\t\t\ttreasury = 8000
\t\t\tany_pop = { limit = { has_pop_culture = criollo } consciousness = 1 }
\t\t}
\t\tai_will_do = { factor = 3 }
\t}

\tman_the_presidio_line = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = { tag = NSP tag = MEX }
\t\t\tNOT = { has_country_flag = h18c_presidios_manned }
\t\t}
\t\tallow = { money = 14000 war = no }
\t\teffect = {
\t\t\tset_country_flag = h18c_presidios_manned
\t\t\ttreasury = -14000
\t\t\tclr_global_flag = h18_the_border_is_open
\t\t\t137 = { add_province_modifier = { name = the_presidio_line duration = -1 } }
\t\t\t133 = { add_province_modifier = { name = the_presidio_line duration = -1 } }
\t\t\t103 = { add_province_modifier = { name = the_presidio_line duration = -1 } }
\t\t\t102 = { add_province_modifier = { name = the_presidio_line duration = -1 } }
\t\t\t2143 = { add_province_modifier = { name = the_presidio_line duration = -1 } }
\t\t}
\t\tai_will_do = { factor = 2 }
\t}

\tarrange_the_border = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tOR = { tag = NSP tag = MEX }
\t\t\tyear = 1819
\t\t\t# Only a government still answering to Madrid signs this. A republic that
\t\t\t# has already overthrown the viceroyalty keeps the Floridas on its map.
\t\t\tNOT = { has_country_flag = h18c_viceroyalty_fallen }
\t\t\tNOT = { has_country_modifier = the_border_arranged }
\t\t}
\t\tallow = { war = no USA = { war = no } }
\t\teffect = {
\t\t\tset_global_flag = h18_the_border_arranged
\t\t\tadd_country_modifier = { name = the_border_arranged duration = -1 }
\t\t\t# the Floridas and everything east of the Sabine
\t\t\tUSA = {
\t\t\t\t197 = { secede_province = THIS add_core = THIS }
\t\t\t\t198 = { secede_province = THIS add_core = THIS }
\t\t\t\t199 = { secede_province = THIS add_core = THIS }
\t\t\t\t200 = { secede_province = THIS add_core = THIS }
\t\t\t\t194 = { secede_province = THIS add_core = THIS }
\t\t\t}
\t\t\t197 = { remove_core = NSP }
\t\t\t198 = { remove_core = NSP }
\t\t\t199 = { remove_core = NSP }
\t\t\t200 = { remove_core = NSP }
\t\t\t194 = { remove_core = NSP }
\t\t\tUSA = {
\t\t\t\tadd_country_modifier = { name = the_border_arranged duration = -1 }
\t\t\t\trelation = { who = THIS value = 80 }
\t\t\t}
\t\t\tprestige = -5
\t\t\tany_pop = { limit = { has_pop_culture = criollo } militancy = 2 }
\t\t}
\t\tai_will_do = { factor = 4 }
\t}
""")
loc("invite_the_empresarios_title", "Invite the Empresarios")
loc("invite_the_empresarios_desc",
    "Grants of land in Texas to contractors who will bring settlers, on terms: they "
    "become Catholic, they swear to this government, they bring no slaves. The "
    "frontier is empty, the Comanche raid it at will, and a colony of farmers who pay "
    "taxes is worth more than a wilderness that does not. Every one of the conditions "
    "will be ignored and everyone signing knows it, but the revenue is immediate and "
    "the problem is twenty years away.")
loc("man_the_presidio_line_title", "Man the Presidio Line")
loc("man_the_presidio_line_desc",
    "Garrisons at San Antonio, Bexar, Santa Fe, Tucson and the Paso, properly paid for "
    "once instead of promised annually. It closes the border to anyone arriving "
    "without leave and it costs what three campaigns in the south would cost. The "
    "regiments that go north are the regiments that are not available to put down "
    "anything else.")
loc("arrange_the_border_title", "Arrange the Border: the Adams-Onis Treaty")
loc("arrange_the_border_desc",
    "The Floridas and everything east of the Sabine, in exchange for Washington giving "
    "up the pretence that Texas was ever part of Louisiana. We concede what we have "
    "not been able to garrison since Jackson marched into Pensacola and hanged two "
    "British subjects without asking anybody. The men who negotiate it will be accused "
    "of giving away an empire, which is true, and of giving away an empire we "
    "possessed, which is not.")
log["decisions"] = 3

# --- the filibuster republics -------------------------------------------------------
REPUBLICS = [("TEX", [132, 133, 137, 138], "Texas"),
             ("CAL", [90, 89, 87, 84], "California"),
             ("RGR", [103, 104, 102, 2143], "the Rio Grande")]
for n, (tag, provs, name) in enumerate(REPUBLICS):
    eid = 9102590 + n
    held = "\n".join(f"            {p} = {{ controlled_by = REB }}" for p in provs[:2])
    # The acquire idiom, in the new republic's own scope: `secede_province = THIS`
    # takes a province whoever holds it, and several of these are Comanche or Apache
    # rather than Mexican. A country cannot hand over land it does not own.
    take = (f"        {tag} = {{\n"
            + "".join(f"            {p} = {{ secede_province = THIS add_core = THIS }}\n"
                      for p in provs)
            + "        }\n")
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "1854_Alamo"
    fire_only_once = yes

    trigger = {{
        OR = {{ tag = NSP tag = MEX }}
        NOT = {{ exists = {tag} }}
        OR = {{
{held}
        }}
    }}
    mean_time_to_happen = {{ months = 14 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_global_flag = h18_{tag.lower()}_declared
        {tag} = {{ set_country_flag = h18c_independent }}
{take}        prestige = -15
        badboy = -2
        USA = {{ relation = {{ who = THIS value = -40 }} }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 3 consciousness = 2 }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", f"The Republic of {name}")
    loc(f"EVTDESC{eid}",
        "They have held the country for a year and a half, elected a convention, "
        "written a constitution in English and raised a flag nobody has seen before. "
        "Our cores are not renounced and never will be -- no government here could "
        "survive conceding them -- but there is no army within six hundred miles of "
        "the place and the men who would have to march there are needed elsewhere. "
        "Washington has expressed regret and will recognise it within the year.")
    loc(f"EVTOPTA{eid}", "We do not concede it. We cannot reach it.")
    log["republics"] += 1

# --- the filibusters themselves rise out of the settlers ----------------------------
s = rd(f"{MOD}/common/rebel_types.txt")
if "the settlers themselves" not in s:
    m = re.search(r"^nationalist_rebels\s*=\s*\{", s, re.M)
    i = m.end(); d = 1
    while i < len(s) and d:
        if s[i] == "{": d += 1
        elif s[i] == "}": d -= 1
        i += 1
    body = s[m.end():i-1]
    sp = re.search(r"spawn_chance\s*=\s*\{", body)
    add = ("\n        # the settlers themselves: an American pop on Mexican soil, in a\n"
           "        # province the frontier has opened, with no presidio on it\n"
           "        modifier = {\n            factor = 3\n"
           "            OR = { has_pop_culture = yankee has_pop_culture = dixie\n"
           "                   has_pop_culture = texan }\n"
           "            location = {\n"
           "                has_province_modifier = the_frontier_is_open\n"
           "                NOT = { has_province_modifier = the_presidio_line }\n"
           "            }\n        }\n"
           "        modifier = {\n            factor = 0.3\n"
           "            location = { has_province_modifier = the_presidio_line }\n        }\n")
    nb = body[:sp.end()] + add + body[sp.end():]
    wr(f"{MOD}/common/rebel_types.txt", s[:m.end()] + nb + s[i-1:])
    log["filibuster rebels wired"] = 1

wr(f"{MOD}/events/1800_Filibusters.txt", "\n".join(EV))
wr(f"{MOD}/decisions/1800_Filibusters.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/33_filibusters.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
