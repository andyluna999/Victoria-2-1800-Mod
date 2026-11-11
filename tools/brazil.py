"""Brazil: a court in flight, a co-equal kingdom, and an empire nobody intended.

Brazil never became the Empire of Brazil in any playthrough. The two decisions that
were supposed to produce it -- the Prince remaining or obeying the Cortes -- set flags
and modifiers and never changed the tag, so the State of Brazil stayed a Portuguese
viceroyalty to 1936 while HPM's own localisation sat there with
`BRZ_absolute_monarchy = The Empire of Brazil` waiting for a country to use it.

The sequence is the strangest in the hemisphere and the only one that ends in a crown.

  **1807.** Junot's columns are three days from Lisbon and the entire Portuguese court
  -- the Prince Regent, the mad Queen, fifteen thousand people, the treasury, the
  archives and the library -- boards the fleet under Royal Navy escort and sails for
  Rio. It is the only time in history a European monarchy moved to its colony.

  **1815.** Brazil is raised to a kingdom co-equal with Portugal, partly because the
  Congress of Vienna could not receive a monarch who ruled from a colony. The
  arrangement everyone treated as temporary has produced a capital in the southern
  hemisphere and a Brazilian court that has no intention of going back to being
  governed from the Tagus.

  **1820-21.** The Porto revolution demands a constitution and the King's return, and
  that the colonial arrangements be wound back. Joao VI sails. He leaves his son Pedro
  as regent and, by several accounts, tells him that if Brazil is going to separate he
  had better put the crown on his own head before some adventurer does.

  **January 1822.** The Cortes orders Pedro home too. He answers in one word -- *fico*,
  I remain -- and in September, on the banks of the Ipiranga, draws his sword.

So the player gets the fork that mattered: obey the Cortes and Brazil goes back in the
box, or remain and become the only monarchy the Americas produced that lasted.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import os, collections

MOD = _BUILD
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

MODS = """
the_court_in_rio = {
\ticon = 8
\ttax_efficiency = 0.2
\tadministrative_efficiency_modifier = 0.2
\tglobal_immigrant_attract = 0.4
\tprestige = 0.5
\tresearch_points_modifier = 0.1
}

the_co_equal_kingdom = {
\ticon = 8
\tcore_pop_consciousness_modifier = 1.0
\tdiplomatic_points_modifier = 0.25
\ttax_efficiency = 0.15
}

the_recolonisation = {
\ticon = 1
\tcore_pop_militancy_modifier = 3.0
\ttax_efficiency = -0.2
\tglobal_immigrant_attract = -0.4
}

the_empire_of_brazil = {
\ticon = 8
\tcore_pop_militancy_modifier = -2.0
\tprestige = 1.0
\tglobal_assimilation_rate = 0.3
\tadministrative_efficiency_modifier = 0.15
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_court_in_rio" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 4

def ev(eid, body, title, desc, opts):
    EV.append(body)
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    for k, v in opts.items(): loc(k, v)
    log["events"] += 1

# --- 1807: the court sails ------------------------------------------------------------
# --- 1807: Junot marches, which is why the court sails -----------------------------------
ev(9102799, """country_event = {
    id = 9102799
    title = "EVTNAME9102799"
    desc = "EVTDESC9102799"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = FRA
        year = 1807
        NOT = { year = 1812 }
        NOT = { has_global_flag = h18_junot_marches }
    }
    mean_time_to_happen = { months = 6 }

    option = {
        name = "EVTOPTA9102799"
        set_global_flag = h18_junot_marches
        badboy = 2
        war = {
            target = POR
            attacker_goal = { casus_belli = cut_down_to_size }
            defender_goal = { casus_belli = status_quo }
            call_ally = yes
        }
    }
}
""", "Portugal Will Close Its Ports",
"The Continental System has one hole in it and the hole is Lisbon. Portugal has been "
"asked to close its ports to British shipping, seize British property and declare war "
"on its ally of four hundred years, and has spent five months producing elegant "
"replies that concede the first two in principle and the third never. Junot is at "
"Bayonne with twenty-five thousand men, and the road to Lisbon is three weeks in good "
"weather.",
{"EVTOPTA9102799": "Then he marches."})


ev(9102800, """country_event = {
    id = 9102800
    title = "EVTNAME9102800"
    desc = "EVTDESC9102800"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = EBR
        year = 1807
        NOT = { year = 1815 }
        OR = {
            has_global_flag = h18_junot_marches
            POR = { war = yes }
        }
    }
    mean_time_to_happen = { months = 3 }

    option = {
        name = "EVTOPTA9102800"
        set_global_flag = h18_the_court_in_rio
        set_country_flag = h18b_court_arrived
        add_country_modifier = { name = the_court_in_rio duration = -1 }
        capital = 2447
        prestige = 20
        any_pop = { limit = { has_pop_culture = portuguese } consciousness = 2 }
    }
}
""", "The Court Sails for Rio",
"Junot is three days from Lisbon and the entire court is going aboard: the Prince "
"Regent, the Queen who has not been sane in fourteen years, fifteen thousand "
"courtiers and clerks, the treasury, the archives and the royal library, under escort "
"of a British squadron that has been waiting in the Tagus for exactly this. No "
"European monarchy has ever moved to its own colony. By the time anyone has worked "
"out what it means, the capital of the Portuguese empire will be in the southern "
"hemisphere.",
{"EVTOPTA9102800": "The throne goes where the King goes."})

# --- 1815: the co-equal kingdom --------------------------------------------------------
ev(9102801, """country_event = {
    id = 9102801
    title = "EVTNAME9102801"
    desc = "EVTDESC9102801"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = EBR
        year = 1815
        NOT = { year = 1821 }
        has_country_flag = h18b_court_arrived
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9102801"
        set_country_flag = h18b_co_equal
        add_country_modifier = { name = the_co_equal_kingdom duration = -1 }
        prestige = 15
        POR = { relation = { who = THIS value = 40 } }
        any_pop = { limit = { has_pop_culture = brasileiro } consciousness = 2 militancy = -2 }
    }
}
""", "The United Kingdom of Portugal, Brazil and the Algarves",
"Brazil is raised to a kingdom co-equal with Portugal, for reasons that are mostly "
"about the Congress of Vienna: the powers could not comfortably receive a monarch who "
"ruled from a colony, and the difficulty was solved by the colony ceasing to be one. "
"Lisbon is told it is a formality. Nobody in Rio treats it as one, and the men who "
"have spent eight years running an empire from here can see precisely what has just "
"been conceded.",
{"EVTOPTA9102801": "Not a colony. A kingdom."})

# --- 1820-21: the Cortes recalls the King -----------------------------------------------
ev(9102802, """country_event = {
    id = 9102802
    title = "EVTNAME9102802"
    desc = "EVTDESC9102802"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = EBR
        year = 1820
        NOT = { year = 1826 }
        has_country_flag = h18b_co_equal
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9102802"
        set_country_flag = h18b_regency
        prestige = 5
        any_pop = { limit = { has_pop_culture = brasileiro } consciousness = 3 }
        POR = { relation = { who = THIS value = -30 } }
    }
}
""", "The Cortes Recalls the King",
"Porto has risen for a constitution and the Cortes wants the King home and the "
"colonial arrangements wound back -- Brazil returned to the condition it was in before "
"the court arrived, with its ports closed and its courts referred to Lisbon. Joao "
"sails. He leaves his son Pedro behind as regent and, by more than one account, tells "
"him that if this country is going to separate itself he had better put the crown on "
"his own head before some adventurer does it for him.",
{"EVTOPTA9102802": "The Prince remains as regent."})

# --- 1822: Fico, and the Empire ----------------------------------------------------------
ev(9102803, """country_event = {
    id = 9102803
    title = "EVTNAME9102803"
    desc = "EVTDESC9102803"
    picture = "1822_iturbide_crowned"
    fire_only_once = yes

    trigger = {
        tag = EBR
        year = 1822
        NOT = { year = 1830 }
        has_country_flag = h18b_regency
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9102803"
        set_country_flag = h18b_fico
        set_global_flag = h18_the_empire_of_brazil
        all_core = { remove_core = EBR }
        change_tag = BRZ
        government = absolute_monarchy
        vote_franschise = landed_voting
        upper_house_composition = appointed
        add_country_modifier = { name = the_empire_of_brazil duration = -1 }
        remove_country_modifier = colonial_trade_monopoly
        prestige = 30
        POR = { relation = { who = THIS value = -120 } }
        any_pop = { limit = { has_pop_culture = brasileiro } militancy = -4 consciousness = 3 }
        any_pop = { limit = { has_pop_culture = portuguese } militancy = 3 }
        ai_chance = { factor = 85 }
    }
    option = {
        name = "EVTOPTB9102803"
        set_country_flag = h18b_obeyed
        add_country_modifier = { name = the_recolonisation duration = -1 }
        remove_country_modifier = the_court_in_rio
        remove_country_modifier = the_co_equal_kingdom
        capital = 519
        prestige = -15
        POR = { relation = { who = THIS value = 80 } }
        any_pop = { limit = { has_pop_culture = brasileiro } militancy = 6 consciousness = 4 }
        ai_chance = { factor = 15 }
    }
}
""", "Fico: I Remain",
"The Cortes has ordered the Prince home as well, to complete his education, which is "
"the phrase they chose. Eight thousand signatures have been delivered asking him to "
"stay and the Paulistas have sent word that if he goes they will not answer for what "
"happens next. He is twenty-three. The answer he gives is one word, and it is "
"reported in Lisbon before anyone there has grasped that a regent who refuses to come "
"home is no longer a regent.",
{"EVTOPTA9102803": "Fico. Independence or death.",
 "EVTOPTB9102803": "I am my father's son and the Cortes is my father's."})

# --- the Prince decisions are superseded -------------------------------------------------
f = f"{MOD}/decisions/1800_Americas_Choices.txt"
if os.path.exists(f):
    s = rd(f)
    for name in ("the_prince_remains", "the_prince_sails_for_lisbon"):
        m = __import__("re").search(rf"\n\t{name} = \{{", s)
        if not m: continue
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        s = s[:m.start()] + s[i:]
        log["superseded decisions removed"] += 1
    wr(f, s)

wr(f"{MOD}/events/1800_Brazil.txt", "\n".join(EV))
wr(f"{MOD}/localisation/36_brazil.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<30}{v}")
