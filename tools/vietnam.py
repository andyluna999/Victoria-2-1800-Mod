"""The Tay Son war, corrected.

All of this came from a player who knows the period, and almost every point was right.

**The capitals were both Hanoi.** Nguyen Anh governed from Gia Dinh, which is Saigon,
and had done since he retook it in 1788. The Tay Son governed from Phu Xuan, which is
Hue. Neither of them was anywhere near Hanoi in 1800 -- it was a provincial town by
then and had not been a capital since the Le.

**The Nguyen had no fleet.** This is the worst of the errors, because the fleet is how
they won. Nguyen Anh built a navy with European advisers and Western-rigged ships, and
the war was decided at sea: Thi Nai in February 1801 destroyed the Tay Son fleet and
opened the road to Phu Xuan. A Nguyen faction with nine regiments and no ships cannot
fight the war it is supposed to fight.

**Nguyen Van Truong was on the wrong side and in the wrong service.** He had been a
Tay Son officer and defected years before; by 1800 he was Nguyen Anh's admiral, and he
commanded at Thi Nai.

**Three Tay Son commanders were missing.** Tran Quang Dieu, who was besieging Quy Nhon
in February 1800; Vu Van Dung, who commanded the fleet at Thi Nai; and Bui Thi Xuan,
who was at Quy Nhon with Dieu and led the last resistance in 1802 -- one of very few
women to command an army anywhere in this period and executed by elephant for it.

**And the name.** Nguyen Anh's regime in 1800 was the Nguyen Lords, Chua Nguyen; it
became the Nguyen dynasty when he took the throne as Gia Long in 1802. The country was
not called Viet Nam until the Qing granted the name in 1804, and granted that one
rather than the Nam Viet he asked for, because Nam Viet could be read as a claim on
Nanyue and therefore on southern China.

Tannu Tuva is also renamed: in 1800 it was Tannu Uriankhai.

What is not done here is the map. Muang Phuan on the Xiangkhoang plateau and the Sip
Song Chau Tai in the Son La highlands were Tai polities under tribute rather than
Vietnamese provinces, and representing that properly means new tags and redrawn
borders rather than a rename.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
EV, LOC, DEC = [], [], []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

GIA_DINH, PHU_XUAN, QUY_NHON = 1380, 1375, 1379

# --- the names ---------------------------------------------------------------------------
for k, v in [("PROV1380", "Gia Dinh"), ("PROV1375", "Phu Xuan"),
             ("PROV1364", "Oudong"),
             ("DAI", "Nguyen Lords"), ("DAI_ADJ", "Nguyen"),
             ("DAI_absolute_monarchy", "Nguyen Lords"),
             ("DAI_prussian_constitutionalism", "Nguyen Lords"),
             ("TNT", "Tannu Uriankhai"), ("TNT_ADJ", "Uriankhai"),
             ("TNT_absolute_monarchy", "Tannu Uriankhai"),
             ("VNM", "Viet Nam"), ("VNM_ADJ", "Vietnamese"),
             ("VNM_absolute_monarchy", "Empire of Viet Nam")]:
    loc(k, v)
log["names corrected"] = 13

# --- the capitals ------------------------------------------------------------------------
for tag, cap, why in (("DAI", GIA_DINH, "Gia Dinh, retaken 1788"),
                      ("TYS", PHU_XUAN, "Phu Xuan")):
    g = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s = rd(g[0])
    parts = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^\s*capital\s*=\s*\d+", f"capital = {cap}", head, flags=re.M)
    wr(g[0], head.rstrip("\n") + "\n" + tail)
    log["capitals moved off Hanoi"] += 1

# --- the Nguyen fleet, which is how they won ------------------------------------------------
wr(f"{MOD}/history/units/DAI_oob.txt",
   "# The forces of Nguyen Anh in 1800, holding the south from Gia Dinh and Quy Nhon.\n"
   "#\n"
   "# The fleet matters more than the army. Nguyen Anh built a navy with European\n"
   "# advisers and Western-rigged ships, and the war was settled at sea: Thi Nai in\n"
   "# February 1801 destroyed the Tay Son fleet and opened the road to Phu Xuan.\n"
   "# Nguyen Van Truong, who had been a Tay Son officer and defected years before,\n"
   "# commanded there.\n\n"
   'leader = {\n\tname = "Nguyen Van Truong"\n\tdate = 1799.1.1\n\ttype = sea\n'
   "\tpersonality = daring\n\tbackground = war_college\n\tprestige = 0.7\n}\n\n"
   'leader = {\n\tname = "Nguyen Anh"\n\tdate = 1799.1.1\n\ttype = land\n'
   "\tpersonality = au_fait\n\tbackground = natural_born_leader\n\tprestige = 0.8\n}\n\n"
   'leader = {\n\tname = "Le Van Duyet"\n\tdate = 1799.1.1\n\ttype = land\n'
   "\tpersonality = relentless\n\tbackground = exranker\n\tprestige = 0.6\n}\n\n"
   'army = {\n\tname = "Quan Nguyen"\n\tlocation = ' + str(GIA_DINH) + "\n"
   + "".join(f'\tregiment = {{\n\t\tname = "{i+1}. Infantry"\n\t\ttype = infantry\n'
             f"\t\thome = {p}\n\t}}\n"
             for i, p in enumerate([GIA_DINH, GIA_DINH, 1379, 1381, 1382, QUY_NHON]))
   + "}\n\n"
   'navy = {\n\tname = "Thuy Quan Nguyen"\n\tlocation = ' + str(GIA_DINH) + "\n"
   + "".join(f'\tship = {{\n\t\tname = "{n}"\n\t\ttype = frigate\n\t}}\n'
             for n in ("Phuong Phi", "Bang Phi", "Long Phi", "Dinh Hai"))
   + "".join(f'\tship = {{\n\t\tname = "{i+1}. Galley"\n\t\ttype = clipper_transport\n\t}}\n'
             for i in range(3))
   + "}\n")
log["the Nguyen fleet"] = 7

# --- the Tay Son commanders who were missing -------------------------------------------------
f = f"{MOD}/history/units/TYS_oob.txt"
if os.path.exists(f):
    s = rd(f)
    # Nguyen Van Truong was not theirs and had not been for years
    # he defected to Nguyen Anh years before 1800 and commanded their fleet
    m = re.search(r'leader = \{[^{}]*?name = "Nguyen Van Truong"[^{}]*?\}\s*', s, re.S)
    if m:
        s = s[:m.start()] + s[m.end():]
    add = (
     'leader = {\n\tname = "Tran Quang Dieu"\n\tdate = 1799.1.1\n\ttype = land\n'
     "\tpersonality = relentless\n\tbackground = natural_born_leader\n\tprestige = 0.7\n}\n\n"
     'leader = {\n\tname = "Bui Thi Xuan"\n\tdate = 1799.1.1\n\ttype = land\n'
     "\tpersonality = audacious\n\tbackground = cavalry_school\n\tprestige = 0.6\n}\n\n"
     'leader = {\n\tname = "Vu Van Dung"\n\tdate = 1799.1.1\n\ttype = sea\n'
     "\tpersonality = daring\n\tbackground = cartographer\n\tprestige = 0.5\n}\n\n")
    if "Tran Quang Dieu" not in s:
        s = add + s
    wr(f, s)
    log["Tay Son commanders restored"] = 3

# --- Siam and the Tay Son were not on speaking terms -------------------------------------------
f = f"{MOD}/history/diplomacy/1800_asia.txt"
if os.path.exists(f):
    s = rd(f)
    if "TYS" not in s or "SIA" not in s:
        wr(f, s.rstrip() + "\n")
EV.append("""country_event = {
    id = 9103300
    title = "EVTNAME9103300"
    desc = "EVTDESC9103300"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = TYS
        exists = SIA
    }
    mean_time_to_happen = { days = 6 }

    option = {
        name = "EVTOPTA9103300"
        SIA = { relation = { who = THIS value = -150 } }
        relation = { who = SIA value = -150 }
    }
}
""")
loc("EVTNAME9103300", "Siam and the Tay Son")
loc("EVTDESC9103300",
    "Bangkok has sheltered Nguyen Anh, armed him, and twice sent armies into the delta "
    "on his behalf -- the last of which was destroyed at Rach Gam by Nguyen Hue in a "
    "single night. Quang Trung spent his reign pushing back against Siamese influence "
    "in Laos and Cambodia and the court has not revised the policy since his death. "
    "There is nothing to discuss with Siam and there has not been for fifteen years.")
loc("EVTOPTA9103300", "Nothing to discuss.")
log["events"] += 1

# --- the Nguyen Dynasty gets a tag of its own ------------------------------------------------
VNM_FILE = """capital = 1380
primary_culture = vietnamese
religion = mahayana
government = absolute_monarchy
plurality = 0.0
nationalvalue = nv_order
literacy = 0.05
civilized = no
prestige = 12

ruling_party = VNM_conservative
last_election = 1795.1.1
upper_house = {
\tfascist = 0
\tliberal = 5
\tconservative = 80
\treactionary = 15
\tanarcho_liberal = 0
\tsocialist = 0
\tcommunist = 0
}
"""
import os as _os2
if not glob.glob(f"{MOD}/history/countries/VNM - *.txt"):
    wr(f"{MOD}/history/countries/VNM - Viet Nam.txt", VNM_FILE)
    ct = rd(f"{MOD}/common/countries.txt")
    if "\nVNM" not in ct:
        wr(f"{MOD}/common/countries.txt",
           ct.rstrip() + '\nVNM = "countries/VNM - Viet Nam.txt"\n')
    # the parties, since a country needs one for every ideology its house can turn
    cf = glob.glob(f"{MOD}/common/countries/*.txt")
    src_party = rd([x for x in cf if "Dai Viet" in x or "DAI" in x][0]) if any(
        "Dai Viet" in x or "DAI" in x for x in cf) else ""
    parties = ""
    for ide, yr in (("conservative", 1750), ("reactionary", 1750), ("liberal", 1799),
                    ("anarcho_liberal", 1799), ("socialist", 1848),
                    ("communist", 1848), ("fascist", 1900)):
        parties += (f'\nparty = {{\n\tname = "VNM_{ide}"\n\tstart_date = {yr}.1.1\n'
                    f"\tend_date = 2000.1.1\n\n\tideology = {ide}\n\n"
                    "\tsocial_policy = no_position_set\n\teconomic_policy = state_capitalism\n"
                    "\ttrade_policy = protectionism\n\treligious_policy = moralism\n"
                    "\tcitizenship_policy = residency\n\twar_policy = pro_military\n}\n")
    wr(f"{MOD}/common/countries/VNM - Viet Nam.txt",
       "color = { 180 60 50 }\n\ngraphical_culture = AsianGC\n" + parties)
    for ide, nm in (("conservative", "Trieu Dinh"), ("reactionary", "Cuu Trieu"),
                    ("liberal", "Duy Tan"), ("anarcho_liberal", "Dong Du"),
                    ("socialist", "Xa Hoi"), ("communist", "Cong San"),
                    ("fascist", "Phuc Quoc")):
        loc(f"VNM_{ide}", nm)
    log["the Nguyen Dynasty gets a tag"] = 1

# --- 1802: the Nguyen win, and what the country is then called -------------------------------
EV.append(f"""country_event = {{
    id = 9103301
    title = "EVTNAME9103301"
    desc = "EVTDESC9103301"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = DAI
        year = 1802
        NOT = {{ year = 1815 }}
        NOT = {{ exists = TYS }}
    }}
    mean_time_to_happen = {{ months = 4 }}

    option = {{
        name = "EVTOPTA9103301"
        set_global_flag = h18_gia_long
        # the Tay Son are finished and their claim finishes with them
        all_core = {{ remove_core = TYS }}
        all_core = {{ remove_core = DAI }}
        change_tag = VNM
        government = absolute_monarchy
        prestige = 25
        any_pop = {{ militancy = -3 consciousness = 2 }}
    }}
}}

country_event = {{
    id = 9103302
    title = "EVTNAME9103302"
    desc = "EVTDESC9103302"
    picture = "administration"
    fire_only_once = yes

    trigger = {{
        tag = VNM
        has_global_flag = h18_gia_long
        year = 1804
    }}
    mean_time_to_happen = {{ months = 6 }}

    option = {{
        name = "EVTOPTA9103302"
        set_global_flag = h18_viet_nam_named
        prestige = 10
        QNG = {{ relation = {{ who = THIS value = 40 }} }}
    }}
}}
""")
loc("EVTNAME9103301", "Gia Long")
loc("EVTDESC9103301",
    "Phu Xuan has fallen and the Tay Son are finished, twenty-six years after three "
    "brothers from a village in Binh Dinh overturned everything. Nguyen Anh has taken "
    "the throne and the reign name Gia Long, from Gia Dinh and Thang Long -- the south "
    "he held and the north he has taken -- and the country is governed from one capital "
    "for the first time in two hundred years.")
loc("EVTOPTA9103301", "The south and the north, under one reign name.")
loc("EVTNAME9103302", "The Name the Qing Would Grant")
loc("EVTDESC9103302",
    "The embassy asked Peking to recognise the country as Nam Viet, which is the old "
    "name and the one the court wanted. The Qing have declined and offered Viet Nam "
    "instead, the elements reversed, because Nam Viet is also Nanyue -- a kingdom that "
    "once held Guangdong and Guangxi -- and the Board of Rites has no intention of "
    "appearing to concede a claim on two Chinese provinces to a court that has just "
    "finished a civil war.")
loc("EVTOPTA9103302", "Viet Nam, then. The name is granted, not chosen.")
log["events"] += 2

wr(f"{MOD}/events/1800_Vietnam.txt", "\n".join(EV))
wr(f"{MOD}/localisation/00_AAA_vietnam.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
