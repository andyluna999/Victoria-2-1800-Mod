"""Africa, Asia and Oceania on 1 January 1800.

The 1836 map encodes thirty-six years of things that have not happened. Muhammad Ali
holds Syria, Palestine and Crete — he will not take power in Cairo until 1805 and not
invade Syria until 1831, and in 1800 Egypt itself is under French occupation. Sokoto
will not be founded until 1804. Shaka will not build the Zulu kingdom until after 1816.
Perth, Adelaide, Melbourne and Brisbane are all founded in the 1830s. And the East
India Company holds the Doab, which it takes from Sindhia in 1803.
"""
import json, re, glob, os, collections

MOD = "/home/claude/build/HPM"; W = "/home/claude/work"
L = json.load(open(f"{W}/world_live.json"))
NAME = {int(k): v["n"] for k, v in L["prov"].items()}
log = collections.Counter()

def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# ------------------------------------------------------------------ new tags
NEW = {
 "MAR": ("Maratha Confederacy", [122, 60, 40], 1240, "marathi", "hindu"),
 "HAU": ("Hausa States",        [190, 150, 60], 1945, "hausa",        "sunni"),
}
reg = rd(f"{MOD}/common/countries.txt")
for tag, (nm, col, cap, cult, rel) in NEW.items():
    if re.search(rf"^\s*{tag}\s*=", reg, re.M): continue
    path = f"countries/{tag} {re.sub(r'[^A-Za-z0-9 ]','',nm)}.txt"
    wr(f"{MOD}/common/{path}",
       f"color = {{ {col[0]} {col[1]} {col[2]} }}\ngraphical_culture = IndianGC\n\n"
       "party = {\n" f'\tname = "{tag}_conservative"\n' "\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n"
       "\tideology = conservative\n\tsocial_policy = pro_regulation\n\teconomic_policy = state_capitalism\n"
       "\ttrade_policy = protectionism\n\treligious_policy = moralism\n"
       "\tcitizenship_policy = residency\n\twar_policy = jingoism\n}\n\n"
       "party = {\n" f'\tname = "{tag}_reactionary"\n' "\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n"
       "\tideology = reactionary\n\tsocial_policy = pro_regulation\n\teconomic_policy = state_capitalism\n"
       "\ttrade_policy = protectionism\n\treligious_policy = moralism\n"
       "\tcitizenship_policy = residency\n\twar_policy = pro_military\n}\n\nunit_names = {\n}\n")
    reg = reg.rstrip() + f'\n{tag} = "{path}"\n'
    log["new tags"] += 1
wr(f"{MOD}/common/countries.txt", reg)

for tag, (nm, col, cap, cult, rel) in NEW.items():
    fn = re.sub(r"[^A-Za-z0-9 ]", "", nm)
    for old in glob.glob(f"{MOD}/history/countries/{tag} - *.txt"): os.remove(old)
    wr(f"{MOD}/history/countries/{tag} - {fn}.txt",
       f"capital = {cap}\nprimary_culture = {cult}\nreligion = {rel}\n"
       "government = absolute_monarchy\nplurality = 0.0\nnationalvalue = nv_order\n"
       "literacy = 0.02\nnon_state_culture_literacy = 0.01\ncivilized = no\nprestige = 0\n\n"
       "slavery = yes_slavery\nupper_house_composition = appointed\nvote_franschise = none_voting\n"
       "public_meetings = no_meeting\npress_rights = state_press\ntrade_unions = no_trade_unions\n"
       "voting_system = first_past_the_post\npolitical_parties = underground_parties\n"
       "conscription = no_draft\ndebt_law = peonage\npenal_system = capital_punishment\n"
       "citizens_rights = primary_culture_only\nborder_policy = closed_borders\n\n"
       "wage_reform = no_minimum_wage\nwork_hours = no_work_hour_limit\nsafety_regulations = no_safety\n"
       "health_care = no_health_care\nunemployment_subsidies = no_subsidies\npensions = no_pensions\n"
       "school_reforms = no_schools\nchild_labor = no_regulations\n\n"
       f"ruling_party = {tag}_conservative\nlast_election = 1795.1.1\n"
       "upper_house = {\n\tfascist = 0\n\tliberal = 0\n\tconservative = 70\n\treactionary = 30\n"
       "\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n")
    log["new country histories"] += 1

from PIL import Image
for tag, (nm, col, cap, cult, rel) in NEW.items():
    for sfx in ("", "_communist", "_fascist", "_monarchy", "_republic"):
        fp = f"{MOD}/gfx/flags/{tag}{sfx}.tga"
        if os.path.exists(fp): continue
        im = Image.new("RGB", (93, 64), tuple(col))
        for y in range(64):
            for x in range(93):
                if x < 3 or x > 89 or y < 3 or y > 60: im.putpixel((x, y), (255, 255, 255))
        im.save(fp); log["flags"] += 1

# ------------------------------------------------------------------ ownership
OWN, CORES = {}, collections.defaultdict(list)
def give(tag, *ids):
    for i in ids: OWN[i] = tag
def core(tag, *ids):
    for i in ids: CORES[i].append(tag)

# Egypt: a French army sits on the Nile, and Syria is the Sultan's
# Desaix took Upper Egypt as far as Aswan in 1799; the army holds the whole valley
NILE   = [1745,1746,1747,1748,1749,1750,1751,1752,1753,1754,1755,1756,1757,1758,
          1759,1760,1761,1762,1763,1764,1765,1766,1767,1768,1769,1770,1771,1772,2559]
# the Funj sultanate at Sennar is still independent and will be until 1821
SUDAN  = [1827,1828,1829,1830,1831,1833,1834,1835,1836,1837,1838,1840,1806,1874]
LEVANT = [894,896,897,898,900,902,903,904,905,908,909,912,913,914,915,916,917,918,
          919,920,921,922,847,848,1849]
give("FRA", *[p for p in NILE if p in NAME])
give("TUR", *[p for p in LEVANT if p in NAME])
for p in NILE:
    if p in NAME: core("EGY", p); core("TUR", p)
for p in LEVANT:
    if p in NAME: core("TUR", p)
for p in SUDAN:
    if p in NAME: OWN[p] = ""; core("EGY", p)

# Sokoto is four years in the future; this is Hausaland
HAUSA = [1927,1937,1938,1939,1940,1941,1942,1943,1944,1945,1946,1947,1948,1949,1950]
give("HAU", *[p for p in HAUSA if p in NAME])
for p in HAUSA:
    if p in NAME: core("HAU", p); core("SOK", p)

# there is no Zulu kingdom until Shaka
for p in (2111, 2112, 2113):
    if p in NAME: OWN[p] = ""; core("ZUL", p)

# Australia is one penal colony and its hinterland. Norfolk Island was settled in
# March 1788, six weeks after Sydney, and is kept with them.
AUS_KEEP = {2468, 2469, 2470, 2508}
# Read the owner from the province file, not from world_live.json. That file is
# regenerated after the build, so testing it made this pass unown Norfolk Island on
# every second run and restore it on every other -- two builds of the same input
# producing different output.
for p, v in L["prov"].items():
    pid = int(p)
    if v["ct"] != "australia_new_zealand" or pid in AUS_KEEP: continue
    g = glob.glob(f"{MOD}/history/provinces/*/{pid} - *.txt")
    if not g: continue
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(g[0]))[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    if m and m.group(1) == "ENG":
        OWN[pid] = ""; core("AST", pid)

# India: the Company holds its three presidencies, not the subcontinent.
# Sindhia holds Delhi and the Doab until Assaye in 1803; the Bhonsles hold Orissa;
# the Gaekwads Gujarat. The Peshwa at Pune is nominal head of all of them.
MARATHA = [1235,1237,1238,1239,1240,1261,1275,1276,1282,1291]
give("MAR", *[p for p in MARATHA if p in NAME])
for p in MARATHA:
    if p in NAME: core("MAR", p)
core("MAR", 1298)

prov = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    prov[int(re.match(r"(\d+)", os.path.basename(f)).group(1))] = f

changed = 0
for pid, f in prov.items():
    if pid not in OWN and pid not in CORES: continue
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    if pid in OWN:
        head = re.sub(r"^\s*owner\s*=.*\n", "", head, flags=re.M)
        head = re.sub(r"^\s*controller\s*=.*\n", "", head, flags=re.M)
        if OWN[pid]:
            head = f"owner = {OWN[pid]}\ncontroller = {OWN[pid]}\n" + head.lstrip("\n")
    for t in CORES.get(pid, []):
        if not re.search(rf"^\s*add_core\s*=\s*{t}\s*$", head, re.M):
            head = head.rstrip("\n") + f"\nadd_core = {t}\n"
    wr(f, head.rstrip("\n") + "\n" + tail); changed += 1
log["province files rewritten"] = changed
log["provinces reassigned"] = len([p for p in OWN])

# the Maratha houses answer to the Peshwa
# The Confederacy is destroyed in the Third Anglo-Maratha War, so these end in 1818
# rather than running to 1936 and colliding with HPM's British vassalage of the same
# houses. The houses survive as princely states; the Peshwa does not.
DIP = [("vassal", "MAR", t, n) for t, n in
       (("GWA", "Gwalior"), ("IND", "Indore"), ("NAG", "Nagpur"), ("BER", "Baroda"))]
wr(f"{MOD}/history/diplomacy/1800_asia.txt",
   "\n".join(f"# {a} - {n}\n{k} = {{\n\tfirst = {a}\n\tsecond = {b}\n"
             f"\tstart_date = 1800.1.1\n\tend_date = 1818.1.1\n}}\n"
             for k, a, b, n in DIP))
log["maratha vassals"] = len(DIP)

rows = ["Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x"]
for tag, (nm, col, cap, cult, rel) in NEW.items():
    rows += [f"{tag};{nm};;;;;;;;;;;;;x", f"{tag}_ADJ;{nm.split()[0]};;;;;;;;;;;;;x",
             f"{tag}_conservative;Council of Elders;;;;;;;;;;;;;x",
             f"{tag}_reactionary;The Old Families;;;;;;;;;;;;;x"]
wr(f"{MOD}/localisation/11_world_1800.csv", "\n".join(rows) + "\n")

for k, v in log.items(): print(f"  {k:<32}{v}")
