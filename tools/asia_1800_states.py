"""States that existed in 1800 and that the 1836 map has no room for.

Transcaucasia is the clearest case. HPM carries one tag for the whole region, which is
the shape it takes after Russia finishes conquering it in 1828. In 1800 it is four
different things: the Georgian kingdom of Kartli-Kakheti, independent and under Russian
protection by the Treaty of Georgievsk; the western Georgian principalities; and a row
of Muslim khanates -- Yerevan, Ganja, Baku, Karabakh, Talysh, Shirvan -- that
acknowledged Qajar suzerainty after Agha Mohammad Khan sacked Tbilisi in 1795.

Also here: the Kazakh steppe, which belongs to the Kazakh jüz and not to nobody; the
Nawab of the Carnatic, who rules until the Company annexes him in July 1801; and
Vietnam, which on 1 January 1800 is two countries fighting a civil war that the
Nguyen win in 1802.
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

# tag, name, adjective, colour, capital, culture, religion, graphical culture
NEW = [
 ("IME", "Imereti",            "Imeretian", [110, 150, 110], 1092, "georgian",   "orthodox", "RussianGC"),
 ("YER", "Khanate of Yerevan", "Yerevani",  [170, 130,  80], 1098, "azerbaijani",      "shiite",   "AsianGC"),
 ("GAN", "Khanate of Ganja",   "Ganjan",    [185, 150,  95], 1105, "azerbaijani",      "shiite",   "AsianGC"),
 ("BAK", "Khanate of Baku",    "Bakuvian",  [150, 115,  70], 1102, "azerbaijani",      "shiite",   "AsianGC"),
 ("CRN", "Nawab of the Carnatic", "Carnatic", [200, 160, 110], 1307, "tamil",   "sunni",    "IndianGC"),
 ("TYS", "Tay Son Dynasty",    "Tay Son",   [160,  90,  90], 1369, "vietnamese", "mahayana", "ChineseGC"),
]
reg = rd(f"{MOD}/common/countries.txt")
for tag, nm, adj, col, cap, cult, rel, gfx in NEW:
    if re.search(rf"^\s*{tag}\s*=", reg, re.M): continue
    path = f"countries/{tag} {re.sub(r'[^A-Za-z0-9 ]','',nm)}.txt"
    wr(f"{MOD}/common/{path}",
       f"color = {{ {col[0]} {col[1]} {col[2]} }}\ngraphical_culture = {gfx}\n\n"
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

from PIL import Image
for tag, nm, adj, col, cap, cult, rel, gfx in NEW:
    fn = re.sub(r"[^A-Za-z0-9 ]", "", nm)
    for old in glob.glob(f"{MOD}/history/countries/{tag} - *.txt"): os.remove(old)
    wr(f"{MOD}/history/countries/{tag} - {fn}.txt",
       f"capital = {cap}\nprimary_culture = {cult}\nreligion = {rel}\n"
       "government = absolute_monarchy\nplurality = 0.0\nnationalvalue = nv_order\n"
       "literacy = 0.03\nnon_state_culture_literacy = 0.01\ncivilized = no\nprestige = 0\n\n"
       "slavery = yes_slavery\nupper_house_composition = appointed\nvote_franschise = none_voting\n"
       "public_meetings = no_meeting\npress_rights = state_press\ntrade_unions = no_trade_unions\n"
       "voting_system = first_past_the_post\npolitical_parties = underground_parties\n"
       "conscription = no_draft\ndebt_law = peonage\npenal_system = capital_punishment\n"
       "citizens_rights = primary_culture_only\nborder_policy = closed_borders\n\n"
       "wage_reform = no_minimum_wage\nwork_hours = no_work_hour_limit\nsafety_regulations = no_safety\n"
       "health_care = no_health_care\nunemployment_subsidies = no_subsidies\npensions = no_pensions\n"
       "school_reforms = no_schools\nchild_labor = no_regulations\n\n"
       f"ruling_party = {tag}_conservative\nlast_election = 1795.1.1\n"
       "upper_house = {\n\tfascist = 0\n\tliberal = 0\n\tconservative = 60\n\treactionary = 40\n"
       "\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n")
    for sfx in ("", "_communist", "_fascist", "_monarchy", "_republic"):
        fp = f"{MOD}/gfx/flags/{tag}{sfx}.tga"
        if os.path.exists(fp): continue
        im = Image.new("RGB", (93, 64), tuple(col))
        for y in range(64):
            for x in range(93):
                if x < 3 or x > 89 or y < 3 or y > 60: im.putpixel((x, y), (255, 255, 255))
        im.save(fp); log["flags"] += 1

OWN, CORES = {}, collections.defaultdict(list)
def give(tag, *ids):
    for i in ids: OWN[i] = tag
def core(tag, *ids):
    for i in ids: CORES[i].append(tag)

# --- Transcaucasia, broken up ----------------------------------------------------
GEOP = (1090, 1091, 1093)           # Tblisi, Pasanauri, Akhaltsikhe: Kartli-Kakheti
IMEP = (1092, 1094)                 # Kutaisi and Poti: Imereti and the coast
YERP = (1098, 1101, 1099, 1100)     # Yerevan, Nakhchivan, and the Armenian highland
GANP = (1105, 1106)                 # Ganja and Karabakh
BAKP = (1102, 1104, 1107)           # Baku, Sheki, Talysh
give("GEO", *GEOP); give("IME", *IMEP); give("YER", *YERP)
give("GAN", *GANP); give("BAK", *BAKP)
for t, ids in (("GEO", GEOP), ("IME", IMEP), ("YER", YERP), ("GAN", GANP), ("BAK", BAKP)):
    for i in ids: core(t, i); core("TCA", i)

# --- the Kazakh steppe ------------------------------------------------------------
# the jüz of the steppe. The Turkmen deserts west and south of the Aral belong to
# Khiva's orbit, not to the Kazakhs, so they are left alone.
KAZAKH = [1186, 1187, 1188, 1193]
give("KAZ", *[p for p in KAZAKH if p in NAME])
for p in KAZAKH:
    if p in NAME: core("KAZ", p)

# --- the Carnatic: the Company annexes it in July 1801 ----------------------------
# Madras is the Company's own, and Tanjore and Coimbatore were taken in 1799. What
# is left to the Nawab is the Carnatic proper, until Wellesley takes that too in 1801.
give("CRN", 1307, 1310)
for p in (1304, 1307, 1309, 1310): core("CRN", p)

# --- Vietnam is two countries until 1802 ------------------------------------------
# The Tay Son hold the north from Hue; Nguyen Anh holds Gia Dinh and has just retaken
# Qui Nhon. He takes Phu Xuan in 1801 and proclaims himself Gia Long in 1802.
TAYSON = [1369, 1370, 1371, 1372, 1373, 1374, 1375, 1376, 1377]
give("TYS", *[p for p in TAYSON if p in NAME])
for p in TAYSON:
    if p in NAME: core("TYS", p); core("DAI", p)

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
        head = f"owner = {OWN[pid]}\ncontroller = {OWN[pid]}\n" + head.lstrip("\n")
    for t in CORES.get(pid, []):
        if not re.search(rf"^\s*add_core\s*=\s*{t}\s*$", head, re.M):
            head = head.rstrip("\n") + f"\nadd_core = {t}\n"
    wr(f, head.rstrip("\n") + "\n" + tail); changed += 1
# Kazakhstan's capital in HPM is a province the juz do not hold on this map, so point
# it at one they do rather than leaving a country whose capital is abroad
for f in glob.glob(f"{MOD}/history/countries/KAZ - *.txt"):
    t = rd(f)
    t = re.sub(r"^\s*capital\s*=\s*\d+", "capital = 1187", t, count=1, flags=re.M)
    wr(f, t); log["capital repointed"] += 1

log["province files rewritten"] = changed
log["provinces reassigned"] = len(OWN)

# --- suzerainty -------------------------------------------------------------------
# The khanates acknowledged Qajar suzerainty after 1795 and were taken by Russia
# between 1804 and 1828. Georgia was a Russian protectorate by the Treaty of
# Georgievsk and was annexed outright in 1801. Qatar and the Trucial coast fell under
# Diriyah's authority as the Saudi state reached the Gulf.
DIP = [("vassal", "PER", "YER", "the Khanate of Yerevan", "1828.2.22"),
       ("vassal", "PER", "GAN", "the Khanate of Ganja", "1804.1.3"),
       ("vassal", "PER", "BAK", "the Khanate of Baku", "1806.10.3"),
       ("vassal", "RUS", "GEO", "Kartli-Kakheti, by the Treaty of Georgievsk", "1801.1.18"),
       ("vassal", "TUR", "IME", "Imereti", "1810.4.25"),
       ("vassal", "ENG", "CRN", "the Nawab of the Carnatic", "1801.7.31"),
       ("vassal", "NEJ", "QAT", "Qatar", "1818.1.1"),
       ("vassal", "NEJ", "ABU", "the Trucial coast", "1818.1.1")]
wr(f"{MOD}/history/diplomacy/1800_asia_states.txt",
   "\n".join(f"# {a} - {n}\n{k} = {{\n\tfirst = {a}\n\tsecond = {b}\n"
             f"\tstart_date = 1800.1.1\n\tend_date = {e}\n}}\n" for k, a, b, n, e in DIP))
log["suzerainties"] = len(DIP)

# --- the successions --------------------------------------------------------------
EV, LOC = [], []
def loc(k, v): LOC.append(f"{k};{v};;;;;;;;;;;;;x")
SUCC = [("CRN", "ENG", 1801, "The Carnatic Is Annexed",
         "Lord Wellesley has decided that the Nawab's correspondence with Tipu during "
         "the late war amounts to treason. The Carnatic passes to the Company, and the "
         "Nawab keeps a title and a pension."),
        ("TYS", "DAI", 1802, "Gia Long Proclaimed",
         "Nguyen Anh takes Phu Xuan, then Thang Long, and has himself proclaimed emperor "
         "of a Vietnam united from the Chinese border to Ca Mau for the first time.")]
# `change_tag` makes a country *become* another tag, which is right only when that tag
# is vacant -- the Barbary regencies becoming ALD, TUN and TRI. The Carnatic was told
# to become Britain, and Britain already exists: two live countries holding one tag
# hangs Victoria II rather than erroring, which is what froze the game on 30 June 1801.
# Tay Son -> DAI had the same fault waiting in 1802. When the successor is already on
# the map, the country is annexed into it instead.
LIVE_TAGS = set()
for _f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    _h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                  open(_f, encoding="cp1252", errors="replace").read())[0]
    _m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", _h, re.M)
    if _m: LIVE_TAGS.add(_m.group(1))

eid = 9100600
for tag, suc, yr, title, body in SUCC:
    eid += 1
    verb = "annex_to" if suc in LIVE_TAGS else "change_tag"
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        year = {yr}
        NOT = {{ year = {yr+1} }}
    }}
    mean_time_to_happen = {{ months = 3 }}

    option = {{
        name = "EVTOPTA{eid}"
        {verb} = {suc}
    }}
}}
""")
    loc(f"EVTNAME{eid}", title); loc(f"EVTDESC{eid}", body); loc(f"EVTOPTA{eid}", "It is done.")
for tag, nm, adj, col, cap, cult, rel, gfx in NEW:
    loc(tag, nm); loc(f"{tag}_ADJ", adj)
    loc(f"{tag}_conservative", "The Court"); loc(f"{tag}_reactionary", "The Old Guard")
wr(f"{MOD}/events/1800_AsiaStates.txt", "\n".join(EV))
wr(f"{MOD}/localisation/14_asia_states.csv",
   "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
   + "\n".join(LOC) + "\n")
log["succession events"] = len(SUCC)

for k, v in log.items(): print(f"  {k:<30}{v}")
