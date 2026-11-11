"""The Hejaz, 1800-1818.

On the start date the Sharif of Mecca holds the Holy Cities for the Sultan, and the
Emirate of Diriyah is three days' ride away and expanding. What follows is the single
most consequential thing to happen in Arabia in the period, and the inherited map has
none of it: Diriyah takes Ta'if in 1802, Mecca in April 1803 and Medina in 1805, the
Ottomans discover they cannot dislodge it, and Muhammad Ali is ordered to do the job.
Ibrahim Pasha razes Diriyah in 1818 and the first Saudi state ends.

Two nodes, both weighted. The Saudi conquest is near-certain but not inevitable -- the
Sharif had warning and the Ottomans had a garrison. The Egyptian reconquest took seven
years, two commanders and the ruin of an army, and could very plausibly have failed:
if it does, the Saudis keep the Holy Cities and Muhammad Ali never builds the
reputation he spends on Syria.

Asir goes to Diriyah at the start. The Asiri tribes accepted Wahhabism in the 1790s
and were never the Sharif's.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, collections

MOD = _BUILD; W = _WORK
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

MECCA, JIDDA, MEDINA, TABUK, ABHA = 1151, 1152, 1153, 1154, 1155
HOLY = (MECCA, JIDDA, MEDINA)

prov = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    prov[int(re.match(r"(\d+)", os.path.basename(f)).group(1))] = f

# Asir is Diriyah's, and the Holy Cities carry everyone's claim
OWN = {ABHA: "NEJ"}
CORES = {ABHA: ["NEJ", "HDJ"], MECCA: ["TUR", "NEJ"], JIDDA: ["TUR", "NEJ"],
         MEDINA: ["TUR", "NEJ"], TABUK: ["TUR"]}
for pid in set(list(OWN) + list(CORES)):
    f = prov.get(pid)
    if not f: continue
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    if pid in OWN:
        head = re.sub(r"^\s*owner\s*=.*\n", "", head, flags=re.M)
        head = re.sub(r"^\s*controller\s*=.*\n", "", head, flags=re.M)
        head = f"owner = {OWN[pid]}\ncontroller = {OWN[pid]}\n" + head.lstrip("\n")
    for t in CORES.get(pid, []):
        if not re.search(rf"^\s*add_core\s*=\s*{t}\s*$", head, re.M):
            head = head.rstrip("\n") + f"\nadd_core = {t}\n"
    wr(f, head.rstrip("\n") + "\n" + tail)
    log["provinces adjusted"] += 1

# the Sultan's suzerainty over the Sharif ends when the Sharif loses Mecca
f = f"{MOD}/history/diplomacy/1800_protectorates.txt"
if os.path.exists(f):
    wr(f, rd(f).replace("\tsecond = HDJ\n\tstart_date = 1800.1.1\n\tend_date = 1836.1.1",
                        "\tsecond = HDJ\n\tstart_date = 1800.1.1\n\tend_date = 1803.4.1"))
    log["suzerainty re-dated to the fall of Mecca"] = 1

LOC, EV = [], []
def loc(k, v): LOC.append(f"{k};{v};;;;;;;;;;;;;x")
take = "\n".join(f"        {p} = {{ secede_province = THIS add_core = THIS }}" for p in HOLY)
give_back = "\n".join(f"        {p} = {{ secede_province = HDJ }}" for p in HOLY)

EV.append(f"""country_event = {{
    id = 9100700
    title = "EVTNAME9100700"
    desc = "EVTDESC9100700"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = NEJ
        year = 1802
        NOT = {{ year = 1806 }}
        owns = {ABHA}
        NOT = {{ has_global_flag = hejaz_resolved }}
    }}
    mean_time_to_happen = {{ months = 10 }}

    option = {{
        name = "EVTOPTA9100700"
        set_global_flag = hejaz_resolved
        random_list = {{
            80 = {{ country_event = 9100701 }}
            20 = {{ country_event = 9100702 }}
        }}
    }}
}}

country_event = {{
    id = 9100701
    title = "EVTNAME9100701"
    desc = "EVTDESC9100701"
    picture = "administration"
    is_triggered_only = yes
    option = {{
        name = "EVTOPTA9100701"
        set_global_flag = wahhabi_hejaz
{take}
        prestige = 25
        TUR = {{ prestige = -25 }}
        HDJ = {{ prestige = -20 }}
    }}
}}

country_event = {{
    id = 9100702
    title = "EVTNAME9100702"
    desc = "EVTDESC9100702"
    picture = "administration"
    is_triggered_only = yes
    option = {{
        name = "EVTOPTA9100702"
        prestige = -10
        militancy = 2
        TUR = {{ prestige = 10 }}
    }}
}}

country_event = {{
    id = 9100710
    title = "EVTNAME9100710"
    desc = "EVTDESC9100710"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = NEJ
        has_global_flag = wahhabi_hejaz
        year = 1816
        NOT = {{ year = 1820 }}
    }}
    mean_time_to_happen = {{ months = 14 }}

    option = {{
        name = "EVTOPTA9100710"
        random_list = {{
            75 = {{ country_event = 9100711 }}
            25 = {{ country_event = 9100712 }}
        }}
    }}
}}

country_event = {{
    id = 9100711
    title = "EVTNAME9100711"
    desc = "EVTDESC9100711"
    picture = "administration"
    is_triggered_only = yes
    option = {{
        name = "EVTOPTA9100711"
        clr_global_flag = wahhabi_hejaz
        set_global_flag = diriyah_razed
{give_back}
        prestige = -40
        any_pop = {{ militancy = 4 }}
        EGY = {{ prestige = 30 }}
        TUR = {{ prestige = 15 }}
    }}
}}

country_event = {{
    id = 9100712
    title = "EVTNAME9100712"
    desc = "EVTDESC9100712"
    picture = "administration"
    is_triggered_only = yes
    option = {{
        name = "EVTOPTA9100712"
        set_global_flag = diriyah_endures
        prestige = 40
        EGY = {{ prestige = -30 }}
        TUR = {{ prestige = -20 }}
    }}
}}
""")

loc("EVTNAME9100700", "The Road to Mecca")
loc("EVTDESC9100700",
    "Ta'if has fallen and the Sharif's levies will not stand in the open. Saud ibn "
    "Abd al-Aziz is a day's march from the Holy Cities, and the Ottoman garrison that "
    "was meant to hold them has not been paid in two years.")
loc("EVTOPTA9100700", "March.")
loc("EVTNAME9100701", "The Holy Cities Taken")
loc("EVTDESC9100701",
    "Mecca opens its gates in April and Medina follows. The tombs and domes come down, "
    "the pilgrim caravans from Cairo and Damascus are turned back, and for the first "
    "time in nine hundred years the Sultan is not the protector of the Two Sanctuaries. "
    "Istanbul cannot let this stand and cannot reach it either.")
loc("EVTOPTA9100701", "God is one.")
loc("EVTNAME9100702", "The Sharif Holds")
loc("EVTDESC9100702",
    "The Sharif has had warning enough to provision Jidda and buy the tribes along the "
    "road. The siege is lifted and Saud withdraws into Najd with nothing to show for "
    "the season but losses.")
loc("EVTOPTA9100702", "Another year, then.")
loc("EVTNAME9100710", "Ibrahim Pasha in Najd")
loc("EVTDESC9100710",
    "Seven years of Egyptian campaigning have taken the Hejaz back and reached the edge "
    "of the Najd plateau. Ibrahim Pasha has brought artillery across the desert and is "
    "standing before Diriyah itself. Tusun failed here. His brother does not intend to.")
loc("EVTOPTA9100710", "Let the walls be tested.")
loc("EVTNAME9100711", "Diriyah Razed")
loc("EVTDESC9100711",
    "The capital falls after a five-month siege. The walls are pulled down, the date "
    "palms cut, and Abdullah ibn Saud is sent to Istanbul to be beheaded at the gate of "
    "Hagia Sophia. The first Saudi state is finished. The idea is not: a cousin will be "
    "back in Riyadh within six years.")
loc("EVTOPTA9100711", "The wells are filled in.")
loc("EVTNAME9100712", "The Siege Fails")
loc("EVTDESC9100712",
    "The guns cannot be kept supplied across that distance and the army cannot be kept "
    "fed. Ibrahim withdraws toward the coast with a third of what he brought. Egypt has "
    "spent seven years and an army on the Najd, and the House of Saud still holds Mecca.")
loc("EVTOPTA9100712", "The desert kept us.")

wr(f"{MOD}/events/1800_Hejaz.txt", "\n".join(EV))
wr(f"{MOD}/localisation/15_hejaz.csv",
   "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
   + "\n".join(LOC) + "\n")
log["divergence nodes"] = 2
log["events"] = 6
for k, v in log.items(): print(f"  {k:<40}{v}")
