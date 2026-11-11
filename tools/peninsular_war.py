"""The Spanish collapse, 1807-1814.

This is the hinge the whole scenario turns on. Everything the colonies do between 1808
and 1825 follows from the fact that for six years there was no legitimate government in
Spain to be loyal to, and every man in the Americas had to decide for himself what that
meant.

The sequence:

  **October 1807, Fontainebleau.** France and Spain agree to partition Portugal. Junot
  marches, and a French army is in Spain by arrangement.

  **March 1808, Aranjuez.** A mutiny at the palace forces Godoy out and Charles IV to
  abdicate in favour of his son Ferdinand. Spain now has two kings and neither can
  manage without French consent.

  **May 1808, Bayonne.** Napoleon summons both to France and takes the crown from both.
  This is the legal vacuum: not an abdication to a rival claimant but a dynasty simply
  removed. Every colonial junta that follows will claim to be governing *for Ferdinand*,
  because that claim costs nothing and means anything.

  **2 May 1808, Madrid.** The city rises. Murat shoots the prisoners the next morning,
  Goya paints it, and what the French expected to be an occupation becomes a war of a
  kind European armies had not fought before.

  **July 1808, Bailén.** Dupont's corps surrenders in the open field to a Spanish army.
  Twenty thousand men. It is the first time a Napoleonic corps has done that, and the
  news goes round Europe and across the Atlantic.

  **1809, Joseph.** Napoleon's brother is installed in Madrid, reigning over whatever
  the French army is standing on.

The 1808 event reaches every colony and sets the flag the regency chain reads. It does
not decide what they do -- that is section 8 of the plan and the decisions already on
the shelf. It opens the question.
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

COLONIES = "NSP VPE VNG RDP CGC CBA PTR"
def each(effect):
    return "\n".join(f"        {t} = {{ {effect} }}" for t in COLONIES.split())

# Windows are generous and the gate is the flag, not the calendar.
#
# The first full run had Fontainebleau fire on time in 1807 and Aranjuez miss its
# one-year window entirely; everything after it was then unreachable, because each
# link was gated on an absolute year as well as on the previous flag. The French never
# crossed the Pyrenees because that event's window closed in 1810 and Bayonne had not
# happened yet.
#
# So each link now has six years to fire in rather than one, and what actually orders
# the chain is the flag its predecessor sets. A slow chain is still a chain; a broken
# one is not.
def ev(eid, tag, yr, until, title, desc, opt, effect, needs="", mtth=3):
    until = max(until, yr + 6)
    gate = f"        has_global_flag = {needs}\n" if needs else ""
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        year = {yr}
        NOT = {{ year = {until} }}
{gate}    }}
    mean_time_to_happen = {{ months = {mtth} }}

    option = {{
        name = "EVTOPTA{eid}"
{effect}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["events"] += 1

ev(9101000, "SPA", 1807, 1809, "The Treaty of Fontainebleau",
   "France proposes to partition Portugal between us, with a principality in the Algarve "
   "for Godoy himself. The price is that Junot's army crosses Spain to get there, and "
   "then another to support it, and then another. There are now French troops in Burgos, "
   "Vitoria and Pamplona, and none of them are going to Lisbon.",
   "The Prince of the Peace will have his principality.",
   "        set_global_flag = h18_fontainebleau\n"
   "        FRA = { relation = { who = SPA value = 30 } }\n"
   "        POR = { relation = { who = SPA value = -60 } }\n"
   "        badboy = 2", mtth=2)

ev(9101001, "SPA", 1808, 1809, "The Mutiny at Aranjuez",
   "A crowd of guardsmen and servants has sacked Godoy's house and dragged him out of a "
   "rolled carpet, and the King has abdicated to save his minister's life. Ferdinand is "
   "proclaimed in Madrid to genuine rejoicing. Charles immediately writes to Napoleon "
   "saying the abdication was extorted. Spain has two kings, and the only man who can "
   "say which is real commands two hundred thousand men on our soil.",
   "Long live Ferdinand the Seventh.",
   "        set_global_flag = h18_aranjuez\n"
   "        prestige = -5\n"
   "        any_pop = { militancy = 2 }",
   needs="h18_fontainebleau", mtth=2)

# --- Bayonne: the vacuum --------------------------------------------------------------
EV.append(f"""country_event = {{
    id = 9101002
    title = "EVTNAME9101002"
    desc = "EVTDESC9101002"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = SPA
        year = 1808
        NOT = {{ year = 1810 }}
        has_global_flag = h18_aranjuez
    }}
    mean_time_to_happen = {{ months = 2 }}

    option = {{
        name = "EVTOPTA9101002"
        set_global_flag = h18_bayonne
        prestige = -20
        add_country_modifier = {{ name = the_captive_king duration = 2190 }}
        any_pop = {{ militancy = 5 consciousness = 3 }}
        FRA = {{ relation = {{ who = SPA value = -100 }} }}
{each("country_event = 9101003")}
    }}
}}
""")
loc("EVTNAME9101002", "The Abdications at Bayonne")
loc("EVTDESC9101002",
    "Napoleon invited father and son to Bayonne to arbitrate between them. He has taken "
    "the crown from both. Charles abdicated to him, Ferdinand abdicated to Charles, and "
    "both are now guests in France for as long as he wishes. This is not a disputed "
    "succession. There is simply no King of Spain, and no body in Spain with authority "
    "to say what happens next.")
loc("EVTOPTA9101002", "Then authority must come from somewhere.")

EV.append("""country_event = {
    id = 9101003
    title = "EVTNAME9101003"
    desc = "EVTDESC9101003"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9101003"
        set_country_flag = h18c_bayonne_known
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 5 militancy = 3 }
        any_pop = { limit = { has_pop_culture = mestizo } consciousness = 2 }
    }
}
""")
loc("EVTNAME9101003", "News from Bayonne")
loc("EVTDESC9101003",
    "The packet from Cádiz carries the whole of it: Aranjuez, Bayonne, the abdications, "
    "a French army in Madrid. The viceroy holds his commission from a king who is a "
    "prisoner in France, and the audiencia is already arguing about whether that "
    "commission means anything at all. The lawyers say sovereignty reverts to the "
    "people in the absence of the King. The lawyers have read Suárez, and so has "
    "everyone else in this room.")
loc("EVTOPTA9101003", "Then who governs here?")

ev(9101004, "SPA", 1808, 1810, "The Second of May",
   "Madrid rose yesterday when the French tried to remove the last of the royal family "
   "from the palace. Murat has spent this morning shooting the prisoners on the hill at "
   "Príncipe Pío. The rising is spreading to every province, and it is not an army "
   "rising -- it is priests, muleteers and villagers, and it will not surrender when a "
   "capital falls, because it does not care which capital falls.",
   "It is not a campaign. It is a war of the whole people.",
   "        set_global_flag = h18_dos_de_mayo\n"
   "        any_pop = { militancy = 6 }\n"
   "        prestige = 10\n"
   "        ENG = { relation = { who = SPA value = 100 } }",
   needs="h18_bayonne", mtth=1)

ev(9101005, "SPA", 1808, 1810, "Bailén",
   "General Castaños has taken the surrender of Dupont's entire corps in open country at "
   "Bailén -- some twenty thousand men. No Napoleonic corps has ever surrendered in the "
   "field before. Joseph has abandoned Madrid within a fortnight, Austria is rearming on "
   "the strength of it, and in Caracas and Buenos Aires they are reading that French "
   "armies can be beaten by Spaniards.",
   "Let the news go everywhere.",
   "        set_global_flag = h18_bailen\n"
   "        prestige = 20\n"
   "        FRA = { prestige = -15 }\n"
   "        AUS = { relation = { who = FRA value = -40 } }",
   needs="h18_dos_de_mayo", mtth=3)

ev(9101006, "FRA", 1809, 1811, "Joseph Enters Madrid",
   "My brother is King of Spain, reigning over the ground my soldiers are standing on "
   "and no more. The juntas govern everywhere else in the King's name, the English have "
   "landed in Portugal, and the countryside kills couriers. I have put three hundred "
   "thousand men into this and it consumes them.",
   "Spain will be held.",
   "        set_global_flag = h18_joseph_king\n"
   "        SPA = { add_country_modifier = { name = the_french_occupation duration = 2190 } }\n"
   "        prestige = 5\n"
   "        FRA = { badboy = 3 }",
   needs="h18_bailen", mtth=4)

MODS = """
the_captive_king = {
\ticon = 1
\tadministrative_efficiency_modifier = -0.25
\tcore_pop_militancy_modifier = 2.0
\tcore_pop_consciousness_modifier = 1.5
\ttax_efficiency = -0.2
}

the_french_occupation = {
\ticon = 1
\ttax_efficiency = -0.3
\tsupply_consumption = 0.25
\tcore_pop_militancy_modifier = 3.0
\tland_organisation = -0.15
}
"""
src = open(f"{MOD}/common/event_modifiers.txt", encoding="cp1252", errors="replace").read()
if "the_captive_king" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 2

wr(f"{MOD}/events/1800_Peninsular.txt", "\n".join(EV))
wr(f"{MOD}/localisation/14_peninsular.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
