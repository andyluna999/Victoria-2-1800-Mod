"""
# Capital flight used to stack: five tiers of tax penalty on top of the colonial
# monopoly and the junta, which drove effective taxation below zero -- a state paying
# people to collect its revenue. A tier removes the one below it now, and the worst
# single tier is -12% rather than -25%, so the floor is near zero and not through it.
Capital flight during a popular war of independence.

Not every independence war wrecked its economy. Where the criollo elite led — Iturbide
in 1821, the Buenos Aires junta, Chile — the mines, the mints and the merchant houses
came through more or less intact. Where the war began as a popular rising, as it did
under Hidalgo and Morelos from 1810, the result was different: Guanajuato flooded, the
mercury supply cut, and Mexican merchant capital shipped to Cadiz and Havana. Mexico
reached independence in 1821 with its silver output at a third of its 1809 peak and a
bankrupt treasury.

So the damage is conditioned on *who leads the revolt*, it compounds for every year the
war runs, and it outlives the war. The money does not vanish: it goes to the metropole,
which is where it actually went.

The independence events of WP-17 choose the branch by setting one of two flags on the
colony at the moment the rising begins:

    set_country_flag = popular_insurrection   -- Hidalgo's path: the chain below runs
    set_country_flag = elite_pact             -- Iturbide's path: nothing happens

Nothing here fires unless a flag is set, so it sits inert until that layer exists.
"""
import os

MOD = "/home/claude/build/HPM"
BASE = 9100100
COLONIES = ["NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR"]
METRO = "SPA"

# five tiers. Mining suffers worst because the mines were what the insurgency reached
# first and what needed capital and mercury to keep running.
TIERS = [
    (1, -0.15, -0.05, -0.03,  2000),
    (2, -0.30, -0.10, -0.06,  3000),
    (3, -0.45, -0.15, -0.09,  4000),
    (4, -0.60, -0.20, -0.11,  5000),
    (5, -0.70, -0.25, -0.13,  6000),
]
# The tax column is deliberately shallower than the output columns. Capital flight
# should strangle what the country produces, not invert what the state collects: a
# playtest watched effective taxation go negative, which means a government paying
# people to take its revenue away. Mines and farms still collapse by seventy and
# twenty-five per cent at the worst tier -- that is where the pain belongs.

mods = ["\n# --- capital flight during a popular war of independence ---"]
for n, mine, farm, tax, _ in TIERS:
    mods.append(f"""
capital_flight_{n} = {{
    icon = 4
    mine_rgo_eff = {mine}
    farm_rgo_eff = {farm}
    tax_efficiency = {tax}
    immigrant_push = {0.10 * n:.2f}
    global_pop_militancy_modifier = {0.05 * n:.2f}
}}""")

ev, loc = [], []
tag_or = "\n".join(f"            tag = {t}" for t in COLONIES)
for i, (n, mine, farm, tax, flight) in enumerate(TIERS):
    eid = BASE + n
    prev = f"        has_country_flag = capital_flight_{n-1}\n" if n > 1 else \
           f"        NOT = {{ has_country_flag = capital_flight_1 }}\n"
    clear = (f"        clr_country_flag = capital_flight_{n-1}\n"
             f"        remove_country_modifier = capital_flight_{n-1}\n") if n > 1 else ""
    ev.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = no

    trigger = {{
        OR = {{
{tag_or}
        }}
        has_country_flag = popular_insurrection
        war_with = {METRO}
{prev}        NOT = {{ has_country_flag = capital_flight_{n} }}
    }}
    mean_time_to_happen = {{ months = 12 }}

    option = {{
        name = "EVTOPTA{eid}"
{clear}        set_country_flag = capital_flight_{n}
        add_country_modifier = {{ name = capital_flight_{n} duration = -1 }}
        treasury = -{flight}
        {METRO} = {{ treasury = {flight} }}
    }}
}}
""")
    loc += [f"EVTNAME{eid};Capital Takes Flight;;;;;;;;;;;;;x",
            f"EVTDESC{eid};Another year of insurrection. The mine owners have drawn down "
            "what they can and shipped it to Cadiz; the shafts fill with water for want of "
            "men and mercury, and the merchant houses close their doors.;;;;;;;;;;;;;x",
            f"EVTOPTA{eid};There is nothing to be done.;;;;;;;;;;;;;x",
            f"capital_flight_{n};Capital Flight;;;;;;;;;;;;;x"]

# recovery: once the war is over the damage decays, slowly, one tier a decade
for n, _, _, _, _ in reversed(TIERS):
    eid = BASE + 50 + n
    to = f"""        set_country_flag = capital_flight_{n-1}
        add_country_modifier = {{ name = capital_flight_{n-1} duration = -1 }}
""" if n > 1 else ""
    ev.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = no

    trigger = {{
        has_country_flag = capital_flight_{n}
        war = no
    }}
    mean_time_to_happen = {{ months = 120 }}

    option = {{
        name = "EVTOPTA{eid}"
        clr_country_flag = capital_flight_{n}
        remove_country_modifier = capital_flight_{n}
{to}    }}
}}
""")
    loc += [f"EVTNAME{eid};The Mines Reopen;;;;;;;;;;;;;x",
            f"EVTDESC{eid};Peace, and slowly some of the capital comes back. A shaft is "
            "pumped out, a house reopens. It will be a generation before the old output "
            "is matched.;;;;;;;;;;;;;x",
            f"EVTOPTA{eid};Begin again.;;;;;;;;;;;;;x"]

def w(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

w(f"{MOD}/events/1800_CapitalFlight.txt", "\n".join(ev))
w(f"{MOD}/localisation/08_capital_flight.csv",
  "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
  + "\n".join(loc) + "\n")

em = f"{MOD}/common/event_modifiers.txt"
s = open(em, encoding="cp1252", errors="replace").read()
if "capital_flight_1" not in s:
    open(em, "w", encoding="cp1252", errors="replace", newline="\n").write(s.rstrip() + "\n" + "\n".join(mods) + "\n")

print(f"  capital-flight tiers              {len(TIERS)}")
print(f"  escalation + recovery events      {len(ev)}")
print(f"  mining efficiency at the worst     {int(TIERS[-1][1]*100)}%")
print(f"  shipped to {METRO} over five years  {sum(t[4] for t in TIERS):,}")
