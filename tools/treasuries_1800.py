"""Starting cash positions for 1800, and the mercantilist restriction on the colonies.

Victoria II has no starting-treasury field: `money` and `treasury` exist only as event
effects. So each country's opening position is set by an event that fires on the first
day, which doubles as a readable statement of where that country stands fiscally.

The colonies are the interesting case. New Spain was the richest treasury in the
Americas -- the Mexican mining boom was at its peak and remittances to Madrid ran to
millions a year -- and it was also forbidden to trade with anyone but Spain. Cash rich
and commercially caged. That needs two mechanisms, not one.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import os, re, collections

MOD = _BUILD
EVENT_ID = 9100000

# Victoria II hands every country an opening treasury of its own, so an event that
# simply adds money produces base-plus-ours rather than ours: France came out at
# 350,000 when the whole point was that the Consulate was broke. There is no effect
# that sets a treasury, so it has to be emptied first. HPM's own idiom is a guarded
# drain -- take the money only if the country has it -- and a staircase of them
# reduces any starting balance to under a thousand before the real figure is paid in.
DRAIN = "".join(
    f"        random_owned = {{ limit = {{ owner = {{ money = {v} }} }} "
    f"owner = {{ treasury = -{v} }} }}\n"
    for v in (1_000_000, 500_000, 200_000, 100_000, 50_000, 20_000, 10_000,
              5_000, 2_000, 1_000, 500, 200, 100))

# tag: (treasury, one line of why)
CASH = {
 # --- the colonies: silver and sugar, and no freedom to sell
 "NSP": (300000, "the Mexican mining boom at its height; the richest treasury in the Americas"),
 "VPE": (130000, "Potosi past its peak but Peruvian silver still flowing"),
 "EBR": (110000, "Brazilian gold declining from its mid-century peak, diamonds still paying"),
 "VNG":  (70000, "Bogota's mints and the Caribbean trade"),
 "RDP":  (60000, "the Buenos Aires hide trade and silver transhipped from Potosi"),
 "CGC":  (35000, "a poor captaincy on the far edge of the empire"),
 # --- the powers
 "PRU": (210000, "Frederick's war chest intact; neutral since Basel and solvent"),
 "ENG": (160000, "enormous revenue and an enormous debt; the Bank suspended cash payments in 1797"),
 "RUS":  (55000, "chronically short of coin, the paper rouble depreciating"),
 "TUR":  (40000, "the Nizam-i Cedid reforms outrunning the revenue to pay for them"),
 "AUS":  (18000, "near exhaustion after six years of war; the paper gulden inflating"),
 "FRA":  (12000, "the Consulate inherits an empty treasury; the Banque de France is weeks old"),
 "SPA":  (55000, "silver still arrives, but the British blockade is strangling the treasure fleets"),
 "POR":  (65000, "solvent on Brazilian remittances, and paying Britain for protection"),
 "NET":  (14000, "the Batavian Republic drained by French requisitions"),
 "SWE":  (30000, "solvent, neutral, and living off iron and tar"),
 "DEN":  (35000, "growing rich as a neutral carrier while the powers fight"),
 "SIC":  (25000, "restored by British bayonets and broke"),
 "PAP":  (12000, "an interregnum; the French took the treasury in 1798"),
 "SAR":  ( 6000, "a king on an island with almost nothing left"),
 "LIG":  (18000, "Genoese banking capital, besieged"),
 "SWI":  (15000, "the Helvetic Republic, looted and resented"),
 "USA":  (45000, "Hamilton's system working; the debt funded and the credit good"),
 "MEX":  (0, ""), "BRZ": (0, ""),
}
CASH = {k: v for k, v in CASH.items() if v[0] > 0}

LOC = ["Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x"]
ev = []
eid = EVENT_ID
for tag, (amount, why) in sorted(CASH.items()):
    eid += 1
    ev.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        year = 1800
        NOT = {{ year = 1801 }}
    }}
    mean_time_to_happen = {{ days = 1 }}

    option = {{
        name = "EVTOPTA{eid}"
{DRAIN}        treasury = {amount}
    }}
}}
""")
    LOC.append(f"EVTNAME{eid};The State of the Treasury;;;;;;;;;;;;;x")
    LOC.append(f"EVTDESC{eid};{why.capitalize()}.;;;;;;;;;;;;;x")
    LOC.append(f"EVTOPTA{eid};Very well.;;;;;;;;;;;;;x")

# --- the mercantilist cage ------------------------------------------------------
MONOPOLY = ["NSP", "VPE", "VNG", "RDP", "CGC", "EBR", "CBA", "PTR"]
eid += 1
mono_id = eid
ev.append(f"""country_event = {{
    id = {mono_id}
    title = "EVTNAME{mono_id}"
    desc = "EVTDESC{mono_id}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        OR = {{
{chr(10).join(f'            tag = {t}' for t in MONOPOLY)}
        }}
        year = 1800
        NOT = {{ year = 1801 }}
    }}
    mean_time_to_happen = {{ days = 2 }}

    option = {{
        name = "EVTOPTA{mono_id}"
        add_country_modifier = {{ name = colonial_trade_monopoly duration = -1 }}
    }}
}}
""")
LOC.append(f"EVTNAME{mono_id};The Monopoly of the Metropole;;;;;;;;;;;;;x")
LOC.append(f"EVTDESC{mono_id};Every cargo must sail to the mother country in the mother country's "
           "ships. The colony may be rich and still have nowhere to sell.;;;;;;;;;;;;;x")
LOC.append(f"EVTOPTA{mono_id};As the Crown commands.;;;;;;;;;;;;;x")
LOC.append("colonial_trade_monopoly;Colonial Trade Monopoly;;;;;;;;;;;;;x")

# --- the treasure fleets ---------------------------------------------------------
# A standing treasury is a stock; the silver was a flow. Roughly half the colonial
# surplus was remitted to the metropole every year, and in wartime the convoys did
# not get through -- the British blockade of 1796-1802 is why Spain was short of cash
# despite owning the richest mines on earth. Remittances stop the moment a colony
# stops being a vassal, so independence transfers the income with the territory.
REMIT = {
 "NSP": ("SPA", 12000, "the flota sails from Veracruz"),
 "VPE": ("SPA",  5000, "the silver of Potosi, shipped by way of Panama"),
 "VNG": ("SPA",  2500, "gold from the Chocó and the Bogotá mint"),
 "RDP": ("SPA",  2000, "Potosi silver transhipped down the Plata"),
 "CBA": ("SPA",  1200, "Havana sugar duties and the situado"),
 "CGC": ("SPA",   600, "a thin remittance from a thin colony"),
 "PTR": ("SPA",   400, "the customs of San Juan"),
 "EBR": ("POR",  5000, "the fifth of all gold mined, owed to the Crown"),
}
for tag, (metro, amount, why) in sorted(REMIT.items()):
    eid += 1
    ev.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = no

    trigger = {{
        tag = {tag}
        vassal_of = {metro}
        NOT = {{ war_with = {metro} }}
    }}
    mean_time_to_happen = {{
        months = 12
        modifier = {{ factor = 2.5 {metro} = {{ war = yes }} }}
    }}

    option = {{
        name = "EVTOPTA{eid}"
        treasury = -{amount}
        {metro} = {{ treasury = {amount} }}
    }}
}}
""")
    LOC.append(f"EVTNAME{eid};The Treasure Fleet;;;;;;;;;;;;;x")
    LOC.append(f"EVTDESC{eid};{why.capitalize()}. The colony keeps what it needs to govern "
               "itself and sends the rest home.;;;;;;;;;;;;;x")
    LOC.append(f"EVTOPTA{eid};Load the ships.;;;;;;;;;;;;;x")

def w(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

w(f"{MOD}/events/1800_Treasuries.txt", "\n".join(ev))
w(f"{MOD}/localisation/07_treasuries_1800.csv", "\n".join(LOC) + "\n")

# the modifier itself
em = f"{MOD}/common/event_modifiers.txt"
s = open(em, encoding="cp1252", errors="replace").read()
if "colonial_trade_monopoly" not in s:
    s = s.rstrip() + """

colonial_trade_monopoly = {
    icon = 8
    tariff_efficiency_modifier = -0.40
    import_cost = 0.25
    global_immigrant_attract = -0.50
    research_points_modifier = -0.10
    tax_efficiency = 0.15
}
"""
    open(em, "w", encoding="cp1252", errors="replace", newline="\n").write(s)

print(f"  treasury events                   {len(CASH)}")
print(f"  under the trade monopoly          {len(MONOPOLY)}")
print(f"  annual remittances                {len(REMIT)}  "
      f"({sum(v[1] for v in REMIT.values()):,}/yr to the metropoles)")
print(f"  event ids                         {EVENT_ID+1}-{eid}")
print(f"  richest: NSP {CASH['NSP'][0]:,}   poorest power: FRA {CASH['FRA'][0]:,}")
