"""The national question settles, or it does not.

A defeated insurgency is not a solved one, and a won independence is not automatically
a settled country. Both halves were missing.

**Settling.** Three conditions, and all three have to hold: the country is genuinely
independent -- not a vassal, not in anybody's sphere; it has passed real reforms; and
the bottom of its society is fed, with life needs at seven tenths, literacy at a
quarter, and militancy under four. Meet them and the national movement loses its
argument. It does not disappear: it becomes a liberal one. The men who wanted Mexico
to exist start wanting it to have a constitution, which is what actually happened in
1824 and again in 1833, and sets up the Reforma.

Mechanically the nationalist rebels stop spawning and the liberals pick up what they
were carrying, which is the honest way to say "the question changed".

**Not settling.** Fail any of the three and the question stays open. Separatism rebuilds
from where it was, and a second rising becomes possible -- the civil war events are no
longer once-only for a country that has been put down. Crushing Hidalgo bought eleven
years and produced Iturbide, and a player who wins in 1811 and governs badly should
meet the same thing in 1822.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import os, re, collections

MOD = _BUILD
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

AMERICAS = ("MEX", "PEU", "CLM", "ARG", "CHL", "VNZ", "ECU", "BOL", "URU", "PRG",
            "NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR", "BRZ")
ANY = "OR = { " + " ".join(f"tag = {t}" for t in AMERICAS) + " }"

MODS = """
the_national_question_settled = {
\ticon = 8
\tcore_pop_militancy_modifier = -2.5
\tglobal_assimilation_rate = 0.4
\tglobal_immigrant_attract = 0.3
\tcore_pop_consciousness_modifier = 1.0
\tdiplomatic_points_modifier = 0.2
}

the_question_remains_open = {
\ticon = 1
\tcore_pop_militancy_modifier = 1.0
\tcore_pop_consciousness_modifier = 0.5
\tglobal_assimilation_rate = -0.2
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_national_question_settled" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 2

EV.append(f"""country_event = {{
    id = 9102300
    title = "EVTNAME9102300"
    desc = "EVTDESC9102300"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        {ANY}
        has_country_flag = h18c_independent
        NOT = {{ has_country_flag = h18c_question_settled }}
        # genuinely its own country
        NOT = {{ is_vassal = yes }}
        NOT = {{ is_sphere_leader_of = THIS }}
        war = no
        # the bottom of society is fed, and reads
        poor_strata_life_needs = 0.7
        literacy = 0.25
        NOT = {{ average_militancy = 4 }}
        # and it has actually reformed something
        OR = {{
            political_parties = harassment
            political_parties = gerrymandering
            political_parties = non_secret_ballots
            political_parties = secret_ballots
        }}
        NOT = {{ vote_franschise = none_voting }}
    }}
    mean_time_to_happen = {{ months = 8 }}

    option = {{
        name = "EVTOPTA9102300"
        set_country_flag = h18c_question_settled
        set_global_flag = h18_a_national_question_settled
        remove_country_modifier = the_question_remains_open
        remove_country_modifier = the_war_of_independence
        add_country_modifier = {{ name = the_national_question_settled duration = -1 }}
        set_variable = {{ which = separatism value = 0 }}
        prestige = 20
        any_pop = {{ militancy = -5 consciousness = 3 }}
    }}
}}

country_event = {{
    id = 9102301
    title = "EVTNAME9102301"
    desc = "EVTDESC9102301"
    picture = "administration"

    trigger = {{
        {ANY}
        has_country_flag = h18c_independent
        NOT = {{ has_country_flag = h18c_question_settled }}
        NOT = {{ has_country_modifier = the_question_remains_open }}
        OR = {{
            NOT = {{ poor_strata_life_needs = 0.5 }}
            average_militancy = 5
            is_vassal = yes
        }}
        year = 1820
    }}
    mean_time_to_happen = {{ months = 30 }}

    option = {{
        name = "EVTOPTA9102301"
        add_country_modifier = {{ name = the_question_remains_open duration = -1 }}
        change_variable = {{ which = separatism value = 15 }}
        any_pop = {{ consciousness = 2 }}
    }}
}}
""")
loc("EVTNAME9102300", "The Question Changes")
loc("EVTDESC9102300",
    "Nobody has asked in some years whether this country ought to exist. The men who "
    "carried muskets for it are in the chamber now, arguing about tariffs and the "
    "Church and who may vote, and they are arguing with each other rather than with "
    "Madrid. The old revolutionary societies have not dissolved -- they have renamed "
    "themselves and taken up the constitution instead, which is how these things end "
    "when they end well. There will be plenty of trouble. It will be a different "
    "kind.")
loc("EVTOPTA9102300", "From independence to politics.")
loc("EVTNAME9102301", "The Question Remains Open")
loc("EVTDESC9102301",
    "Independence was supposed to settle something and has settled very little. The "
    "men who fought are unpaid, the countryside is as it was under the viceroy except "
    "poorer, and the people who did well out of the change are the people who were "
    "doing well before it. In the provinces they have begun saying that the wrong "
    "revolution was won, and in some of them they have begun saying it with weapons.")
loc("EVTOPTA9102301", "We have not finished.")
log["events"] = 2

# --- the rebels follow the question --------------------------------------------------
s = rd(f"{MOD}/common/rebel_types.txt")
if "the national question is settled" not in s:
    m = re.search(r"^nationalist_rebels\s*=\s*\{", s, re.M)
    if m:
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[m.end():i-1]
        sp = re.search(r"spawn_chance\s*=\s*\{", body)
        add = ("\n        # Before independence, liberalism IS independence: a creole\n"
               "        # constitutionalist in 1810 wanted a congress of his own, not one\n"
               "        # granted from Cadiz, and no mass pro-Spanish liberal rising ever\n"
               "        # happened in the Americas. The nationalists own the agitation\n"
               "        # until the question is settled, and the liberals inherit it after.\n"
               "        modifier = {\n            factor = 2.2\n"
               "            country = {\n                OR = {\n"
               "                    tag = NSP\n                    tag = VPE\n"
               "                    tag = VNG\n                    tag = RDP\n"
               "                    tag = CGC\n                    tag = CBA\n"
               "                    tag = PTR\n                    tag = MEX\n                    tag = PEU\n                    tag = CLM\n                    tag = ARG\n                    tag = CHL\n                }\n            }\n            NOT = { has_country_flag = h18c_question_settled }\n        }\n"
               "        # Once the national question is settled they stop coming, and\n"
               "        # the liberals pick up what they were carrying.\n"
               "        modifier = {\n            factor = 0\n"
               "            country = { has_country_flag = h18c_question_settled }\n"
               "        }\n"
               "        modifier = {\n            factor = 1.8\n"
               "            country = { has_country_modifier = the_question_remains_open }\n"
               "        }\n")
        nb = body[:sp.end()] + add + body[sp.end():]
        wr(f"{MOD}/common/rebel_types.txt", s[:m.end()] + nb + s[i-1:])
        log["nationalist rebels follow the question"] = 1

s = rd(f"{MOD}/common/rebel_types.txt")
if "they inherit the agitation" not in s:
    m = re.search(r"^liberal_rebels\s*=\s*\{", s, re.M)
    if m:
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[m.end():i-1]
        sp = re.search(r"spawn_chance\s*=\s*\{", body)
        add = ("\n        # A Spanish colony does not produce a mass liberal rising of its\n"
               "        # own: that energy goes into the national question instead, and\n"
               "        # comes back to the liberals once the country exists.\n"
               "        modifier = {\n            factor = 0\n"
               "            country = {\n                OR = {\n"
               "                    tag = NSP\n                    tag = VPE\n"
               "                    tag = VNG\n                    tag = RDP\n"
               "                    tag = CGC\n                    tag = CBA\n"
               "                    tag = PTR\n                    tag = MEX\n                    tag = PEU\n                    tag = CLM\n                    tag = ARG\n                    tag = CHL\n                }\n            }\n            NOT = { has_country_flag = h18c_question_settled }\n        }\n"
               "        # where the national question is settled, they inherit the\n"
               "        # agitation: the same societies, a different demand\n"
               "        modifier = {\n            factor = 2.5\n"
               "            country = { has_country_flag = h18c_question_settled }\n"
               "        }\n")
        nb = body[:sp.end()] + add + body[sp.end():]
        wr(f"{MOD}/common/rebel_types.txt", s[:m.end()] + nb + s[i-1:])
        log["liberals inherit the agitation"] = 1

wr(f"{MOD}/events/1800_National_Question.txt", "\n".join(EV))
wr(f"{MOD}/localisation/30_national_question.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<40}{v}")
