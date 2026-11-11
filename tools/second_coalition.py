"""The War of the Second Coalition, in progress on 1 January 1800.

Without this the map says January 1800 and the world behaves like a peaceful 1836.
The war is the reason Austria is standing in Piedmont, Tuscany and the Legations, the
reason a French army is on the Nile, the reason Malta is under siege, and the reason
Spain's treasure fleets are not getting through. All of that is already on the map as
occupation and blockade; what has been missing is the war itself.

The alignment on the start date, which is not the alignment a year either side of it:

  * Russia has left. Suvorov's army reached winter quarters in Bohemia in the month
    before our start, Paul I has quarrelled with Vienna and London over Switzerland and
    Malta, and within a year he will be arming against Britain, not France. He is
    therefore not in this war.
  * Prussia is neutral and has been since Basel in 1795.
  * Spain is France's ally by San Ildefonso and at war with Britain at sea.
  * The Batavian and Ligurian Republics are belligerents because France says so.
  * Naples has been restored by British bayonets and is in.
  * The Ottomans are in, because of Egypt.

War goals are modest on purpose. Victoria II resolves history wars immediately on
load if the goals are achievable, and the point here is to begin mid-war rather than
to script the outcome.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# the coalition and the republic
ALLIES   = [("ENG", "Great Britain"), ("AUS", "Austria"), ("TUR", "the Ottoman Empire"),
            ("SIC", "Naples"), ("POR", "Portugal")]
FRENCH   = [("FRA", "France"), ("NET", "the Batavian Republic"),
            ("LIG", "the Ligurian Republic"), ("SPA", "Spain")]

lines = ['#name = "War of the Second Coalition"', "",
         "# In progress on the start date. Begun in 1798; Russia withdrew in October 1799.",
         "", "1799.3.12 = {"]
for t, _ in ALLIES: lines.append(f"    add_attacker = {t}")
for t, _ in FRENCH: lines.append(f"    add_defender = {t}")
lines += ["",
 "    # Austria wants Lombardy, which its army is standing in.",
 "    war_goal = {",
 "        casus_belli = acquire_core_state",
 "        actor = AUS",
 "        receiver = FRA",
 "        state_province_id = 726",
 "    }",
 "",
 "    # Britain wants the Republic cut down, not partitioned.",
 "    war_goal = {",
 "        casus_belli = cut_down_to_size",
 "        actor = ENG",
 "        receiver = FRA",
 "    }",
 "",
 "    # The Porte wants Egypt back.",
 "    war_goal = {",
 "        casus_belli = acquire_core_state",
 "        actor = TUR",
 "        receiver = FRA",
 "        state_province_id = 1745",
 "    }",
 "",
 "    # France wants the coalition off its conquests.",
 "    war_goal = {",
 "        casus_belli = status_quo",
 "        actor = FRA",
 "        receiver = AUS",
 "    }",
 "    war_goal = {",
 "        casus_belli = status_quo",
 "        actor = FRA",
 "        receiver = ENG",
 "    }",
 "}", ""]
wr(f"{MOD}/history/wars/SecondCoalition.txt", "\n".join(lines))
log["belligerents"] = len(ALLIES) + len(FRENCH)

# --- diplomacy to match the war ---------------------------------------------------
# HPM's alliances are 1836's. These are the ones that exist on the start date.
al = ['# Alliances in force on 1 January 1800.',
      '# Spain is bound to France by the second Treaty of San Ildefonso of 1796;',
      '# Naples and Portugal are British clients; Austria and Britain are coalition',
      '# partners. Russia and Prussia are deliberately absent: Paul I left the',
      '# coalition in October 1799 and Prussia has been neutral since Basel.', '']
for a, b in (("FRA", "SPA"), ("ENG", "AUS"), ("ENG", "SIC"), ("ENG", "POR"),
             ("ENG", "TUR"), ("AUS", "TUR")):
    al.append(f"alliance = {{\n\tfirst = {a}\n\tsecond = {b}\n"
              f"\tstart_date = 1800.1.1\n\tend_date = 1802.3.25\n}}\n")
    log["alliances"] += 1
wr(f"{MOD}/history/diplomacy/1800_alliances.txt", "\n".join(al))

for k, v in log.items(): print(f"  {k:<24}{v}")
