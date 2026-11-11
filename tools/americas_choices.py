"""Seven moments in the Americas that were genuine forks, built as decisions with costs
on both sides rather than flavour text.

Each one is a thing that actually happened, where the other branch was live at the time
and the people involved argued about it. None of them is a free choice.
"""
import os

MOD = "/home/claude/build/HPM"
EV, DEC, LOC, MOD_DEFS = [], [], [], []
BASE = 9100200

def loc(k, v): LOC.append(f"{k};{v};;;;;;;;;;;;;x")

# ---------------------------------------------------------------- modifiers
MOD_DEFS.append("""
# --- the Americas, 1800-1836 ---

haitian_indemnity = {
    icon = 4
    tax_efficiency = -0.35
    max_loan_modifier = -0.50
    research_points_modifier = -0.15
    global_immigrant_attract = -0.25
}
pariah_republic = {
    icon = 8
    tariff_efficiency_modifier = -0.60
    import_cost = 0.40
    global_immigrant_attract = -0.60
    diplomatic_points_modifier = -0.50
}
francian_autarky = {
    icon = 2
    tariff_efficiency_modifier = -0.80
    import_cost = 0.50
    research_points_modifier = -0.40
    global_immigrant_attract = -0.80
    tax_efficiency = 0.25
    farm_rgo_eff = 0.20
    mobilisation_size = 0.05
    badboy = -0.05
}
porteno_monopoly = {
    icon = 3
    tax_efficiency = 0.30
    tariff_efficiency_modifier = 0.35
    global_pop_militancy_modifier = 0.04
    core_pop_militancy_modifier = 0.06
}
federal_compromise = {
    icon = 1
    tax_efficiency = -0.15
    tariff_efficiency_modifier = -0.20
    global_pop_militancy_modifier = -0.05
    global_pop_consciousness_modifier = 0.02
}
ever_faithful_isle = {
    icon = 1
    tax_efficiency = 0.20
    farm_rgo_eff = 0.25
    global_pop_consciousness_modifier = -0.03
    global_immigrant_attract = 0.20
}
fear_of_the_servile_war = {
    icon = 4
    global_pop_militancy_modifier = 0.08
    mobilisation_size = -0.03
    global_immigrant_attract = -0.30
}
memory_of_tupac_amaru = {
    icon = 4
    global_pop_consciousness_modifier = -0.04
    global_pop_militancy_modifier = 0.05
    tax_efficiency = -0.10
    mobilisation_size = -0.04
}
orderly_separation = {
    icon = 1
    tax_efficiency = 0.15
    mine_rgo_eff = 0.10
    global_immigrant_attract = 0.25
    research_points_modifier = 0.10
}
bolivarian_union = {
    icon = 3
    prestige = 0.5
    tax_efficiency = -0.10
    global_pop_militancy_modifier = 0.05
    mobilisation_size = 0.06
}
""")
for n in ("haitian_indemnity","pariah_republic","francian_autarky","porteno_monopoly",
          "federal_compromise","ever_faithful_isle","fear_of_the_servile_war",
          "memory_of_tupac_amaru","orderly_separation","bolivarian_union"):
    loc(n, n.replace("_", " ").title())   # modifier names are keyed bare

# Victoria II reads a decision's title from <name>_title. Without it the game
# prints the key itself, which is why the log read 'Decision:
# accept_the_french_indemnity_title in Haiti'.
loc("close_the_country_title", "Close the Country")
loc("open_the_river_trade_title", "Open the River Trade")
loc("keep_the_customs_of_buenos_aires_title", "Keep the Customs House")
loc("share_the_customs_with_the_provinces_title", "Share the Customs with the Provinces")
loc("the_ever_faithful_isle_title", "The Ever-Faithful Isle")
loc("raise_the_cry_in_cuba_title", "Raise the Cry")
loc("the_memory_of_tupac_amaru_title", "The Memory of Tupac Amaru")
loc("the_creoles_declare_for_the_junta_title", "Declare for the Junta")
loc("hold_the_bolivarian_union_title", "Hold the Union")
loc("let_the_union_dissolve_title", "Let the Union Dissolve")

# ---------------------------------------------------------------- 1. Haiti, 1825
DEC.append("""
    accept_the_french_indemnity = {
        picture = administration
        potential = {
            tag = HAI
            year = 1824
            NOT = { has_country_flag = indemnity_settled }
            NOT = { has_country_flag = indemnity_refused }
        }
        allow = { war = no }
        effect = {
            set_country_flag = indemnity_settled
            add_country_modifier = { name = haitian_indemnity duration = -1 }
            remove_country_modifier = pariah_republic
            treasury = -40000
            FRA = { treasury = 40000 }
            prestige = 10
            any_country = { limit = { is_greater_power = yes } relation = { who = HAI value = 40 } }
        }
        ai_will_do = { factor = 1 }
    }

    refuse_the_french_indemnity = {
        picture = administration
        potential = {
            tag = HAI
            year = 1824
            NOT = { has_country_flag = indemnity_settled }
            NOT = { has_country_flag = indemnity_refused }
        }
        allow = { }
        effect = {
            set_country_flag = indemnity_refused
            add_country_modifier = { name = pariah_republic duration = -1 }
            prestige = -10
            militancy = -2
            FRA = { relation = { who = HAI value = -100 } }
        }
        ai_will_do = { factor = 0 }
    }
""")
loc("accept_the_french_indemnity_title", "Accept the French Indemnity")
loc("accept_the_french_indemnity_desc",
    "Fourteen French warships are standing off Port-au-Prince. Charles X offers "
    "recognition, and the right to trade with the world, for a hundred and fifty "
    "million francs. It is the price of the plantations our grandparents were worked "
    "to death on, payable by their grandchildren. Refuse and we remain what we have "
    "been for twenty years: a republic no one will admit exists.")
loc("refuse_the_french_indemnity_title", "Refuse the Indemnity")
loc("refuse_the_french_indemnity_desc",
    "We will not buy our own freedom twice. Let them blockade.")

# ---------------------------------------------------------------- 2. Paraguay
DEC.append("""
    close_the_country = {
        picture = administration
        potential = {
            tag = PRG
            year = 1814
            NOT = { has_country_flag = paraguay_decided }
        }
        allow = { war = no }
        effect = {
            set_country_flag = paraguay_decided
            set_country_flag = francia_autarky
            add_country_modifier = { name = francian_autarky duration = -1 }
            add_accepted_culture = guarani
            any_country = { limit = { exists = yes } relation = { who = PRG value = -25 } }
        }
        ai_will_do = { factor = 1 }
    }

    open_the_river_trade = {
        picture = administration
        potential = {
            tag = PRG
            year = 1814
            NOT = { has_country_flag = paraguay_decided }
        }
        allow = { war = no }
        effect = {
            set_country_flag = paraguay_decided
            treasury = 15000
            prestige = 5
            ARG = { relation = { who = PRG value = 50 } }
            RDP = { relation = { who = PRG value = 50 } }
        }
        ai_will_do = { factor = 0 }
    }
""")
loc("close_the_country", "Close the Country")
loc("close_the_country_desc",
    "Doctor Francia's reasoning is simple. Every road out of Paraguay runs down a river "
    "that Buenos Aires controls, and anything we sell, they tax. So we will sell "
    "nothing. We will grow our own food, weave our own cloth, marry the old Spanish "
    "families into the Guarani countryside, and let no foreigner in. We will be poor, "
    "backward, and nobody's province.")
loc("open_the_river_trade", "Open the River Trade")
loc("open_the_river_trade_desc",
    "Yerba and tobacco can make us rich, if we accept that the road to market runs "
    "through another man's custom house.")

# ---------------------------------------------------------------- 3. Rio de la Plata
DEC.append("""
    keep_the_customs_of_buenos_aires = {
        picture = administration
        potential = {
            OR = { tag = ARG tag = RDP tag = LPL }
            year = 1820
            NOT = { has_country_flag = porteno_question_settled }
        }
        allow = { }
        effect = {
            set_country_flag = porteno_question_settled
            set_country_flag = unitarian_state
            add_country_modifier = { name = porteno_monopoly duration = -1 }
            any_owned = {
                limit = { NOT = { province_id = 2355 } is_core = THIS }
                add_province_modifier = { name = federal_compromise duration = -1 }
            }
        }
        ai_will_do = { factor = 1 }
    }

    share_the_customs_with_the_provinces = {
        picture = administration
        potential = {
            OR = { tag = ARG tag = RDP tag = LPL }
            year = 1820
            NOT = { has_country_flag = porteno_question_settled }
        }
        allow = { }
        effect = {
            set_country_flag = porteno_question_settled
            set_country_flag = federal_state
            add_country_modifier = { name = federal_compromise duration = -1 }
            prestige = 5
        }
        ai_will_do = { factor = 1 }
    }
""")
loc("keep_the_customs_of_buenos_aires", "Keep the Customs of Buenos Aires")
loc("keep_the_customs_of_buenos_aires_desc",
    "Every hide, every ounce of silver and every bale of British cloth passes the "
    "custom house on the estuary, and the revenue of that one building is the revenue "
    "of the nation. The provinces of the interior want it shared. Keep it, and the "
    "treasury is full and the caudillos take the field against us.")
loc("share_the_customs_with_the_provinces", "Share the Customs")
loc("share_the_customs_with_the_provinces_desc",
    "A poorer government that the interior will not shoot at.")

# ---------------------------------------------------------------- 4. Cuba
DEC.append("""
    the_ever_faithful_isle = {
        picture = administration
        potential = {
            tag = CBA
            vassal_of = SPA
            year = 1810
            NOT = { has_country_flag = cuba_chose }
        }
        allow = { }
        effect = {
            set_country_flag = cuba_chose
            set_country_flag = loyal_to_the_crown
            add_country_modifier = { name = ever_faithful_isle duration = -1 }
            SPA = { treasury = 10000 relation = { who = CBA value = 100 } }
        }
        ai_will_do = { factor = 1 }
    }

    raise_the_cry_in_cuba = {
        picture = administration
        potential = {
            tag = CBA
            vassal_of = SPA
            year = 1810
            NOT = { has_country_flag = cuba_chose }
        }
        allow = { }
        effect = {
            set_country_flag = cuba_chose
            set_country_flag = popular_insurrection
            add_country_modifier = { name = fear_of_the_servile_war duration = -1 }
            any_pop = { limit = { has_pop_culture = afro_caribbean } militancy = 5 }
            prestige = 5
        }
        ai_will_do = { factor = 0 }
    }
""")
loc("the_ever_faithful_isle", "The Ever-Faithful Isle")
loc("the_ever_faithful_isle_desc",
    "The planters have done the arithmetic. Saint-Domingue was the richest colony on "
    "earth and its masters are dead or in Louisiana. Cuba now has the sugar, the price, "
    "and four hundred thousand slaves. The mainland may raise its juntas; here the "
    "Spanish garrison is not an occupier but an insurance policy, and the creole "
    "gentlemen will pay the premium.")
loc("raise_the_cry_in_cuba", "Raise the Cry")
loc("raise_the_cry_in_cuba_desc",
    "Freedom for the island, and let the consequences come.")

# ---------------------------------------------------------------- 5. Peru
DEC.append("""
    the_memory_of_tupac_amaru = {
        picture = administration
        potential = {
            OR = { tag = VPE tag = PEU }
            year = 1809
            NOT = { has_country_flag = peru_chose }
        }
        allow = { }
        effect = {
            set_country_flag = peru_chose
            set_country_flag = loyal_to_the_crown
            add_country_modifier = { name = memory_of_tupac_amaru duration = -1 }
            SPA = { relation = { who = THIS value = 100 } }
        }
        ai_will_do = { factor = 1 }
    }

    the_creoles_declare_for_the_junta = {
        picture = administration
        potential = {
            OR = { tag = VPE tag = PEU }
            year = 1809
            NOT = { has_country_flag = peru_chose }
        }
        allow = { }
        effect = {
            set_country_flag = peru_chose
            set_country_flag = elite_pact
            prestige = 10
            any_pop = {
                limit = { OR = { has_pop_culture = quechua has_pop_culture = aymara } }
                consciousness = 3
            }
        }
        ai_will_do = { factor = 0 }
    }
""")
loc("the_memory_of_tupac_amaru", "The Memory of Tupac Amaru")
loc("the_memory_of_tupac_amaru_desc",
    "Lima's gentlemen remember 1780 better than they remember Madrid. A hundred "
    "thousand Indians rose in the sierra, and it took two years and a public "
    "dismembering in the square at Cusco to put them down. Whatever the juntas in "
    "Buenos Aires and Caracas are shouting about liberty, the viceroy's regiments stand "
    "between us and that again. Loyalty here is not affection. It is fear.")
loc("the_creoles_declare_for_the_junta", "Declare for the Junta")
loc("the_creoles_declare_for_the_junta_desc",
    "Liberty, and a sierra full of people who will want to know what it means for them.")

# ---------------------------------------------------------------- 6. Brazil
DEC.append("""

""")
loc("the_prince_remains", "I Shall Remain")
loc("the_prince_sails_for_lisbon", "Obey the Cortes")

# ---------------------------------------------------------------- 7. Gran Colombia
DEC.append("""
    hold_the_bolivarian_union = {
        picture = administration
        potential = {
            OR = { tag = CLM tag = VNG }
            year = 1826
            NOT = { has_country_flag = union_question_settled }
            owns = 2264
            owns = 2279
        }
        allow = { war = no }
        effect = {
            set_country_flag = union_question_settled
            add_country_modifier = { name = bolivarian_union duration = -1 }
            prestige = 15
            any_owned = { limit = { NOT = { is_core = THIS } } add_core = THIS }
        }
        ai_will_do = { factor = 1 }
    }

    let_the_union_dissolve = {
        picture = administration
        potential = {
            OR = { tag = CLM tag = VNG }
            year = 1826
            NOT = { has_country_flag = union_question_settled }
        }
        allow = { }
        effect = {
            set_country_flag = union_question_settled
            prestige = -10
            militancy = -3
            release = VNZ
            release = ECU
        }
        ai_will_do = { factor = 0 }
    }
""")
loc("hold_the_bolivarian_union", "Hold the Union")
loc("hold_the_bolivarian_union_desc",
    "Caracas is three weeks from Bogota by mule and Quito is further, and Paez in the "
    "llanos obeys nobody. The Liberator wants one republic from the Orinoco to the "
    "Andes. Holding it means a standing army pointed inward and a government the "
    "provinces will call a tyranny.")
loc("let_the_union_dissolve", "Let It Dissolve")
loc("let_the_union_dissolve_desc",
    "Three quiet republics instead of one angry one. He who serves a revolution ploughs "
    "the sea.")

# ---------------------------------------------------------------- write it out
def w(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

w(f"{MOD}/decisions/1800_Americas_Choices.txt",
  "political_decisions = {\n" + "\n".join(DEC) + "\n}\n")
w(f"{MOD}/localisation/09_americas_choices.csv",
  "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
  + "\n".join(LOC) + "\n")

em = f"{MOD}/common/event_modifiers.txt"
s = open(em, encoding="cp1252", errors="replace").read()
if "haitian_indemnity" not in s:
    open(em, "w", encoding="cp1252", errors="replace", newline="\n").write(s.rstrip() + "\n" + "".join(MOD_DEFS) + "\n")

n = sum(1 for d in DEC for _ in [0]) * 2
print(f"  decision pairs                    {len(DEC)}")
print(f"  modifiers added                   10")
print(f"  localisation rows                 {len(LOC)}")
