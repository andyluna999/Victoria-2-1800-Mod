"""Make France Napoleonic.

The first full run to 1824 produced this war record: France accepted peace from Prussia
in 1807, from Spain in 1810, and from Britain, Sweden and Russia along the way. In 1813
the Netherlands declared war on it and in 1817 Ireland did. France won Austerlitz and
Wagram and lost or settled everything else.

Jena is the one that gives it away. On 14 October 1806 France destroyed the Prussian
army in a single day and occupied Berlin a fortnight later; in our run Prussia offered
terms and France took them. The cause is arithmetic: a hundred and twenty-eight French
regiments against a coalition fielding three hundred and sixty.

Four changes, in rising order of how much they interfere.

**The army.** France conscripted on a scale nobody else attempted until the 1860s --
the levée en masse was a decade old by 1800 and the Grande Armée of 1805 was around
two hundred thousand men in the field with as many again in depots. The war-footing
multiplier goes from double to triple and a half.

**The Grande Armée.** Not a cheat but a description: corps organisation, marshals who
could act without orders, artillery massed under a gunner emperor, and soldiers who
marched faster than anyone expected armies to move. It decays from 1813, when the
cadres that made it were dead in Russia.

**War goals.** The coalitions were attacking with `cut_down_to_size`, which is why
France ended the period dismembered -- the AI took territory the coalitions never got
until 1814. They attack with `status_quo` now: they are trying to make France stop,
not to partition it.

**The battles.** Austerlitz, Jena, Wagram and Tilsit are scripted, because a campaign
where Prussia beats France in 1806 is not an alternate history, it is a broken one. Each
fires only while the relevant war is actually being fought, and applies war exhaustion
and prestige rather than dictating a peace: France wins the battle and still has to
finish the war.

Spain is the exception that matters: on the French branch of the Peninsular War, Joseph
gets an actual satellite rather than an event telling you he is king.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

# --- the modifiers -------------------------------------------------------------------
MODS = """
the_grande_armee = {
\ticon = 2
\tland_organisation = 0.25
\tland_attack_modifier = 0.2
\torg_regain = 0.25
\tland_unit_start_experience = 15
\tmobilisation_size = 0.05
\tsupply_consumption = -0.15
\tleadership = 2
}

the_cadres_are_gone = {
\ticon = 1
\tland_organisation = -0.1
\torg_regain = -0.15
\tmobilisation_economy_impact = 0.25
}

beaten_in_the_field = {
\ticon = 1
\twar_exhaustion = 2.0
\tland_organisation = -0.2
\tcore_pop_militancy_modifier = 1.0
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_grande_armee" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

# --- France starts with it, granted by event ------------------------------------------
# NOT by a line in history/countries. `add_country_modifier` is not a valid key in a
# country history file -- HPM uses it there exactly zero times -- and Victoria II stops
# parsing the file at an unknown key. Putting it on line 15 silently discarded
# everything after it: France's prestige, its technologies, its reforms and its ruling
# party, which is why France loaded with no prestige, no technology and no army.
EV.append("""country_event = {
    id = 9101410
    title = "EVTNAME9101410"
    desc = "EVTDESC9101410"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = FRA
        year = 1800
    }
    mean_time_to_happen = { days = 2 }

    option = {
        name = "EVTOPTA9101410"
        add_country_modifier = { name = the_grande_armee duration = 4745 }
    }
}
""")
loc("EVTNAME9101410", "The Army of the Republic")
loc("EVTDESC9101410",
    "Nine years of war have produced something no other state in Europe has: an army "
    "organised in permanent corps, each able to fight alone until the others arrive, "
    "commanded by men promoted for winning rather than for birth, and marching faster "
    "than any staff in Vienna or Berlin believes an army can move.")
loc("EVTOPTA9101410", "It is not numbers. It is speed.")
log["France given the Grande Armee"] = 1

# --- the war footing ---------------------------------------------------------------------
p = "tools/oob_new_tags.py"
t = open(p).read()
t = t.replace('WAR = {"FRA": 2.0, "AUS": 1.8,',
              '# France conscripted on a scale nobody matched until the 1860s. Double was\n'
              '# not enough: it lost Jena.\nWAR = {"FRA": 3.5, "AUS": 1.8,')
open(p, "w").write(t)

# --- coalition goals ----------------------------------------------------------------------
p = "tools/coalitions.py"
t = open(p).read()
t = t.replace('["FRA"], "cut_down_to_size", None, allies=["RUS", "SWE", "ENG"]',
              '["FRA"], "status_quo", None, allies=["RUS", "SWE", "ENG"]')
t = t.replace('["FRA"], "cut_down_to_size", None, allies=["RUS"]',
              '["FRA"], "status_quo", None, allies=["RUS"]')
t = t.replace('["FRA"], "cut_down_to_size", None, allies=["ENG"]',
              '["FRA"], "status_quo", None, allies=["ENG"]')
t = t.replace('["RUS"], "cut_down_to_size", None, needs="h18_fourth_coalition"',
              '["RUS"], "status_quo", None, needs="h18_fourth_coalition"')
open(p, "w").write(t)

# --- the battles ----------------------------------------------------------------------------
def battle(eid, yr, until, foe, title, desc, opt, extra_fr="", extra_foe=""):
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = FRA
        year = {yr}
        NOT = {{ year = {until} }}
        war_with = {foe}
    }}
    mean_time_to_happen = {{ months = 4 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_global_flag = h18_battle_{eid}
        prestige = 15
{extra_fr}        {foe} = {{
            add_country_modifier = {{ name = beaten_in_the_field duration = 730 }}
            prestige = -20
            war_exhaustion = 15
{extra_foe}        }}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["battles"] += 1

battle(9101400, 1805, 1810, "AUS", "Austerlitz",
 "The Pratzen heights were given up deliberately and the allies walked onto them. The "
 "centre went in at nine, the army was cut in two by noon, and by four the Russians were "
 "on the frozen ponds with the artillery firing into the ice behind them. The Emperor "
 "Francis has asked for an armistice in person. The Tsar has gone home.",
 "The sun of Austerlitz.")

battle(9101401, 1806, 1812, "PRU", "Jena and Auerstedt",
 "Two battles fourteen miles apart on the same morning, and the Prussian army has "
 "ceased to exist in both. Davout beat the main body at Auerstedt with a single corps "
 "and was not believed when he reported it. Berlin in a fortnight, the fortresses "
 "surrendering as fast as the cavalry can reach them, and Frederick's sword sent back "
 "to Paris.",
 "The army of Frederick is a sword that has rusted.",
 extra_foe="            add_country_modifier = { name = the_cadres_are_gone duration = 2190 }\n")

battle(9101402, 1809, 1816, "AUS", "Wagram",
 "Five hundred guns on a plain and a hundred and fifty thousand men a side, which is "
 "the largest battle Europe has seen. It was won by the grand battery in the centre and "
 "it cost more than Austerlitz did. The Archduke withdrew in good order and asked for "
 "terms the next week, which is the most anyone has managed.",
 "A battle, not a masterpiece.")

# Tilsit: Russia changes sides.
EV.append("""country_event = {
    id = 9101403
    title = "EVTNAME9101403"
    desc = "EVTDESC9101403"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = FRA
        year = 1807
        NOT = { year = 1810 }
        has_global_flag = h18_fourth_coalition
    }
    mean_time_to_happen = { months = 6 }

    option = {
        name = "EVTOPTA9101403"
        set_global_flag = h18_tilsit
        prestige = 20
        RUS = {
            relation = { who = FRA value = 150 }
            prestige = -10
        }
        PRU = {
            prestige = -25
            add_country_modifier = { name = the_cadres_are_gone duration = 2190 }
        }
    }
}
""")
loc("EVTNAME9101403", "The Raft at Tilsit")
loc("EVTDESC9101403",
    "A pavilion built on a raft moored in the middle of the Niemen, so that neither "
    "emperor need set foot on the other's bank. The Tsar's opening remark was that he "
    "hates the English as much as I do. Prussia is to lose half its territory and its "
    "king was left standing on the shore in the rain while it was decided. Russia joins "
    "the Continental System and the war on the continent is over.")
loc("EVTOPTA9101403", "I hate them too. Then we shall agree about everything.")

# --- Joseph gets a real satellite ----------------------------------------------------------
EV.append("""country_event = {
    id = 9101404
    title = "EVTNAME9101404"
    desc = "EVTDESC9101404"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = FRA
        year = 1809
        NOT = { year = 1813 }
        has_global_flag = h18_joseph_king
        war_with = SPA
    }
    mean_time_to_happen = { months = 8 }

    option = {
        name = "EVTOPTA9101404"
        set_global_flag = h18_spain_satellite
        SPA = {
            country_event = 9101405
        }
        prestige = 10
        badboy = 2
    }
}

country_event = {
    id = 9101405
    title = "EVTNAME9101405"
    desc = "EVTDESC9101405"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9101405"
        FRA = { create_vassal = THIS }
        government = absolute_monarchy
        add_country_modifier = { name = the_french_occupation duration = 1825 }
        any_pop = { militancy = 4 }
    }
}
""")
loc("EVTNAME9101404", "A Throne for Joseph")
loc("EVTDESC9101404",
    "The guerrilla has not stopped and will not, but the Juntas have been driven to the "
    "sea and my brother holds the capital, the treasury and the machinery of the state. "
    "Spain becomes a kingdom of the French system: its own crown, its own army, its own "
    "constitution written at Bayonne, and its foreign policy decided in Paris.")
loc("EVTOPTA9101404", "Let him be king in fact as well as name.")
loc("EVTNAME9101405", "The Bayonne Statute")
loc("EVTDESC9101405",
    "A constitution nobody in Spain asked for, granted by a king nobody in Spain chose, "
    "promising an end to feudal dues and the Inquisition. Some of the ablest men in the "
    "country have taken office under it, on the argument that a reformed Spain under a "
    "Bonaparte is better than an unreformed one under nobody. They will be called "
    "afrancesados for the rest of their lives and most will die in France.")
loc("EVTOPTA9101405", "Better a French king than no kingdom.")

wr(f"{MOD}/events/1800_Battles.txt", "\n".join(EV))
wr(f"{MOD}/localisation/20_battles.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<34}{v}")
