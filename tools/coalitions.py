"""The coalition wars, 1805-1812.

The Second Coalition was scripted and nothing after it, so France fought until about
1806 and then stood still for thirty years. The whole shape of the period is missing:
Napoleonic Europe is a sequence of coalitions that form, lose, and re-form, and the map
of 1815 is what the last one left behind.

Victoria II will not generate these on its own. The AI declares small opportunistic
wars -- Prussia on France in April 1800, Russia on Prussia in May -- but it will not
build a coalition, and it has no reason to fight Austerlitz.

So each coalition is declared as a war, on its date, by an event rather than a history
file: a history war can only be dated before the start, and these are all after it.
Each is gated on the one before, so a timeline that has already diverged does not keep
producing coalitions that make no sense.

  **Third, 1805.** Britain, Austria, Russia and Sweden. Ends at Austerlitz and
  Pressburg: Austria loses Venetia and the Tyrol.

  **Fourth, 1806.** Prussia comes in alone and late, four days' march from Jena. Ends
  at Tilsit with Prussia halved and Russia changing sides.

  **The Peninsular War, 1808.** Not a coalition: a French army crossing the Pyrenees
  under a treaty, and then not leaving. Gated on Bayonne, so it only happens if the
  Spanish collapse actually ran.

  **Fifth, 1809.** Austria alone, on the strength of what Spain is doing to the French
  army. Ends at Wagram.

  **Russia, 1812.** The invasion. Gated on Tilsit having happened, because without it
  there is no Continental System for Russia to leave.

The war goals are modest. Victoria II resolves a history war the moment its goals are
achievable, and the point is to fight the period, not to script its outcome.
"""
import os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

def war(eid, actor, yr, until, title, desc, opt, enemies, goal_cb, goal_state,
        at_peace=True, allies=(), needs="", sets="", mtth=3, extra=""):
    """An event that declares a war. The actor is whoever historically moved first.

    The window is widened for the same reason as the Peninsular chain: a coalition
    gated on the previous one's flag cannot fire if its own calendar window has shut
    while that flag was still unset."""
    until = max(until, yr + 6)
    decl = []
    first = enemies[0]
    decl.append(f"        war = {{\n"
                f"            target = {first}\n"
                f"            attacker_goal = {{ casus_belli = {goal_cb}"
                + (f" state_province_id = {goal_state}" if goal_state else "")
                + f" }}\n"
                # France defends with an acquisitive goal. Both sides on status_quo made
            # every coalition war a draw by construction: Austerlitz, Jena and Tilsit
            # all fired and not one square mile of Europe changed hands in eleven years.
            f"            defender_goal = {{ casus_belli = cut_down_to_size }}\n"
                f"        }}")
    for e in enemies[1:]:
        decl.append(f"        {e} = {{ war = {{ target = {actor} "
                    f"attacker_goal = {{ casus_belli = status_quo }} }} }}")
    for a in allies:
        decl.append(f"        {a} = {{ war = {{ target = {first} "
                    f"attacker_goal = {{ casus_belli = status_quo }} }} }}")
    gate = f"        has_global_flag = {needs}\n" if needs else ""
    # A coalition forms only out of peace -- Austria does not declare twice. But when
    # France is the actor it is launching an invasion, and France in 1812 is never at
    # peace: the Peninsular War alone sees to that. Requiring it meant the Russian
    # campaign never fired, and Smolensk, Frankfurt and the Congress of Vienna all
    # hung off that one event.
    peace = "        war = no\n" if at_peace else f"        NOT = {{ war_with = {enemies[0]} }}\n"
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {actor}
        year = {yr}
        NOT = {{ year = {until} }}
{peace}{gate}{extra}    }}
    mean_time_to_happen = {{ months = {mtth} }}

    option = {{
        name = "EVTOPTA{eid}"
        set_global_flag = {sets}
{chr(10).join(decl)}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", desc); loc(f"EVTOPTA{eid}", opt)
    log["wars declared"] += 1

war(9101200, "AUS", 1805, 1807,
    "The Third Coalition",
    "Britain is paying again, and this time Russia and Sweden have signed. Mack is to "
    "march on Bavaria before the French can come up from the Rhine, and the Tsar's "
    "armies are already moving west. The Grande Armée is encamped at Boulogne facing "
    "the Channel, a hundred and fifty thousand strong, and nobody in Vienna believes it "
    "can turn round and cross Germany before the winter.",
    "Mack will be at Ulm before they are at the Rhine.",
    ["FRA"], "status_quo", None, allies=["RUS", "SWE", "ENG"],
    sets="h18_third_coalition", mtth=2)

war(9101201, "PRU", 1806, 1808,
    "The Fourth Coalition",
    "Prussia stayed out of the Third while Austria was broken, and now stands alone "
    "against the army that broke it. The ultimatum demands the French leave Germany "
    "within a fortnight. The staff is confident; most of its officers learned their "
    "trade under Frederick, forty years ago, and the army has not fought a major war "
    "since.",
    "The French will withdraw beyond the Rhine.",
    ["FRA"], "status_quo", None, allies=["RUS"],
    needs="h18_third_coalition", sets="h18_fourth_coalition", mtth=2)

war(9101202, "FRA", 1808, 1810,
    "The French Cross the Pyrenees",
    "The army that went to Portugal under the treaty has not come back, and three more "
    "corps have followed it. Madrid is occupied, the royal family is at Bayonne, and "
    "the Emperor has decided that a country which cannot keep its own dynasty in order "
    "is better governed from Paris. Nobody in the French command expects this to take "
    "more than a season.",
    "Spain will be governed properly.",
    ["SPA"], "conquest", None, needs="h18_bayonne",
    sets="h18_peninsular_war", mtth=2)

war(9101203, "AUS", 1809, 1811,
    "The Fifth Coalition",
    "Three hundred thousand French soldiers are in Spain and cannot leave it, and the "
    "Archduke has spent three years rebuilding this army for exactly such a moment. "
    "The proclamation to the troops speaks of the liberty of Germany. Britain is "
    "paying. Russia, which is now technically France's ally, has promised to move "
    "slowly.",
    "The freedom of Germany depends on our exertions.",
    ["FRA"], "status_quo", None, allies=["ENG"],
    needs="h18_peninsular_war", sets="h18_fifth_coalition", mtth=3)

war(9101204, "FRA", 1812, 1814,
    "The Invasion of Russia",
    "The Tsar has opened his ports to British goods and the Continental System is worth "
    "nothing if Russia stands outside it. Six hundred thousand men are crossing the "
    "Niemen, the largest army ever assembled in Europe, and fewer than half of them are "
    "French. The Emperor expects a battle on the frontier and a treaty within two "
    "months.",
    "Let us march on Moscow.",
    ["RUS"], "status_quo", None, needs="h18_fourth_coalition",
    sets="h18_russian_campaign", mtth=3, at_peace=False)

wr(f"{MOD}/events/1800_Coalitions.txt", "\n".join(EV))
wr(f"{MOD}/localisation/16_coalitions.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
