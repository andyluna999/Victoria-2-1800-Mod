# `acquire_all_cores` carries truce_months = 48 and takes twelve months to construct,
# so a republic that wins a white peace waits four years before it can move again --
# and the wars of independence were not fought at that tempo. Mexico fought Spain
# continuously from 1810 to 1821 with no truce anybody respected.
#
# So the republics get their own instrument: the same zero-infamy claim on their own
# cores, constructed in three months and with a truce of six, which is short enough to
# fight the war the way it was actually fought.
CB = """
# A republic reclaiming the country it already considers its own. The same claim
# `acquire_all_cores` makes, at the tempo these wars were actually fought: Mexico was
# at war with Spain continuously for eleven years and no truce between them was ever
# worth the paper.
reclaim_the_republic = {
    sprite_index = 5
    is_triggered_only = yes
    months = 3

    badboy_factor = 0
    prestige_factor = 2
    peace_cost_factor = 0.5
    penalty_factor = 1

    break_truce_prestige_factor = 1
    break_truce_infamy_factor = 0
    break_truce_militancy_factor = 1
    truce_months = 6

    good_relation_prestige_factor = 1
    good_relation_infamy_factor = 0
    good_relation_militancy_factor = 1

    always = yes

    can_use = {
        THIS = { has_country_flag = h18c_the_claim_stands }
        THIS = {
            OR = {
                tag = MEX
                tag = PEU
                tag = CLM
                tag = ARG
                tag = CHL
                tag = TEX
            }
        }
        any_owned_province = { is_core = THIS }
    }

    po_demand_state = yes

    war_name = RECLAIM_REPUBLIC_NAME
}
"""
import os
MOD="/home/claude/build/HPM"
p=f"{MOD}/common/cb_types.txt"
s=open(p,encoding='cp1252',errors='replace').read()
if "\nreclaim_the_republic = {" not in s:
    open(p,'w',encoding='cp1252',errors='replace',newline='\n').write(s.rstrip()+"\n"+CB+"\n")
    print("  reclaim_the_republic added")
