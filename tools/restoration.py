"""The Restoration: Ferdinand comes home and asks for his empire back.

Between 1808 and 1813 there is no Spain to obey. The King is in France, the Junta
Central is a committee in a besieged port, and every viceroyalty governs itself by
default -- which the game already models, because an occupied Spain cannot garrison
anything. What the game did not model is what happens when that ends.

In March 1814 Ferdinand VII crosses the Pyrenees, tears up the Constitution within six
weeks, and turns to the Americas. The viceroyalties are asked to submit: give up the
interim privileges, resume the remittances, take back the monopoly, stand down the
militia. Most of them did, because the audiencias were packed with peninsulars whose
careers ran through Madrid and who had been waiting six years for exactly this.

Where a creole junta had taken the government -- where an Iturrigaray survived his
night, or a viceroy convened one himself -- the answer was genuinely open, and
refusing meant war with a Spain that had just helped beat Napoleon.

**And the delay compounds, which is the point.** A viceroyalty that submits in 1814
buys a decade of quiet at the price of its autonomy, and the republican movement loses
its argument. One that equivocates gets a worse problem every year: the men who wanted
a creole kingdom lose patience and the men who want a republic gain recruits. One that
declares outright fights Spain at its post-Napoleonic strongest, but never faces a
popular rising at all, because it is the revolution.

The conservative who waits too long gets the radical outcome he was trying to avoid.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

VICE = ["NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR"]
ANY = "OR = { " + " ".join(f"tag = {t}" for t in VICE) + " }"

MODS = """
the_interim_government = {
\ticon = 8
\ttax_efficiency = 0.25
\tadministrative_efficiency_modifier = 0.1
\tcore_pop_consciousness_modifier = 0.5
\tmobilisation_size = 0.04
}

the_old_order_restored = {
\ticon = 1
\ttax_efficiency = -0.15
\tcore_pop_militancy_modifier = 2.0
\tcore_pop_consciousness_modifier = 1.0
\tglobal_immigrant_attract = -0.3
}

the_years_of_equivocation = {
\ticon = 1
\tcore_pop_consciousness_modifier = 1.5
\tcore_pop_militancy_modifier = 1.0
\tadministrative_efficiency_modifier = -0.1
}

the_restored_monarchy = {
\ticon = 2
\tprestige = 0.5
\tmobilisation_size = 0.05
\tland_organisation = 0.1
\tdiplomatic_points_modifier = 0.2
}
"""
src = rd(f"{MOD}/common/event_modifiers.txt")
if "the_interim_government" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 4

# --- 1808-1813: the kingdom governs itself because there is nobody to obey ----------
EV.append(f"""country_event = {{
    id = 9102400
    title = "EVTNAME9102400"
    desc = "EVTDESC9102400"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        {ANY}
        has_country_flag = h18c_bayonne_known
        NOT = {{ has_country_flag = h18c_independent }}
    }}
    mean_time_to_happen = {{ months = 4 }}

    option = {{
        name = "EVTOPTA9102400"
        set_country_flag = h18c_interim
        add_country_modifier = {{ name = the_interim_government duration = -1 }}
        remove_country_modifier = colonial_trade_monopoly
    }}
}}

country_event = {{
    id = 9102401
    title = "EVTNAME9102401"
    desc = "EVTDESC9102401"
    picture = "administration"

    trigger = {{
        {ANY}
        has_country_flag = h18c_interim
        NOT = {{ has_country_flag = h18c_independent }}
        NOT = {{ has_country_flag = h18c_submitted }}
        year = 1810
    }}
    mean_time_to_happen = {{ months = 30 }}

    option = {{
        name = "EVTOPTA9102401"
        change_variable = {{ which = separatism value = 6 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 1 }}
    }}
}}
""")
loc("EVTNAME9102400", "There Is Nobody to Obey")
loc("EVTDESC9102400",
    "No orders have come from Spain in eleven months, and the last set were signed by "
    "a committee in Seville that has since fled to Cadiz and may not exist. The "
    "audiencia continues to sit, the treasury continues to collect, and the ships that "
    "used to carry the silver east are not coming. Nothing has been declared and "
    "nothing has changed except that this kingdom is now governing itself, which it "
    "turns out it is perfectly capable of doing.")
loc("EVTOPTA9102400", "We govern in the King's name, in his absence.")
loc("EVTNAME9102401", "Another Season of Not Deciding")
loc("EVTDESC9102401",
    "The arrangement that was going to last until the King returned has lasted longer "
    "than anybody meant it to, and the men who were content with it at the start have "
    "begun to notice how much better things work without Madrid taking a share. Nobody "
    "has proposed anything. Everybody has started thinking about it.")
loc("EVTOPTA9102401", "We will decide when there is something to decide.")
log["events"] += 2

# --- 1814: Ferdinand returns and asks ----------------------------------------------
EV.append(f"""country_event = {{
    id = 9102410
    title = "EVTNAME9102410"
    desc = "EVTDESC9102410"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = SPA
        year = 1814
        NOT = {{ year = 1819 }}
        has_global_flag = h18_ferdinand_absolutist
    }}
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA9102410"
        set_global_flag = h18_the_dominions_demanded
        add_country_modifier = {{ name = the_restored_monarchy duration = -1 }}
        prestige = 10
        any_country = {{
            limit = {{ has_country_flag = h18c_interim }}
            country_event = {{ id = 9102411 days = 20 }}
        }}
    }}
}}
""")
loc("EVTNAME9102410", "The Dominions Are Called to Account")
loc("EVTDESC9102410",
    "The King is back in Madrid, the Constitution is waste paper, and the men who "
    "governed in his name while he was a prisoner are being asked to explain what "
    "they did with his kingdoms. The instruction going out to every audiencia in the "
    "Americas is not a negotiation: the interim arrangements end, the remittances "
    "resume, the monopoly is restored and the militia stands down. Six years of "
    "governing themselves is to be treated as six years of holding the fort.")
loc("EVTOPTA9102410", "They will return to their obedience.")
log["events"] += 1

EV.append(f"""country_event = {{
    id = 9102411
    title = "EVTNAME9102411"
    desc = "EVTDESC9102411"
    picture = "administration"
    is_triggered_only = yes

    option = {{
        name = "EVTOPTA9102411"
        set_country_flag = h18c_submitted
        clr_country_flag = h18c_interim
        remove_country_modifier = the_interim_government
        add_country_modifier = {{ name = the_old_order_restored duration = -1 }}
        add_country_modifier = {{ name = colonial_trade_monopoly duration = -1 }}
        change_variable = {{ which = separatism value = -25 }}
        SPA = {{ relation = {{ who = THIS value = 60 }} }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = -4 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = 4 consciousness = 3 }}
        ai_chance = {{
            factor = 8
            modifier = {{ factor = 0.2 has_country_flag = h18c_junta_governs }}
            modifier = {{ factor = 0.3 has_country_modifier = the_junta_of_new_spain }}
            modifier = {{ factor = 0.4 check_variable = {{ which = separatism value = 40 }} }}
        }}
    }}
    option = {{
        name = "EVTOPTB9102411"
        set_country_flag = h18c_equivocating
        add_country_modifier = {{ name = the_years_of_equivocation duration = -1 }}
        change_variable = {{ which = separatism value = 5 }}
        SPA = {{ relation = {{ who = THIS value = -40 }} }}
        ai_chance = {{ factor = 2 }}
    }}
    option = {{
        name = "EVTOPTC9102411"
        set_country_flag = h18c_refused_the_king
        set_country_flag = h18c_independent
        set_global_flag = h18_plan_de_iguala
        all_core = {{ remove_core = THIS }}
        change_tag = MEX
        government = absolute_monarchy
        vote_franschise = landed_voting
        upper_house_composition = appointed
        change_variable = {{ which = separatism value = 25 }}
        SPA = {{
            relation = {{ who = THIS value = -150 }}
            war = {{
                target = THIS
                attacker_goal = {{ casus_belli = war_of_independence_cb }}
                defender_goal = {{ casus_belli = status_quo }}
                call_ally = yes
            }}
        }}
        # the creoles have what they wanted and are content
        any_pop = {{ limit = {{ has_pop_culture = criollo }} militancy = -6 consciousness = 4 }}
        # everyone else has a new set of masters with the same tribute rolls
        any_pop = {{ limit = {{ has_pop_culture = mestizo }} militancy = -2 consciousness = 3 }}
        any_pop = {{ limit = {{ has_pop_culture = nahua }} militancy = -1 consciousness = 2 }}
        any_pop = {{ limit = {{ has_pop_culture = maya }} militancy = -1 consciousness = 2 }}
        any_pop = {{ limit = {{ has_pop_culture = zapotec }} militancy = -1 consciousness = 2 }}
        any_pop = {{ limit = {{ has_pop_culture = spanish }} militancy = 5 }}
        prestige = 15
        ai_chance = {{
            factor = 1
            modifier = {{ factor = 5 has_country_flag = h18c_junta_governs }}
            modifier = {{ factor = 4 has_country_flag = h18c_autonomous }}
            modifier = {{ factor = 0 NOT = {{ check_variable = {{ which = separatism value = 30 }} }} }}
        }}
    }}
}}
""")
loc("EVTNAME9102411", "The King Requires an Answer")
loc("EVTDESC9102411",
    "The order has arrived and it is not addressed to a government -- it is addressed "
    "to officials who are presumed to have been minding the furniture. Submit and this "
    "kingdom goes back into the box it was in in 1807: the monopoly, the remittances, "
    "the audiencia answerable to Madrid, the militia disbanded before it gets ideas. "
    "The peninsulars on the council have been waiting six years to read this letter "
    "aloud. The creoles who have spent those years actually governing are doing the "
    "arithmetic on what they would be giving back.")
loc("EVTOPTA9102411", "We were always the King's. Let him have his kingdom.")
loc("EVTOPTB9102411", "Acknowledge the letter. Answer it later.")
loc("EVTOPTC9102411", "Then we are a kingdom, and we will crown our own.")
log["events"] += 1

# --- equivocation turns into somebody else's revolution ----------------------------
EV.append(f"""country_event = {{
    id = 9102412
    title = "EVTNAME9102412"
    desc = "EVTDESC9102412"
    picture = "administration"

    trigger = {{
        {ANY}
        has_country_flag = h18c_equivocating
        NOT = {{ has_country_flag = h18c_independent }}
        NOT = {{ has_country_flag = h18c_submitted }}
    }}
    mean_time_to_happen = {{ months = 18 }}

    option = {{
        name = "EVTOPTA9102412"
        change_variable = {{ which = separatism value = 10 }}
        any_pop = {{ limit = {{ has_pop_culture = mestizo }} militancy = 2 consciousness = 2 }}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 1 }}
    }}
}}
""")
loc("EVTNAME9102412", "The Patience of the Creoles Runs Out")
loc("EVTDESC9102412",
    "Another year of governing as though the question were still open, and the men who "
    "wanted a kingdom of their own under a crown have begun to lose the argument to "
    "the men who do not want a crown at all. The second group has the advantage of "
    "being able to say what it wants out loud.")
loc("EVTOPTA9102412", "We are running out of road.")
log["events"] += 1

# --- the casus belli -----------------------------------------------------------------
CB = """
# Spain's right to bring its dominions to heel after the French are gone. Ferdinand
# recognised no American republic in his life and spent the 1820s trying to reconquer
# them; this expires in 1830, with Barradas's failure at Tampico.
restore_the_dominions = {
    sprite_index = 2
    is_triggered_only = no
    months = 12

    badboy_factor = 0
    prestige_factor = 1
    peace_cost_factor = 1
    penalty_factor = 1

    break_truce_prestige_factor = 1
    break_truce_infamy_factor = 1
    break_truce_militancy_factor = 1
    truce_months = 24

    good_relation_prestige_factor = 1
    good_relation_infamy_factor = 1
    good_relation_militancy_factor = 1

    always = yes

    can_use = {
        THIS = { tag = SPA }
        THIS = { has_global_flag = h18_the_dominions_demanded }
        NOT = { year = 1830 }
        OR = {
            tag = MEX
            tag = PEU
            tag = CLM
            tag = ARG
            tag = CHL
            tag = NSP
            tag = VPE
            tag = VNG
            tag = RDP
            tag = CGC
        }
    }

    po_become_puppet = yes

    war_name = RESTORE_DOMINIONS_NAME
}
"""
path = f"{MOD}/common/cb_types.txt"
s = rd(path)
if "restore_the_dominions" not in s:
    open(path, "w", encoding="cp1252", errors="replace",
         newline="\n").write(s.rstrip() + "\n" + CB + "\n")
    log["casus belli"] = 1
loc("RESTORE_DOMINIONS_NAME", "Spanish Reconquest of $DEFENDER$")

wr(f"{MOD}/events/1800_Restoration.txt", "\n".join(EV))
wr(f"{MOD}/localisation/31_restoration.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<22}{v}")
