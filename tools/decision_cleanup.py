"""A decision is a standing policy. An event is a moment that arrives.

Nineteen decisions reached a New Spain player in one undifferentiated list, and ten of
them were not policies at all. A viceroy did not browse a menu and select "proclaim a
junta": the cabildo abierto convened, the question was put, and he answered it. The
Constitution of Cadiz did not appear in his options; it arrived by ship in a box.

Three were not even choices. The intendancy system was imposed in 1786, the Seminario
de Mineria opened in 1792 and the tobacco estanco had run since 1765 -- a viceroy in
1800 inherited all three, and offering them as decisions is like offering to found the
audiencia. They are applied at the start instead, where they belong.

Everything here preserves the flags and modifiers the old decisions set, because
nineteen other chains read them -- `h18c_independent` alone is tested thirty-four
times. What changes is how the player meets the question, not what answering it does.

What stays a decision, because it genuinely is one:

    Admit the Neutral Traders     the 1797 decree was suspended in 1799 and renewed in
                                  1801: a live question every year
    Expand the Colonial Militia   standing policy since 1762
    Fortify the Coast             standing policy
    Man the Presidio Line         standing policy
    Suppress the Juntistas        standing policy once there are juntistas
    Invite the Empresarios        standing policy once the frontier is open
    Bring the Militia into the    a choice inside a window, which is what a decision
      Capital                     is good at

What becomes an event, because it arrived:

    The Consolidacion             a royal decree of December 1804
    The Constitution of Cadiz     arrived by ship in 1812
    The Junta Question            1808-1810, when the King was taken
    Renouncing Madrid             a rupture
    Independence, kingdom or      one crisis, two answers
      republic
    Adams-Onis                    a negotiation Washington opened
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
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

VICE = ["NSP", "VPE", "VNG", "RDP", "CGC"]
ANY = "OR = { " + " ".join(f"tag = {t}" for t in VICE) + " }"

# --- 1. the three a viceroy inherits ---------------------------------------------------
EV.append(f"""country_event = {{
    id = 9102900
    title = "EVTNAME9102900"
    desc = "EVTDESC9102900"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        {ANY}
        NOT = {{ has_country_modifier = intendancy_system }}
    }}
    mean_time_to_happen = {{ days = 3 }}

    option = {{
        name = "EVTOPTA9102900"
        add_country_modifier = {{ name = intendancy_system duration = -1 }}
        add_country_modifier = {{ name = creole_university duration = -1 }}
        add_country_modifier = {{ name = estanco_del_tabaco duration = -1 }}
    }}
}}
""")
loc("EVTNAME9102900", "The Inheritance of the Bourbon Reforms")
loc("EVTDESC9102900",
    "The intendants have been collecting since 1786 and the old corregidores who used "
    "to sell office and squeeze the villages are gone, replaced by salaried men from "
    "Spain who are harder to bribe and much harder to like. The Seminario de Mineria "
    "has been teaching since ninety-two and its graduates are the best mining "
    "engineers in the world, all of them creoles, none of them eligible for the "
    "offices their education fits them for. And the tobacco estanco has been printing "
    "money for the Crown for thirty-five years. None of this is ours to decide. It is "
    "what we were handed.")
loc("EVTOPTA9102900", "We govern what our predecessors built.")
log["events"] += 1

# --- 2. the Consolidacion: a decree, not a menu item ------------------------------------
EV.append(f"""country_event = {{
    id = 9102901
    title = "EVTNAME9102901"
    desc = "EVTDESC9102901"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        {ANY}
        year = 1804
        NOT = {{ year = 1810 }}
        NOT = {{ has_country_flag = consolidacion_settled }}
    }}
    mean_time_to_happen = {{ months = 4 }}

    option = {{
        name = "EVTOPTA9102901"
        set_country_flag = consolidacion_settled
        set_country_flag = consolidacion_enforced
        change_variable = {{ which = separatism value = 20 }}
        treasury = 45000
        SPA = {{ treasury = 90000 relation = {{ who = THIS value = 40 }} }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 5 consciousness = 3 }}
        ai_chance = {{ factor = 40 }}
    }}
    option = {{
        name = "EVTOPTB9102901"
        set_country_flag = consolidacion_settled
        set_country_flag = consolidacion_evaded
        change_variable = {{ which = separatism value = -10 }}
        treasury = 6000
        SPA = {{ relation = {{ who = THIS value = -50 }} }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -2 }}
        ai_chance = {{ factor = 60 }}
    }}
}}
""")
loc("EVTNAME9102901", "The Consolidacion de Vales Reales")
loc("EVTDESC9102901",
    "A decree from Madrid, dated December, requiring the Church in the Americas to "
    "call in every mortgage and charitable loan it holds and remit the proceeds to the "
    "Crown. Those loans are the entire credit system of this kingdom: every hacienda, "
    "every mine, every mill is financed through a chaplaincy or a pious endowment, "
    "because there are no banks here and never have been. Calling them in at once "
    "will transfer perhaps ten million pesos to Spain and ruin most of the families "
    "who have been lending this government money for a century. It can be enforced to "
    "the letter, or it can be administered the way inconvenient decrees have always "
    "been administered here.")
loc("EVTOPTA9102901", "The King has asked. The King will be paid.")
loc("EVTOPTB9102901", "We obey, but we do not comply.")
log["events"] += 1

# --- 3. the Constitution arrives by ship -------------------------------------------------
EV.append(f"""country_event = {{
    id = 9102902
    title = "EVTNAME9102902"
    desc = "EVTDESC9102902"
    picture = "1812_cadiz_constitution"
    fire_only_once = yes

    trigger = {{
        {ANY}
        has_global_flag = h18_constitution_1812
        NOT = {{ has_country_flag = h18c_constitutional }}
        NOT = {{ has_country_flag = h18c_refused_constitution }}
        NOT = {{ has_country_flag = h18c_independent }}
    }}
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA9102902"
        set_country_flag = h18c_constitutional
        add_country_modifier = {{ name = constitutional_province duration = -1 }}
        government = prussian_constitutionalism
        vote_franschise = landed_voting
        political_reform = wealth_voting
        change_variable = {{ which = separatism value = -20 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -4 consciousness = 2 }}
        ai_chance = {{ factor = 70 }}
    }}
    option = {{
        name = "EVTOPTB9102902"
        set_country_flag = h18c_refused_constitution
        change_variable = {{ which = separatism value = 8 }}
        SPA = {{ relation = {{ who = THIS value = 30 }} }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 4 }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = -3 }}
        ai_chance = {{ factor = 30 }}
    }}
}}
""")
loc("EVTNAME9102902", "The Constitution Arrives from Cadiz")
loc("EVTDESC9102902",
    "It came in a box, off a ship, from a city under siege. Three hundred and eighty-"
    "four articles written by deputies who included twenty-odd Americans, declaring "
    "that sovereignty resides in the nation, that the Americas are not colonies but "
    "provinces, and that their inhabitants are Spaniards with the vote. It also "
    "excludes anyone of African descent from citizenship, which in this kingdom is a "
    "great many people, and the representation it offers works out to rather less than "
    "our population would suggest. Swearing it makes us a constitutional province of a "
    "nation whose King is a prisoner. Refusing it leaves us exactly what we were.")
loc("EVTOPTA9102902", "We swear it in the plaza, with the bells rung.")
loc("EVTOPTB9102902", "We will wait for the King to tell us what he thinks of it.")
log["events"] += 1

# --- 4. strip the decisions these replace -------------------------------------------------
RETIRE = ["establish_the_intendancies", "endow_the_royal_seminary", "the_tobacco_estanco",
          "enforce_the_consolidacion", "evade_the_consolidacion",
          "accept_the_constitution_of_cadiz", "refuse_the_constitution_of_cadiz"]
for f in sorted(glob.glob(f"{MOD}/decisions/1800_*.txt")):
    s = rd(f)
    n = 0
    for name in RETIRE:
        m = re.search(rf"\n\t{name} = \{{", s)
        if not m: continue
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        s = s[:m.start()] + s[i:]
        n += 1
        log["decisions retired"] += 1
    if n: wr(f, s)

# the numerals implied an order the list never showed
for f in glob.glob(f"{MOD}/localisation/*.csv"):
    s = rd(f)
    t = re.sub(r"^([a-z_0-9]+_title);(I{1,3}V?|IV)\. ", r"\1;", s, flags=re.M)
    if t != s:
        wr(f, t); log["roman numerals removed"] += len(re.findall(r";(I{1,3}V?|IV)\. ", s))

wr(f"{MOD}/events/1800_Decision_Cleanup.txt", "\n".join(EV))
wr(f"{MOD}/localisation/37_cleanup.csv",
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
