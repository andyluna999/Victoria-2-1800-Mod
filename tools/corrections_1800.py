"""Border corrections, checked against the sources.

Each of these is a case where HPM's 1836 map encodes a later conquest, or where our
own first pass was too cautious. The common thread is that 1836 borders quietly carry
thirty-six years of annexations.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, collections

MOD = _BUILD; W = _WORK
L = json.load(open(f"{W}/world_live.json"))
NAME = {int(k): v["n"] for k, v in L["prov"].items()}
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

OWN, CORES = {}, collections.defaultdict(list)
def give(tag, *ids):
    for i in ids: OWN[i] = tag
def core(tag, *ids):
    for i in ids: CORES[i].append(tag)

# --- North Africa: France does not take Algiers until 1830 -----------------------
# HPM's 1836 map has the coast French. In 1800 this is the Regency of Algiers, an
# Ottoman vassal in name and an independent corsair state in practice. HPM already
# carries the ALD tag for the interior, so the coast simply rejoins it.
give("ALD", 1700, 1701, 1709, 1704)      # Algiers, Bougie, Bone, Oran
core("ALD", 1700, 1701, 1709, 1704)
core("FRA", 1700)                         # France keeps a claim it will act on in 1830

# Ile de France is French until 1810; Britain takes it at the end of the long war
give("FRA", 2125)
core("ENG", 2125)

# --- India: the Company is a coastal power with three presidencies ---------------
# Poona is the Peshwa's capital and stays so until 1818; Nasik and Belgaum likewise.
# The Company holding them is the 1818 settlement, not the 1800 one.
give("MAR", 1298, 1299, 1302)             # Nasik, Poona, Belgaum
core("MAR", 1298, 1299, 1302, 1300, 1301)
# Allahabad is ceded by Awadh in the Treaty of Lucknow in 1801
give("AWA", 1243)
core("AWA", 1243)
# Assam is Ahom until 1826, Manipur and Tripura their own until later still
give("ASM", 1258, 1259, 2566)
core("ASM", 1258, 1259, 2566)

# --- the Gulf of Guinea: a Spanish claim nobody is standing on ---------------------
# Portugal ceded Fernando Po, Annobon and the right to trade on the mainland coast to
# Spain by the Treaty of El Pardo in 1778. The expedition sent to take possession was
# a catastrophe: the Conde de Argelejo died within months, fever killed most of the
# garrison, and in 1783 the survivors abandoned the islands and sailed for Brazil.
# From then until the British lease of 1827 and the Spanish return in 1843 there was
# no administration there at all. So Spain holds the title and not the ground, which
# in Victoria II is a core on an unowned province -- and an invitation to go back.
core("SPA", 1955, 1973)
# the Carolines are claimed on the same basis and will not be occupied until the 1880s
core("SPA", 610, 2519)

# --- Arabia: the First Saudi State holds Najd ------------------------------------
# Jabal Shammar came under Diriyah's control in the 1790s and Al-Hasa fell in 1795.
# Mecca does not fall until 1803, so the Hejaz stays with the Sharif.
give("NEJ", 1160, 1158)                   # Hail, Rafha
core("NEJ", 1160, 1158)

prov = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    prov[int(re.match(r"(\d+)", os.path.basename(f)).group(1))] = f

changed = 0
# --- the claim lines of the viceroyalties ------------------------------------------
# A successor republic cannot hold a core its colonial predecessor never claimed. The
# Comancheria is the clearest case: Spain claimed the whole southern plains as part of
# the Provincias Internas, and the eight Comanche provinces that carry a MEX core --
# including Santa Fe, El Paso and Las Cruces, which are Spanish towns -- carried no NSP
# core at all. Spain held the presidios and the Comanche held the plains, which is a
# claim without possession, exactly as in the Gulf of Guinea below.
#
# Done by rule rather than by list: wherever a successor republic has a core, its
# viceroyalty gets one too.
SUCCESSION = {"MEX": "NSP", "PEU": "VPE", "CLM": "VNG", "ARG": "RDP",
              "CHL": "CGC", "BRZ": "EBR", "CUB": "CBA", "PRI": "PTR"}
for _pid, _f in prov.items():
    _head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(_f))[0]
    _have = set(re.findall(r"^\s*add_core\s*=\s*([A-Z]{3})", _head, re.M))
    for _suc, _vic in SUCCESSION.items():
        if _suc in _have and _vic not in _have:
            core(_vic, _pid)


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
log["province files rewritten"] = changed
log["provinces reassigned"] = len(OWN)

# --- who answers to whom ---------------------------------------------------------
# The Barbary regencies were Ottoman in name and self-governing in fact; vassalage is
# the closest thing Victoria II has to that. The Mughal emperor in Delhi is a Maratha
# protege -- Sindhia has held the capital since 1788 and will until Assaye in 1803.
# End dates matter: France takes Algiers in 1830, the Maratha Confederacy falls in
# 1818, and Sindhia loses Delhi at Assaye in 1803. Running any of these to 1936 would
# leave the state with two overlords the moment HPM's own entry begins.
# Algiers, Tunis and Tripoli are handled by barbary_states.py, which gives each its
# own 1800 tag and its own end date; listing them here as well would hand the
# successor tags a second overlord.
DIP = [("vassal", "MAR", "MUG", "the Mughal Emperor at Delhi", "1803.9.23"),
       ("vassal", "MAR", "MAH", "the Maratha house of Kolhapur", "1818.1.1")]
wr(f"{MOD}/history/diplomacy/1800_regencies.txt",
   "\n".join(f"# {a} - {n}\n{k} = {{\n\tfirst = {a}\n\tsecond = {b}\n"
             f"\tstart_date = 1800.1.1\n\tend_date = {e}\n}}\n"
             for k, a, b, n, e in DIP))
log["regencies and protectorates"] = len(DIP)

# --- the Porte's reach ------------------------------------------------------------
# Rather than carving the empire up, give it the weakness it actually had: Egypt under
# the Mamluk beys, the Barbary regencies self-governing, Albanian and Balkan pashas
# obeying when it suited them.
em = f"{MOD}/common/event_modifiers.txt"
s = rd(em)
if "ottoman_decentralisation" not in s:
    wr(em, s.rstrip() + """

ottoman_decentralisation = {
    icon = 8
    tax_efficiency = -0.25
    administrative_efficiency_modifier = -0.20
    global_pop_militancy_modifier = 0.04
    mobilisation_size = -0.03
    supply_consumption = 0.10
}
""")
ev = """country_event = {
    id = 9100400
    title = "EVTNAME9100400"
    desc = "EVTDESC9100400"
    picture = "administration"
    fire_only_once = yes

    trigger = {
        tag = TUR
        year = 1800
        NOT = { year = 1801 }
    }
    mean_time_to_happen = { days = 2 }

    option = {
        name = "EVTOPTA9100400"
        add_country_modifier = { name = ottoman_decentralisation duration = -1 }
    }
}
"""
wr(f"{MOD}/events/1800_Porte.txt", ev)
wr(f"{MOD}/localisation/12_corrections.csv",
   "Key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portuguese;Russian;Finnish;x\n"
   "EVTNAME9100400;The Reach of the Porte;;;;;;;;;;;;;x\n"
   "EVTDESC9100400;The Sultan's writ runs as far as his soldiers do and no further. Egypt "
   "answers to the Mamluk beys, Algiers and Tunis to themselves, and the pashas of Albania "
   "and Rumelia obey when it suits them. The Nizam-i Cedid is meant to change this, and the "
   "janissaries are meant to prevent it.;;;;;;;;;;;;;x\n"
   "EVTOPTA9100400;Govern what can be governed.;;;;;;;;;;;;;x\n"
   "ottoman_decentralisation;Decentralised Administration;;;;;;;;;;;;;x\n")
log["porte modifier"] = 1

for k, v in log.items(): print(f"  {k:<34}{v}")
