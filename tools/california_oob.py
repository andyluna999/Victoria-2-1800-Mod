import re, glob, os
MOD="/home/claude/build/HPM"
# California can be released by this chain and had no order of battle at all, so it
# would have declared itself and stood there with nothing. Texas has three regiments;
# a Californian republic raised from settlers and rancheros is about the same.
body = """# The Bear Flag men: a few hundred settlers, some rancheros who went with them, and
# nothing anyone would call an army. Read at the start of the game and handed over if
# this country ever comes into being.

leader = {
\tname = "John Fremont"
\tdate = 1845.1.1
\ttype = land
\tpersonality = audacious
\tbackground = natural_born_leader
\tprestige = 0.3
}

army = {
\tname = "Californian Battalion"
\tlocation = 87
\tregiment = {
\t\tname = "1. Bear Flag"
\t\ttype = irregular
\t\thome = 87
\t}
\tregiment = {
\t\tname = "2. Bear Flag"
\t\ttype = irregular
\t\thome = 89
\t}
\tregiment = {
\t\tname = "1. Ranchero Cavalry"
\t\ttype = cavalry
\t\thome = 90
\t}
}
"""
open(f"{MOD}/history/units/CAL_oob.txt","w",encoding="cp1252",errors="replace",newline="\n").write(body)
print("  CAL given an order of battle")
