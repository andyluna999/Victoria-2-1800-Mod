import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections
MOD=_BUILD
log=collections.Counter()
def rd(p): return open(p,encoding="cp1252",errors="replace").read()
def wr(p,t): open(p,"w",encoding="cp1252",errors="replace",newline="\n").write(t)

# A regiment is filled only from a soldier pop of an ACCEPTED culture. New Spain's
# soldier pops are 87% mestizo, Maya, Nahua and Miskito, so its army existed on paper
# and could not be manned -- the same bug as the empty garrisons, one layer down.
#
# The historical answer is the right one: the Bourbon colonial army WAS creole and
# mestizo. The militia regiments that fought for the King at Calderon were raised from
# exactly these people, and the viceroyalty treated them as subjects of the Crown. So
# the viceroyalties accept the castas, which is both accurate and what makes them
# playable. Peninsular Spain does not -- that distinction is the whole grievance.
EXTRA = {
 "NSP": ["mestizo", "nahua", "maya", "zapotec", "mixtec"],
 "VPE": ["mestizo", "quechua", "aymara"],
 "VNG": ["mestizo", "chibcha"],
 "RDP": ["mestizo", "guarani"],
 "CGC": ["mestizo", "mapuche"],
 "CBA": ["mestizo", "afro_caribbean"],
 "PTR": ["mestizo", "afro_caribbean"],
 "EBR": ["mestizo", "afro_caribbean"],
 "MEX": ["criollo", "nahua", "maya", "zapotec", "mixtec"],
 "PEU": ["criollo", "quechua", "aymara"],
 "CLM": ["criollo", "chibcha"],
 "ARG": ["mestizo", "guarani"],
 "CHL": ["mestizo", "mapuche"],
}
# only cultures the game actually defines
defined=set()
for f in glob.glob(f"{MOD}/common/cultures.txt"):
    # cultures.txt mixes tabs and four-space indentation; match either
    defined |= set(re.findall(r"^(?:\t\t|    )([a-z_]+)\s*=\s*\{", rd(f), re.M))
for tag, cults in EXTRA.items():
    g=glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s=rd(g[0])
    parts=re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n"+"\n".join(parts[1:]) if len(parts)>1 else "")
    prim=re.search(r"^\s*primary_culture\s*=\s*(\w+)", head, re.M)
    have=set(re.findall(r"^\s*culture\s*=\s*(\w+)", head, re.M))
    if prim: have.add(prim.group(1))
    add=""
    for c in cults:
        if c in have: continue
        if defined and c not in defined: continue
        add += f"culture = {c}\n"
        log["cultures accepted"]+=1
    if add:
        head=re.sub(r"(^\s*primary_culture\s*=.*\n)", r"\1"+add, head, count=1, flags=re.M)
        wr(g[0], head.rstrip("\n")+"\n"+tail)
        log["countries changed"]+=1

# and a viceroyalty is not a nothing: give the colonies real prestige
PRES={"NSP":5,"VPE":4,"VNG":3,"RDP":2,"CGC":1,"CBA":2,"PTR":1,"EBR":5}
for tag,v in PRES.items():
    g=glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s=rd(g[0])
    if re.search(r"^prestige\s*=\s*0\s*$", s, re.M):
        wr(g[0], re.sub(r"^prestige\s*=\s*0\s*$", f"prestige = {v}", s, count=1, flags=re.M))
        log["prestige given"]+=1
for k,v in sorted(log.items()): print(f"  {k:<26}{v}")
