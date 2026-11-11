"""A demographic audit for 1800, run on every build.

Four of these checks were written after finding Scotland, Wales, Ireland and Australia
wrong by eye. The point is that none of them should ever have needed an eye.

HPM's culture map is correct for 1836 and wrong for 1800 in three repeatable ways: a
people filed under a catch-all culture, a settler population sized for the later date,
and a distribution following settlement that has not happened yet. Each check below
targets one of those.
"""
import json, collections, sys, os

W = "/home/claude/work"
L = json.load(open(f"{W}/world_live.json"))
P = {int(k): v for k, v in L["prov"].items()}
C, CU = L["countries"], L["cultures"]
SCALE = 0.25
findings = []
def note(sev, check, detail):
    findings.append((sev, check, detail))

pops = collections.defaultdict(collections.Counter)
ctot = collections.Counter(); cwhere = collections.defaultdict(collections.Counter)
for pid, t, c, r, sz in L["pops"]:
    pops[pid][CU[c]] += sz; ctot[CU[c]] += sz; cwhere[CU[c]][P[pid]["ct"]] += sz
held = collections.defaultdict(list)
for p, v in P.items():
    if v["o"]: held[v["o"]].append(p)

# measured over core provinces only: an empire's total is not its nation's population
EXPECT_CORE = True
# legitimate cases, not findings
PRIMARY_OK = {"QNG",            # a Manchu dynasty ruling a Han empire, by definition
              "ENG", "NET", "POR", "SPA", "FRA", "DEN",   # metropole over colonies
              # a ruling house of one people over another is the normal condition of
              # the age, not a mistake: the Nizam's court was Persianate over Telugu
              # and Marathi, Gabu's Mandinka over Fulbe, Angoche's Swahili over Makua
              "HYD", "GBU", "AGC", "BDK", "MKN", "DAG", "OMA", "YER", "GAZ", "MAS",
              "YNN", "SAR", "MAR", "MCK", "KRM", "XBI"}
SETTLER_OK = {"Azores", "Canary Islands", "Madeira", "Saint Helena", "Reunion",
              "Mauritius", "Bourbon", "Cape Verde", "Falkland Islands", "Bermuda",
              "Tristan da Cunha"}
# a country split in two on the start date is measured as the pair
PAIRED = {"DAI": ("DAI", "TYS"), "HDJ": ("HDJ",), "NEJ": ("NEJ",)}

AUDITED = {"north_america", "south_america", "australia_new_zealand"}
BRITISH_ISLES = set(range(254, 277))
def audited(pid): return P[pid]["ct"] in AUDITED or pid in BRITISH_ISLES

# --- 1. a culture that exists and holds nobody -----------------------------------
# This is how Scotland was found: `scottish` was on the map in North America and
# absent from Scotland. A defined culture with no pops anywhere is either a people
# who have been filed under someone else's name, or dead weight.
ALLOWED_EMPTY = {
 # successor and formable cultures that correctly hold nobody in 1800
 "australian", "anglo_canadian", "alaskan", "texan", "mexican", "brazilian",
 "central_american", "caribeno", "afro_antillean", "native_american_minor",
 # superseded by the Americas pass
 "aimara", "mayan", "tupinamba", "patagonian", "dakota",
 "north_andean", "south_andean", "platinean",
}
empty = sorted(c for c in CU if not c.startswith("__") and ctot[c] == 0
               and c not in ALLOWED_EMPTY)
if empty:
    note("HIGH", "cultures defined but holding nobody anywhere", ", ".join(empty))

# --- 2. a catch-all culture carrying a whole region -------------------------------
# Cultures that LUMP distinct peoples together, so a region made entirely of one is
# worth a look. Deliberately excludes the cultures that are the genuine majority of
# their own homeland: beifaren in Shandong, russian around Moscow and turkish in
# Anatolia are not errors, and flagging them buried the ones that were.
CATCHALL = {"british", "french", "north_german", "south_german", "spanish",
            "italian", "north_italian", "south_italian", "arab", "portuguese"}
# and the homelands where even a lumping culture is simply the people who live there
NATIVE_OK = {"french": ("FRA_4",), "spanish": ("SPA_4", "SPA_5"),
             "portuguese": ("POR_5",), "british": ("ENG_2",),
             "south_italian": ("SIC", "NAP", "PAP"),
             "north_german": ("PRU", "HAN", "MEC", "OLD", "SAX", "HAM", "LUB", "BRE",
                              "ANH", "BRU", "LIP", "NAS", "HES", "HEK", "WAL", "SWH"),
             "south_german": ("BAV", "WUR", "BAD", "AUS_6", "AUS_5", "SWI", "FRM"),
             # Lombardy, Venetia and the Legations really are north Italian, and
             # London really is British
             "north_italian": ("LOM", "VEN", "SAR_7", "TUS", "AUS_72", "PAP_74",
                               "MOD", "PAR", "LUC"),
             "british": ("ENG_2", "ENG_3")}
reg = collections.defaultdict(collections.Counter)
for pid, mix in pops.items():
    if audited(pid): continue
    for c, v in mix.items(): reg[P[pid]["rg"]][c] += v
flagged = []
for rg, mix in reg.items():
    tot = sum(mix.values())
    if tot < 400_000 * SCALE: continue
    top, tv = mix.most_common(1)[0]
    if top in CATCHALL and tv / tot > 0.95 and not any(
            rg.startswith(pre) for pre in NATIVE_OK.get(top, ())):
        flagged.append((int(tot / SCALE), rg, top, round(100 * tv / tot)))
flagged.sort(reverse=True)
if flagged:
    note("MED", f"{len(flagged)} regions are >95% one catch-all culture",
         "; ".join(f"{rg} {top} {sh}% ({tot:,})" for tot, rg, top, sh in flagged[:8]))

# --- 3. a country whose own primary culture is a minority in its own core ---------
# Restricted to core provinces: an empire's primary being a minority across its
# colonies is correct and uninteresting. At home it is a filing error.
rows = []
for tag, c in C.items():
    core = [p for p in held[tag] if tag in P[p]["cr"] and not audited(p)]
    if len(core) < 2: continue
    tot = sum(sum(pops[p].values()) for p in core)
    if tot < 150_000 * SCALE: continue
    prim = c.get("prim") or ""
    share = sum(pops[p].get(prim, 0) for p in core) / tot if tot else 0
    if share < 0.35 and tag not in PRIMARY_OK:
        m = collections.Counter()
        for p in core:
            for k, v in pops[p].items(): m[k] += v
        rows.append((round(100 * share), tag, c["name"][:22], prim, int(tot / SCALE),
                     ", ".join(f"{k} {round(100*v/tot)}%" for k, v in m.most_common(2))))
rows.sort()
if rows:
    note("MED", f"{len(rows)} countries whose primary culture is a minority at home",
         "; ".join(f"{t} {nm} primary {pr} {sh}% [{mix}]" for sh, t, nm, pr, _, mix in rows[:6]))

# --- 4. national population against a 1800 estimate -------------------------------
# Census where one exists, standard historical-demography series otherwise.
# Everything a country holds on the start date, colonies included. Colonial empires
# whose totals are dominated by their possessions are left out rather than given a
# meaningless number: Britain's holdings here include Bengal.
EXPECT = {
 "FRA": 37_000_000,    # France with Belgium, the Rhineland, Piedmont and the Nile
 "RUS": 37_000_000,    # the empire, Siberia included
 "QNG": 330_000_000,
 "AUS": 23_500_000,    # Habsburg lands with Hungary, Galicia, Lombardy, Venetia
 "TUR": 21_000_000,    # Rumelia, Anatolia, the Levant and Iraq, less French Egypt
 "JAP": 30_000_000, "KOR": 13_000_000, "PRU": 9_500_000,
 "SIC": 5_600_000, "IRE": 5_000_000, "USA": 5_300_000, "PER": 6_000_000,
 "SWE": 3_300_000, "DEN": 2_450_000, "SIA": 3_000_000, "BUR": 4_000_000,
 "DAI": 10_000_000,   # estimates for Vietnam in 1800 run from 6M to 13M; the
                      # Nguyen registers counted taxpayers, not people "MOR": 3_000_000, "ETH": 4_000_000, "AFG": 5_000_000,
 "NEP": 2_000_000,
}
off = []
for tag, want in EXPECT.items():
    tags = PAIRED.get(tag, (tag,))
    ps = [p for t in tags for p in held.get(t, [])]
    if not ps: continue
    got = int(sum(sum(pops[p].values()) for p in ps) / SCALE)
    if want and abs(got - want) / want > 0.20:
        off.append((abs(got - want) / want, tag, got, want))
off.sort(reverse=True)
if off:
    note("MED", f"{len(off)} countries more than 20% off their 1800 estimate",
         "; ".join(f"{t} {g:,} vs {w:,} ({'+' if g>w else ''}{round(100*(g-w)/w)}%)"
                   for _, t, g, w in off[:8]))

# --- 5. settler populations where settlement has barely begun ---------------------
# Australia's Europeans were twenty-three times too many because the distribution
# followed 1836 colonies. Any European culture holding a large share of a province
# outside Europe and the Americas is worth a look.
# Written after Australia, where a colony three years old held a third of a continent.
# Russian Siberia is not that case: settlement there began in the 1580s and by 1800
# Russians were about half its population, so Siberia is excluded rather than flagged
# every build.
EURO = {"british", "french", "dutch", "portuguese", "spanish", "north_german",
        "south_german", "danish", "swedish", "scottish", "irish"}
big = []
for pid, mix in pops.items():
    if audited(pid) or P[pid]["ct"] in ("europe",): continue
    tot = sum(mix.values())
    if tot < 20_000 * SCALE: continue
    eur = sum(v for c, v in mix.items() if c in EURO)
    if eur / tot > 0.40 and P[pid]["n"] not in SETTLER_OK:
        big.append((int(eur / SCALE), P[pid]["n"], P[pid]["ct"], round(100 * eur / tot)))
big.sort(reverse=True)
if big:
    note("MED", f"{len(big)} non-European provinces are >40% European settlers",
         "; ".join(f"{n} ({ct[:6]}) {sh}% = {e:,}" for e, n, ct, sh in big[:8]))

print("=" * 78)
print("DEMOGRAPHIC AUDIT — the 1800 world")
print("=" * 78)
if not findings:
    print("\n  no findings\n")
else:
    for sev, check, detail in findings:
        print(f"\n[{sev}] {check}")
        for part in detail.split("; "):
            print(f"      {part}")
print()
world = int(sum(ctot.values()) / SCALE)
print(f"  world population {world:,}   (about 980,000,000 in 1800)")
print(f"  cultures in use  {sum(1 for c in CU if ctot[c])} of {len(CU)}")
sys.exit(0)
