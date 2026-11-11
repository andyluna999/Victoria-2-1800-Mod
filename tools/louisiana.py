"""Louisiana, 1800-1803.

Three beats, and the first is a genuine fork that nobody remembers being one.

**1 October 1800, San Ildefonso.** Godoy agreed in secret to hand Louisiana back to
France. Spain did not get money for it. Charles IV got a kingdom in Italy for his
daughter and her husband the Duke of Parma -- the Kingdom of Etruria, carved out of
Tuscany -- and six ships of the line. Spain traded the largest territory in North
America for a throne for a son-in-law, and the Spanish court thought it had done well,
because Louisiana had cost the treasury money every year since 1762 and was indefensible
against the Americans already crossing the Mississippi.

That is the fork. Retroceding is historical and the court's own judgement. Retaining
is defensible on the map and ruinous on the ledger: Louisiana loses money, cannot be
garrisoned, and puts Spain directly in the path of American expansion with no French
buffer.

**October 1802, the right of deposit.** The Spanish intendant at New Orleans revoked
the Americans' right to land goods for transshipment, which was the single provocation
that made Jefferson -- who disliked federal spending and loose construction of the
constitution -- decide to buy the place. It fires on either branch, and on the Spanish
branch it is far more dangerous.

**30 April 1803, the sale.** Jefferson sent Monroe to buy New Orleans for ten million.
Talleyrand offered the whole territory. Napoleon had lost an army in Saint-Domingue to
yellow fever, needed money for the war he was about to restart, and had concluded he
could not hold Louisiana against the Royal Navy. The price was sixty million francs
plus assumed claims -- about fifteen million dollars for 828,000 square miles.

If Spain kept Louisiana there is no sale, and the chain routes to a confrontation at
New Orleans instead.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections

MOD = _BUILD
log = collections.Counter()
EV, LOC = [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# Louisiana is what New Spain holds that France has a core on: the Mississippi valley
# from the Gulf to Missouri. Read from the map rather than hard-coded, so a change to
# the province layer carries through.
LOU = []
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                    open(f, encoding="cp1252", errors="replace").read())[0]
    o = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    if o and o.group(1) == "NSP" and re.search(r"^\s*add_core\s*=\s*FRA\s*$", head, re.M):
        LOU.append(pid)
LOU.sort()
log["Louisiana provinces"] = len(LOU)
# Spain ceded the territory, not just the settled part of it. Forty-two provinces
# carry a French core -- the Mississippi watershed as the game models it -- and New
# Spain cores all of them, while administering six. Clearing only the six left Mexico
# with a permanent claim on the Dakotas, Nebraska and Kansas.
#
# Santa Fe and Pueblo are excluded: those are New Mexico, were never part of
# Louisiana under any reading, and Spain's claim to them survived the cession by a
# quarter of a century.
CLAIM_ONLY = [43, 106, 107, 112, 113, 116, 117, 119, 120, 121, 122, 123, 124,
              125, 126, 127, 130, 131, 134, 135, 136, 143, 145, 147, 148, 149,
              128, 129, 150, 151, 152, 153, 154, 155, 156, 157]


def secede(to):
    """Hand the province over and drop the old owner's claim.

    A viceroyalty that has been ordered by its own King to give Louisiana to France
    does not retain a claim on it: the cession is the Crown's act and New Spain is the
    Crown's possession. Keeping the cores would have left Mexico with a standing claim
    to the Mississippi valley for the rest of the game."""
    moved = "\n".join(
        f"        {p} = {{ secede_province = {to} remove_core = NSP }}" for p in LOU)
    # and the claim dies on the rest of the territory, which Spain is also giving up
    claims = "\n".join(f"        {p} = {{ remove_core = NSP }}" for p in CLAIM_ONLY)
    return moved + "\n" + claims

# --- 1800: San Ildefonso --------------------------------------------------------------
EV.append(f"""country_event = {{
    id = 9100900
    title = "EVTNAME9100900"
    desc = "EVTDESC9100900"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = SPA
        year = 1800
        NOT = {{ year = 1801 }}
    }}
    # A nine-month mean in a twelve-month window is about a one-in-four chance of
    # never firing at all. Three months makes it near-certain, and the treaty was
    # signed on 1 October 1800 anyway.
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA9100900"
        set_global_flag = h18_louisiana_retroceded
        # The transfer runs in New Spain's own scope, not Spain's. Louisiana belongs to
        # the viceroyalty, and a secede_province issued from Madrid for provinces Madrid
        # does not own does nothing at all -- the first run retroceded on paper and the
        # map never changed. Routing it through NSP also means the player, who is
        # usually the viceroy, finds out that his northern frontier has been traded.
        NSP = {{ country_event = 9100904 }}
        FRA = {{ relation = {{ who = SPA value = 50 }} prestige = 10 }}
        prestige = 5
        treasury = 10000
        ai_chance = {{ factor = 85 }}
    }}
    option = {{
        name = "EVTOPTB9100900"
        set_global_flag = h18_louisiana_retained
        FRA = {{ relation = {{ who = SPA value = -40 }} }}
        prestige = -5
        NSP = {{ add_country_modifier = {{ name = the_louisiana_burden duration = -1 }} }}
        ai_chance = {{ factor = 15 }}
    }}
}}
""")
loc("EVTNAME9100900", "The Third Treaty of San Ildefonso")
loc("EVTDESC9100900",
    "The First Consul wants Louisiana back and has sent Berthier to Madrid to say so. "
    "He offers no money. He offers a kingdom in Italy -- Etruria, carved from Tuscany -- "
    "for Her Majesty's daughter and the Duke of Parma, and six ships of the line. "
    "Louisiana has cost the treasury money every year since we took it from France in "
    "1762; it cannot be garrisoned; and the Americans are already crossing the "
    "Mississippi in numbers we cannot count, let alone stop. Godoy thinks it a bargain. "
    "The alternative is to keep a province that loses money and invites a war with the "
    "United States that France would not fight for us.")
loc("EVTOPTA9100900", "A throne in Italy is worth a wilderness.")
loc("EVTOPTB9100900", "We will not hand back North America.")

# --- what the viceroy is told -----------------------------------------------------
EV.append(f"""country_event = {{
    id = 9100904
    title = "EVTNAME9100904"
    desc = "EVTDESC9100904"
    picture = "administration"
    is_triggered_only = yes

    option = {{
        name = "EVTOPTA9100904"
{secede("FRA")}
        any_pop = {{ limit = {{ has_pop_culture = criollo }} consciousness = 2 militancy = 1 }}
        prestige = -5
    }}
}}
""")
loc("EVTNAME9100904", "Louisiana Is Given Away")
loc("EVTDESC9100904",
    "A courier from Madrid, by way of Havana, carrying a treaty nobody here was consulted "
    "about. Louisiana goes back to France. His Majesty has received in exchange a kingdom "
    "in Italy for his daughter. This viceroyalty has received a new neighbour on the "
    "Mississippi, and it is the French Republic.")
loc("EVTOPTA9100904", "Madrid did not ask us.")

# --- 1802: the right of deposit ---------------------------------------------------------
EV.append("""country_event = {
    id = 9100901
    title = "EVTNAME9100901"
    desc = "EVTDESC9100901"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = USA
        year = 1802
        NOT = { year = 1804 }
    }
    mean_time_to_happen = { months = 4 }

    option = {
        name = "EVTOPTA9100901"
        set_global_flag = h18_right_of_deposit
        any_pop = { limit = { has_pop_culture = yankee } consciousness = 2 militancy = 1 }
        any_pop = { limit = { has_pop_culture = dixie } militancy = 3 }
        prestige = -3
    }
}
""")
loc("EVTNAME9100901", "The Right of Deposit Revoked")
loc("EVTDESC9100901",
    "The intendant at New Orleans has withdrawn the right of American merchants to land "
    "goods there for transshipment, and with it the only practical outlet for everything "
    "grown west of the Appalachians. The western settlements are talking about taking "
    "the city. The President, who dislikes federal spending and loose readings of the "
    "constitution, has begun to think about buying it instead.")
loc("EVTOPTA9100901", "The Mississippi must be open.")

# --- 1803: the sale ----------------------------------------------------------------------
EV.append(f"""country_event = {{
    id = 9100902
    title = "EVTNAME9100902"
    desc = "EVTDESC9100902"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = FRA
        year = 1803
        NOT = {{ year = 1805 }}
        has_global_flag = h18_louisiana_retroceded
        USA = {{ exists = yes }}
    }}
    mean_time_to_happen = {{ months = 4 }}

    option = {{
        name = "EVTOPTA9100902"
        set_global_flag = h18_louisiana_purchase
        any_owned = {{
            limit = {{
                is_core = FRA
                continent = north_america
                # Louisiana, not the Antilles. Saint-Domingue and Santo Domingo are
                # French in 1800 and are not for sale -- one of them is about to
                # become Haiti, and selling the island to Washington meant Haiti
                # never existed in any playthrough.
                NOT = {{ province_id = 2213 }}
                NOT = {{ province_id = 2214 }}
                NOT = {{ province_id = 2215 }}
                NOT = {{ province_id = 2216 }}
            }}
            secede_province = USA
        }}
        treasury = 60000
        USA = {{ treasury = -60000 prestige = 15 }}
        prestige = 5
        ai_chance = {{
            factor = 95
            modifier = {{ factor = 2 war_with = ENG }}
        }}
    }}
    option = {{
        name = "EVTOPTB9100902"
        set_global_flag = h18_louisiana_kept_by_france
        USA = {{ relation = {{ who = FRA value = -60 }} }}
        prestige = 5
        ai_chance = {{
            factor = 5
            # Napoleon sold because the war with Britain was restarting and the Royal
            # Navy could take New Orleans whenever it liked. A France already at war
            # with Britain has no business refusing; the first run rolled this branch
            # at ten per cent and the Purchase never happened.
            modifier = {{ factor = 0 war_with = ENG }}
        }}
    }}
}}
""")
loc("EVTNAME9100902", "Monroe Comes to Buy a City")
loc("EVTDESC9100902",
    "The Americans have sent Monroe with authority to offer ten million dollars for New "
    "Orleans and the Floridas. Talleyrand has asked him what he would give for the whole "
    "of Louisiana. The army sent to Saint-Domingue is dead of yellow fever, the war with "
    "Britain will resume within weeks, and the Royal Navy can take New Orleans whenever "
    "it chooses. Sixty million francs now is better than nothing later, and a United "
    "States large enough to trouble Britain is worth something on its own.")
loc("EVTOPTA9100902", "Sell it. The whole of it.")
loc("EVTOPTB9100902", "France does not retreat from America.")

# --- the branch where Spain kept it ---------------------------------------------------------
EV.append("""country_event = {
    id = 9100903
    title = "EVTNAME9100903"
    desc = "EVTDESC9100903"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = USA
        year = 1803
        NOT = { year = 1807 }
        has_global_flag = h18_louisiana_retained
        has_global_flag = h18_right_of_deposit
    }
    mean_time_to_happen = { months = 10 }

    option = {
        name = "EVTOPTA9100903"
        set_global_flag = h18_new_orleans_bought_from_spain
        badboy = 2
        NSP = { treasury = 25000 }
        treasury = -25000
        ai_chance = { factor = 60 }
    }
    option = {
        name = "EVTOPTB9100903"
        set_global_flag = h18_new_orleans_crisis
        SPA = { relation = { who = USA value = -80 } }
        NSP = { relation = { who = USA value = -80 } }
        any_pop = { limit = { has_pop_culture = dixie } militancy = 4 }
        ai_chance = { factor = 40 }
    }
}
""")
loc("EVTNAME9100903", "New Orleans, With Spain Still There")
loc("EVTDESC9100903",
    "Louisiana never went back to France, so there is no Frenchman in Paris willing to "
    "sell us a continent to spite the British. There is a Spanish intendant at New "
    "Orleans holding the mouth of the Mississippi, and a Spanish empire that will not "
    "part with it for any price we have offered. The western settlements have stopped "
    "asking the government to negotiate.")
loc("EVTOPTA9100903", "Offer for the city alone.")
loc("EVTOPTB9100903", "Then the militia will open the river.")

MODS = """
the_louisiana_burden = {
\ticon = 4
\ttax_efficiency = -0.06
\tsupply_consumption = 0.1
\tglobal_immigrant_attract = -0.1
}
"""
src = open(f"{MOD}/common/event_modifiers.txt", encoding="cp1252", errors="replace").read()
if "the_louisiana_burden" not in src:
    open(f"{MOD}/common/event_modifiers.txt", "w", encoding="cp1252",
         errors="replace", newline="\n").write(src.rstrip() + "\n" + MODS + "\n")
    log["modifiers"] = 1

wr(f"{MOD}/events/1800_Louisiana.txt", "\n".join(EV))
wr(f"{MOD}/localisation/13_louisiana.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["events"] = len(EV); log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<28}{v}")
