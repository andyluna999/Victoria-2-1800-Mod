"""Iturrigaray, and the first coup in Mexican history.

When news of Bayonne reached Mexico City in July 1808, Viceroy José de Iturrigaray did
something no viceroy had done: he asked. He convened the ayuntamiento of Mexico City
and let it argue, in public, about who governed New Spain now that there was no King.
The criollo lawyers answered with Suárez -- that sovereignty reverts to the people in
the absence of a legitimate sovereign -- and proposed a junta to govern in Ferdinand's
name. Iturrigaray did not say no.

On the night of 15 September 1808, three hundred armed men led by the merchant Gabriel
de Yermo seized the palace, arrested the viceroy in his bed, and shipped him to Spain.
The Audiencia installed a compliant old soldier and declared the matter closed.

It was the first coup in Mexican history and it settled nothing except the method. The
criollos had tried the legal route, in the open, with the viceroy's consent, and a
private army of peninsular merchants had ended it in a night. Two years later Hidalgo
rang the bell at Dolores, and the men who followed him had watched this happen.

The player is the viceroy. The choice is Iturrigaray's: convene the junta and risk
Yermo, or hold for the peninsular party and keep a throne nobody is sitting on.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# The opening question, reached from Bayonne.
EV.append("""country_event = {
    id = 9101100
    title = "EVTNAME9101100"
    desc = "EVTDESC9101100"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = NSP
        year = 1808
        NOT = { year = 1810 }
        has_country_flag = h18c_bayonne_known
    }
    mean_time_to_happen = { months = 2 }

    option = {
        name = "EVTOPTA9101100"
        set_country_flag = h18c_junta_convened
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 4 militancy = -2 }
        any_pop = { limit = { has_pop_culture = spanish } militancy = 4 }
        prestige = 5
        random_list = {
            70 = { country_event = { id = 9101101 days = 45 } }
            30 = { country_event = { id = 9101102 days = 45 } }
        }
        ai_chance = { factor = 55 }
    }
    option = {
        name = "EVTOPTB9101100"
        set_country_flag = h18c_held_for_the_audiencia
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 3 militancy = 3 }
        any_pop = { limit = { has_pop_culture = spanish } militancy = -2 }
        SPA = { relation = { who = THIS value = 30 } }
        ai_chance = { factor = 45 }
    }
}
""")
loc("EVTNAME9101100", "The Viceroy Is Asked Who Governs")
loc("EVTDESC9101100",
    "There is no King. The ayuntamiento of Mexico City has petitioned for a junta to "
    "govern this kingdom in Ferdinand's name until he is restored, and its lawyers cite "
    "Suárez: in the absence of a legitimate sovereign, authority reverts to the people "
    "who granted it. The Audiencia calls this treason dressed as theology, and the "
    "peninsular merchants -- who own the import trade and know exactly what a creole "
    "junta would do to it -- are saying so in the streets. No viceroy has ever convened "
    "such a body. No viceroy has ever had no King.")
loc("EVTOPTA9101100", "Let the ayuntamiento meet.")
loc("EVTOPTB9101100", "The Audiencia governs until His Majesty returns.")

# Yermo's night.
EV.append("""country_event = {
    id = 9101101
    title = "EVTNAME9101101"
    desc = "EVTDESC9101101"
    picture = "administration"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9101101"
        set_global_flag = h18_yermo_coup
        set_country_flag = h18c_viceroy_deposed
        add_country_modifier = { name = the_yermo_settlement duration = -1 }
        any_pop = { limit = { has_pop_culture = criollo } militancy = 6 consciousness = 5 }
        any_pop = { limit = { has_pop_culture = mestizo } militancy = 3 }
        prestige = -10
        SPA = { relation = { who = THIS value = 20 } }
    }
}
""")
loc("EVTNAME9101101", "The Coup Succeeds: the Viceroy Is Taken")
loc("EVTDESC9101101",
    "Three hundred armed men of the Parián, led by the merchant Gabriel de Yermo, came "
    "over the palace wall at one in the morning and took the viceroy out of his bed. He "
    "is on a ship to Cádiz. The Audiencia has installed Garibay, who is eighty and will "
    "sign whatever is placed before him, and has declared the question of the junta "
    "closed. The creoles have just learned what happens when they ask politely and in "
    "public, with the viceroy's own consent. They will not ask again.")
loc("EVTOPTA9101101", "Then the next men will not ask.")

# The junta holds.
EV.append("""country_event = {
    id = 9101102
    title = "EVTNAME9101102"
    desc = "EVTDESC9101102"
    picture = "administration"
    is_triggered_only = yes

    option = {
        name = "EVTOPTA9101102"
        set_global_flag = h18_mexico_junta_holds
        set_country_flag = h18c_junta_governs
        government = presidential_dictatorship
        political_parties = harassment
        add_country_modifier = { name = the_junta_of_new_spain duration = -1 }
        any_pop = { limit = { has_pop_culture = criollo } militancy = -4 consciousness = 4 }
        any_pop = { limit = { has_pop_culture = spanish } militancy = 5 }
        prestige = 15
    }
}
""")
loc("EVTNAME9101102", "The Coup Fails: the Junta Sits")
loc("EVTDESC9101102",
    "Yermo's men were arrested at the gate; somebody in the palace guard talked. The "
    "junta of New Spain sits in Mexico City, governs in the name of Ferdinand VII, and "
    "sends no silver to a Spain that has no government to receive it. Every peninsular "
    "merchant in the Parián regards it as a rebellion that has not yet admitted what it "
    "is. They may be right. Nobody here has said the word independence, and nobody here "
    "has said the word obedience either.")
loc("EVTOPTA9101102", "We govern for the King, wherever he is.")

MODS = """
the_yermo_settlement = {
\ticon = 1
\tcore_pop_militancy_modifier = 2.0
\tcore_pop_consciousness_modifier = 1.0
\tadministrative_efficiency_modifier = -0.1
\tglobal_assimilation_rate = -0.3
}

the_junta_of_new_spain = {
\ticon = 8
\ttax_efficiency = 0.1
\tadministrative_efficiency_modifier = 0.1
\tcore_pop_consciousness_modifier = 1.0
\tresearch_points_modifier = 0.08
}
"""
src = open(f"{MOD}/common/event_modifiers.txt", encoding="cp1252", errors="replace").read()
if "the_yermo_settlement" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 2

wr(f"{MOD}/events/1800_Iturrigaray.txt", "\n".join(EV))
wr(f"{MOD}/localisation/15_iturrigaray.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["events"] = len(EV); log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
