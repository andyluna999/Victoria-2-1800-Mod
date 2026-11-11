"""Haiti after independence, 1804-1822.

The revolution is the famous part and the eighteen years after it are the interesting
part, because that is where the republic decides what it is going to be.

  **1804** Dessalines orders the remaining French colonists killed. Between three and
  five thousand die. He spares the Polish legionnaires, who had deserted Leclerc rather
  than fight people fighting for their freedom, and the Germans, and the priests and
  doctors. The 1805 constitution then declares every Haitian black regardless of
  complexion, naturalises the Poles as such, and forbids any white to own land.

  **1806** He is shot at Pont-Rouge by a conspiracy his own generals are in. Christophe
  and Pétion both have a hand in it and neither will admit it.

  **The split.** Christophe takes the north and makes it a kingdom: a nobility with
  invented titles, the Citadelle built on the mountain by forced labour, plantation
  discipline restored under the name of a royal corvée, and an export economy that
  works. Pétion takes the south and breaks the plantations up into smallholdings for
  the men who fought. His republic is poor, free, and produces almost nothing for sale.

  That is a real argument about what the revolution was for, and the mod gives it to
  the player as one rather than as a thirteen-year civil war between two AI tags --
  which Victoria II would simulate badly and which would obscure the choice.

  **1815** Pétion gives Bolívar refuge, arms, powder, ships, a printing press and men,
  after the Venezuelan republics have collapsed and no one else in the hemisphere will
  touch him. He asks one thing in return: free the slaves in whatever you liberate.
  Bolívar did. This is the single most consequential thing Haiti ever did abroad, and
  it is available only on Pétion's path, because Christophe's kingdom had no interest
  in funding republics.

  **1820** Christophe, half-paralysed by a stroke and facing mutiny, shoots himself.
  **1822** Boyer marches into Santo Domingo and holds the whole island for twenty-two
  years.
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

MODS = """
the_general_toussaint = {
\ticon = 2
\tland_organisation = 0.3
\tland_defense_modifier = 0.35
\torg_regain = 0.25
\tmobilisation_size = 0.1
\tleadership = 2
\tsupply_consumption = -0.2
}

the_1805_constitution = {
\ticon = 2
\tglobal_immigrant_attract = -0.5
\tcore_pop_militancy_modifier = -1.0
\tglobal_assimilation_rate = -0.4
\tbadboy = 0.02
}

the_royal_corvee = {
\ticon = 4
\trgo_output = 0.3
\ttax_efficiency = 0.2
\tcore_pop_militancy_modifier = 2.0
\tglobal_population_growth = -0.001
}

the_land_of_smallholders = {
\ticon = 8
\trgo_output = -0.25
\ttax_efficiency = -0.2
\tcore_pop_militancy_modifier = -2.5
\tglobal_population_growth = 0.002
\tglobal_assimilation_rate = 0.2
}

the_bolivarian_debt = {
\ticon = 8
\tprestige = 0.5
\tdiplomatic_points_modifier = 0.25
}
"""
src = open(f"{MOD}/common/event_modifiers.txt", encoding="cp1252", errors="replace").read()
if "the_royal_corvee" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = MODS.count(" = {")

def ev(eid, body, title, desc, opts):
    EV.append(body)
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    for k, v in opts.items(): loc(k, v)
    log["events"] += 1

# --- 1804: the massacre ---------------------------------------------------------------
ev(9101306, """country_event = {
    id = 9101306
    title = "EVTNAME9101306"
    desc = "EVTDESC9101306"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = HAI
        year = 1804
        NOT = { year = 1806 }
    }
    mean_time_to_happen = { months = 3 }

    option = {
        name = "EVTOPTA9101306"
        set_country_flag = h18h_the_massacre
        add_country_modifier = { name = the_1805_constitution duration = -1 }
        badboy = 4
        prestige = -5
        ENG = { relation = { who = THIS value = -50 } }
        USA = { relation = { who = THIS value = -50 } }
        any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = -3 }
        ai_chance = { factor = 75 }
    }
    option = {
        name = "EVTOPTB9101306"
        set_country_flag = h18h_the_colonists_spared
        prestige = 5
        ENG = { relation = { who = THIS value = 20 } }
        any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = 3 consciousness = 2 }
        ai_chance = { factor = 25 }
    }
}
""", "The Colonists Who Stayed",
"Some two thousand French remain, on plantations they still believe are theirs, in a "
"country that has just stopped being France. The General says that while one of them "
"draws breath the revolution is provisional, and that the French will come back for "
"them as they came back for Guadeloupe, where slavery was restored last year. The "
"Poles who deserted Leclerc rather than fight us are not in question, nor the priests, "
"nor the doctors.",
{"EVTOPTA9101306": "The revolution must be made permanent.",
 "EVTOPTB9101306": "We did not fight to become them."})

# --- 1806: Pont-Rouge ------------------------------------------------------------------
ev(9101307, """country_event = {
    id = 9101307
    title = "EVTNAME9101307"
    desc = "EVTDESC9101307"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = HAI
        year = 1806
        NOT = { year = 1809 }
        # Either way. Dessalines was shot by his own generals over the land question
        # and his treatment of the mulatto officers, not over the colonists -- gating
        # this on the massacre meant a player who spared them kept him for ever.
        OR = {
            has_country_flag = h18h_the_massacre
            has_country_flag = h18h_the_colonists_spared
        }
    }
    mean_time_to_happen = { months = 6 }

    option = {
        name = "EVTOPTA9101307"
        set_country_flag = h18h_christophe
        government = absolute_monarchy
        add_country_modifier = { name = the_royal_corvee duration = -1 }
        prestige = 10
        any_pop = { limit = { type = farmers } militancy = 4 }
        any_pop = { limit = { type = aristocrats } consciousness = 3 }
        ai_chance = { factor = 50 }
    }
    option = {
        name = "EVTOPTB9101307"
        set_country_flag = h18h_petion
        government = presidential_dictatorship
        vote_franschise = landed_voting
        add_country_modifier = { name = the_land_of_smallholders duration = -1 }
        any_pop = { limit = { type = farmers } militancy = -5 consciousness = 2 }
        ai_chance = { factor = 50 }
    }
}
""", "Pont-Rouge",
"The Emperor was shot this morning on the road north out of Port-au-Prince, by soldiers "
"of his own army, in an ambush his own generals arranged. Nobody will say which of them "
"ordered it and both of the men who matter were certainly in it. Christophe holds the "
"north with the army and intends a kingdom. Pétion holds the south and intends to give "
"the plantations to the men who took them. The question is what the revolution was for, "
"and it is going to be answered now.",
{"EVTOPTA9101307": "A kingdom in the north: order, and the Citadelle.",
 "EVTOPTB9101307": "A republic in the south: the land to those who fought."})

# --- 1815: Pétion and Bolívar ------------------------------------------------------------
ev(9101310, """country_event = {
    id = 9101310
    title = "EVTNAME9101310"
    desc = "EVTDESC9101310"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = HAI
        year = 1815
        NOT = { year = 1818 }
        has_country_flag = h18h_petion
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9101310"
        set_global_flag = h18_petion_funds_bolivar
        add_country_modifier = { name = the_bolivarian_debt duration = -1 }
        treasury = -15000
        prestige = 15
        VNG = { country_event = { id = 9101311 days = 30 } }
        CLM = { country_event = { id = 9101311 days = 30 } }
        ai_chance = { factor = 85 }
    }
    option = {
        name = "EVTOPTB9101310"
        set_global_flag = h18_bolivar_refused
        prestige = -5
        treasury = 5000
        ai_chance = { factor = 15 }
    }
}
""", "A Venezuelan at Les Cayes",
"The republics he raised have collapsed twice and he has come here because there is "
"nowhere else: the British will not have him, the Americans will not arm him, and the "
"Jamaican planters tried to have him killed. He is asking for powder, muskets, ships "
"and men. The President is minded to give him all of it and to take nothing for it "
"except a promise: that wherever his armies go, the slaves are freed. He is also "
"minded to ask that Haiti's name appear nowhere in the business, because a republic of "
"former slaves endorsing a liberator would be the end of the liberator.",
{"EVTOPTA9101310": "Arms, ships, and one condition.",
 "EVTOPTB9101310": "We cannot afford another man's war."})

ev(9101311, """country_event = {
    id = 9101311
    title = "EVTNAME9101311"
    desc = "EVTDESC9101311"
    picture = "administration"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9101311"
        prestige = 10
        set_country_flag = h18c_armed_from_haiti
        any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = -3 consciousness = 3 }
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 2 }
    }
}
""", "Arms from Les Cayes",
"The expedition sailed from a Haitian port with Haitian powder and Haitian gunners, and "
"the price of it was a proclamation freeing every slave in the territories we take. "
"The planters who bankrolled the first republic will not like it. The men who will "
"actually do the fighting will.",
{"EVTOPTA9101311": "Freedom for those who take up arms."})

# --- 1820 and 1822 -------------------------------------------------------------------------
ev(9101312, """country_event = {
    id = 9101312
    title = "EVTNAME9101312"
    desc = "EVTDESC9101312"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = HAI
        year = 1820
        NOT = { year = 1823 }
        OR = {
            has_country_flag = h18h_christophe
            has_country_flag = h18h_petion
        }
    }
    mean_time_to_happen = { months = 6 }

    option = {
        name = "EVTOPTA9101312"
        set_country_flag = h18h_reunified
        remove_country_modifier = the_royal_corvee
        add_country_modifier = { name = the_land_of_smallholders duration = -1 }
        government = presidential_dictatorship
        prestige = 10
        any_pop = { militancy = -3 }
    }
}
""", "The Silver Bullet",
"Christophe has been half-paralysed since he collapsed at mass in August, the garrison "
"at Saint-Marc has gone over, and his own guard is coming up the hill to the palace at "
"Sans-Souci. He has shot himself rather than be taken. The kingdom dissolves within the "
"week and the island has one government for the first time since Pont-Rouge.",
{"EVTOPTA9101312": "One republic, from Môle to Jacmel."})

ev(9101313, """country_event = {
    id = 9101313
    title = "EVTNAME9101313"
    desc = "EVTDESC9101313"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = HAI
        year = 1822
        NOT = { year = 1825 }
        has_country_flag = h18h_reunified
        NOT = { has_global_flag = santo_domingo_accepted }
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9101313"
        set_global_flag = h18_boyer_occupation
        2214 = { secede_province = THIS add_core = THIS }
        2216 = { secede_province = THIS add_core = THIS }
        badboy = 3
        prestige = 10
        any_pop = { limit = { has_pop_culture = afro_caribbean } consciousness = 2 }
        ai_chance = { factor = 80 }
    }
    option = {
        name = "EVTOPTB9101313"
        set_global_flag = h18_hispaniola_divided
        prestige = -3
        ai_chance = { factor = 20 }
    }
}
""", "The Whole Island",
"Santo Domingo declared itself independent of Spain nine weeks ago and has already "
"asked Gran Colombia to protect it. The President's view is that no part of this island "
"can be left to a government that permits slavery, because the French will use it as a "
"doorway the moment they decide to come back. The Dominicans' view of being protected "
"from slavery by annexation has not been asked for.",
{"EVTOPTA9101313": "The island is one and indivisible.",
 "EVTOPTB9101313": "Let them govern themselves."})


# --- Toussaint, and the parley at Ennery ------------------------------------------
# Haiti kept being conquered by the United States in playtests, and the deeper reason
# is that it is modelled as a small friendless state when for four years it was the
# strongest military power in the Caribbean. Toussaint beat the Spanish, the British
# and Rigaud in succession, and the British expedition that tried to take Saint-
# Domingue lost more men there than Wellington lost in the whole Peninsular War.
#
# So while he lives, Haiti fights like that. And he is lost the way he was actually
# lost: not in battle, but at a parley. In June 1802 Brunet invited him to discuss
# terms at Ennery, arrested him at the table and put him on a ship. He died in a cell
# in the Jura the next April, and Napoleon's officers admitted afterwards that
# nothing else would have worked.
EV.append("""country_event = {
    id = 9101320
    title = "EVTNAME9101320"
    desc = "EVTDESC9101320"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = HAI
        year = 1800
    }
    mean_time_to_happen = { days = 4 }

    option = {
        name = "EVTOPTA9101320"
        set_country_flag = h18h_toussaint_lives
        add_country_modifier = { name = the_general_toussaint duration = -1 }
    }
}

country_event = {
    id = 9101321
    title = "EVTNAME9101321"
    desc = "EVTDESC9101321"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = HAI
        has_country_flag = h18h_toussaint_lives
        has_global_flag = h18_leclerc
        year = 1802
        NOT = { year = 1807 }
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9101321"
        set_country_flag = h18h_went_to_the_parley
        random_list = {
            70 = { country_event = { id = 9101322 days = 10 } }
            30 = { country_event = { id = 9101323 days = 10 } }
        }
        ai_chance = { factor = 60 }
    }
    option = {
        name = "EVTOPTB9101321"
        set_country_flag = h18h_refused_the_parley
        prestige = -5
        any_pop = { militancy = 2 }
        FRA = { relation = { who = THIS value = -40 } }
        ai_chance = { factor = 40 }
    }
}

country_event = {
    id = 9101322
    title = "EVTNAME9101322"
    desc = "EVTDESC9101322"
    picture = "administration"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9101322"
        clr_country_flag = h18h_toussaint_lives
        set_country_flag = h18h_toussaint_taken
        remove_country_modifier = the_general_toussaint
        prestige = -15
        any_pop = { militancy = 5 consciousness = 3 }
    }
}

country_event = {
    id = 9101323
    title = "EVTNAME9101323"
    desc = "EVTDESC9101323"
    picture = "administration"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9101323"
        prestige = 15
        any_pop = { militancy = -2 }
        FRA = { prestige = -10 }
    }
}
""")
loc("EVTNAME9101320", "The First of the Blacks")
loc("EVTDESC9101320",
    "He was a coachman at fifty and is governor-general at fifty-seven, having beaten "
    "the Spanish, the British and Rigaud in that order with an army he built out of "
    "people who had been property. The British lost more men in this colony than they "
    "will lose in Spain. Whatever else is true of Saint-Domingue, it is not a place "
    "anybody takes cheaply while he is in it.")
loc("EVTOPTA9101320", "An army out of nothing, and nobody has beaten it.")
loc("EVTNAME9101321", "The Invitation to Ennery")
loc("EVTDESC9101321",
    "General Brunet writes that he wishes to discuss the arrangements, that the hour "
    "is late, that he is unwell and cannot travel, and would the General be so good as "
    "to come to him. The letter is courteous in a way that courteous letters from "
    "French generals have not lately been. Every officer here has told him not to go. "
    "He has observed that he has given his word, and that a man who will not treat "
    "cannot make peace.")
loc("EVTOPTA9101321", "I have given my word. I will go.")
loc("EVTOPTB9101321", "Let him come to me, or let there be no terms.")
loc("EVTNAME9101322", "Taken at the Table")
loc("EVTDESC9101322",
    "He was arrested in the room, put aboard the Creole the same night and is gone to "
    "France. In overturning me they have felled only the trunk of the tree of liberty, "
    "he said at the quay; it will spring up again, for its roots are many and deep. He "
    "will die of cold and hunger in a fortress in the Jura within the year. The roots "
    "turn out to be exactly as deep as he said.")
loc("EVTOPTA9101322", "They have felled only the trunk.")
loc("EVTNAME9101323", "He Did Not Go Alone")
loc("EVTDESC9101323",
    "He came with four hundred of the guard and Brunet's dragoons were not enough, and "
    "the thing that was meant to happen at that table did not happen. The French have "
    "lost the only card they held that did not require them to win in the field, and "
    "they are not going to win in the field.")
loc("EVTOPTA9101323", "A man who will not treat cannot make peace. A fool goes alone.")
log["events"] += 4

wr(f"{MOD}/events/1800_Haiti_After.txt", "\n".join(EV))
wr(f"{MOD}/localisation/19_haiti_after.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
