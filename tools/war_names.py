"""Name the wars of independence what they were called.

Victoria II builds a war's name from its casus belli, so using `civil_war` gave us
"the New Spanish Civil War" for the Grito de Dolores. This casus belli is the same
one in every mechanical respect and differs only in what the war is called.
"""
import re
MOD="/home/claude/build/HPM"
path=f"{MOD}/common/cb_types.txt"
s=open(path,encoding='cp1252',errors='replace').read()
# rewrite our casus belli to mirror civil_war exactly, differing only in its name
NEW = '''
# The wars of independence were coming out named "the New Spanish Civil War", because
# Victoria II names a war from its casus belli and we were using civil_war. This is
# the same casus belli in every mechanical respect -- the whole country is the stake,
# it cannot be constructed, it carries no infamy -- and differs only in what the war
# is called, which for these is what it was called at the time.
war_of_independence_cb = {
    sprite_index = 2
    is_triggered_only = yes
    months = 1
    constructing_cb = no
    crisis = no

    can_use = {
        always = no
    }

    badboy_factor = 0
    prestige_factor = 1
    peace_cost_factor = 1
    penalty_factor = 1

    break_truce_prestige_factor = 5
    break_truce_infamy_factor = 0.5
    break_truce_militancy_factor = 0.5
    truce_months = 48

    good_relation_prestige_factor = 1
    good_relation_infamy_factor = 1
    good_relation_militancy_factor = 1

    po_annex = yes

    war_name = WAR_OF_INDEPENDENCE_NAME
}
'''
s = re.sub(r"\nwar_of_independence_cb = \{.*?\n\}\n", "\n", s, flags=re.S)
open(path,'w',encoding='cp1252',errors='replace',newline='\n').write(s.rstrip()+"\n"+NEW+"\n")
t=re.sub(r"#.*","",open(path,encoding='cp1252',errors='replace').read())
print("  braces balance:", t.count('{')==t.count('}'))
