"""From Moscow to Waterloo: the three years the arc was missing.

France marched on Moscow in 1812 and the next thing that happened was a peace
conference in which it kept the Grand Empire. There was no retreat, no 1813 campaign,
no Leipzig, no invasion of France, no abdication and no Waterloo -- so every
playthrough ended with Napoleon holding Venetia, Illyria and Poland into the 1840s,
which is why the borders look wrong.

The real sequence is the most dramatic three years in the period and it is all forks:

  **The retreat.** Six hundred thousand men crossed the Niemen and twenty thousand
  recrossed it. The army is not defeated in battle; it is destroyed by distance and
  cold, and the Grande Armee modifier goes with it.

  **The defection.** Yorck signs the Convention of Tauroggen without orders and takes
  the Prussian corps out of the French army. Prussia follows him, Austria follows
  Prussia, and the Sixth Coalition is the whole of Europe.

  **Leipzig.** Half a million men over four days, the largest battle fought anywhere
  before 1914, and the Saxons change sides in the middle of it.

  **The abdication.** The marshals refuse to march on Paris. Napoleon can abdicate for
  Elba or fight the campaign of France with boys, and the campaign of France was
  tactically his best work and lost anyway.

  **The Hundred Days.** He lands with a thousand men and the army sent to stop him
  joins him. Then Waterloo, which was close.

Each fork can go the other way, because they genuinely could: at Leipzig the Saxons
might have held, at Waterloo Grouchy might have marched to the guns. A France that
wins those is a France that keeps the Grand Empire, and that is the alternate history
worth having rather than the one where nothing happens at all.
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

MODS = """
the_retreat_from_moscow = {
\ticon = 1
\tland_organisation = -0.4
\tmobilisation_size = -0.1
\tsupply_consumption = 0.3
\tcore_pop_militancy_modifier = 2.0
\twar_exhaustion = 2.0
\tprestige = -1.0
}

the_sixth_coalition = {
\ticon = 1
\tland_attack_modifier = 0.15
\tmobilisation_size = 0.1
\torg_regain = 0.15
}

the_campaign_of_france = {
\ticon = 2
\tland_defense_modifier = 0.3
\torg_regain = 0.25
\tmobilisation_size = 0.15
\tsupply_consumption = -0.2
}

the_flight_of_the_eagle = {
\ticon = 2
\tland_attack_modifier = 0.2
\tland_organisation = 0.2
\tmobilisation_size = 0.2
\tdiplomatic_points_modifier = -0.5
}

the_restoration_of_the_bourbons = {
\ticon = 1
\tcore_pop_militancy_modifier = 2.5
\tcore_pop_consciousness_modifier = 1.0
\tprestige = -0.5
\tland_organisation = -0.15
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "\nthe_retreat_from_moscow = {" not in src:
    wr(f"{MOD}/common/event_modifiers.txt", src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 5

def ev(eid, body, title, desc, opts):
    EV.append(body); loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    for k, v in opts.items(): loc(k, v)
    log["events"] += 1

COAL = ("RUS", "PRU", "AUS", "ENG", "SWE")

# --- 1812: the retreat -------------------------------------------------------------------
ev(9102030, """country_event = {
    id = 9102030
    title = "EVTNAME9102030"
    desc = "EVTDESC9102030"
    picture = "vacation_on_siberia"
    fire_only_once = yes

    trigger = {
        tag = FRA
        has_global_flag = h18_march_on_moscow
        NOT = { has_global_flag = h18_the_retreat }
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9102030"
        set_global_flag = h18_the_retreat
        remove_country_modifier = the_grande_armee
        add_country_modifier = { name = the_retreat_from_moscow duration = 2555 }
        prestige = -25
        war_exhaustion = 20
        leadership = -40
        any_pop = { limit = { has_pop_culture = french } militancy = 4 consciousness = 2 }
        RUS = { prestige = 25 }
    }
}
""", "The Retreat",
"Six hundred thousand men crossed the Niemen in June. The city they marched four "
"hundred leagues to take was burned by its own governor before they entered it, there "
"was nobody left in it to negotiate with, and the Tsar did not answer any of the three "
"letters. They left on the nineteenth of October with winter five weeks away and the "
"Cossacks on both flanks of a column a hundred miles long. Perhaps twenty thousand "
"recrossed the river. The army was not beaten in any battle. It simply stopped "
"existing.",
{"EVTOPTA9102030": "The army is gone. The Emperor is in Paris raising another."})

# --- 1813: Tauroggen and the Sixth Coalition ----------------------------------------------
ev(9102031, f"""country_event = {{
    id = 9102031
    title = "EVTNAME9102031"
    desc = "EVTDESC9102031"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = PRU
        has_global_flag = h18_the_retreat
        year = 1813
        NOT = {{ year = 1817 }}
    }}
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA9102031"
        set_global_flag = h18_sixth_coalition
        add_country_modifier = {{ name = the_sixth_coalition duration = -1 }}
        prestige = 15
        any_pop = {{ militancy = -3 consciousness = 3 }}
{"".join(f"        {t} = {{ add_country_modifier = {{ name = the_sixth_coalition duration = -1 }} }}" + chr(10) for t in ("RUS", "AUS", "SWE"))}        war = {{
            target = FRA
            attacker_goal = {{ casus_belli = cut_down_to_size }}
            defender_goal = {{ casus_belli = status_quo }}
            call_ally = yes
        }}
    }}
}}
""", "The Convention of Tauroggen",
"General Yorck has signed a neutrality with the Russians on his own authority, without "
"orders, which is treason and which he has done anyway because the alternative was "
"marching the Prussian corps back into a French army that no longer exists. Berlin "
"has disavowed him and is arranging to join him. Vienna will take longer and arrive "
"at the same place. The Emperor is raising a new army out of the conscription class "
"of 1814 and it is a very young army.",
{"EVTOPTA9102031": "All Germany, then. Let it be all of it."})

# --- 1813: Leipzig ---------------------------------------------------------------------------
ev(9102032, """country_event = {
    id = 9102032
    title = "EVTNAME9102032"
    desc = "EVTDESC9102032"
    picture = "ambush_army"
    fire_only_once = yes

    trigger = {
        tag = FRA
        has_global_flag = h18_sixth_coalition
        year = 1813
        NOT = { year = 1818 }
        war_with = PRU
    }
    mean_time_to_happen = { months = 8 }

    option = {
        name = "EVTOPTA9102032"
        set_global_flag = h18_leipzig_lost
        prestige = -30
        war_exhaustion = 15
        leadership = -25
        add_country_modifier = { name = the_campaign_of_france duration = 1095 }
        any_pop = { limit = { has_pop_culture = french } militancy = 3 }
        ai_chance = { factor = 80 }
    }
    option = {
        name = "EVTOPTB9102032"
        set_global_flag = h18_leipzig_held
        prestige = 30
        PRU = { war_exhaustion = 20 prestige = -15 }
        AUS = { war_exhaustion = 15 prestige = -10 }
        any_pop = { limit = { has_pop_culture = french } militancy = -3 }
        ai_chance = { factor = 20 }
    }
}
""", "Leipzig: the Battle of the Nations",
"Half a million men over four days, which is more than have ever been put in one "
"place, and in the middle of the third day the Saxon divisions walked across and "
"turned their guns around. The bridge over the Elster was blown while the rearguard "
"was still on the wrong side of it. If the line holds, Germany stays French and the "
"coalition has nothing left to try. If it does not, there is nothing between the "
"allies and the Rhine.",
{"EVTOPTA9102032": "The bridge is blown too early. We are falling back on the Rhine.",
 "EVTOPTB9102032": "The Saxons break and the line holds behind them."})

# --- 1814: the abdication ------------------------------------------------------------------
ev(9102033, """country_event = {
    id = 9102033
    title = "EVTNAME9102033"
    desc = "EVTDESC9102033"
    picture = "treaty_of_paris_1856"
    fire_only_once = yes

    trigger = {
        tag = FRA
        has_global_flag = h18_leipzig_lost
        year = 1814
        NOT = { year = 1819 }
    }
    mean_time_to_happen = { months = 6 }

    option = {
        name = "EVTOPTA9102033"
        set_global_flag = h18_abdication
        add_country_modifier = { name = the_restoration_of_the_bourbons duration = -1 }
        remove_country_modifier = the_campaign_of_france
        government = hms_government
        prestige = -40
        end_war = AUS
        end_war = PRU
        end_war = RUS
        any_pop = { limit = { has_pop_culture = french } militancy = 5 consciousness = 2 }
        ai_chance = { factor = 70 }
    }
    option = {
        name = "EVTOPTB9102033"
        set_global_flag = h18_fought_to_the_end
        war_exhaustion = 25
        prestige = -15
        any_pop = { limit = { has_pop_culture = french } militancy = 7 }
        ai_chance = { factor = 30 }
    }
}
""", "The Marshals Will Not March",
"The allies are in Paris, the Senate has voted his deposition, and at Fontainebleau "
"the marshals have told him to his face that the army will not march on the capital. "
"He has offered to abdicate in favour of his son and been refused. The terms on the "
"table are Elba, a title, a pension and four hundred men, which is an absurd thing to "
"offer the man who held this continent for a decade, and the alternative is a civil "
"war he would fight with conscripts of seventeen.",
{"EVTOPTA9102033": "Abdicate. France has bled enough.",
 "EVTOPTB9102033": "There is still an army. There is still a campaign."})

# --- 1815: the Hundred Days -------------------------------------------------------------------
ev(9102034, """country_event = {
    id = 9102034
    title = "EVTNAME9102034"
    desc = "EVTDESC9102034"
    picture = "ambush_army"
    fire_only_once = yes

    trigger = {
        tag = FRA
        has_global_flag = h18_abdication
        year = 1815
        NOT = { year = 1820 }
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9102034"
        set_global_flag = h18_the_hundred_days
        remove_country_modifier = the_restoration_of_the_bourbons
        add_country_modifier = { name = the_flight_of_the_eagle duration = 1095 }
        government = absolute_monarchy
        prestige = 15
        any_pop = { limit = { has_pop_culture = french } militancy = -4 consciousness = 3 }
        ENG = {
            war = {
                target = THIS
                attacker_goal = { casus_belli = cut_down_to_size }
                defender_goal = { casus_belli = status_quo }
                call_ally = yes
            }
        }
        ai_chance = { factor = 60 }
    }
    option = {
        name = "EVTOPTB9102034"
        set_global_flag = h18_elba_kept
        prestige = -5
        ai_chance = { factor = 40 }
    }
}
""", "A Thousand Men Land at Golfe-Juan",
"He has left Elba with the guard that was allowed him and come ashore near Antibes. "
"The regiment sent from Grenoble to arrest him formed line across the road, and he "
"walked out in front of it alone, opened his coat and invited them to fire on their "
"Emperor. They have joined him. So has every unit sent since, so has Ney, who "
"promised to bring him back in an iron cage. He will be in Paris within the month "
"without a shot fired, and every power in Europe has already declared him an outlaw.",
{"EVTOPTA9102034": "To Paris. The eagles will fly from steeple to steeple.",
 "EVTOPTB9102034": "The island is enough. It is finished."})

ev(9102035, """country_event = {
    id = 9102035
    title = "EVTNAME9102035"
    desc = "EVTDESC9102035"
    picture = "ambush_army"
    fire_only_once = yes

    trigger = {
        tag = FRA
        has_global_flag = h18_the_hundred_days
        war_with = ENG
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9102035"
        set_global_flag = h18_waterloo_lost
        remove_country_modifier = the_flight_of_the_eagle
        add_country_modifier = { name = the_restoration_of_the_bourbons duration = -1 }
        government = hms_government
        prestige = -35
        leadership = -30
        end_war = ENG
        any_pop = { limit = { has_pop_culture = french } militancy = 6 }
        ai_chance = { factor = 75 }
    }
    option = {
        name = "EVTOPTB9102035"
        set_global_flag = h18_waterloo_won
        prestige = 40
        ENG = { war_exhaustion = 25 prestige = -25 }
        PRU = { war_exhaustion = 20 }
        any_pop = { limit = { has_pop_culture = french } militancy = -5 consciousness = 2 }
        ai_chance = { factor = 25 }
    }
}
""", "Waterloo",
"A ridge, a farmhouse and a sunken road, in mud that delayed the opening of the guns "
"by three hours. Grouchy is somewhere to the east with a third of the army, following "
"orders written before anyone knew where the Prussians had gone, and at four in the "
"afternoon the smudge appearing on the right flank is either Grouchy or it is Blucher. "
"The margin is the width of that question.",
{"EVTOPTA9102035": "It is Blucher. The Guard is falling back, and the Guard does not fall back.",
 "EVTOPTB9102035": "It is Grouchy. The line opposite is breaking."})

wr(f"{MOD}/events/1800_Napoleonic_Fall.txt", "\n".join(EV))
wr(f"{MOD}/localisation/43_fall.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
