"""Europe on 1 January 1800, per the Narrative & Event Plan section 3.

War of the Second Coalition still running. Napoleon First Consul for seven weeks.
France holds Belgium, the left bank of the Rhine, Savoy, Nice and Piedmont; Austria
has retaken Lombardy; the Cisalpine, Roman and Parthenopean republics are gone; the
Holy Roman Empire still stands; Poland does not exist.
"""
import json, re, glob, os, collections

MOD = "/home/claude/build/HPM"
W = "/home/claude/work"
L = json.load(open(f"{W}/world_live.json"))
NAME = {int(k): v["n"] for k, v in L["prov"].items()}
log = collections.Counter()

def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# ---------------------------------------------------------------- new tags
NEW = {
 "LIG": ("Ligurian Republic", [34, 90, 54], "FRA", "colony"),
 # The Republic of Ragusa outlived Venice and Genoa and kept its independence as an
 # Ottoman tributary until Napoleon abolished it in 1808. Austria only gets Dubrovnik
 # in 1814, which is why the 1836 map shows it Austrian.
 "RAG": ("Republic of Ragusa", [180, 60, 60], "TUR", "colony"),
}
reg = rd(f"{MOD}/common/countries.txt")
for tag, (nm, col, over, rel) in NEW.items():
    if re.search(rf"^\s*{tag}\s*=", reg, re.M): continue
    path = f"countries/{tag} {re.sub(r'[^A-Za-z0-9 ]','',nm)}.txt"
    wr(f"{MOD}/common/{path}",
       f"color = {{ {col[0]} {col[1]} {col[2]} }}\ngraphical_culture = ItalianGC\n\n"
       "party = {\n" f'\tname = "{tag}_liberal"\n' "\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n"
       "\tideology = liberal\n\tsocial_policy = pro_regulation\n\teconomic_policy = laissez_faire\n"
       "\ttrade_policy = free_trade\n\treligious_policy = pluralism\n"
       "\tcitizenship_policy = limited_citizenship\n\twar_policy = anti_military\n}\n\n"
       "party = {\n" f'\tname = "{tag}_conservative"\n' "\tstart_date = 1750.1.1\n\tend_date = 1950.1.1\n"
       "\tideology = conservative\n\tsocial_policy = pro_regulation\n\teconomic_policy = state_capitalism\n"
       "\ttrade_policy = protectionism\n\treligious_policy = moralism\n"
       "\tcitizenship_policy = residency\n\twar_policy = jingoism\n}\n\nunit_names = {\n}\n")
    reg = reg.rstrip() + f'\n{tag} = "{path}"\n'
    log["new tags"] += 1
wr(f"{MOD}/common/countries.txt", reg)

# ------------------------------------------------------- ownership, 1 Jan 1800
# province id -> owner
OWN = {}
def give(tag, *ids):
    for i in ids: OWN[i] = tag

# France: the Republic and everything it had annexed by 1800
give("FRA", 387,388,389,390,391, 392,393,394,395,398)          # Belgium, annexed 1795
give("FRA", 396, 397)                                          # Spa, Luxembourg
give("FRA", 572, 575, 576, 577, 579)                           # Trier, Cologne, Aachen, Kleve, Koblenz
give("FRA", 570, 571, 573, 574)                                # Mainz, Kaiserslautern, Saarbrucken, Kreuznach
give("FRA", 381)                                               # Maastricht, annexed 1795
give("FRA", 465, 466, 472)                                     # Savoy and Nice, annexed 1792
give("FRA", 720, 721, 722, 723)                                # Piedmont, annexed Feb 1799
give("FRA", 607)                                               # Geneva, annexed 1798
give("FRA", 854)                                               # Malta: French garrison until Sept 1800

# Italy
give("LIG", 724, 725)                                          # Genoa and Savona
give("SAR", 765, 766)                                          # the king is left with the island
give("PAP", 741, 742, 743, 749, 750, 751, 752)                 # the Pope's title, not his control
give("AUS", 726, 727, 728, 2669)                               # Lombardy, retaken 1799
give("AUS", 729, 730, 731, 732, 733)                           # Venetia, from Campo Formio
give("AUS", 2582)                                              # Kotor, Venetian Albania
give("RAG", 782)                                               # Dubrovnik: still a republic

# the Partitions: Poland does not exist
give("PRU", 706, 708, 709, 710, 712, 717)                      # South Prussia
give("PRU", 707, 719)                                          # New East Prussia
give("RUS", 936, 937)                                          # Grodno and Brest stay Russian
give("AUS", 711, 713, 715, 716)                                # West Galicia
give("AUS", 703, 704, 705, 714)                                # Krakow and Galicia
give("NEH", 608)                                               # Neuchatel: a principality of the King of Prussia
give("RUS", 339)                                               # Viipuri: Old Finland, Russian since 1743

# the Baltic and the North
give("RUS", 349,350,351,352,353, 354,355,356,357,358,359)      # Estonia, Livonia, Courland
give("SWE", 336,337,338,342, 340,341,343,344, 345,346,347,348) # Finland is Swedish until 1809
give("SWE", 548)                                               # Swedish Pomerania
give("DEN", 305,306,307,308, 309,310,311,312, 313,314,315,316) # Norway
give("DEN", 370, 371, 369, 529, 533)                           # Schleswig, Holstein, Lauenburg, Heligoland

# the Ottoman lands
give("TUR", 834,839,840,841,842, 835,836,837,838,845)          # Greece
give("TUR", 794,795,796,797)                                   # Serbia
give("TUR", 800, 2569, 2577)                                   # Ottoman Montenegro
give("ION", 826, 827)                                          # the Septinsular Republic
give("MOL", 676, 677, 678)                                     # Bessarabia is still Moldavian

# the British Isles
give("IRE", 254,255,256, 257,258,259, 260,261,262, 263,264,265)

# --- occupation on 1 January 1800: who actually holds the ground.
# The 1799 Austro-Russian campaign swept the French out of Italy. Suvorov took Turin
# in June and Melas garrisoned Piedmont; the Austrian Imperial Commission governed
# Lombardy until 30 May 1800. Austria held the Three Legations, taken from the
# Cisalpine Republic and claimed under the Treaty of Tolentino. Tuscany's Grand Duke
# had been deposed in March 1799 and the country was under Austrian occupation.
# Rome was held by Neapolitan troops through the papal interregnum -- Pius VI died in
# August 1799 and Pius VII was not elected until 14 March 1800.
CONTROL = {}
for p_ in (720, 721, 722, 723): CONTROL[p_] = "AUS"   # Piedmont: French title, Austrian army
for p_ in (741, 742, 743):      CONTROL[p_] = "AUS"   # Bologna, Ferrara, Ravenna
for p_ in (744, 745, 747, 748): CONTROL[p_] = "AUS"   # Tuscany
for p_ in (749, 750, 751, 752): CONTROL[p_] = "SIC"   # Rome and the Patrimony

prov = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    prov[int(re.match(r"(\d+)", os.path.basename(f)).group(1))] = f

# cores that must exist for the 1800 map and for later events
CORES = {
 "FRA": [387,388,389,390,391,392,393,394,395,398,396,397,572,575,576,577,579,570,571,573,574,
         381,465,466,472,720,721,722,723,607,854],
 "BEL": [387,388,389,390,391,392,393,394,395,398],
 "NET": [375,376,377,378,379,380,382,383,384,385,386,381],
 "POL": [706,708,709,710,712,717,707,719,711,713,715,716,703,704,705,714,699,700,701,936,937],
 "SAR": [720,721,722,723,724,725,765,766,465,466,472],
 "LIG": [724,725],
 "RAG": [782],
 "GRE": [834,839,840,841,842,835,836,837,838,845,826,827],
 "SER": [794,795,796,797],
 "IRE": [254,255,256,257,258,259,260,261,262,263,264,265],
 "SWE": [336,337,338,342,340,341,343,344,345,346,347,348,548],
 "FIN": [336,337,338,342,340,341,343,344,345,346,347,348,339],
 "NOR": [305,306,307,308,309,310,311,312,313,314,315,316],
 "ION": [826,827],
 "MOL": [676,677,678],
 "ITA": [726,727,728,729,730,731,732,741,742,743,749,750,751,752,724,725,738,739,740,744,745,747,748],
}

changed = 0
for pid, f in prov.items():
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    before = head
    if pid in OWN or pid in CONTROL:
        o = OWN.get(pid) or (re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M) or [None, None])[1]
        if isinstance(o, tuple): o = o[0]
        m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
        o = OWN.get(pid) or (m.group(1) if m else None)
        head = re.sub(r"^\s*owner\s*=.*\n", "", head, flags=re.M)
        head = re.sub(r"^\s*controller\s*=.*\n", "", head, flags=re.M)
        if o:
            head = f"owner = {o}\ncontroller = {CONTROL.get(pid, o)}\n" + head.lstrip("\n")
    extra = [t for t, ids in CORES.items() if pid in ids]
    if extra:
        have = set(re.findall(r"^\s*add_core\s*=\s*([A-Z]{3})", head, re.M))
        add = [t for t in extra if t not in have]
        if add:
            m = re.search(r"^(?:owner|controller)\s*=.*\n(?:^controller\s*=.*\n)?", head, re.M)
            at = m.end() if m else 0
            head = head[:at] + "".join(f"add_core = {t}\n" for t in add) + head[at:]
    if OWN.get(pid):
        o = OWN[pid]
        if not re.search(rf"^\s*add_core\s*=\s*{o}\s*$", head, re.M) and o in ("FRA","PRU","AUS","RUS","SWE","DEN","TUR","IRE","LIG","ION","SAR","PAP"):
            pass
    if head != before:
        wr(f, head.rstrip("\n") + "\n" + tail); changed += 1
log["province files rewritten"] = changed
log["provinces reassigned"] = len(OWN)
log["provinces under occupation"] = len(CONTROL)

# ------------------------------------------------------------------ diplomacy
# France's sister republics, Britain's two personal unions, the Porte's tributaries
DIP = [("vassal","FRA","NET","the Batavian Republic","1810.7.9"),
       ("vassal","FRA","SWI","the Helvetic Republic","1815.1.1"),
       ("vassal","FRA","LIG","the Ligurian Republic","1805.6.4"),
       ("union","ENG","HAN","Hanover","1837.6.20"),
       ("union","ENG","IRE","Ireland","1801.1.1"),
       ("vassal","TUR","WAL","Wallachia","1877.5.21"),
       ("vassal","TUR","MOL","Moldavia","1877.5.21"),
       ("vassal","TUR","ION","the Septinsular Republic","1815.1.1"),
       ("vassal","PRU","NEH","Neuchatel","1814.1.1"),
       ("vassal","TUR","RAG","the Republic of Ragusa","1808.1.31")]
lines = []
for kind, first, second, nm, endd in DIP:
    lines.append(f"# {first} - {nm}\n{kind} = {{\n\tfirst = {first}\n\tsecond = {second}\n"
                 f"\tstart_date = 1800.1.1\n\tend_date = {endd}\n}}\n")
    log["european dependencies"] += 1
wr(f"{MOD}/history/diplomacy/1800_europe.txt", "\n".join(lines))

# ------------------------------------------------- history files for the new tags
CAP={"LIG":724,"RAG":782}
rows_all=[]
for tag,(nm,col,over,rel) in NEW.items():
    fn=re.sub(r"[^A-Za-z0-9 ]","",nm)
    for old in glob.glob(f"{MOD}/history/countries/{tag} - *.txt"): os.remove(old)
    wr(f"{MOD}/history/countries/{tag} - {fn}.txt",
       f"capital = {CAP.get(tag,1)}\nprimary_culture = north_italian\nreligion = catholic\n"
       "government = democracy\nplurality = 10.0\nnationalvalue = nv_liberty\n"
       "literacy = 0.15\nnon_state_culture_literacy = 0.05\ncivilized = yes\nprestige = 0\n\n"
       "# Political reforms\nslavery = no_slavery\nupper_house_composition = appointed\n"
       "vote_franschise = landed_voting\npublic_meetings = yes_meeting\npress_rights = censored_press\n"
       "trade_unions = no_trade_unions\nvoting_system = first_past_the_post\n"
       "political_parties = harassment\nconscription = yes_conscription\ndebt_law = peonage\n"
       "penal_system = capital_punishment\ncitizens_rights = culture_voting_only\n"
       "border_policy = open_borders\n\n# Social reforms\nwage_reform = no_minimum_wage\n"
       "work_hours = no_work_hour_limit\nsafety_regulations = no_safety\nhealth_care = no_health_care\n"
       "unemployment_subsidies = no_subsidies\npensions = no_pensions\nschool_reforms = no_schools\n"
       "child_labor = no_regulations\n\n"
       f"ruling_party = {tag}_liberal\nlast_election = 1799.1.1\n"
       "upper_house = {\n\tfascist = 0\n\tliberal = 60\n\tconservative = 30\n"
       "\treactionary = 10\n\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n\n"
       "flintlock_rifles = 1\npost_nelsonian_thought = 1\nguild_based_production = 1\n")
    log["new country histories"]+=1
    ADJ={"LIG":"Ligurian","RAG":"Ragusan"}
    rows_all.extend([f"{tag};{nm};;;;;;;;;;;;;x",
          f"{tag}_ADJ;{ADJ.get(tag,nm)};;;;;;;;;;;;;x",
          f"{tag}_liberal;Partito Patriottico;;;;;;;;;;;;;x",
          f"{tag}_conservative;Partito Moderato;;;;;;;;;;;;;x"])

wr(f"{MOD}/localisation/06_europe_1800.csv",
   "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
   +"\n".join(rows_all)+"\n")

for k, v in log.items(): print(f"  {k:<32}{v}")
