"""Compile a World Builder export into build/HPM: ownership, cores, countries, pops.

Runs after write_world.py. The export is the source of truth for everything it
carries; write_world.py's own colonial tags are dropped if the map does not use them.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, os, re, glob, collections, shutil
from PIL import Image

MOD = _BUILD
EXP = json.load(open(f"{_WORK}/export_split.json"))
BASE = json.load(open(f"{_WORK}/world_data.json"))
START = "1800.1.1"
P, C, POPS = EXP["provinces"], EXP["countries"], EXP["pops"]
log = collections.Counter()

def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="cp1252", errors="replace", newline="\n").write(text)
def r(path): return open(path, encoding="cp1252", errors="replace").read()
def ck(c): return re.sub(r"(?<!^)(?=[A-Z])", "_", c).lower().replace("__", "_")
known_base = set(BASE["countries"])

# --------------------------------------------- drop colonial tags the map never used
UNUSED = [t for t in ("NSP","CGG","VNG","CGV","QIT","VPE","CHQ","VRP","CGC","CBA","PTR","EBR")
          if t not in C and not any(v["owner"] == t for v in P.values())]
reg = r(f"{MOD}/common/countries.txt")
for t in UNUSED:
    m = re.search(rf'^\s*{t}\s*=\s*"?([^"\n]+?)"?\s*$', reg, re.M)
    if m:
        f = os.path.join(MOD, "common", m.group(1).strip())
        if os.path.exists(f): os.remove(f)
        reg = re.sub(rf'^\s*{t}\s*=.*\n', "", reg, flags=re.M)
    for h in glob.glob(f"{MOD}/history/countries/{t} - *.txt"): os.remove(h)
w(f"{MOD}/common/countries.txt", reg)
log["unused colonial tags removed"] = len(UNUSED)

# ------------------------------------------- primary cultures for the new nations only
# The export only carries an explicit primary for the handful of countries the layer
# configured; the other 500 are blank because the field postdates the saved state.
# Blank means "unchanged", NOT "infer one" -- guessing there would overwrite 475 correct
# HPM values. And for the new nations, matching the name beats counting pops: inference
# made Apache into Navajo and the Anishinaabe Confederation into Anglo-Canadians.
BY_NAME = {
 "Shoshone-Bannock Confederation":"shoshone", "Anishinaabe Confederation":"anishinaabe",
 "Apache":"apache", "Arikara-Mandan-Hidatsa":"MandanArikara",
 "Blackfoot Confederacy":"blackfoot", "Choctaw":"choctaw", "Creek Confederacy":"creek",
 "Chickasaw":"chickasaw", "Coast Salish":"salish", "Chinook":"chinook",
 "Comanche Nation":"comanche", "Cherokee Nation":"cherokee", "Crow Nation":"crow",
 "Iroquois":"haudenosaunee", "Mapuche":"patagonian", "Navajo":"navajo",
 "Nez Perce":"NezPerce", "Osage Nation":"osage", "Pawnee Confederacy":"pawnee",
 "Viceroyalty of Rio de la Plata":"criollo", "Salish Confederation":"salish",
 "Seminole Nation":"seminole", "Sioux Nation":"sioux", "Tlingit":"tlingit",
 "Yupik":"yupik",
}
agg = collections.defaultdict(collections.Counter)
for p in POPS:
    o = P.get(str(p["province"]), {}).get("owner")
    if o: agg[o][p["culture"]] += p["size"]
inferred, guessed = {}, []
for tag, c in C.items():
    if c.get("primary_culture") or tag in known_base: continue
    nm = c["name"]
    if nm in BY_NAME:
        inferred[tag] = BY_NAME[nm]
    elif agg.get(tag):
        inferred[tag] = agg[tag].most_common(1)[0][0]; guessed.append(f"{tag}({nm})")
log["primaries from the nation's name"] = len([t for t in inferred if C[t]["name"] in BY_NAME])
log["primaries guessed from pops"] = len(guessed)

# ------------------------------------------------------- new tags: definitions + flags
new = [t for t in C if t not in known_base]
PAL = {}
for tag in new:
    c = C[tag]
    nm = re.sub(r"[^A-Za-z0-9 ]", "", c["name"])
    # an earlier stage may have written this tag under a different name; two history
    # files for one tag is undefined behaviour, so clear any stragglers first
    for old in glob.glob(f"{MOD}/history/countries/{tag} - *.txt") + \
               glob.glob(f"{MOD}/common/countries/{tag} *.txt"):
        os.remove(old); log["stale duplicate files removed"] += 1
    # and drop the registry line too, or the append below is skipped and the tag is
    # left pointing at the file we just deleted
    _reg = r(f"{MOD}/common/countries.txt")
    if re.search(rf"^\s*{tag}\s*=", _reg, re.M):
        w(f"{MOD}/common/countries.txt", re.sub(rf"^\s*{tag}\s*=.*\n", "", _reg, flags=re.M))
    rel = f"countries/{tag} {nm}.txt"      # tag-prefixed so two nations cannot collide
    col = c["color"]
    PAL[tag] = col
    w(f"{MOD}/common/{rel}",
      f"color = {{ {col[0]} {col[1]} {col[2]} }}\n"
      "graphical_culture = NativeGC\n\n"
      "party = {\n"
      f'\tname = "{tag}_conservative"\n\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n'
      "\tideology = conservative\n\tsocial_policy = pro_regulation\n"
      "\teconomic_policy = state_capitalism\n\ttrade_policy = protectionism\n"
      "\treligious_policy = moralism\n\tcitizenship_policy = residency\n\twar_policy = jingoism\n}\n\n"
      "party = {\n"
      f'\tname = "{tag}_reactionary"\n\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n'
      "\tideology = reactionary\n\tsocial_policy = pro_regulation\n"
      "\teconomic_policy = state_capitalism\n\ttrade_policy = protectionism\n"
      "\treligious_policy = moralism\n\tcitizenship_policy = residency\n\twar_policy = pro_military\n}\n\n"
      "unit_names = {\n}\n")
    if not re.search(rf"^\s*{tag}\s*=", r(f"{MOD}/common/countries.txt"), re.M):
        w(f"{MOD}/common/countries.txt", r(f"{MOD}/common/countries.txt").rstrip()
          + f'\n{tag} = "{rel}"\n')
    log["new country definitions"] += 1

# flags: a plain field in the country's colour so nothing renders as a missing texture
for tag, col in PAL.items():
    for suffix in ("", "_communist", "_fascist", "_monarchy", "_republic"):
        p = f"{MOD}/gfx/flags/{tag}{suffix}.tga"
        if os.path.exists(p): continue
        im = Image.new("RGB", (93, 64), tuple(col))
        for y in range(64):
            for x in range(93):
                if x < 3 or x > 89 or y < 3 or y > 60:
                    im.putpixel((x, y), (255, 255, 255))
        im.save(p)
        log["placeholder flags"] += 1

# ------------------------------------------------------------ country history files
UNCIV = {t for t in new if (inferred.get(t) or C[t].get("primary_culture") or "") in
         {"comanche","sioux","cherokee","creek","choctaw","chickasaw","haudenosaunee",
          "anishinaabe","osage","pawnee","mandan_arikara","blackfoot","crow","shoshone",
          "salish","nez_perce","chinook","apache","navajo","tlingit","yupik","inuit",
          "cree","dene","seminole","ute","cheyenne","arapaho","caddo","pueblo","piman",
          "california_nations","algonquian","aleut","metis","miskito","taino_remnant"}}
# capital = the biggest place the country holds, not the lowest province id. The
# lowest id put the Viceroyalty of New Spain's capital in rural California.
provpop = collections.Counter()
for p_ in POPS: provpop[int(p_["province"])] += p_["size"]
FIXED = {"NSP": 2172, "VNG": 2247, "VPE": 2295, "CGC": 2324, "EBR": 2447, "RDP": 2348}
CAPS = {}
for tag in new:
    owned = [int(k) for k, v in P.items() if v["owner"] == tag]
    if tag in FIXED and FIXED[tag] in owned:
        CAPS[tag] = FIXED[tag]
    elif owned:
        CAPS[tag] = max(owned, key=lambda q: provpop.get(q, 0))
    else:
        CAPS[tag] = 1
for tag in new:
    c = C[tag]
    nm = re.sub(r"[^A-Za-z0-9 ]", "", c["name"])
    prim = c.get("primary_culture") or inferred.get(tag, "")
    acc = "".join(f"culture = {ck(a)}\n" for a in (c.get("accepted_cultures") or []))
    unciv = tag in UNCIV
    rel = "animist" if unciv else "catholic"
    w(f"{MOD}/history/countries/{tag} - {nm}.txt",
      f"capital = {CAPS[tag]}\n"
      f"primary_culture = {ck(prim)}\n{acc}"
      f"religion = {rel}\n"
      "government = absolute_monarchy\n"
      "plurality = 0.0\n"
      f"nationalvalue = nv_tradition\n"
      f"literacy = {'0.01' if unciv else '0.05'}\n"
      "non_state_culture_literacy = 0.01\n"
      f"civilized = {'no' if unciv else 'yes'}\n"
      "prestige = 0\n\n"
      "# Political reforms\n"
      "slavery = yes_slavery\nupper_house_composition = appointed\n"
      "vote_franschise = none_voting\npublic_meetings = no_meeting\n"
      "press_rights = state_press\ntrade_unions = no_trade_unions\n"
      "voting_system = first_past_the_post\npolitical_parties = underground_parties\n"
      "conscription = no_draft\ndebt_law = peonage\npenal_system = capital_punishment\n"
      "citizens_rights = primary_culture_only\nborder_policy = closed_borders\n\n"
      "# Social reforms\n"
      "wage_reform = no_minimum_wage\nwork_hours = no_work_hour_limit\n"
      "safety_regulations = no_safety\nhealth_care = no_health_care\n"
      "unemployment_subsidies = no_subsidies\npensions = no_pensions\n"
      "school_reforms = no_schools\nchild_labor = no_regulations\n\n"
      f"ruling_party = {tag}_conservative\nlast_election = 1795.1.1\n"
      "upper_house = {\n\tfascist = 0\n\tliberal = 0\n\tconservative = 70\n"
      "\treactionary = 30\n\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n\n"
      "# Starting technology\n" + ("" if unciv else "flintlock_rifles = 1\n"))
    log["new country histories"] += 1

# ------------------------------- primary / accepted on every country the export touches
for tag, c in C.items():
    hits = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not hits or tag in new: continue
    prim = c.get("primary_culture")
    if not prim: continue      # blank means leave HPM's own value alone
    s = r(hits[0])
    s = re.sub(r"^\s*culture\s*=\s*[A-Za-z_0-9]+\s*\n", "", s, flags=re.M)
    s = re.sub(r"^\s*primary_culture\s*=\s*[A-Za-z_0-9]+\s*$",
               f"primary_culture = {ck(prim)}", s, count=1, flags=re.M)
    acc = "".join(f"culture = {ck(a)}\n" for a in (c.get("accepted_cultures") or []))
    s = re.sub(r"(^primary_culture\s*=.*\n)", r"\1" + acc, s, count=1, flags=re.M)
    w(hits[0], s)
    log["country cultures applied"] += 1

# Victoria II distinguishes colonial level 1 from level 2, but the World Builder only
# tracks "is colonial" as a boolean, so a straight write collapsed 550 level-2 colonies
# to level 1. Recover the level from pristine HPM wherever the flag is still set.
ORIG_COL = {}
for f in glob.glob(f"{_SRC}/history/provinces/*/*.txt"):
    m = re.match(r"(\d+)", os.path.basename(f))
    if not m: continue
    mm = re.search(r"^\s*colonial\s*=\s*(\d+)",
                   re.sub(r"#.*", "", r(f)), re.M)
    if mm: ORIG_COL[int(m.group(1))] = int(mm.group(1))

# ------------------------------------------------------------ province histories
files = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    m = re.match(r"(\d+)", os.path.basename(f))
    if m: files[int(m.group(1))] = f
for k, v in P.items():
    pid = int(k); f = files.get(pid)
    if not f: log["province file missing"] += 1; continue
    s = r(f)
    body = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = body[0], ("\n" + "\n".join(body[1:]) if len(body) > 1 else "")
    for key in ("owner", "controller", "add_core", "trade_goods", "life_rating",
                "colonial", "naval_base", "fort", "railroad"):
        head = re.sub(rf"^\s*{key}\s*=.*\n", "", head, flags=re.M)
    lines = []
    if v["owner"]:
        lines.append(f"owner = {v['owner']}")
        lines.append(f"controller = {v['controller'] or v['owner']}")
    for core in sorted(set(v["cores"])):
        lines.append(f"add_core = {core}")
    if v.get("trade_goods"): lines.append(f"trade_goods = {v['trade_goods']}")
    if v.get("life_rating"): lines.append(f"life_rating = {v['life_rating']}")
    if v.get("colonial"):
        lines.append(f"colonial = {max(int(v['colonial']), ORIG_COL.get(pid, 1))}")
    for key in ("naval_base", "fort", "railroad"):
        if v.get(key): lines.append(f"{key} = {v[key]}")
    w(f, "\n".join(lines) + "\n" + head.strip("\n") + tail)
    log["province files written"] += 1

# ------------------------------------------------------------------------- pops
shutil.rmtree(f"{MOD}/history/pops/{START}", ignore_errors=True)
bucket = collections.defaultdict(lambda: collections.defaultdict(list))
for p in POPS:
    pid = int(p["province"]); f = files.get(pid)
    if not f or p["size"] <= 0: continue
    bucket[os.path.basename(os.path.dirname(f))][pid].append(
        (p["type"], ck(p["culture"]), p["religion"], int(p["size"])))
for name, provs in bucket.items():
    txt = ""
    for pid in sorted(provs):
        txt += f"{pid} = {{\n"
        for ty, cu, rl, sz in provs[pid]:
            txt += f"\t{ty} = {{\n\t\tculture = {cu}\n\t\treligion = {rl}\n\t\tsize = {sz}\n\t}}\n"
        txt += "}\n\n"
    w(f"{MOD}/history/pops/{START}/{name}.txt", txt)
log["pop files"] = len(bucket)
log["pop entries"] = sum(len(v) for b in bucket.values() for v in b.values())

# ------------------------------------------------------- diplomacy: who rules whom
# The overlord relationships only existed in the export. Nothing wrote them into the
# mod, so every viceroyalty loaded as an independent country rather than a colony.
KIND = {"colony": "vassal", "puppet": "vassal", "substate": "substate",
        "protectorate": "vassal", "personal_union": "union"}
lines, meta = [], {}
for tag, c in sorted(C.items()):
    ov = c.get("overlord")
    if ov and ov in C:
        k = KIND.get(c.get("relationship", "puppet"), "vassal")
        lines.append(f"# {C[ov]['name']} - {c['name']}\n{k} = {{\n\tfirst = {ov}\n"
                     f"\tsecond = {tag}\n\tstart_date = {START}\n\tend_date = 1936.1.1\n}}\n")
        log["vassal relationships"] += 1
    if c.get("becomes") or (c.get("on_independence") or {}).get("primary_culture"):
        oi = c.get("on_independence") or {}
        meta[tag] = {"becomes": c.get("becomes") or oi.get("becomes") or "",
                     "independence_primary": oi.get("primary_culture", ""),
                     "independence_accepted": oi.get("accepted_cultures", [])}
w(f"{MOD}/history/diplomacy/1800_colonial_rule.txt", "\n".join(lines))
# the successor and post-independence cultures have no home in a Victoria II file yet
# -- they drive events we have not written -- so they travel alongside the mod
json.dump(meta, open(f"{_WORK}/world_meta.json", "w"))
log["successor records"] = len(meta)

# ------------------------------------------------------------------ localisation
rows = []
for tag in new:
    rows.append(f"{tag};{C[tag]['name']};;;;;;;;;;;;;x")
    rows.append(f"{tag}_ADJ;{C[tag]['name']};;;;;;;;;;;;;x")
    rows.append(f"{tag}_conservative;Council;;;;;;;;;;;;;x")
    rows.append(f"{tag}_reactionary;Elders;;;;;;;;;;;;;x")
for tag in ("MEX", "CLM"):
    if tag in C: rows.append(f"{tag};{C[tag]['name']};;;;;;;;;;;;;x")
w(f"{MOD}/localisation/05_1800_nations.csv",
  "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
  + "\n".join(rows) + "\n")
log["localisation rows"] = len(rows)

for k, v in log.items(): print(f"  {k:<32}{v}")
print("\n  inferred primaries:", ", ".join(f"{k}={v}" for k, v in sorted(inferred.items())[:12]))
