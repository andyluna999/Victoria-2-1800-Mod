"""Two probabilistic divergence nodes, plus a correction to Hispaniola.

The design rule these follow: a historical moment is not a script. Every node is a
weighted draw, calibrated so an unattended run reproduces what happened most of the
time while leaving the other branch genuinely live. Victoria II's `random_list` takes
flat integer weights, so the odds are stated in the file and can be argued with.

Node 1 -- Pativilca, January 1824. Bolivar lay close to death at Pativilca for weeks,
thin enough that Mosquera described him as a wreck, and recovered to fight Junin and
Ayacucho. Nothing made that recovery inevitable. If he dies, Gran Colombia passes to
Santander: a lawyer, a superb administrator, and not a caudillo.

Node 2 -- Santo Domingo, December 1821. Nunez de Caceres declared the Estado
Independiente del Haiti Espanol and formally petitioned to join Gran Colombia. Before
Bogota answered, Boyer marched and annexed the whole island for twenty-two years. The
petition was real and the answer was never given.
"""
import os, re

MOD = "/home/claude/build/HPM"
EV, LOC, MODS = [], [], []
def loc(k, v): LOC.append(f"{k};{v};;;;;;;;;;;;;x")

MODS.append("""
# --- divergence: the Liberator ---

santander_republic = {
    icon = 1
    research_points_modifier = 0.20
    tax_efficiency = 0.20
    global_pop_consciousness_modifier = 0.02
    prestige = -0.5
    mobilisation_size = -0.04
    land_organisation = -0.10
}
the_liberator_lives = {
    icon = 3
    prestige = 0.5
    mobilisation_size = 0.05
    land_organisation = 0.10
    global_pop_militancy_modifier = 0.02
}
""")
loc("santander_republic", "The Republic of Laws")
loc("the_liberator_lives", "The Liberator Lives")

# ---------------------------------------------------------- node 1: Pativilca
EV.append("""country_event = {
    id = 9100300
    title = "EVTNAME9100300"
    desc = "EVTDESC9100300"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        OR = { tag = CLM tag = VNG }
        year = 1824
        NOT = { year = 1825 }
        NOT = { has_global_flag = pativilca_resolved }
    }
    mean_time_to_happen = { months = 3 }

    option = {
        name = "EVTOPTA9100300"
        set_global_flag = pativilca_resolved
        random_list = {
            70 = {
                set_global_flag = bolivar_lives
                add_country_modifier = { name = the_liberator_lives duration = -1 }
                country_event = 9100301
            }
            30 = {
                set_global_flag = bolivar_dead
                add_country_modifier = { name = santander_republic duration = -1 }
                country_event = 9100302
            }
        }
    }
}

country_event = {
    id = 9100301
    title = "EVTNAME9100301"
    desc = "EVTDESC9100301"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100301"
        prestige = 10
    }
}

country_event = {
    id = 9100302
    title = "EVTNAME9100302"
    desc = "EVTDESC9100302"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100302"
        prestige = -15
        VPE = { prestige = 10 }
        SPA = { prestige = 10 }
        any_pop = { militancy = 1 }
    }
}
""")
loc("EVTNAME9100300", "The Sickness at Pativilca")
loc("EVTDESC9100300",
    "He has been in the village three weeks, in a chair on the shaded side of a "
    "mud-walled house, too weak to stand. Mosquera found him there and could not keep "
    "the shock off his face; the Liberator, thirty pounds lighter, asked him what he "
    "meant to do now. Triumph, he said. The army south of here is waiting on a man who "
    "may not see February.")
loc("EVTOPTA9100300", "Await the physicians.")
loc("EVTNAME9100301", "Triumph")
loc("EVTDESC9100301",
    "He gets out of the chair. Within the year Junin and Ayacucho are won and Spanish "
    "America is finished as a Spanish possession.")
loc("EVTOPTA9100301", "As he said he would.")
loc("EVTNAME9100302", "The Liberator Is Dead")
loc("EVTDESC9100302",
    "He dies at Pativilca in the first week of February, and the republic falls to "
    "Santander, who is everything Bolivar was not: a lawyer, a constitutionalist, a man "
    "who files things. There will be no dictatorship and no Ocana, and also no one to "
    "hold Caracas and Quito together by force of personality. In the south, the royalist "
    "army that would have broken at Ayacucho does not break.")
loc("EVTOPTA9100302", "The man of laws takes the chair.")

# ------------------------------------------------- node 2: the Ephemeral Independence
EV.append("""country_event = {
    id = 9100310
    title = "EVTNAME9100310"
    desc = "EVTDESC9100310"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        OR = { tag = CLM tag = VNG }
        year = 1821
        NOT = { year = 1823 }
        NOT = { exists = DOM }
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9100310"
        set_global_flag = santo_domingo_accepted
        prestige = 10
        2214 = { secede_province = THIS add_core = THIS }
        2216 = { secede_province = THIS add_core = THIS }
        HAI = { relation = { who = THIS value = -200 } country_event = 9100311 }
        ai_chance = { factor = 45 }
    }

    option = {
        name = "EVTOPTB9100310"
        set_global_flag = santo_domingo_declined
        HAI = { relation = { who = THIS value = 50 } country_event = 9100312 }
        ai_chance = { factor = 55 }
    }
}

country_event = {
    id = 9100311
    title = "EVTNAME9100311"
    desc = "EVTDESC9100311"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100311"
        random_list = {
            65 = {
                badboy = -2
                war = {
                    target = FROM
                    attacker_goal = { casus_belli = acquire_core_state state_province_id = 2214 }
                }
            }
            35 = {
                prestige = -10
                militancy = 2
            }
        }
    }
}

country_event = {
    id = 9100312
    title = "EVTNAME9100312"
    desc = "EVTDESC9100312"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100312"
        prestige = 10
        2214 = { secede_province = THIS add_core = THIS }
        2216 = { secede_province = THIS add_core = THIS }
    }
}
""")
loc("EVTNAME9100310", "The Ephemeral Independence")
loc("EVTDESC9100310",
    "Jose Nunez de Caceres has raised a flag over Santo Domingo, declared the "
    "Independent State of Spanish Haiti, and asked -- formally, in writing, by courier "
    "-- to be admitted to Gran Colombia. He has about four hundred men. Boyer has "
    "thirty-six thousand and considers the whole island his. Bogota is two thousand "
    "miles away and has no fleet worth the name.")
loc("EVTOPTA9100310", "Admit them to the Republic.")
loc("EVTOPTB9100310", "We cannot defend what we cannot reach.")
loc("EVTNAME9100311", "Boyer Looks East")
loc("EVTDESC9100311",
    "The Colombians have taken the eastern half of the island. The President-for-Life "
    "has spent eleven years insisting that Hispaniola is one and indivisible, and he "
    "has an army that has never lost on it.")
loc("EVTOPTA9100311", "The island is one.")
loc("EVTNAME9100312", "Unification of the Island")
loc("EVTDESC9100312",
    "No answer comes from Bogota. In February Boyer crosses the frontier unopposed and "
    "Nunez de Caceres sails for Venezuela. The island will be governed from "
    "Port-au-Prince for twenty-two years.")
loc("EVTOPTA9100312", "Nine weeks of independence.")

# ---------------------------------------- node 3: the Havana junta, July 1808
# The strongest of the three, and the least known. When news of Bayonne reached
# Havana the criollo planters led by Francisco de Arango y Parreno proposed a Junta
# Suprema to govern Cuba in Ferdinand's name -- the same move Caracas, Buenos Aires
# and Bogota were making in the same months. The Captain-General, Someruelos, was
# initially willing. The peninsular merchants and the Audiencia killed it, and a
# street demonstration on 27 July settled the matter.
#
# What killed it was not loyalty. It was Saint-Domingue. Every planter in the room
# had done the arithmetic on four hundred thousand slaves and a weakened garrison,
# and decided that a junta was a risk they could not take. So the odds here are low,
# and they are lower still if Cuba has already chosen the ever-faithful path.
EV.append("""country_event = {
    id = 9100320
    title = "EVTNAME9100320"
    desc = "EVTDESC9100320"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = CBA
        year = 1808
        NOT = { year = 1810 }
        NOT = { has_global_flag = havana_junta_resolved }
    }
    mean_time_to_happen = {
        months = 4
        modifier = { factor = 2 has_country_flag = loyal_to_the_crown }
    }

    option = {
        name = "EVTOPTA9100320"
        set_global_flag = havana_junta_resolved
        random_list = {
            25 = { country_event = 9100321 }
            75 = { country_event = 9100322 }
        }
    }
}

country_event = {
    id = 9100321
    title = "EVTNAME9100321"
    desc = "EVTDESC9100321"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100321"
        set_country_flag = elite_pact
        government = democracy
        prestige = 15
        SPA = { relation = { who = THIS value = -75 } }
        any_pop = { limit = { has_pop_culture = criollo } consciousness = 3 }
    }
}

country_event = {
    id = 9100322
    title = "EVTNAME9100322"
    desc = "EVTDESC9100322"
    picture = "administration"
    is_triggered_only = yes
    option = {
        name = "EVTOPTA9100322"
        set_country_flag = loyal_to_the_crown
        prestige = -5
        SPA = { relation = { who = THIS value = 50 } }
        any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = -1 }
    }
}
""")
loc("EVTNAME9100320", "The Junta at Havana")
loc("EVTDESC9100320",
    "The King is a prisoner at Bayonne and there is no government in Spain worth the "
    "name. Arango y Parreno and the planters propose a Junta Suprema to hold Cuba for "
    "Ferdinand until he returns -- what Caracas has done, and Buenos Aires, and "
    "Bogota. Someruelos has not said no. The peninsular merchants have, loudly, and "
    "every man in the room is thinking about Saint-Domingue.")
loc("EVTOPTA9100320", "Let the cabildo meet.")
loc("EVTNAME9100321", "A Junta Is Proclaimed")
loc("EVTDESC9100321",
    "The cabildo carries it. Cuba governs itself in the King's name, which is what "
    "every other junta in the Americas has said on the way to saying something else. "
    "The planters have gambled that they can hold the island without Madrid's "
    "regiments, and the slaves have noticed.")
loc("EVTOPTA9100321", "For Ferdinand, and for ourselves.")
loc("EVTNAME9100322", "The Crowd in the Plaza")
loc("EVTDESC9100322",
    "On the twenty-seventh of July the peninsular merchants put a crowd into the "
    "square against the junta, and the planters discover they would rather be governed "
    "badly from Madrid than take their chances. Someruelos keeps his post. Cuba will "
    "be called the ever-faithful isle for it, and the phrase will stick for ninety "
    "years.")
loc("EVTOPTA9100322", "Better the garrison than the alternative.")

def w(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

w(f"{MOD}/events/1800_Divergence.txt", "\n".join(EV))
w(f"{MOD}/localisation/10_divergence.csv",
  "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
  + "\n".join(LOC) + "\n")

em = f"{MOD}/common/event_modifiers.txt"
s = open(em, encoding="cp1252", errors="replace").read()
if "santander_republic" not in s:
    open(em, "w", encoding="cp1252", errors="replace", newline="\n").write(s.rstrip() + "\n" + "".join(MODS) + "\n")

# ---- correction: Hispaniola was ceded to France at Basel in 1795, and the eastern
# half was never part of New Spain. The Viceroyalty was holding it with Mexican cores.
fixed = 0
import glob
for pid, cores in ((2214, ["DOM", "HAI", "SPA", "FRA"]), (2216, ["DOM", "HAI", "SPA", "FRA"])):
    g = glob.glob(f"{MOD}/history/provinces/*/{pid} - *.txt")
    if not g: continue
    t = open(g[0], encoding="cp1252", errors="replace").read()
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", t)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    for k in ("owner", "controller", "add_core"):
        head = re.sub(rf"^\s*{k}\s*=.*\n", "", head, flags=re.M)
    head = ("owner = SPA\ncontroller = SPA\n"
            + "".join(f"add_core = {c}\n" for c in cores) + head.lstrip("\n"))
    open(g[0], "w", encoding="cp1252", errors="replace", newline="\n").write(head.rstrip("\n") + "\n" + tail)
    fixed += 1

from PIL import Image
for tag_, col_ in (("LIG", (34, 90, 54)), ("RAG", (180, 60, 60))):
  for suffix in ("", "_communist", "_fascist", "_monarchy", "_republic"):
    fp = f"{MOD}/gfx/flags/{tag_}{suffix}.tga"
    if not os.path.exists(fp):
        im = Image.new("RGB", (93, 64), col_)
        for y in range(64):
            for x in range(93):
                if x < 3 or x > 89 or y < 3 or y > 60: im.putpixel((x, y), (255, 255, 255))
        im.save(fp)

print(f"  divergence nodes                  3")
print(f"  events                            6")
print(f"  Hispaniola provinces corrected    {fixed}  (New Spain -> Spain, Mexican cores removed)")
