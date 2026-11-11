"""The Barbary states as they were in 1800, not as they were in 1836.

KAR and KML are already taken in HPM, so the Karamanli tag is KRM.

All three were Ottoman in name and self-governing in fact, and all three were ruled by
dynasties the 1836 map has no room for. The same pattern as the viceroyalties: the
1800 state is its own tag, the 1836 tag keeps its cores and waits as the successor,
and an event converts one into the other on the date it actually happened.

  Regency of Algiers   -> French Algeria, 5 July 1830, when Hussein Dey surrenders
  Beylik of Tunis      -> the same Husainid state, which is why the handover in 1836
                          is a renaming rather than a conquest
  Karamanli Tripoli    -> Ottoman Tripolitania, 1835, when the Porte lands troops and
                          ends 124 years of Karamanli rule
"""
import json, re, glob, os, collections

MOD = "/home/claude/build/HPM"; W = "/home/claude/work"
L = json.load(open(f"{W}/world_live.json"))
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# tag, name, adjective, colour, successor, capital, culture, the date it ends
STATES = [
 ("RGA", "Regency of Algiers", "Algerine",  [ 40, 110,  70], "ALD", 1700, "maghrebi", "1830.7.5",
  "The Dey surrenders Algiers to a French expeditionary force."),
 ("BTN", "Beylik of Tunis",    "Tunisian",  [120, 155,  90], "TUN", 1725, "maghrebi", "1836.1.1",
  "The Husainid beys rule on; only the name on the map changes."),
 ("KRM", "Karamanli Tripoli",  "Tripoline", [150, 125,  60], "TRI", 1731, "maghrebi", "1835.5.26",
  "An Ottoman squadron lands at Tripoli and ends 124 years of Karamanli rule."),
]

reg = rd(f"{MOD}/common/countries.txt")
for tag, nm, adj, col, suc, cap, cult, end, why in STATES:
    if re.search(rf"^\s*{tag}\s*=", reg, re.M): continue
    path = f"countries/{tag} {re.sub(r'[^A-Za-z0-9 ]','',nm)}.txt"
    wr(f"{MOD}/common/{path}",
       f"color = {{ {col[0]} {col[1]} {col[2]} }}\ngraphical_culture = AfricanGC\n\n"
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
for tag, nm, adj, col, suc, cap, cult, end, why in STATES:
    fn = re.sub(r"[^A-Za-z0-9 ]", "", nm)
    for old in glob.glob(f"{MOD}/history/countries/{tag} - *.txt"): os.remove(old)
    wr(f"{MOD}/history/countries/{tag} - {fn}.txt",
       f"capital = {cap}\nprimary_culture = {cult}\nreligion = sunni\n"
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

# --- hand the territory over, and leave the successor its cores ------------------
prov = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    prov[int(re.match(r"(\d+)", os.path.basename(f)).group(1))] = f
moved = 0
for tag, nm, adj, col, suc, cap, cult, end, why in STATES:
    for pid, f in prov.items():
        s = rd(f)
        parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
        head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
        m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
        if not m or m.group(1) != suc: continue
        head = re.sub(r"^\s*owner\s*=.*\n", "", head, flags=re.M)
        head = re.sub(r"^\s*controller\s*=.*\n", "", head, flags=re.M)
        head = f"owner = {tag}\ncontroller = {tag}\n" + head.lstrip("\n")
        for t in (tag, suc):
            if not re.search(rf"^\s*add_core\s*=\s*{t}\s*$", head, re.M):
                head = head.rstrip("\n") + f"\nadd_core = {t}\n"
        wr(f, head.rstrip("\n") + "\n" + tail); moved += 1
log["provinces handed over"] = moved

# --- Ottoman suzerainty, ending on the day each state does -----------------------
wr(f"{MOD}/history/diplomacy/1800_barbary.txt",
   "\n".join(f"# TUR - {nm}\nvassal = {{\n\tfirst = TUR\n\tsecond = {tag}\n"
             f"\tstart_date = 1800.1.1\n\tend_date = {end}\n}}\n"
             for tag, nm, adj, col, suc, cap, cult, end, why in STATES))
log["ottoman suzerainties"] = len(STATES)

# --- the succession, on the date it happened --------------------------------------
EV, LOC = [], []
def loc(k, v): LOC.append(f"{k};{v};;;;;;;;;;;;;x")
eid = 9100500
for tag, nm, adj, col, suc, cap, cult, end, why in STATES:
    eid += 1
    y, mo, d = end.split(".")
    EV.append(f"""country_event = {{
    id = {eid}
    title = "EVTNAME{eid}"
    desc = "EVTDESC{eid}"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = {tag}
        year = {y}
        NOT = {{ year = {int(y)+1} }}
    }}
    mean_time_to_happen = {{ months = 2 }}

    option = {{
        name = "EVTOPTA{eid}"
        # the Regency ceases to exist, and so do its claims
        all_core = {{ remove_core = {tag} }}
        change_tag = {suc}
    }}
}}
""")
    loc(f"EVTNAME{eid}", f"The End of the {nm}")
    loc(f"EVTDESC{eid}", why)
    loc(f"EVTOPTA{eid}", "So it passes.")
for tag, nm, adj, col, suc, cap, cult, end, why in STATES:
    loc(tag, nm); loc(f"{tag}_ADJ", adj)
    loc(f"{tag}_conservative", "The Divan"); loc(f"{tag}_reactionary", "The Janissary Odjak")
wr(f"{MOD}/events/1800_Barbary.txt", "\n".join(EV))
wr(f"{MOD}/localisation/13_barbary.csv",
   "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
   + "\n".join(LOC) + "\n")
log["succession events"] = len(STATES)

meta = {}
try: meta = json.load(open(f"{W}/world_meta.json"))
except Exception: pass
for tag, nm, adj, col, suc, cap, cult, end, why in STATES:
    meta[tag] = {"becomes": suc, "independence_primary": cult, "independence_accepted": []}
json.dump(meta, open(f"{W}/world_meta.json", "w"))

for k, v in log.items(): print(f"  {k:<30}{v}")
