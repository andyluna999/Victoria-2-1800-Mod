"""A country needs a party for every ideology its Upper House can turn.

The run died on 4 January 1817, three days after the Upper House rearranged and three
weeks after the government changed hands -- and the viceroyalties had exactly two
parties between them, conservative and reactionary. Two hundred and sixty-two of the
mod's countries have seven. Mexico has twelve.

When consciousness rises the Upper House turns liberal, and Victoria II then looks for
a liberal party to form a government. For a country that has none there is nothing to
find. That is the sequence the log shows: party change, Upper House rearranged, crash.

So the colonial tags get the standard spread, dated the way Mexico's are -- the
liberals and anarcho-liberals present from the start because the creoles reading
Raynal in 1800 are precisely who they are, the socialists and communists from 1848,
the fascists from 1900. Their policies are the viceroyalty's own: protectionist,
moralist, and nobody much interested in extending the franchise.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections

MOD = _BUILD
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# ideology -> (start, end, social, economic, trade, religious, citizenship, war)
SPREAD = [
 ("liberal",         1799, "no_position_set", "laissez_faire",  "free_trade",
                           "secularized", "limited_citizenship", "anti_military"),
 ("anarcho_liberal", 1799, "no_position_set", "laissez_faire",  "free_trade",
                           "secularized", "full_citizenship",    "pacifism"),
 ("socialist",       1848, "pro_regulation", "state_capitalism", "protectionism",
                           "secularized", "full_citizenship",    "anti_military"),
 ("communist",       1848, "pro_regulation", "planned_economy", "protectionism",
                           "pro_atheism",  "full_citizenship",   "pro_military"),
 ("fascist",         1900, "pro_regulation", "state_capitalism", "protectionism",
                           "moralism",     "residency",          "jingoism"),
]
NAMES = {
 "liberal": "Partido Liberal", "anarcho_liberal": "Club de los Exaltados",
 "socialist": "Partido Socialista", "communist": "Partido Comunista",
 "fascist": "Union Nacional",
}
TAGS = ["NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR", "EBR"]
LOC = []

for f in glob.glob(f"{MOD}/common/countries/*.txt"):
    s = rd(f)
    have = set(re.findall(r'name\s*=\s*"([A-Z]{3})_', s))
    tag = next((t for t in TAGS if t in have), None)
    if not tag: continue
    present = set(re.findall(rf'name\s*=\s*"{tag}_(\w+)"', s))
    add = ""
    for ide, yr, soc, eco, tra, rel, cit, war in SPREAD:
        if ide in present: continue
        add += (f'\nparty = {{\n\tname = "{tag}_{ide}"\n'
                f'\tstart_date = {yr}.1.1\n\tend_date = 2000.1.1\n\n'
                f'\tideology = {ide}\n\n'
                f'\tsocial_policy = {soc}\n\teconomic_policy = {eco}\n'
                f'\ttrade_policy = {tra}\n\treligious_policy = {rel}\n'
                f'\tcitizenship_policy = {cit}\n\twar_policy = {war}\n}}\n')
        LOC.append((f"{tag}_{ide}", NAMES[ide]))
        log["parties added"] += 1
    if add:
        wr(f, s.rstrip("\n") + "\n" + add)
        log["countries given a full spread"] += 1

if LOC:
    os.makedirs(f"{MOD}/localisation", exist_ok=True)
    wr(f"{MOD}/localisation/32_colonial_parties.csv",
       "\n".join(f"{k};{v};;;;;;;;;;;;x" for k, v in LOC) + "\n")

# verify
short = []
for f in glob.glob(f"{MOD}/common/countries/*.txt"):
    s = rd(f)
    for t in TAGS:
        ids = set(re.findall(rf'name\s*=\s*"{t}_\w+"[\s\S]{{0,200}}?ideology\s*=\s*(\w+)', s))
        if ids and len(ids) < 5: short.append(f"{t}:{sorted(ids)}")
log["colonial tags still short"] = len(short)
for k, v in sorted(log.items()): print(f"  {k:<34}{v}")
