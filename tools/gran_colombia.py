"""Gran Colombia: a union of three countries that had never been one.

The Venezuelan chain ran revolution, victory, and stop. The thing it was all for --
the Republic of Colombia, proclaimed at Angostura in December 1819 -- was never built,
and the tag sat in the files with no cores and nothing to create it. So a player could
win the war of independence and find that the country the war produced did not exist.

The union is the point of the whole arc and so is its failure. It lasted eleven years
and came apart along exactly the line Madrid had drawn in 1777, which is the argument
for modelling the Captaincy General separately in the first place.

What this adds, in order:

  **1817, Piar.** Manuel Piar won San Felix, which is the victory that gave the
  republic Guayana and therefore a base. He was a pardo from Curacao, he would not
  take orders from Bolivar, and he was shot at Angostura in October on a charge of
  inciting race war. Bolivar wrote afterwards that it was the hardest order he ever
  gave and that it saved the country. Both halves of that are arguable.

  **1819, Angostura.** The congress meets in a river town, Bolivar crosses the
  flooded llanos and the Andes in the rainy season, Boyaca opens New Granada, and in
  December a republic is proclaimed comprising Venezuela, New Granada and a Quito
  that is still entirely Spanish.

  **1820, Trujillo.** Bolivar and Morillo meet and sign an armistice and a treaty
  regularising the war -- no more war to the death on either side. Morillo goes home.
  The armistice is broken within six months when Maracaibo declares for the republic.

  **1826, La Cosiata.** Paez is summoned to Bogota to answer for a conscription
  dispute and Valencia tells him not to go. The affair -- the word means roughly "the
  silly business" -- is the first open Venezuelan rejection of government from Bogota
  and it never really ends.

  **1830.** Venezuela separates in January, Quito in May, and Bolivar dies in December
  at Santa Marta on his way to exile, having written that those who served the
  revolution had ploughed the sea.
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

ANGOSTURA, BOGOTA, QUITO, CARACAS = 2275, 2247, 2279, 2264

MODS = """
the_union_of_angostura = {
\ticon = 8
\tprestige = 0.8
\tdiplomatic_points_modifier = 0.3
\tcore_pop_consciousness_modifier = 1.0
\tadministrative_efficiency_modifier = -0.1
}

la_cosiata = {
\ticon = 1
\tcore_pop_militancy_modifier = 2.5
\tadministrative_efficiency_modifier = -0.25
\ttax_efficiency = -0.15
\tland_organisation = -0.1
}

the_sea_was_ploughed = {
\ticon = 1
\tprestige = -0.5
\tcore_pop_consciousness_modifier = 1.5
\tcore_pop_militancy_modifier = 1.0
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "\nthe_union_of_angostura = {" not in src:
    wr(f"{MOD}/common/event_modifiers.txt", src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 3

def ev(eid, body, title, desc, opts):
    EV.append(body); loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc)
    for k, v in opts.items(): loc(k, v)
    log["events"] += 1

# --- 1817: Piar ----------------------------------------------------------------------------
ev(9103420, """country_event = {
    id = 9103420
    title = "EVTNAME9103420"
    desc = "EVTDESC9103420"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = VNZ
        has_country_flag = h18v_angostura
        NOT = { year = 1820 }
        NOT = { exists = GCO }
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9103420"
        set_country_flag = h18v_piar_shot
        prestige = -5
        leadership = -10
        any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = 5 consciousness = 3 }
        any_pop = { limit = { has_pop_culture = criollo } militancy = -3 }
        ai_chance = { factor = 70 }
    }
    option = {
        name = "EVTOPTB9103420"
        set_country_flag = h18v_piar_spared
        prestige = 5
        any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = -4 consciousness = 2 }
        any_pop = { limit = { has_pop_culture = criollo } militancy = 4 consciousness = 2 }
        ai_chance = { factor = 30 }
    }
}
""", "The Trial of General Piar",
"He won San Felix, which is the battle that gave this republic Guayana and therefore a "
"base to exist in, and since then he has refused orders, left the army without leave "
"and been heard telling pardo officers that the creoles will discard them once the "
"Spanish are gone. He is not wrong about that and saying it is the charge. The court "
"martial has found him guilty of inciting a race war and sentenced him to be shot in "
"the plaza at Angostura. The signature required is the Liberator's.",
{"EVTOPTA9103420": "Sign it. The republic cannot have two armies.",
 "EVTOPTB9103420": "Exile him. I will not shoot the man who won San Felix."})

# --- 1819: Angostura, and the union ------------------------------------------------------------
ev(9103421, f"""country_event = {{
    id = 9103421
    title = "EVTNAME9103421"
    desc = "EVTDESC9103421"
    picture = "map_of_colombia"
    fire_only_once = yes

    trigger = {{
        tag = VNZ
        has_country_flag = h18v_angostura
        year = 1819
        NOT = {{ year = 1828 }}
        NOT = {{ exists = GCO }}
    }}
    mean_time_to_happen = {{ months = 9 }}

    option = {{
        name = "EVTOPTA9103421"
        set_global_flag = h18_gran_colombia
        set_country_flag = h18c_independent
        all_core = {{ remove_core = VNZ }}
        change_tag = GCO
        government = presidential_dictatorship
        vote_franschise = landed_voting
        capital = {ANGOSTURA}
        add_country_modifier = {{ name = the_union_of_angostura duration = -1 }}
        add_accepted_culture = criollo
        add_accepted_culture = mestizo
        prestige = 30
        any_pop = {{ militancy = -4 consciousness = 4 }}
        ai_chance = {{ factor = 85 }}
    }}
    option = {{
        name = "EVTOPTB9103421"
        set_country_flag = h18v_venezuela_alone
        prestige = 5
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 2 }}
        ai_chance = {{ factor = 15 }}
    }}
}}
""", "The Congress of Angostura",
"Twenty-six deputies in a river town six hundred miles from Caracas, which is still "
"Spanish, debating a constitution for a country that does not yet control most of "
"itself. The Liberator has proposed a hereditary senate and a president for life and "
"been talked out of the second. The republic to be proclaimed comprises Venezuela, "
"New Granada and Quito -- and Quito is entirely in Spanish hands, which the congress "
"has decided is a detail. There is an argument that a country this size cannot be "
"governed from anywhere. There is a better one that three of them separately will be "
"eaten.",
{"EVTOPTA9103421": "One republic, from the Orinoco to the Amazon.",
 "EVTOPTB9103421": "Venezuela is enough of a country to govern."})

# --- 1820: Trujillo ----------------------------------------------------------------------------
ev(9103422, """country_event = {
    id = 9103422
    title = "EVTNAME9103422"
    desc = "EVTDESC9103422"
    picture = "treaty_of_paris_1856"
    fire_only_once = yes

    trigger = {
        OR = { tag = GCO tag = VNZ }
        has_country_flag = h18c_independent
        year = 1820
        NOT = { year = 1824 }
        has_global_flag = h18_trienio
    }
    mean_time_to_happen = { months = 5 }

    option = {
        name = "EVTOPTA9103422"
        set_country_flag = h18v_trujillo
        prestige = 10
        war_exhaustion = -15
        SPA = { relation = { who = THIS value = 50 } war_exhaustion = -10 }
        any_pop = { militancy = -3 }
        ai_chance = { factor = 70 }
    }
    option = {
        name = "EVTOPTB9103422"
        prestige = -3
        any_pop = { militancy = 2 }
        ai_chance = { factor = 30 }
    }
}
""", "The Armistice at Trujillo",
"Riego's mutiny has changed everything in Madrid and Morillo has orders to negotiate "
"rather than fight. The two of them met at Santa Ana, embraced in front of both "
"staffs, dined at the same table and slept in the same house, which nobody present "
"could quite believe. The agreement suspends the war for six months and -- more "
"importantly -- ends the war to the death on both sides, which has been the character "
"of this conflict since 1813. Morillo is going home. He has asked to be remembered to "
"the Liberator.",
{"EVTOPTA9103422": "Six months, and no more executions of prisoners.",
 "EVTOPTB9103422": "There is nothing to negotiate while a Spaniard remains."})

# --- 1826: La Cosiata ----------------------------------------------------------------------------
ev(9103423, """country_event = {
    id = 9103423
    title = "EVTNAME9103423"
    desc = "EVTDESC9103423"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = GCO
        year = 1826
        NOT = { year = 1834 }
    }
    mean_time_to_happen = { months = 8 }

    option = {
        name = "EVTOPTA9103423"
        set_country_flag = h18g_cosiata
        add_country_modifier = { name = la_cosiata duration = -1 }
        any_pop = { militancy = 4 consciousness = 3 }
        prestige = -8
        ai_chance = { factor = 60 }
    }
    option = {
        name = "EVTOPTB9103423"
        set_country_flag = h18g_paez_obeyed
        prestige = 8
        any_pop = { militancy = -2 }
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 2 }
        ai_chance = { factor = 40 }
    }
}
""", "La Cosiata",
"Paez has been summoned to Bogota to answer for how he conducted a conscription in "
"Caracas, and the municipality of Valencia has told him not to go and proclaimed him "
"civil and military chief of Venezuela on its own authority. Nobody involved is quite "
"calling it a secession, which is why it has acquired the name it has -- the silly "
"business, roughly. What it actually is: the first time a Venezuelan has openly "
"refused an order from Bogota, and the discovery that nothing happens when he does.",
{"EVTOPTA9103423": "Valencia has spoken for Venezuela. Bogota can object.",
 "EVTOPTB9103423": "He goes to Bogota. The union is worth the humiliation."})

# --- 1830: the separation --------------------------------------------------------------------------
ev(9103424, f"""country_event = {{
    id = 9103424
    title = "EVTNAME9103424"
    desc = "EVTDESC9103424"
    picture = "map_of_colombia"
    fire_only_once = yes

    trigger = {{
        tag = GCO
        year = 1830
        NOT = {{ year = 1840 }}
        OR = {{
            has_country_flag = h18g_cosiata
            year = 1833
        }}
    }}
    mean_time_to_happen = {{ months = 6 }}

    option = {{
        name = "EVTOPTA9103424"
        set_global_flag = h18_colombia_dissolved
        add_country_modifier = {{ name = the_sea_was_ploughed duration = -1 }}
        VNZ = {{
            all_core = {{ secede_province = THIS }}
            capital = {CARACAS}
        }}
        ECU = {{ all_core = {{ secede_province = THIS }} }}
        all_core = {{ remove_core = GCO }}
        change_tag = CLM
        capital = {BOGOTA}
        prestige = -20
        any_pop = {{ militancy = 4 consciousness = 2 }}
        ai_chance = {{ factor = 80 }}
    }}
    option = {{
        name = "EVTOPTB9103424"
        set_country_flag = h18g_union_held
        remove_country_modifier = la_cosiata
        add_country_modifier = {{ name = the_union_preserved duration = -1 }}
        political_reform = federalism
        prestige = 15
        any_pop = {{ militancy = -4 consciousness = 2 }}
        ai_chance = {{ factor = 20 }}
    }}
}}
""", "The Sea Was Ploughed",
"Venezuela separated in January and Quito in May, and in both cases the men who did it "
"were the generals who had made the republic. The Liberator resigned in April, has "
"been refused permission to land at La Guaira by the country he liberated, and is at "
"Santa Marta on the coast with a consumption and no money, waiting for a ship to "
"Europe he will not board. His own assessment, written a few weeks ago to a friend, "
"was that those who served the revolution had ploughed the sea. Granting the point "
"and conceding the federation are different things, and the second was available for "
"eleven years.",
{"EVTOPTA9103424": "Three countries, then. It was always three countries.",
 "EVTOPTB9103424": "Concede the federation. It is late and it may still answer."})

wr(f"{MOD}/events/1800_Gran_Colombia.txt", "\n".join(EV))
wr(f"{MOD}/localisation/47_gran_colombia.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
