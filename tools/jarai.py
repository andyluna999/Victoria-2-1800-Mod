"""The Central Highlands were not Vietnamese, and the war was fought on the coast.

Reported by a player: Pleiku was given to the Nguyen Lords as ordinary territory, and
the Tay Son war therefore ran through the highlands. It did not. The plateau was Jarai
country, and the Nguyen relationship with it was tributary rather than territorial --
embassies to the Potao Apui and the Potao Ia, the Fire King and the Water King, who
received gifts and sent them back, and who governed nobody on the court's behalf.

Vietnamese states had no administration up there and did not try to build one until
the French did it for them in the 1890s. The lowland term for the highlanders, moi,
meant savage, which is a reasonable summary of how the relationship was understood
from Hue.

So Pleiku becomes Jarai, and the consequence is the correction that matters: the Tay
Son and the Nguyen now face each other on the coastal plain at Quy Nhon, which is
where they actually fought. Quy Nhon was the Tay Son's own home province and their
first capital; Nguyen Anh took it in 1799, Tran Quang Dieu besieged it through 1800
and 1801 and took it back, and by then it no longer mattered, because the fleet had
settled the war at Thi Nai and gone north to Phu Xuan.

The Jarai are given the culture of the people who actually lived there rather than
being painted Vietnamese, which required adding one.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
LOC = []
def loc(k, v): LOC.append((k, v))
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)
def rd(p): return open(p, encoding="cp1252", errors="replace").read()

PLEIKU = 1378

# --- the culture -----------------------------------------------------------------------------
cul = rd(f"{MOD}/common/cultures.txt")
if "\t\tjarai = {" not in cul:
    m = re.search(r"^southeast_asian\s*=\s*\{", cul, re.M)
    if m:
        i = m.end()
        block = ("\n\t\tjarai = {\n\t\t\tcolor = { 120 140 90 }\n"
                 "\t\t\tfirst_names = { Ksor Rcom Siu Nay Rahlan Puih Hiao Kpa }\n"
                 "\t\t\tlast_names = { Ksor Rcom Siu Nay Rahlan Puih Hiao Kpa }\n\t\t}\n")
        wr(f"{MOD}/common/cultures.txt", cul[:i] + block + cul[i:])
        log["the Jarai get a culture"] = 1
loc("jarai", "Jarai")

# --- the country ------------------------------------------------------------------------------
if not glob.glob(f"{MOD}/history/countries/JRI - *.txt"):
    wr(f"{MOD}/history/countries/JRI - Jarai.txt",
       f"capital = {PLEIKU}\n"
       "primary_culture = jarai\n"
       "religion = animist\n"
       "government = theocracy\n"
       "plurality = 0.0\n"
       "nationalvalue = nv_order\n"
       "literacy = 0.01\n"
       "civilized = no\n"
       "prestige = 1\n\n"
       "ruling_party = JRI_conservative\n"
       "last_election = 1795.1.1\n"
       "upper_house = {\n\tfascist = 0\n\tliberal = 0\n\tconservative = 70\n"
       "\treactionary = 30\n\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n")
    ct = rd(f"{MOD}/common/countries.txt")
    if "\nJRI" not in ct:
        wr(f"{MOD}/common/countries.txt",
           ct.rstrip() + '\nJRI = "countries/JRI - Jarai.txt"\n')
    parties = "color = { 120 140 90 }\n\ngraphical_culture = AsianGC\n"
    for ide, yr in (("conservative", 1750), ("reactionary", 1750), ("liberal", 1799),
                    ("anarcho_liberal", 1799), ("socialist", 1848),
                    ("communist", 1848), ("fascist", 1900)):
        parties += (f'\nparty = {{\n\tname = "JRI_{ide}"\n\tstart_date = {yr}.1.1\n'
                    f"\tend_date = 2000.1.1\n\n\tideology = {ide}\n\n"
                    "\tsocial_policy = no_position_set\n\teconomic_policy = state_capitalism\n"
                    "\ttrade_policy = protectionism\n\treligious_policy = moralism\n"
                    "\tcitizenship_policy = residency\n\twar_policy = anti_military\n}\n")
    wr(f"{MOD}/common/countries/JRI - Jarai.txt", parties)
    for ide, nm in (("conservative", "Potao Apui"), ("reactionary", "The Elders"),
                    ("liberal", "The Younger Villages"), ("anarcho_liberal", "The Unbound"),
                    ("socialist", "The Common Fields"), ("communist", "The Levellers"),
                    ("fascist", "The War Band")):
        loc(f"JRI_{ide}", nm)
    loc("JRI", "Jarai"); loc("JRI_ADJ", "Jarai")
    loc("JRI_theocracy", "Jarai")
    log["the country"] = 1

# --- the plateau ------------------------------------------------------------------------------
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid != PLEIKU: continue
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^\s*owner\s*=\s*\w+", "owner = JRI", head, flags=re.M)
    head = re.sub(r"^\s*controller\s*=\s*\w+", "controller = JRI", head, flags=re.M)
    head = re.sub(r"^\s*add_core\s*=\s*DAI\s*\n", "", head, flags=re.M)
    if "add_core = JRI" not in head:
        head = head.rstrip("\n") + "\nadd_core = JRI\n"
    wr(f, head.rstrip("\n") + "\n" + tail)
    log["the plateau is Jarai"] = 1

# --- the pops up there are not Vietnamese --------------------------------------------------------
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s = rd(f)
    m = re.search(rf"^{PLEIKU}\s*=\s*\{{", s, re.M)
    if not m: continue
    i = m.end(); d = 1
    while i < len(s) and d:
        if s[i] == "{": d += 1
        elif s[i] == "}": d -= 1
        i += 1
    body = s[m.end():i-1]
    nb = re.sub(r"culture = vietnamese", "culture = jarai", body)
    nb = re.sub(r"religion = \w+", "religion = animist", nb)
    if nb != body:
        wr(f, s[:m.end()] + nb + s[i-1:])
        log["the people up there are Jarai"] = 1

# --- a few hundred spears -------------------------------------------------------------------------
wr(f"{MOD}/history/units/JRI_oob.txt",
   "# The Jarai did not keep an army. What they had was village levies and the\n"
   "# authority of the Fire King, which was religious rather than military and did\n"
   "# not extend to telling anybody to march.\n\n"
   f'army = {{\n\tname = "Jarai Levy"\n\tlocation = {PLEIKU}\n'
   + "".join(f'\tregiment = {{\n\t\tname = "{i+1}. Levy"\n\t\ttype = irregular\n'
             f"\t\thome = {PLEIKU}\n\t}}\n" for i in range(2))
   + "}\n")
log["regiments"] = 2

wr(f"{MOD}/localisation/48_jarai.csv",
   "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")
log["localisation rows"] = len(LOC)
for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
