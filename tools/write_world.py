"""Compile the World Builder data into Victoria II files inside build/HPM.

Everything is written as cp1252 with LF endings, matching HPM. Nothing is appended
blindly: existing blocks are rewritten in place so the files stay diffable.
"""
import json, os, re, glob, collections, shutil

W, MOD = "/home/claude/work", "/home/claude/build/HPM"
BASE = json.load(open(f"{W}/world_data.json"))
LAYER = json.load(open("/mnt/user-data/outputs/HPM_NA_1800_cultures_pops.json"))
PROVVARS = {int(k): v for k, v in LAYER.get("province_vars", {}).items()}
CC = LAYER.get("country_cultures", {})
START = "1800.1.1"

def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="cp1252", errors="replace", newline="\n") as f:
        f.write(text)

def r(path):
    return open(path, encoding="cp1252", errors="replace").read()

log = collections.Counter()

# ------------------------------------------------------------------ 1. cultures
GROUPS_NEW = {"mesoamerican": ("nativeamerican", "no"), "aridoamerican": ("nativeamerican", "no"),
              "eastern_woodlands": ("nativeamerican", "no"), "plains_nations": ("nativeamerican", "no"),
              "plateau_northwest": ("nativeamerican", "no"), "arctic_nations": ("nativeamerican", "no"),
              "circumcaribbean": ("nativeamerican", "no")}

NAMES = json.load(open(f"{W}/culture_names.json"))

def culture_block(name, colour, first, last, indent="\t\t"):
    i, i2 = indent, indent + "\t"
    return (f"{i}{name} = {{\n"
            f"{i2}color = {{ {colour[0]} {colour[1]} {colour[2]} }}\n"
            f"{i2}first_names = {{ {' '.join(first)} }}\n"
            f"{i2}last_names = {{ {' '.join(last)} }}\n"
            f"{i}}}\n")

def build_cultures():
    src = r(f"{MOD}/common/cultures.txt")
    want = LAYER["culture_groups"]                       # culture -> group
    # cultures.txt is 4-space indented, so counting whitespace is not a reliable
    # test for "is this a culture or a nested key". Walk the braces instead.
    have, depth = set(), 0
    for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}", src):
        t = m.group(0)
        if t == "}": depth -= 1
        elif t == "{": depth += 1
        else:
            if depth == 1 and m.group(1) not in ("color","leader","unit","union","is_overseas"):
                have.add(m.group(1))
            depth += 1
    # map our display names to engine-safe keys
    keyed = {c: re.sub(r"(?<!^)(?=[A-Z])", "_", c).lower().replace("__", "_") for c in want}
    bygroup = collections.defaultdict(list)
    for c, g in want.items():
        if keyed[c] not in have:
            bygroup[g].append(c)
    out = src.rstrip() + "\n"
    added = 0
    for g, members in sorted(bygroup.items()):
        blocks = ""
        for c in sorted(members):
            n = NAMES.get(c, NAMES["_fallback"])
            blocks += culture_block(keyed[c], n["color"], n["first"], n["last"])
            added += 1
        if re.search(rf"^{g}\s*=\s*\{{", out, re.M):
            # insert before the group's closing brace
            m = re.search(rf"^{g}\s*=\s*\{{", out, re.M)
            i, depth = m.end(), 1
            while i < len(out) and depth:
                if out[i] == "{": depth += 1
                elif out[i] == "}": depth -= 1
                i += 1
            out = out[:i-1] + blocks + out[i-1:]
        else:
            leader, overseas = GROUPS_NEW.get(g, ("european", "no"))
            out += (f"\n{g} = {{\n\tleader = {leader}\n\tis_overseas = {overseas}\n"
                    f"\tunit = NativeGC\n{blocks}}}\n")
    w(f"{MOD}/common/cultures.txt", out)
    log["cultures added"] = added
    return keyed

KEY = build_cultures()
def ck(c): return KEY.get(c, c.lower())

# ------------------------------------------------------- 2. colonial country tags
reg = r(f"{MOD}/common/countries.txt")
new_tag_lines = []
for tag, cfg in CC.items():
    if not cfg.get("create"):
        continue
    nm = cfg["create"]["name"]
    # prefix with the tag: the colonial "Puerto Rico" collided with HPM's own PRI file
    # and silently replaced it, then took it with them when the unused tags were pruned
    fn = tag + " " + re.sub(r"[^A-Za-z0-9 ]", "", nm)
    path = f"countries/{fn}.txt"
    if re.search(rf"^\s*{tag}\s*=", reg, re.M):
        continue
    col = cfg["create"]["color"]
    w(f"{MOD}/common/{path}",
      f"color = {{ {col[0]} {col[1]} {col[2]} }}\n"
      "graphical_culture = SpanishGC\n\n"
      "party = {\n"
      f'\tname = "{tag}_conservative"\n'
      "\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n"
      "\tideology = conservative\n"
      "\tsocial_policy = pro_regulation\n\teconomic_policy = state_capitalism\n"
      "\ttrade_policy = protectionism\n\treligious_policy = moralism\n"
      "\tcitizenship_policy = residency\n\twar_policy = jingoism\n"
      "}\n\n"
      "party = {\n"
      f'\tname = "{tag}_liberal"\n'
      "\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n"
      "\tideology = liberal\n"
      "\tsocial_policy = pro_regulation\n\teconomic_policy = laissez_faire\n"
      "\ttrade_policy = free_trade\n\treligious_policy = pluralism\n"
      "\tcitizenship_policy = limited_citizenship\n\twar_policy = anti_military\n"
      "}\n\n"
      "unit_names = {\n}\n")
    new_tag_lines.append(f'{tag} = "{path}"\n')
    log["colonial country files"] += 1
if new_tag_lines:
    w(f"{MOD}/common/countries.txt", reg.rstrip() + "\n\n# 1800 colonial administrations\n" + "".join(new_tag_lines))

# ----------------------------------------------- 3. history/countries for new tags
for tag, cfg in CC.items():
    if not cfg.get("create"):
        continue
    nm = cfg["create"]["name"]
    fn = re.sub(r"[^A-Za-z0-9 ]", "", nm)
    acc = "".join(f"culture = {ck(c)}\n" for c in cfg.get("accepted", []))
    cap = {"NSP": 2172, "CGG": 2186, "VNG": 2244, "CGV": 2254, "QIT": 2279,
           "VPE": 2300, "CHQ": 2320, "VRP": 2348, "CGC": 2360, "CBA": 2209,
           "PTR": 2222, "EBR": 2447}.get(tag, 1)
    w(f"{MOD}/history/countries/{tag} - {re.sub(r"[^A-Za-z0-9 ]", "", nm)}.txt",
      f"capital = {cap}\n"
      f"primary_culture = {ck(cfg['primary'])}\n"
      f"{acc}"
      "religion = catholic\n"
      "government = absolute_monarchy\n"
      "plurality = 0.0\n"
      "nationalvalue = nv_order\n"
      "literacy = 0.05\n"
      "non_state_culture_literacy = 0.01\n"
      "civilized = yes\n"
      "prestige = 0\n\n"
      "# Political reforms\n"
      "slavery = yes_slavery\n"
      "upper_house_composition = appointed\n"
      "vote_franschise = none_voting\n"
      "public_meetings = no_meeting\n"
      "press_rights = state_press\n"
      "trade_unions = no_trade_unions\n"
      "voting_system = first_past_the_post\n"
      "political_parties = underground_parties\n"
      "conscription = no_draft\n"
      "debt_law = peonage\n"
      "penal_system = capital_punishment\n"
      "citizens_rights = primary_culture_only\n"
      "border_policy = closed_borders\n\n"
      "# Social reforms\n"
      "wage_reform = no_minimum_wage\n"
      "work_hours = no_work_hour_limit\n"
      "safety_regulations = no_safety\n"
      "health_care = no_health_care\n"
      "unemployment_subsidies = no_subsidies\n"
      "pensions = no_pensions\n"
      "school_reforms = no_schools\n"
      "child_labor = no_regulations\n\n"
      f'ruling_party = {tag}_conservative\n'
      "last_election = 1795.1.1\n"
      "upper_house = {\n\tfascist = 0\n\tliberal = 10\n\tconservative = 80\n"
      "\treactionary = 10\n\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n\n"
      "# Starting technology\n"
      "flintlock_rifles = 1\n"
      "post_nelsonian_thought = 1\n"
      "guild_based_production = 1\n")
    log["colonial history files"] += 1

# ------------------------------------------- 4. primary / accepted on existing tags
for tag, cfg in CC.items():
    if cfg.get("create"):
        continue
    hits = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not hits:
        log["country file missing"] += 1
        continue
    s = r(hits[0])
    s = re.sub(r"^\s*primary_culture\s*=\s*[A-Za-z_0-9]+\s*$",
               f"primary_culture = {ck(cfg['primary'])}", s, count=1, flags=re.M)
    s = re.sub(r"^\s*culture\s*=\s*[A-Za-z_0-9]+\s*\n", "", s, flags=re.M)
    acc = "".join(f"culture = {ck(c)}\n" for c in cfg.get("accepted", []))
    s = re.sub(r"(^primary_culture\s*=.*\n)", r"\1" + acc, s, count=1, flags=re.M)
    w(hits[0], s)
    log["country cultures rewritten"] += 1

# --------------------------------------------------------- 5. province histories
PROV = {int(k): v for k, v in BASE["prov"].items()}
files = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    m = re.match(r"(\d+)", os.path.basename(f))
    if m: files[int(m.group(1))] = f
for pid, v in PROVVARS.items():
    f = files.get(pid)
    if not f:
        log["province file missing"] += 1
        continue
    s = r(f)
    for key, val in v.items():
        if re.search(rf"^\s*{key}\s*=.*$", s, re.M):
            if val in (0, "0") and key in ("railroad", "fort", "naval_base"):
                s = re.sub(rf"^\s*{key}\s*=.*\n", "", s, flags=re.M)
            else:
                s = re.sub(rf"^\s*{key}\s*=.*$", f"{key} = {val}", s, count=1, flags=re.M)
        elif not (val in (0, "0")):
            s = s.rstrip() + f"\n{key} = {val}\n"
    w(f, s)
    log["province files rewritten"] += 1

# ------------------------------------------------------------------- 6. pops
pops = collections.defaultdict(lambda: collections.defaultdict(list))
owner_of = {}
for pid, v in PROV.items():
    owner_of[pid] = v["o"] or "XXX"
layer_prov = set(int(p["province"]) for p in LAYER["pops"])
# keep every pop outside the layer's reach, replace the rest
old = collections.defaultdict(list)
for pid, t, c, rl, sz in BASE["pops"]:
    if pid in layer_prov: continue
    old[pid].append((BASE["pop_types"][t], BASE["cultures"][c], BASE["religions"][rl], sz))
new = collections.defaultdict(list)
for p in LAYER["pops"]:
    new[int(p["province"])].append((p["type"], ck(p["culture"]), p["religion"], p["size"]))

bucket = collections.defaultdict(dict)       # file stem -> {pid: [rows]}
def stem(pid):
    f = files.get(pid)
    return os.path.basename(os.path.dirname(f)) if f else "misc"
for src in (old, new):
    for pid, rows in src.items():
        bucket[stem(pid)].setdefault(pid, []).extend(rows)

outdir = f"{MOD}/history/pops/{START}"
if os.path.isdir(f"{MOD}/history/pops/1836.1.1"):
    shutil.rmtree(f"{MOD}/history/pops/1836.1.1")
if os.path.isdir(outdir):
    shutil.rmtree(outdir)
for name, provs in bucket.items():
    txt = ""
    for pid in sorted(provs):
        rows = [x for x in provs[pid] if x[3] > 0]
        if not rows: continue
        txt += f"{pid} = {{\n"
        for ty, cu, rl, sz in rows:
            txt += (f"\t{ty} = {{\n\t\tculture = {cu}\n\t\treligion = {rl}\n"
                    f"\t\tsize = {sz}\n\t}}\n")
        txt += "}\n\n"
    if txt:
        w(f"{outdir}/{name}.txt", txt)
        log["pop files"] += 1
log["pop provinces"] = len(set(list(old) + list(new)))

# ------------------------------------------------------- 7. start date & bookmark
d = r(f"{MOD}/common/defines.lua")
d = re.sub(r"start_date\s*=\s*'[\d.]+'", f"start_date = '{START}'", d)
w(f"{MOD}/common/defines.lua", d)
w(f"{MOD}/common/bookmarks.txt",
  'bookmark =\n{\n\tname = "GC_NAME"\n\tdesc = "GC_DESC"\n'
  f"\tdate = {START}\n\tcameraX = 1600\n\tcameraY = 1100\n}}\n")
log["start date"] = START

# ------------------------------------------------------------ 8. localisation
DISPLAY = {"french_creole":"Louisiana Creole","mandan_arikara":"Mandan-Arikara",
 "nez_perce":"Nez Perce","taino_remnant":"Taino","california_nations":"California Nations",
 "anglo_canadian":"Anglo-Canadian","french_canadian":"French Canadian",
 "afro_american":"African American","afro_caribbean":"Afro-Caribbean",
 "haudenosaunee":"Haudenosaunee","purepecha":"Purepecha","piman":"O'odham",
 "dene":"Dene","algonquian":"Algonquian","criollo":"Criollo","mestizo":"Mestizo"}
ADJ = {"NSP":"New Spanish","CGG":"Guatemalan","VNG":"New Granadan","CGV":"Venezuelan",
 "QIT":"Quiteno","VPE":"Peruvian","CHQ":"Charcan","VRP":"Platine","CGC":"Chilean",
 "CBA":"Cuban","PTR":"Puerto Rican","EBR":"Brazilian"}
rows = ["Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x"]
for c in sorted(LAYER["culture_groups"]):
    k = ck(c)
    nice = DISPLAY.get(k) or k.replace("_", " ").title()
    rows.append(f"{k};{nice};;;;;;;;;;;;;x")
for g in sorted(set(LAYER["culture_groups"].values())):
    rows.append(f"{g};{g.replace('_',' ').title()};;;;;;;;;;;;;x")
for tag, cfg in CC.items():
    if not cfg.get("create"): continue
    rows.append(f"{tag};{cfg['create']['name']};;;;;;;;;;;;;x")
    rows.append(f"{tag}_ADJ;{ADJ.get(tag,cfg['create']['name'])};;;;;;;;;;;;;x")
    rows.append(f"{tag}_conservative;Partido Realista;;;;;;;;;;;;;x")
    rows.append(f"{tag}_liberal;Partido Patriota;;;;;;;;;;;;;x")
w(f"{MOD}/localisation/04_1800_cultures_and_colonies.csv", "\n".join(rows) + "\n")
log["localisation rows"] = len(rows) - 1

for k, v in log.items():
    print(f"  {k:<32}{v}")
