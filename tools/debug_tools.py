"""A testing shelf: reach the content without waiting for the calendar.

Victoria II's tick rate is compiled into the executable. There is no define for it and
no console command that raises it, so speed 5 is the ceiling and waiting out 1808 at
that speed is the only way to see 1808 -- unless the content can be summoned.

So: one decision turns the shelf on, and the rest appear. Each fires a whole chain at
once, on whatever date you happen to be sitting on. Test the Iturrigaray coup in 1801,
watch the Constitution of Cádiz arrive and be torn up inside a minute, run the coalition
wars back to back.

They are hidden until enabled and every one sets a flag, so an ordinary campaign never
sees them and a tested campaign is obviously a tested one.

The console does the rest. `event <id>` fires one event for your country; the ids are
in tools/EVENT_IDS.md and listed in TESTING.md beside this.
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
D, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

def dec(name, title, desc, effect, potential_extra=""):
    D.append(f"""\t{name} = {{
\t\tpicture = administration
\t\tpotential = {{
\t\t\thas_country_flag = testing_enabled
{potential_extra}\t\t}}
\t\tallow = {{ always = yes }}
\t\teffect = {{
{effect}
\t\t}}
\t\tai_will_do = {{ factor = 0 }}
\t}}
""")
    loc(name + "_title", title); loc(name + "_desc", desc)
    log["testing decisions"] += 1

D.append("""\tenable_testing_tools = {
\t\tpicture = administration
\t\tpotential = {
\t\t\tai = no
\t\t\tNOT = { has_country_flag = testing_enabled }
\t\t}
\t\tallow = { always = yes }
\t\teffect = {
\t\t\tset_country_flag = testing_enabled
\t\t\tset_global_flag = this_campaign_was_tested
\t\t}
\t\tai_will_do = { factor = 0 }
\t}
""")
loc("enable_testing_tools_title", "Enable the testing shelf")
loc("enable_testing_tools_desc",
    "Reveals a set of decisions that fire whole scripted chains at once, so a chain "
    "dated to 1808 can be examined in 1801. Everything they do is permanent and the "
    "campaign is marked as tested. There is no way to switch them off again.")

dec("test_the_spanish_collapse",
    "Run: the Spanish collapse",
    "Fontainebleau, Aranjuez, Bayonne, the Second of May, Bailén and Joseph in Madrid, "
    "in sequence, a few days apart. This is what opens the regency chain, so the "
    "colonial decisions follow from it.",
    "\t\t\tSPA = { country_event = { id = 9101000 days = 1 } }\n"
    "\t\t\tSPA = { country_event = { id = 9101001 days = 4 } }\n"
    "\t\t\tSPA = { country_event = { id = 9101002 days = 8 } }\n"
    "\t\t\tSPA = { country_event = { id = 9101004 days = 12 } }\n"
    "\t\t\tSPA = { country_event = { id = 9101005 days = 16 } }\n"
    "\t\t\tFRA = { country_event = { id = 9101006 days = 20 } }")

dec("test_the_viceroy",
    "Run: Iturrigaray and the coup",
    "The question of who governs New Spain with the King a prisoner, and Yermo's answer "
    "to it. Needs the collapse to have run first, since the viceroy is reacting to "
    "Bayonne.",
    "\t\t\tNSP = { set_country_flag = h18c_bayonne_known }\n"
    "\t\t\tNSP = { country_event = { id = 9101100 days = 45 } }")

dec("test_the_constitution",
    "Run: the constitutional track",
    "The Cortes at Cádiz, the Constitution of 1812, Ferdinand tearing it up, Riego "
    "restoring it, and the French ending it again. The whole arc that turns loyal "
    "criollos into separatists, compressed into a month.",
    "\t\t\tSPA = { country_event = { id = 9100800 days = 1 } }\n"
    "\t\t\tSPA = { country_event = { id = 9100802 days = 8 } }\n"
    "\t\t\tSPA = { country_event = { id = 9100804 days = 16 } }\n"
    "\t\t\tSPA = { country_event = { id = 9100806 days = 24 } }\n"
    "\t\t\tSPA = { country_event = { id = 9100808 days = 32 } }")

dec("test_louisiana",
    "Run: the Louisiana chain",
    "San Ildefonso, the viceroy being told, the right of deposit, and Monroe in Paris.",
    "\t\t\tSPA = { country_event = { id = 9100900 days = 1 } }\n"
    "\t\t\tUSA = { country_event = { id = 9100901 days = 6 } }\n"
    "\t\t\tFRA = { country_event = { id = 9100902 days = 12 } }")

dec("test_the_coalitions",
    "Run: the coalition wars",
    "The Third, Fourth and Fifth Coalitions and the march on Moscow, declared in turn. "
    "They are real wars and will be fought, so expect the map to move.",
    "\t\t\tset_global_flag = h18_third_coalition\n"
    "\t\t\tset_global_flag = h18_fourth_coalition\n"
    "\t\t\tset_global_flag = h18_bayonne\n"
    "\t\t\tset_global_flag = h18_peninsular_war\n"
    "\t\t\tAUS = { country_event = { id = 9101200 days = 1 } }\n"
    "\t\t\tPRU = { country_event = { id = 9101201 days = 40 } }\n"
    "\t\t\tAUS = { country_event = { id = 9101203 days = 80 } }\n"
    "\t\t\tFRA = { country_event = { id = 9101204 days = 120 } }")

dec("test_a_full_treasury",
    "Give this country money and men",
    "Fifty thousand in the treasury, research points, and a year of instant prestige, "
    "so a chain that needs a solvent state can be reached without playing one.",
    "\t\t\ttreasury = 50000\n\t\t\tresearch_points = 500\n\t\t\tprestige = 25")

dec("test_the_grito",
    "Run: the Grito and the civil wars",
    "Fires the risings for New Spain, New Granada, Rio de la Plata and Chile at once, "
    "with separatism already past the threshold, so the civil wars, the republics and "
    "their armies can all be checked in a minute rather than in ten years.",
    "\t\t\tset_country_flag = h18c_bayonne_known\n"
    "\t\t\tset_variable = { which = separatism value = 40 }\n"
    "\t\t\tNSP = { set_variable = { which = separatism value = 40 } }\n"
    "\t\t\tVNG = { set_variable = { which = separatism value = 40 } }\n"
    "\t\t\tRDP = { set_variable = { which = separatism value = 40 } }\n"
    "\t\t\tCGC = { set_variable = { which = separatism value = 40 } }\n"
    "\t\t\tNSP = { set_country_flag = h18c_bayonne_known }\n"
    "\t\t\tVNG = { set_country_flag = h18c_bayonne_known }\n"
    "\t\t\tRDP = { set_country_flag = h18c_bayonne_known }\n"
    "\t\t\tCGC = { set_country_flag = h18c_bayonne_known }\n"
    "\t\t\tNSP = { country_event = { id = 9101700 days = 2 } }\n"
    "\t\t\tVNG = { country_event = { id = 9101712 days = 4 } }\n"
    "\t\t\tRDP = { country_event = { id = 9101718 days = 6 } }\n"
    "\t\t\tCGC = { country_event = { id = 9101724 days = 8 } }")

wr(f"{MOD}/decisions/1800_Testing.txt",
   "# A testing shelf. Hidden until `enable_testing_tools` is taken, never used by the\n"
   "# AI, and it marks the campaign. Delete this file to remove it entirely.\n\n"
   "political_decisions = {\n\n" + "\n".join(D) + "\n}\n")
wr(f"{MOD}/localisation/17_testing.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
