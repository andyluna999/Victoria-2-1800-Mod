"""Reform earns the loyalty the revolution did not.

Independence left the mestizos and the indigenous pueblos with a change of masters and
their consciousness raised, which is the honest outcome: the castas were still castas,
the tribute was still collected, and the men who had fought were told the revolution
was complete. That consciousness is a debt, and this is how a government pays it.

Four reforms matter here and they are the four that actually came up:

  **The franchise.** Landed voting means the hacendados and nobody else. Wealth voting
  takes in the creole professions. Universal voting takes in the people who fought.
  Each step down the property qualification is felt by everyone it newly includes.

  **Citizens' rights.** The 1812 Constitution excluded anyone of African descent from
  citizenship and every republic after it kept some version of the castas on the
  books. Full citizenship is the single largest thing a government here can do.

  **Schools.** The Seminario taught creoles. A public school system in the pueblos is
  the first institution most of them ever saw that was not a tax collector or a
  priest, and the generation that passes through it stops being a caste.

  **Accepting the culture.** Not a reform in the engine's sense but the real measure:
  a republic whose primary culture is creole Spanish and whose majority is mestizo and
  Nahua is a republic governed by a minority, and admitting as much changes everything
  about how it is obeyed.

None of them is free and none of them is instant. They cost the creoles something
every time, because every one of them takes a privilege away from somebody who has it.
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
the_debt_acknowledged = {
\ticon = 8
\tcore_pop_militancy_modifier = -2.0
\tglobal_assimilation_rate = 0.4
\ttax_efficiency = 0.1
\tprestige = 0.3
}

the_castas_abolished = {
\ticon = 8
\tcore_pop_militancy_modifier = -1.5
\tnon_accepted_pop_militancy_modifier = -2.0
\tglobal_immigrant_attract = 0.2
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "\nthe_debt_acknowledged = {" not in src:
    wr(f"{MOD}/common/event_modifiers.txt", src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 2

# the republics and the kingdoms that come out of the wars
AMER = ["MEX", "PEU", "CLM", "ARG", "CHL", "BRZ", "URU", "PRG", "BOL", "GCO"]
ANY = "OR = { " + " ".join(f"tag = {t}" for t in AMER) + " }"
# the people independence left behind
MARGINAL = ["mestizo", "nahua", "maya", "zapotec", "mixtec", "quechua", "aymara",
            "guarani", "mapuche", "chibcha", "afro_caribbean"]

def felt(mil, con=0):
    """What the marginalised cultures feel when a reform lands."""
    out = ""
    for c in MARGINAL:
        bits = f"militancy = {mil}"
        if con: bits += f" consciousness = {con}"
        out += (f"        any_pop = {{ limit = {{ has_pop_culture = {c} }} {bits} }}\n")
    return out

def ev(eid, trig, mtth, title, desc, opts, effect):
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
{trig}    }}
    mean_time_to_happen = {{ months = {mtth} }}

    option = {{
        name = "EVTOPTA{eid}"
{effect}    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    for k, v in opts.items(): loc(k, v)
    log["events"] += 1

# --- the franchise, each step down the property qualification --------------------------
for n, (code, name, mil) in enumerate([
        ("wealth_voting", "the Property Qualification Lowered", -3),
        ("universal_voting", "Universal Suffrage", -5)]):
    ev(9103100 + n,
       f"        {ANY}\n        has_country_flag = h18c_independent\n"
       f"        vote_franschise = {code}\n",
       4, name,
       "The men who carried muskets in the war are on the rolls, which is a sentence "
       "that would have been seditious in this country twenty years ago and is now "
       "simply administrative. The hacendados have pointed out, correctly, that they "
       "are now outnumbered in their own districts by their own labourers. That is "
       "what the word means.",
       {f"EVTOPTA{9103100 + n}": "Let them vote."},
       felt(mil, 1) +
       "        any_pop = { limit = { has_pop_culture = criollo } militancy = 2 }\n"
       "        prestige = 5\n")

# --- citizens' rights: the castas struck off ---------------------------------------------
ev(9103110,
   f"        {ANY}\n        has_country_flag = h18c_independent\n"
   "        citizens_rights = all_voting_pops\n"
   "        NOT = { has_country_modifier = the_castas_abolished }\n",
   4, "The Castas Struck Off the Register",
   "The colonial registers recorded sixteen gradations of descent and attached a "
   "different set of rights to each, and the Constitution of Cadiz, which called "
   "itself liberal, excluded everyone of African descent from citizenship outright. "
   "Striking the whole apparatus off is not generosity; it is the removal of a thing "
   "that was invented to make tribute easier to collect. The men who keep the "
   "registers have protested that they will no longer know who anybody is.",
   {"EVTOPTA9103110": "There are no castas. There are citizens."},
   felt(-6, 2) +
   "        add_country_modifier = { name = the_castas_abolished duration = -1 }\n"
   "        any_pop = { limit = { has_pop_culture = criollo } militancy = 3 }\n"
   "        prestige = 10\n")

# --- schools in the pueblos ---------------------------------------------------------------
ev(9103111,
   f"        {ANY}\n        has_country_flag = h18c_independent\n"
   "        OR = { school_reforms = low_schools school_reforms = acceptable_schools\n"
   "               school_reforms = good_schools }\n",
   6, "Schools in the Pueblos",
   "A schoolmaster in every village of five hundred, paid from the treasury, teaching "
   "in Spanish to children whose parents do not speak it. It is the first institution "
   "most of these pueblos have ever seen that is neither a tax collector nor a priest, "
   "and the generation that passes through it will not think of itself as a caste. "
   "The curas have objected on the grounds that the schoolmasters are not always "
   "devout. They are right, and that is rather the point.",
   {"EVTOPTA9103111": "A schoolmaster in every pueblo."},
   felt(-4, 1) +
   "        add_country_modifier = { name = the_debt_acknowledged duration = -1 }\n"
   "        prestige = 8\n")

# --- and the real measure: admitting who the country is ------------------------------------
ev(9103112,
   f"        {ANY}\n        has_country_flag = h18c_independent\n"
   "        NOT = { has_country_flag = h18c_the_nation_admitted }\n"
   "        OR = {\n"
   "            citizens_rights = all_voting_pops\n"
   "            vote_franschise = universal_voting\n"
   "        }\n",
   10, "Who This Country Belongs To",
   "The republic's primary culture is the Spanish of the creole professions and its "
   "majority speaks something else. Every official document, every court, every school "
   "inspection assumes a country that is perhaps a fifth of the people in it. The "
   "question has been avoidable for forty years because the people it concerns were "
   "not consulted, and it has stopped being avoidable for exactly the same reason.",
   {"EVTOPTA9103112": "Admit what the country is."},
   "        set_country_flag = h18c_the_nation_admitted\n"
   "        set_country_flag = h18c_question_settled\n"
   "        add_accepted_culture = mestizo\n"
   + felt(-8, -2) +
   "        add_country_modifier = { name = the_debt_acknowledged duration = -1 }\n"
   "        any_pop = { limit = { has_pop_culture = criollo } militancy = 4 consciousness = 2 }\n"
   "        prestige = 15\n")

wr(f"{MOD}/events/1800_The_Reckoning.txt", "\n".join(EV))
wr(f"{MOD}/localisation/42_reckoning.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
log["cultures that feel a reform"] = len(MARGINAL)
for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
