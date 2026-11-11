"""Deeper sweep than lint.py: cross-file references and value validity."""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, csv, collections, json
import sys
SRC=_SRC
MOD=os.environ.get("AUDIT_TARGET",_BUILD) if False else None
import os as _os
MOD=_os.environ.get("AUDIT_TARGET",_BUILD)
BF=f"{_TOOLS}/audit_baseline.json"
BASE=json.load(open(BF)) if (os.path.exists(BF) and not _os.environ.get("AUDIT_RECORD")) else {}
REC={}
def rd(p): return re.sub(r"#.*","",open(p,encoding="cp1252",errors="replace").read())
bad=0
def chk(n, ok, d=""):
    global bad
    d=str(d); REC[n]=d
    if ok: print("  ok    "+n+(("  -> "+d) if d else "")); return
    if BASE.get(n)==d: print("  known "+n+"  -> same in pristine HPM"); return
    print("  BUG   "+n+(("  -> "+d) if d else "")); bad+=1

# reference sets
tags=set(re.findall(r"^\s*([A-Z]{3})\s*=",rd(f"{MOD}/common/countries.txt"),re.M))
goods=set(re.findall(r"^\s{1,8}([a-z_0-9]+)\s*=\s*\{",rd(f"{MOD}/common/goods.txt"),re.M))
rels=set(re.findall(r"^\s{1,8}([a-z_0-9]+)\s*=\s*\{",rd(f"{MOD}/common/religion.txt"),re.M))
govs=set(re.findall(r"^([a-z_0-9]+)\s*=\s*\{",rd(f"{MOD}/common/governments.txt"),re.M))
nvs=set(re.findall(r"^([a-z_0-9]+)\s*=\s*\{",rd(f"{MOD}/common/nationalvalues.txt"),re.M))
ptypes={os.path.basename(f)[:-4] for f in glob.glob(f"{MOD}/poptypes/*.txt")}
defn={int(r[0]) for r in csv.reader(open(f"{MOD}/map/definition.csv",encoding="latin-1"),delimiter=";") if r and r[0].isdigit()}
sea=set(int(x) for x in re.search(r"sea_starts\s*=\s*\{(.*?)\}",rd(f"{MOD}/map/default.map"),re.S).group(1).split())
gfxc=set(re.findall(r"^\s*([A-Za-z]+GC)\s*=",rd(f"{SRC}/common/countries.txt"),re.M))

# --- province histories
owners=collections.Counter(); cores=collections.Counter(); colvals=collections.Counter()
badgoods=[]; badtag=[]; seaprov=[]; provown={}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid=int(re.match(r"(\d+)",os.path.basename(f)).group(1)); s=rd(f)
    head=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",s)[0]
    o=re.search(r"\bowner\s*=\s*([A-Z]{3})",head)
    c=re.search(r"\bcontroller\s*=\s*([A-Z]{3})",head)
    g=re.search(r"\btrade_goods\s*=\s*([a-z_0-9]+)",head)
    col=re.search(r"\bcolonial\s*=\s*(\d+)",head)
    if o: owners[o.group(1)]+=1; provown[pid]=o.group(1)
    for t in re.findall(r"\badd_core\s*=\s*([A-Z]{3})",head): cores[t]+=1
    for t in filter(None,[o and o.group(1), c and c.group(1)]+re.findall(r"\badd_core\s*=\s*([A-Z]{3})",head)):
        if t not in tags: badtag.append((pid,t))
    if g and g.group(1) not in goods: badgoods.append((pid,g.group(1)))
    if col: colvals[col.group(1)]+=1
    if pid in sea and o: seaprov.append(pid)
chk("every owner/controller/core tag is registered", not badtag, sorted(set(badtag))[:6])
chk("every trade good exists", not badgoods, badgoods[:6])
chk("no sea province has an owner", not seaprov, seaprov[:6])
print(f"       colonial values in use: {dict(colvals)}")

# --- colonial level preserved against pristine HPM
lost=[]
for f in glob.glob(f"{SRC}/history/provinces/*/*.txt"):
    pid=int(re.match(r"(\d+)",os.path.basename(f)).group(1))
    # only the start-date block counts; a colonial=2 inside an 1861 block is not
    # something the 1800 start ever reads
    _head=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",rd(f))[0]
    m=re.search(r"^\s*colonial\s*=\s*(\d+)",_head,re.M)
    if m and m.group(1)=="2":
        n=glob.glob(f"{MOD}/history/provinces/*/{os.path.basename(f)}")
        if n:
            m2=re.search(r"^\s*colonial\s*=\s*(\d+)",
                         re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",rd(n[0]))[0],re.M)
            if not m2 or m2.group(1)!="2": lost.append(pid)
chk("colonial level 2 not downgraded", not lost, f"{len(lost)} provinces lost level 2, e.g. {lost[:6]}")

# --- country histories
badgov=[];badrel=[];badnv=[];badcap=[];badparty=[];badgfx=[];dupacc=[]
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    tag=os.path.basename(f)[:3]; s=rd(f)
    head=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",s)[0]
    for pat,store,ref in ((r"government\s*=\s*([a-z_]+)",badgov,govs),
                          (r"\breligion\s*=\s*([a-z_]+)",badrel,rels),
                          (r"nationalvalue\s*=\s*([a-z_]+)",badnv,nvs)):
        m=re.search(pat,head)
        if m and m.group(1) not in ref: store.append((tag,m.group(1)))
    cap=re.search(r"capital\s*=\s*(\d+)",head)
    if cap and int(cap.group(1)) not in defn: badcap.append((tag,cap.group(1)))
    prim=re.search(r"primary_culture\s*=\s*(\w+)",head)
    accs=re.findall(r"^\s*culture\s*=\s*(\w+)",head,re.M)
    if prim and prim.group(1) in accs: dupacc.append(tag)
    rp=re.search(r"ruling_party\s*=\s*(\w+)",head)
    if rp:
        rel=re.search(rf'^\s*{tag}\s*=\s*"?([^"\n]+?)"?\s*$',rd(f"{MOD}/common/countries.txt"),re.M)
        if rel:
            cf=os.path.join(MOD,"common",rel.group(1).strip())
            if os.path.exists(cf) and f'"{rp.group(1)}"' not in rd(cf): badparty.append((tag,rp.group(1)))
chk("every government type exists", not badgov, badgov[:6])
chk("every state religion exists", not badrel, badrel[:6])
chk("every national value exists", not badnv, badnv[:6])
chk("every capital is a real province", not badcap, badcap[:6])
chk("ruling_party is defined in the country file", not badparty, badparty[:6])
chk("primary culture is not also listed as accepted", not dupacc, dupacc[:6])

for f in glob.glob(f"{MOD}/common/countries/*.txt"):
    m=re.search(r"graphical_culture\s*=\s*(\w+)",rd(f))
    if m and m.group(1) not in gfxc: badgfx.append((os.path.basename(f),m.group(1)))
chk("every graphical_culture is known", not badgfx, badgfx[:6])

# --- flags
noflag=[t for t in sorted(tags) if not os.path.exists(f"{MOD}/gfx/flags/{t}.tga")]
chk("every tag has a base flag", not noflag, noflag[:8])

# --- pops
seen=collections.defaultdict(list); badpt=[]; badpr=[]; zero=0
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s=rd(f)
    for m in re.finditer(r"^(\d+)\s*=\s*\{",s,re.M): seen[int(m.group(1))].append(os.path.basename(f))
    for m in re.finditer(r"^\s*([a-z_]+)\s*=\s*\{\s*\n\s*culture",s,re.M):
        if m.group(1) not in ptypes: badpt.append(m.group(1))
    for m in re.finditer(r"religion\s*=\s*([a-z_]+)",s):
        if m.group(1) not in rels: badpr.append(m.group(1))
    zero+=len(re.findall(r"size\s*=\s*0\b",s))
dup={k:v for k,v in seen.items() if len(v)>1}
chk("no province is defined in two pop files", not dup, list(dup.items())[:3])
chk("every pop type is valid", not badpt, sorted(set(badpt))[:6])
chk("every pop religion exists", not badpr, sorted(set(badpr))[:6])
chk("no zero-size pops", zero==0, zero)
owned_nopop=[p for p,t in provown.items() if p not in seen and p not in sea]
chk("every owned land province has pops", not owned_nopop, f"{len(owned_nopop)} e.g. {owned_nopop[:6]}")

# --- localisation
keys=collections.Counter()
for f in glob.glob(f"{MOD}/localisation/*.csv"):
    for ln in open(f,encoding="cp1252",errors="replace"):
        if ";" in ln: keys[ln.split(";")[0]]+=1
# Base-game tags take their names from Victoria II's own localisation, which is not in
# this folder -- Afghanistan has always been named by the game and not by HPM. Only
# tags our own content creates need a name from us.
_ours = set()
for _f in glob.glob(f"{_TOOLS}/*.py"):
    _ours |= set(re.findall(r'"([A-Z]{3})"\s*:\s*\(', open(_f).read()))
_pristine = {os.path.basename(x).split(" - ")[0].strip()
             for x in glob.glob(f"{_SRC}/history/countries/*.txt")
             if " - " in os.path.basename(x)}
missloc=[t for t in sorted(tags)
         if keys.get(t,0)==0 and t not in _pristine]
chk("every tag we invent has a localised name", not missloc, missloc[:8])

if _os.environ.get("AUDIT_RECORD"):
    json.dump(REC, open(BF,"w"), indent=1); print("\nbaseline recorded")
print(f"\n{'NO NEW BUGS' if not bad else str(bad)+' NEW BUG(S)'}")
