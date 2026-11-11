"""The Napoleonic arc: a beginning, a middle, an end, and a Congress whatever happens.

Eleven years of the first full run produced Austerlitz, Jena and Tilsit as events and
not one square mile changing hands in Europe. The battles were there and the
consequences were not, because both sides of every coalition war were fighting for
`status_quo` -- a construction that cannot produce a settlement.

So the arc now has three parts.

**The beginning** is where the game starts: the Second Coalition, already on the map,
Austria in Piedmont and a French army on the Nile.

**The middle** is the four settlements, each attached to the battle that produced it.
Pressburg takes Venetia and the Tyrol from Austria. Tilsit takes Prussian Poland and
Westphalia. Schonbrunn takes Illyria. Each fires only if France actually won the war
in question, and each is a decision Napoleon takes rather than a thing that happens --
which is where the risk lives.

**The risks.** Four points where the historical choice was genuinely open and the man
who made it knew it:

  * **Tilsit, 1807.** Napoleon considered abolishing Prussia entirely and Alexander
    talked him out of it over three days on the raft. Partitioning it removes a great
    power and guarantees Russian enmity; leaving it is what actually happened and is
    why there was a Prussia to march on Paris in 1814.
  * **Moscow, 1812.** Stop at Smolensk with the army intact and winter in Poland, or
    go on. Every marshal present argued for stopping.
  * **Frankfurt, 1813.** The Allies offered France the Rhine, the Alps and the
    Pyrenees -- larger than any king had ruled -- and Napoleon let the offer lapse.
  * **1814.** Abdicate, or fight the campaign in France that his staff thought the
    best of his life and lost anyway.

**The end** is a Congress, and it happens whatever the result. If France is beaten
there is a Congress of Vienna and the 1815 map. If France is standing there is a
Congress of Paris and a French Europe. If neither, the powers settle from exhaustion.
It is not dated to 1815: it fires when the wars actually conclude, and a backstop in
1822 catches any timeline where they simply peter out -- because a period needs an
ending even when nobody won.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

VENETIA = [729, 730, 731, 733]
TYROL = [612, 734]
POLAND = [706, 717, 708]
WESTPHALIA = [581, 582]
ILLYRIA = [768, 736, 771, 773]

def give(prov, to):
    """Transfer by the acquire idiom, in the receiving country's own scope.

    `secede_province = THIS` takes a province whoever currently holds it, and works
    from the scope of the country doing the taking. Writing `secede_province = AUS`
    from France's scope is the same mistake that made Spain's retrocession of
    Louisiana do nothing: a country cannot hand over land it does not hold.
    """
    inner = "".join(f"            {p} = {{ secede_province = THIS add_core = THIS }}\n"
                    for p in prov)
    if to == "FRA":
        return "".join(f"        {p} = {{ secede_province = THIS add_core = THIS }}\n"
                       for p in prov)
    return f"        {to} = {{\n{inner}        }}\n"

MODS = """
the_grand_empire = {
\ticon = 8
\tprestige = 1.0
\tdiplomatic_points_modifier = 0.3
\tcore_pop_militancy_modifier = -0.5
\tbadboy = 0.05
}

the_settlement_of_vienna = {
\ticon = 8
\tcore_pop_militancy_modifier = -1.5
\tcore_pop_consciousness_modifier = -1.0
\tdiplomatic_points_modifier = 0.2
}

the_hundred_days = {
\ticon = 1
\tland_organisation = 0.2
\tmobilisation_size = 0.08
\twar_exhaustion = 1.5
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_grand_empire" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

# ---------------------------------------------------------------- the settlements
def settlement(eid, yr, foe, needs, title, desc, opts):
    """A dictated peace follows the victory that produced it.

    Pressburg used to wait only on the coalition forming, so in one run it fired in
    May 1805 and ended the war before Austerlitz could be fought in it -- the battle
    never happened and the treaty that was named after it arrived anyway. Each
    settlement now waits on its own battle's flag.
    """
    """A dictated peace fires while the war is still being fought.

    The first version waited for `NOT = { war_with = AUS }`, on the reasoning that a
    settlement follows a peace. The AI never makes that peace, so Pressburg never
    fired and not one province changed hands in Europe across eleven years. The
    settlement is not the consequence of the peace -- it is the peace, and it ends
    the war itself.
    """
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = FRA
        year = {yr}
        NOT = {{ year = {yr + 6} }}
        has_global_flag = {needs}
        war_with = {foe}
    }}
    mean_time_to_happen = {{ months = 2 }}

{opts}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    log["settlements"] += 1

settlement(9102000, 1805, "AUS", "h18_battle_9101400",
 "The Peace of Pressburg",
 "Signed in the castle at Pressburg four weeks after Austerlitz, and it is a dictated "
 "peace in the proper sense: the Emperor Francis was not consulted so much as informed. "
 "Venetia and the Dalmatian coast come to the Kingdom of Italy, the Tyrol goes to "
 "Bavaria, and Francis gives up the title of Holy Roman Emperor, which has been in his "
 "family for three hundred and fifty years and is about to stop existing.",
 f"""    option = {{
        name = "EVTOPTA9102000"
        ai_chance = {{ factor = 85 }}
        set_global_flag = h18_pressburg
        add_country_modifier = {{ name = the_grand_empire duration = -1 }}
{give(VENETIA, "FRA")}{give(TYROL, "BAV")}        prestige = 20
        badboy = 3
        end_war = AUS
        AUS = {{ prestige = -20 }}
    }}
    option = {{
        name = "EVTOPTB9102000"
        set_global_flag = h18_pressburg_lenient
        prestige = 10
        AUS = {{ relation = {{ who = FRA value = 60 }} }}
        ai_chance = {{ factor = 15 }}
    }}""")
loc("EVTOPTA9102000", "Venetia, the Tyrol, and the end of the Empire.")
loc("EVTOPTB9102000", "Terms Austria can live with, and may remember.")

settlement(9102001, 1807, "PRU", "h18_battle_9101401",
 "The Terms of Tilsit",
 "Prussia is beaten so completely that the question is not what to take but whether to "
 "leave anything. Half its territory can be carved into a Grand Duchy of Warsaw and a "
 "Kingdom of Westphalia and it will remain a state of the second rank for a generation. "
 "Or it can be abolished: there is no army left to prevent it, and Davout has drawn up "
 "how. The Tsar has spent three days on the raft asking that it be spared, which is the "
 "only reason the question is open at all.",
 """    option = {
        name = "EVTOPTA9102001"
        set_global_flag = h18_tilsit_terms
        add_country_modifier = { name = the_grand_empire duration = -1 }
""" + give(POLAND, "FRA") + give(WESTPHALIA, "FRA") + """        prestige = 25
        badboy = 4
        end_war = PRU
        PRU = { prestige = -30 add_country_modifier = { name = the_cadres_are_gone duration = 2555 } }
        RUS = { relation = { who = FRA value = 40 } }
        ai_chance = { factor = 70 }
    }
    option = {
        name = "EVTOPTB9102001"
        set_global_flag = h18_prussia_partitioned
""" + give(POLAND, "FRA") + give(WESTPHALIA, "FRA") + """        581 = { add_core = FRA }
        prestige = 35
        badboy = 9
        end_war = PRU
        PRU = { prestige = -60 }
        RUS = { relation = { who = FRA value = -80 } }
        AUS = { relation = { who = FRA value = -50 } }
        ai_chance = { factor = 30 }
    }""")
loc("EVTOPTA9102001", "Leave him a kingdom. The Tsar asks it.")
loc("EVTOPTB9102001", "There will be no Prussia.")

settlement(9102002, 1809, "AUS", "h18_battle_9101402",
 "The Treaty of Schonbrunn",
 "Signed in Vienna, in the palace, with the Austrian court elsewhere. Illyria and the "
 "Adriatic coast come to France, Galicia goes to Warsaw and Salzburg to Bavaria, and "
 "Austria is reduced to a landlocked power with an army capped by treaty. The "
 "archduchess is part of the arrangement, which Metternich proposed and Napoleon "
 "accepted on the grounds that a dynasty is cheaper than a garrison.",
 f"""    option = {{
        name = "EVTOPTA9102002"
        set_global_flag = h18_schonbrunn
{give(ILLYRIA, "FRA")}        prestige = 20
        badboy = 3
        end_war = AUS
        AUS = {{ prestige = -25 relation = {{ who = FRA value = 30 }} }}
    }}""")
loc("EVTOPTA9102002", "Illyria, and the archduchess.")

# ---------------------------------------------------------------- the risks
EV.append("""country_event = {
    id = 9102010
    title = "EVTNAME9102010"
    desc = "EVTDESC9102010"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = FRA
        year = 1812
        NOT = { year = 1816 }
        has_global_flag = h18_russian_campaign
        war_with = RUS
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9102010"
        set_global_flag = h18_march_on_moscow
        prestige = 10
        add_country_modifier = { name = the_cadres_are_gone duration = 3650 }
        any_pop = { militancy = 3 }
        RUS = { war_exhaustion = 20 prestige = -10 }
        ai_chance = { factor = 75 }
    }
    option = {
        name = "EVTOPTB9102010"
        set_global_flag = h18_halted_at_smolensk
        prestige = -5
        RUS = { relation = { who = FRA value = 20 } }
        ai_chance = { factor = 25 }
    }
}

country_event = {
    id = 9102011
    title = "EVTNAME9102011"
    desc = "EVTDESC9102011"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = FRA
        year = 1813
        NOT = { year = 1817 }
        has_global_flag = h18_march_on_moscow
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9102011"
        set_global_flag = h18_frankfurt_refused
        prestige = 5
        ai_chance = { factor = 65 }
    }
    option = {
        name = "EVTOPTB9102011"
        set_global_flag = h18_frankfurt_accepted
        prestige = -15
        badboy = -4
        AUS = { relation = { who = FRA value = 60 } }
        RUS = { relation = { who = FRA value = 40 } }
        ENG = { relation = { who = FRA value = 30 } }
        ai_chance = { factor = 35 }
    }
}
""")
loc("EVTNAME9102010", "Smolensk, and the Road Beyond It")
loc("EVTDESC9102010",
    "Smolensk is taken and burned and the Russian army has gone east again without "
    "giving battle, which is what it has done since the Niemen. A third of the men who "
    "crossed are already gone to heat, typhus and desertion and no one has fought "
    "anybody. Every marshal in the tent argues for wintering here, holding Poland and "
    "finishing it next year. Moscow is two hundred and eighty miles further on and "
    "there is nothing between here and it.")
loc("EVTOPTA9102010", "They will treat when I am in their capital.")
loc("EVTOPTB9102010", "We winter at Smolensk.")
loc("EVTNAME9102011", "The Frankfurt Proposals")
loc("EVTDESC9102011",
    "Metternich's offer, and it is serious: France keeps the Rhine, the Alps and the "
    "Pyrenees -- more than Louis XIV ever held, more than any king of France has ruled "
    "-- and gives up everything beyond. The Allies have made it because they are not "
    "certain they can win and would rather not find out. To accept is to admit the "
    "Empire is over while keeping France larger than it has ever been. To let it lapse "
    "is to wager the whole of it on one more campaign.")
loc("EVTOPTA9102011", "France does not negotiate from her own soil.")
loc("EVTOPTB9102011", "The natural frontiers. Take it.")

# ---------------------------------------------------------------- the end
def congress(eid, needs, title, desc, opt, effect, extra="", yr=1814, until=1824):
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {'FRA' if 'paris' in needs else 'AUS'}
        year = {yr}
        NOT = {{ year = {until} }}
        NOT = {{ has_global_flag = h18_the_congress_has_met }}
{extra}    }}
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA{eid}"
        set_global_flag = h18_the_congress_has_met
{effect}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["endings"] += 1

ALLIES = "        any_country = {\n            limit = { OR = { tag = AUS tag = RUS tag = PRU tag = ENG } }\n" \
         "            add_country_modifier = { name = the_settlement_of_vienna duration = -1 }\n            prestige = 15\n        }\n"

congress(9102020, "vienna_beaten",
 "The Congress of Vienna",
 "Every sovereign in Europe is in one city and the serious business is done by four "
 "men in a room: Metternich, Castlereagh, Alexander and Hardenberg, with Talleyrand "
 "talking his way in on the grounds that a France without Napoleon is a France worth "
 "balancing against. What they build is not justice and does not pretend to be. It is "
 "an arrangement of weights, designed by men who watched a continent burn for twenty "
 "years and intend that whoever tries it next will find four great powers already "
 "agreed about what to do.",
 "A balance, and let it hold a hundred years.",
 "        prestige = 25\n" + ALLIES +
 "        FRA = { prestige = -30 badboy = -10 }\n",
 extra="        FRA = { NOT = { has_country_modifier = the_grand_empire } }\n"
       "        OR = {\n            has_global_flag = h18_abdication\n"
       "            has_global_flag = h18_waterloo_lost\n"
       "            has_global_flag = h18_frankfurt_accepted\n            year = 1818\n        }\n")

congress(9102021, "paris_victorious",
 "The Congress of Paris",
 "The Emperor has summoned them and they have come, which is the difference between "
 "this and Vienna. The Confederation of the Rhine is confirmed, Poland is a kingdom "
 "under French protection, Austria keeps what it has been allowed to keep and Prussia "
 "keeps rather less. Britain is not in the room and has not stopped paying anybody. "
 "The settlement is a French one and it will last exactly as long as the man who made "
 "it, which nobody present is tactless enough to say.",
 "Europe arranged, and from Paris.",
 "        prestige = 40\n"
 "        add_country_modifier = { name = the_grand_empire duration = -1 }\n"
 "        any_country = {\n            limit = { OR = { tag = AUS tag = PRU } }\n"
 "            prestige = -20\n            relation = { who = FRA value = -40 }\n        }\n",
 extra="        FRA = { has_country_modifier = the_grand_empire }\n"
       "        NOT = { has_global_flag = h18_abdication }\n"
       "        NOT = { has_global_flag = h18_waterloo_lost }\n"
       "        OR = {\n            has_global_flag = h18_leipzig_held\n"
       "            has_global_flag = h18_waterloo_won\n"
       "            has_global_flag = h18_halted_at_smolensk\n            year = 1820\n        }\n")

congress(9102022, "vienna_exhausted",
 "The Peace of Exhaustion",
 "No congress was summoned and none was needed. The war stopped because the money "
 "stopped, and the frontiers are where the armies happened to be standing when it did. "
 "There is no settlement, no system and no four powers agreed about anything -- only a "
 "set of truces that everybody intends to keep until it is convenient not to. The "
 "diplomats who would have built something call it a peace. The soldiers call it an "
 "interval.",
 "An interval, then.",
 "        prestige = 5\n"
 "        any_country = {\n            limit = { OR = { tag = FRA tag = AUS tag = RUS tag = PRU tag = ENG } }\n"
 "            any_pop = { militancy = -2 }\n        }\n",
 yr=1818, until=1830)

wr(f"{MOD}/events/1800_Napoleonic_Arc.txt", "\n".join(EV))
wr(f"{MOD}/localisation/26_arc.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<22}{v}")
