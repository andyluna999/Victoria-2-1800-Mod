"""The Liberator arrives nine years late, and nobody opposes him.

Simon Bolivar was already the best commander in this mod -- prestige 1.0, audacious,
a natural born leader, level with Napoleon and Nelson. Two things around him were
wrong.

He is dated 1819, which is Boyaca: his triumph, not his beginning. He wrote the
Cartagena Manifesto in 1812, took Caracas in the Admirable Campaign of 1813 and was
being called the Liberator by October of that year. Colombia is born in 1810, so for
nine years it fought the entire war under Antonio Narino, an admirable man rated
`amateur` at prestige 0.4. The Liberator turned up after the hard part.

And the Viceroyalty of New Granada had no commanders at all -- not one -- so the
royalist side of the bloodiest campaign in the hemisphere was being fought by nobody
in particular. Morillo, Samano and Boves belong there: Boves especially, whose llanero
cavalry destroyed the Second Republic and who is the reason Bolivar spent 1814 in
flight rather than in Caracas.

He also gets what Toussaint has: a modifier while he lives. Not because he was a
better general than his contemporaries -- he lost more battles than he won -- but
because he could cross the Andes in the rainy season with an army that had no boots
and arrive with enough of it to fight, which is a different and rarer thing.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

MODS = """
the_liberator = {
\ticon = 2
\tland_attack_modifier = 0.25
\tland_organisation = 0.2
\tsupply_consumption = -0.35
\torg_regain = 0.25
\tcore_pop_militancy_modifier = -1.0
\tprestige = 0.5
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "\nthe_liberator = {" not in src:
    wr(f"{MOD}/common/event_modifiers.txt", src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 1

# the Liberator at the date he began, not the date he won
f = f"{MOD}/history/units/CLM_oob.txt"
if os.path.exists(f):
    s = rd(f)
    s = re.sub(r'(name = "Simon Bolivar"\s*\n\s*)date = \S+',
               r'\1date = 1813.1.1', s)
    s = re.sub(r'(name = "Antonio Jose de Sucre"\s*\n\s*)date = \S+',
               r'\1date = 1817.1.1', s)
    wr(f, s)
    log["Bolivar's command backdated to"] = 1813

# and the royalists who beat him twice
ROYAL = f"""
leader = {{
\tname = "Pablo Morillo"
\tdate = 1815.1.1
\ttype = land
\tpersonality = relentless
\tbackground = exranker
\tprestige = 0.7
}}

leader = {{
\tname = "Jose Tomas Boves"
\tdate = 1813.1.1
\ttype = land
\tpersonality = merciless
\tbackground = cavalry_school
\tprestige = 0.6
}}

leader = {{
\tname = "Juan Samano"
\tdate = 1810.1.1
\ttype = land
\tpersonality = cautious
\tbackground = drillmaster
\tprestige = 0.3
}}
"""
f = f"{MOD}/history/units/VNG_oob.txt"
if os.path.exists(f):
    s = rd(f)
    if "Morillo" not in s:
        wr(f, ROYAL.lstrip("\n") + "\n" + s)
        log["royalist commanders given to New Granada"] = 3

# the modifier, granted while he is alive and the country is fighting for itself
EV = """country_event = {
    id = 9102950
    title = "EVTNAME9102950"
    desc = "EVTDESC9102950"
    picture = "1819_bolivar"
    fire_only_once = yes

    trigger = {
        tag = CLM
        year = 1813
        NOT = { year = 1831 }
        exists = yes
    }
    mean_time_to_happen = { months = 6 }

    option = {
        name = "EVTOPTA9102950"
        set_country_flag = h18c_the_liberator_lives
        add_country_modifier = { name = the_liberator duration = -1 }
        prestige = 10
        any_pop = { limit = { has_pop_culture = criollo } militancy = -3 consciousness = 3 }
    }
}

country_event = {
    id = 9102951
    title = "EVTNAME9102951"
    desc = "EVTDESC9102951"
    picture = "1819_bolivar"
    fire_only_once = yes

    trigger = {
        tag = CLM
        has_country_flag = h18c_the_liberator_lives
        year = 1830
    }
    mean_time_to_happen = { months = 10 }

    option = {
        name = "EVTOPTA9102951"
        clr_country_flag = h18c_the_liberator_lives
        remove_country_modifier = the_liberator
        prestige = -5
        any_pop = { militancy = 2 consciousness = 1 }
    }
}
"""
wr(f"{MOD}/events/1800_Bolivar.txt", EV)
LOC = [
 ("EVTNAME9102950", "The Liberator"),
 ("EVTDESC9102950",
  "He has written a manifesto from exile explaining precisely why the first republic "
  "fell -- federalism, sentiment, and the refusal to raise a real army -- and then "
  "marched from the Magdalena to Caracas in three months to prove he had understood "
  "it. He loses more battles than he wins and it does not seem to matter: he can take "
  "an army over the Andes in the rainy season without boots and arrive with enough of "
  "it left to fight, and no royalist general in the Americas can do anything "
  "comparable."),
 ("EVTOPTA9102950", "Let him command."),
 ("EVTNAME9102951", "He Ploughed the Sea"),
 ("EVTDESC9102951",
  "He is forty-seven, consumptive, and on the road to the coast with the intention of "
  "leaving for Europe, which he will not reach. The union he built is coming apart "
  "behind him into the three countries it was made from, and his own judgement on the "
  "whole business, delivered a few weeks ago, was that those who served the revolution "
  "had ploughed the sea."),
 ("EVTOPTA9102951", "The Liberator is dead."),
]
wr(f"{MOD}/localisation/39_bolivar.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["events"] = 2
for k, v in sorted(log.items()): print(f"  {k:<40}{v}")
