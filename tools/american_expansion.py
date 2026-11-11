"""The United States goes west, at the pace it actually went.

The run reached 1877 with the native nations largely intact, which is not a merciful
alternate history so much as an inert one: the AI was given a continent of small
neighbours and no reason or means to move on them. Westward expansion is the central
fact of nineteenth-century North America and the thing the whole filibuster system
leans against.

So it is scheduled, and the schedule hangs off the Louisiana Purchase -- without it
the United States has no claim west of the Mississippi and none of this happens. Each
step is a treaty-and-removal of the kind that actually occurred, on roughly its date,
taking the nations whose land that step covered:

    1814  the Creek cession after Horseshoe Bend
    1825  the Osage and Kansa treaties, and the Missouri frontier
    1830  Removal: the Choctaw, Chickasaw, Cherokee and Seminole
    1838  the Platte and the eastern Sioux country
    1851  Fort Laramie: the high plains tribes acknowledge the roads
    1864  the Navajo and Apache campaigns
    1877  the last northern wars

Each is a decision rather than an event, so a player of the United States owns it, and
each carries real infamy. They are not free and they are not quiet.
"""
import re, glob, os, collections, json

MOD = "/home/claude/build/HPM"
log = collections.Counter()
DEC, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

P = {int(k): v for k, v in json.load(open("/home/claude/work/world_live.json"))["prov"].items()}
HOLDS = collections.defaultdict(list)
for pid, v in P.items():
    if v["o"]: HOLDS[v["o"]].append(pid)

STEPS = [
 ("the_creek_cession", 1814, ["CRK"], 2,
  "The Creek Cession",
  "Twenty-three million acres taken at Fort Jackson from a people who had just been "
  "beaten at Horseshoe Bend, including a great deal belonging to Creeks who had fought "
  "on our side. General Jackson's view is that a defeated nation has nothing to "
  "negotiate with and that the distinction between friendly and hostile Creeks is a "
  "refinement the frontier cannot afford."),
 ("the_osage_treaties", 1825, ["OSA", "KAN"], 2,
  "The Osage and Kansa Treaties",
  "The Osage give up Missouri and Arkansas for an annuity and a reservation further "
  "west, which is the arrangement every one of these treaties makes and which has "
  "never yet survived the arrival of the next wave of settlers."),
 ("indian_removal", 1830, ["CRK", "CHA", "CCY", "SEM", "CAW"], 6,
  "The Indian Removal Act",
  "The civilised tribes are to be moved beyond the Mississippi, by treaty where "
  "possible and otherwise not. The Cherokee have a written constitution, a newspaper "
  "and a Supreme Court judgment in their favour, and will be marched west in winter "
  "regardless, because the Court has no army and Georgia does."),
 ("the_platte_purchase", 1838, ["PAW", "OTO", "SIO"], 3,
  "The Platte and the Eastern Sioux",
  "The Platte country is bought, which is the polite word, and the eastern bands are "
  "moved off the Missouri bluffs. It opens the road that every wagon train to Oregon "
  "and California will use for the next thirty years."),
 ("fort_laramie", 1851, ["SIO", "CHY", "ARA", "CRA"], 4,
  "The Treaty of Fort Laramie",
  "The plains nations acknowledge the roads through their country and accept "
  "boundaries drawn by men who have not seen most of the land in question, in return "
  "for annuities Congress will reduce within five years. Everyone signing understands "
  "it is about the roads."),
 ("the_southwest_campaigns", 1864, ["NAV", "APA", "ARI"], 4,
  "The Navajo and Apache Campaigns",
  "Carleton's columns burn the orchards in the Canyon de Chelly and march the Navajo "
  "three hundred miles to the Bosque Redondo, where a quarter of them die. It is "
  "called a removal and it is conducted as a siege."),
 ("the_last_wars", 1877, ["SIO", "NEZ", "BLA", "CHY"], 5,
  "The Last of the Northern Wars",
  "The Black Hills were guaranteed by treaty until gold was found in them. What "
  "follows is presented as a war and is in substance a clearance, and it ends with the "
  "Nez Perce stopped forty miles from the Canadian line after a thousand-mile retreat "
  "their pursuers openly admired."),
]

for key, yr, tags, bb, title, desc in STEPS:
    live = [t for t in tags if HOLDS.get(t)]
    if not live: continue
    take = "".join(f"\t\t\t{t} = {{ all_core = {{ remove_core = {t} }} }}\n"
                   f"\t\t\tannex_to = {{ who = THIS target = {t} }}\n" if False else
                   f"\t\t\t{t} = {{ annex_to = USA }}\n" for t in live)
    DEC.append(f"""\t{key} = {{
\t\tpicture = conquest_of_the_desert
\t\tpotential = {{
\t\t\ttag = USA
\t\t\thas_global_flag = h18_louisiana_purchase
\t\t\tyear = {yr}
\t\t\tNOT = {{ has_country_flag = {key}_done }}
\t\t\tOR = {{
{"".join(f"\t\t\t\texists = {t}" + chr(10) for t in live)}\t\t\t}}
\t\t}}
\t\tallow = {{ war = no }}
\t\teffect = {{
\t\t\tset_country_flag = {key}_done
{take}\t\t\tbadboy = {bb}
\t\t\tprestige = 5
\t\t\tany_pop = {{ limit = {{ has_pop_culture = yankee }} consciousness = 1 }}
\t\t}}
\t\tai_will_do = {{ factor = 8 }}
\t}}
""")
    loc(f"{key}_title", title); loc(f"{key}_desc", desc)
    log["removals scheduled"] += 1
    log["nations taken"] += len(live)

wr(f"{MOD}/decisions/1800_American_Expansion.txt",
   "political_decisions = {\n\n" + "\n".join(DEC) + "\n}\n")
wr(f"{MOD}/localisation/34_expansion.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
