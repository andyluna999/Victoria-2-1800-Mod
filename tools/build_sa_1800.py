"""South America, 1800. Same method as North America: census-anchored totals, weights
as shares out of 100, province-level overrides where a region spans cultural zones,
and iterative proportional fitting so both margins hold."""
import json, collections

W = "/home/claude/work"
L = json.load(open(f"{W}/world_live.json"))
ST = {int(k): v for k, v in json.load(open(f"{W}/prov_stats.json")).items()}
SCALE = 0.25
SA = {int(k): v for k, v in L["prov"].items() if v["ct"] == "south_america"}

# culture -> group, religion, archetype, real 1800 population
C = {
 "spanish":    ("iberian","catholic","peninsular",      70000),
 "portuguese": ("iberian","catholic","peninsular",      60000),   # reinois
 "criollo":    ("latin_american_cultures","catholic","criollo", 1150000),
 "mestizo":    ("latin_american_cultures","catholic","mestizo", 2000000),
 "brasileiro": ("latin_american_cultures","catholic","criollo",  950000),
 "AfroBrazilian":  ("african_diaspora_cultures","catholic","enslaved",1900000),
 "AfroCaribbean":  ("african_diaspora_cultures","catholic","enslaved", 620000),
 "quechua":    ("andean","catholic","settled_native", 1300000),
 "aymara":     ("andean","catholic","settled_native",  520000),
 "chibcha":    ("andean","catholic","settled_native",  150000),
 "mapuche":    ("southern_cone","animist","settled_native", 180000),
 "tehuelche":  ("southern_cone","animist","nomad_native",    45000),
 "guarani":    ("southern_cone","catholic","settled_native",200000),
 "guaycuru":   ("southern_cone","animist","nomad_native",    60000),
 "tupi":       ("amazonian_peoples","animist","settled_native",130000),
 "je":         ("amazonian_peoples","animist","nomad_native",  110000),
 "carib":      ("amazonian_peoples","animist","nomad_native",   80000),
 "arawak":     ("amazonian_peoples","animist","settled_native",  95000),
 "amazonian":  ("amazonian_peoples","animist","nomad_native",   600000),
 "british":    ("british","protestant","urban",   9000),
 "dutch":      ("beneluxian","protestant","urban",14000),
 "french":     ("french","catholic","urban",       8000),
 "polynesian": ("oceanic","animist","settled_native", 3000),
}

ARCH = {
 "urban":{"artisans":.33,"clerks":.11,"bureaucrats":.11,"aristocrats":.10,"farmers":.14,
          "clergymen":.06,"soldiers":.06,"officers":.03,"capitalists":.03,"labourers":.03},
 "peninsular":{"aristocrats":.22,"bureaucrats":.20,"artisans":.14,"clerks":.12,"clergymen":.12,
               "capitalists":.08,"officers":.06,"soldiers":.04,"farmers":.02},
 "criollo":{"farmers":.52,"artisans":.14,"aristocrats":.09,"bureaucrats":.06,"clergymen":.05,
            "soldiers":.05,"labourers":.04,"clerks":.025,"officers":.015,"capitalists":.01},
 "mestizo":{"farmers":.58,"labourers":.24,"artisans":.10,"soldiers":.04,"clergymen":.015,
            "aristocrats":.01,"clerks":.01,"officers":.005},
 "enslaved":{"slaves":.90,"labourers":.07,"artisans":.025,"farmers":.005},
 "settled_native":{"farmers":.90,"artisans":.045,"clergymen":.02,"aristocrats":.02,"soldiers":.015},
 "nomad_native":{"farmers":.80,"soldiers":.12,"aristocrats":.04,"clergymen":.025,"artisans":.015},
}

# shares out of 100, by HPM region
R = {
 # Caribbean coast, Venezuela and the Guianas
 "ENG_2228":{"AfroCaribbean":60,"criollo":20,"dutch":20},
 "VNZ_2234":{"mestizo":45,"AfroCaribbean":25,"criollo":20,"chibcha":5,"spanish":5},
 "VNZ_2265":{"mestizo":40,"AfroCaribbean":28,"criollo":25,"spanish":7},
 "VNZ_2278":{"arawak":30,"carib":30,"mestizo":25,"AfroCaribbean":15},
 "CLM_2251":{"mestizo":40,"AfroCaribbean":30,"criollo":22,"spanish":8},
 "CLM_2247":{"mestizo":35,"chibcha":30,"criollo":28,"spanish":7},
 "CLM_2259":{"mestizo":40,"AfroCaribbean":25,"criollo":17,"quechua":15,"spanish":3},
 "CLM_2262":{"amazonian":70,"arawak":15,"mestizo":15},
 "ENG_1979":{"AfroCaribbean":65,"arawak":12,"carib":8,"dutch":7,"british":4,"french":4},
 # Ecuador and Peru
 "ECU_2279":{"quechua":50,"mestizo":28,"criollo":15,"AfroCaribbean":5,"spanish":2},
 "PEU_2289":{"amazonian":80,"quechua":10,"mestizo":10},
 "PEU_2291":{"quechua":45,"mestizo":33,"criollo":15,"AfroCaribbean":5,"spanish":2},
 "PEU_2300":{"quechua":30,"criollo":30,"mestizo":25,"AfroCaribbean":10,"spanish":5},
 "PEU_2297":{"quechua":72,"mestizo":18,"criollo":8,"spanish":2},
 "PEU_2303":{"aymara":40,"quechua":35,"mestizo":17,"criollo":7,"spanish":1},
 # Upper Peru
 "BOL_2321":{"aymara":50,"quechua":30,"mestizo":13,"criollo":6,"spanish":1},
 "BOL_2305":{"quechua":45,"aymara":30,"mestizo":15,"criollo":9,"spanish":1},
 "BOL_2317":{"mestizo":35,"guarani":25,"amazonian":20,"criollo":18,"spanish":2},
 "BOL_2309":{"aymara":55,"quechua":20,"mestizo":18,"criollo":7},
 # Brazil
 "BRZ_2401":{"amazonian":80,"tupi":10,"brasileiro":6,"AfroBrazilian":4},
 "BRZ_2408":{"amazonian":45,"tupi":20,"AfroBrazilian":18,"brasileiro":15,"portuguese":2},
 "BRZ_2410":{"AfroBrazilian":35,"brasileiro":30,"je":20,"tupi":12,"portuguese":3},
 "BRZ_2428":{"AfroBrazilian":50,"brasileiro":33,"tupi":8,"je":6,"portuguese":3},
 "BRZ_2439":{"AfroBrazilian":52,"brasileiro":32,"je":8,"tupi":5,"portuguese":3},
 "BRZ_2421":{"je":45,"brasileiro":22,"AfroBrazilian":18,"amazonian":15},
 "BRZ_2416":{"amazonian":40,"guaycuru":20,"je":15,"brasileiro":15,"AfroBrazilian":10},
 "BRZ_2446":{"AfroBrazilian":48,"brasileiro":38,"je":7,"portuguese":7},
 "BRZ_2447":{"AfroBrazilian":45,"brasileiro":38,"portuguese":14,"tupi":3},
 "BRZ_2306":{"brasileiro":50,"AfroBrazilian":28,"tupi":12,"portuguese":10},
 "BRZ_2462":{"brasileiro":45,"je":20,"AfroBrazilian":18,"tupi":10,"portuguese":7},
 "BRZ_2461":{"brasileiro":52,"AfroBrazilian":20,"je":16,"portuguese":12},
 "BRZ_2467":{"brasileiro":55,"AfroBrazilian":20,"guarani":12,"portuguese":8,"tehuelche":5},
 # Rio de la Plata
 "PRG_2343":{"guarani":55,"mestizo":30,"criollo":13,"spanish":2},
 "PRG_2338":{"guaycuru":70,"guarani":20,"mestizo":10},
 "ARG_2368":{"quechua":35,"mestizo":35,"criollo":20,"aymara":8,"spanish":2},
 "ARG_2377":{"guaycuru":60,"guarani":20,"mestizo":20},
 "ARG_2387":{"mestizo":50,"criollo":25,"quechua":20,"spanish":5},
 "ARG_2374":{"mestizo":50,"criollo":30,"quechua":15,"spanish":5},
 "ARG_2360":{"mestizo":40,"criollo":30,"guarani":25,"AfroCaribbean":5},
 "ARG_2363":{"mestizo":40,"criollo":40,"AfroCaribbean":10,"guarani":10},
 "ARG_2384":{"mestizo":45,"criollo":40,"AfroCaribbean":8,"spanish":7},
 "ARG_2393":{"mestizo":45,"criollo":35,"mapuche":15,"spanish":5},
 "ARG_2355":{"criollo":45,"mestizo":25,"AfroCaribbean":20,"spanish":8,"tehuelche":2},
 "ARG_2391":{"tehuelche":50,"mapuche":45,"criollo":5},
 "ARG_2398":{"tehuelche":75,"mapuche":20,"british":5},
 "URU_2344":{"criollo":45,"mestizo":28,"AfroCaribbean":20,"spanish":7},
 # Chile
 "CHL_2322":{"mestizo":50,"criollo":35,"spanish":8,"mapuche":7},
 "CHL_2327":{"mapuche":50,"mestizo":32,"criollo":15,"spanish":3},
 "CHL_2332":{"mapuche":45,"tehuelche":35,"criollo":12,"polynesian":8},
}

# province overrides where a region holds more than one world
PROV = {}
for p, v in SA.items():
    if v["n"] == "Easter Island":   PROV[p] = {"polynesian":95,"criollo":5}
    if v["n"] == "Galapagos":       PROV[p] = {"criollo":60,"mestizo":40}
    if v["n"] == "Falkland Islands":PROV[p] = {"british":80,"criollo":20}
    if v["n"] == "Lima":            PROV[p] = {"criollo":38,"mestizo":22,"quechua":18,"AfroCaribbean":14,"spanish":8}
    if v["n"] == "Buenos Aires":    PROV[p] = {"criollo":46,"mestizo":20,"AfroCaribbean":22,"spanish":12}
    if v["n"] == "Rio de Janeiro":  PROV[p] = {"AfroBrazilian":44,"brasileiro":36,"portuguese":18,"tupi":2}
    if v["n"] == "Salvador de Bahia":PROV[p]= {"AfroBrazilian":56,"brasileiro":30,"portuguese":12,"je":2}
    if v["n"] == "Potosi":          PROV[p] = {"quechua":50,"aymara":28,"mestizo":13,"criollo":7,"spanish":2}
    if v["n"] == "Asuncion":        PROV[p] = {"guarani":48,"mestizo":30,"criollo":18,"spanish":4}

# settler weight per region, in thousands, 1800
F1800 = {"BRZ_2447":180,"BRZ_2446":490,"BRZ_2306":160,"BRZ_2439":360,"BRZ_2428":320,
 "BRZ_2410":220,"BRZ_2408":90,"BRZ_2401":40,"BRZ_2421":60,"BRZ_2416":40,"BRZ_2462":40,
 "BRZ_2461":35,"BRZ_2467":70,"ARG_2355":90,"ARG_2384":60,"ARG_2387":50,"ARG_2374":45,
 "ARG_2363":30,"ARG_2360":40,"ARG_2368":55,"ARG_2377":10,"ARG_2393":20,"ARG_2391":3,
 "ARG_2398":1,"URU_2344":35,"PRG_2343":90,"PRG_2338":5,"CHL_2322":420,"CHL_2327":240,
 "CHL_2332":20,"PEU_2300":200,"PEU_2297":160,"PEU_2291":180,"PEU_2303":120,"PEU_2289":15,
 "BOL_2321":240,"BOL_2305":280,"BOL_2317":60,"BOL_2309":30,"ECU_2279":360,"CLM_2247":260,
 "CLM_2251":220,"CLM_2259":180,"CLM_2262":20,"VNZ_2265":320,"VNZ_2234":180,"VNZ_2278":30,
 "ENG_1979":230,"ENG_2228":20}
SETTLER = {"spanish","portuguese","criollo","mestizo","brasileiro","AfroBrazilian",
           "AfroCaribbean","british","dutch","french"}

hpm_pop = collections.Counter()
for pid, t, c, r, sz in L["pops"]:
    if pid in SA: hpm_pop[pid] += sz

claims = {}
for p, v in SA.items():
    w = PROV.get(p) or R.get(v["rg"])
    if w: claims[p] = dict(w)
missing = [SA[p]["n"] for p in SA if p not in claims]
print("  provinces with no assignment      ", len(missing), missing[:6])

share = collections.defaultdict(dict)
for p, w in claims.items():
    rg = SA[p]["rg"]
    for cu, k in w.items():
        if cu in SETTLER and rg in F1800:
            rtot = sum(hpm_pop[q] for q in SA if SA[q]["rg"] == rg) or 1
            base = F1800[rg] * 1000 * hpm_pop[p] / rtot
        elif C[cu][0] == "andean":
            base = max(hpm_pop[p], 1)
        else:
            base = SA[p]["px"]
        share[cu][p] = k * max(base, 1)

prov_total = collections.Counter()
for cu, ps in share.items():
    tgt = C[cu][3] * SCALE; tot = sum(ps.values())
    for q, wv in ps.items(): prov_total[q] += tgt * wv / tot
cells = {}
for q, w in claims.items():
    tw = sum(w.values()) or 1
    for cu, k in w.items(): cells[(q, cu)] = prov_total[q] * k / tw
col_t = {cu: C[cu][3]*SCALE for cu in C if any(c == cu for _, c in cells)}
row_t = dict(prov_total)
for _ in range(60):
    cs = collections.Counter()
    for (q, cu), v in cells.items(): cs[cu] += v
    for key in cells: cells[key] *= (col_t.get(key[1],0)/cs[key[1]]) if cs[key[1]] else 0
    rs = collections.Counter()
    for (q, cu), v in cells.items(): rs[q] += v
    for key in cells: cells[key] *= (row_t[key[0]]/rs[key[0]]) if rs[key[0]] else 0
err = max(abs(sum(v for (q,cu),v in cells.items() if cu==c)-col_t[c])/max(col_t[c],1) for c in col_t)
print(f"  IPF worst culture-total error      {err*100:.2f}%")

out, summary = [], collections.Counter()
by = collections.defaultdict(dict)
for (q, cu), v in cells.items():
    if v >= 10: by[q][cu] = v
for q, mix in by.items():
    for cu, v in mix.items():
        grp, rel, arch, real = C[cu]
        n = int(round(v))
        if n < 10: continue
        rows = [(ty, n*fr) for ty, fr in ARCH[arch].items()]
        placed = 0
        for i, (ty, raw) in enumerate(rows):
            sz = int(round(raw)) if i < len(rows)-1 else n-placed
            placed += sz
            if sz < 5: continue
            out.append({"province": q, "type": ty, "culture": cu, "religion": rel, "size": sz})
            summary[cu] += sz
have = {r["province"] for r in out}
for p, w in claims.items():
    if p in have or not w: continue
    cu = max(w, key=lambda c: w[c]); grp, rel, arch, real = C[cu]
    ty = max(ARCH[arch], key=lambda t: ARCH[arch][t])
    out.append({"province": p, "type": ty, "culture": cu, "religion": rel, "size": 20})
    summary[cu] += 20
print(f"  pop entries                        {len(out)}")
print(f"  provinces covered                  {len({r['province'] for r in out})} of {len(SA)}")
print(f"  South America 1800 total           {sum(summary.values()):,}  (HPM 1836 was 4,664,187)")
print("\n  by culture:")
for cu, v in summary.most_common(): print(f"    {cu:<16}{v:>10,}  {C[cu][1]}")
json.dump({"pops": out, "culture_groups": {c: C[c][0] for c in C}}, open(f"{W}/sa1800.json","w"))
