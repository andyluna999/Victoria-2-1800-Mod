"""Build the World Builder payload from the BUILT mod, so the tool and the game agree."""
import json, re, os, glob, collections
MOD="/home/claude/build/HPM"; W="/home/claude/work"
OLD=json.load(open(f"{W}/world_data.json"))
def rd(p): return re.sub(r"#.*","",open(p,encoding="cp1252",errors="replace").read())

# ---- cultures, groups and colours, straight out of cultures.txt
src=rd(f"{MOD}/common/cultures.txt")
cgroup={}; ccolor={}; depth=0; cur=None; cults=[]
for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}",src):
    t=m.group(0)
    if t=="}": depth-=1
    elif t=="{": depth+=1
    else:
        n=m.group(1)
        if depth==0: cur=n
        elif depth==1 and n not in ("color","leader","unit","union","is_overseas"):
            cgroup[n]=cur; cults.append((n,m.end()))
        depth+=1
for n,pos in cults:
    c=re.search(r"color\s*=\s*\{\s*(\d+)\s+(\d+)\s+(\d+)",src[pos:pos+400])
    ccolor[n]=[int(c.group(i)) for i in (1,2,3)] if c else [130,130,130]
religions=sorted(set(re.findall(r"^\s{1,8}([a-z_0-9]+)\s*=\s*\{",rd(f"{MOD}/common/religion.txt"),re.M)))

# ---- countries
reg=rd(f"{MOD}/common/countries.txt")
COU={}
for m in re.finditer(r'^\s*([A-Z]{3})\s*=\s*"?([^"\n]+?)"?\s*$',reg,re.M):
    tag,rel=m.group(1),m.group(2).strip()
    p=os.path.join(MOD,"common",rel)
    col=[130,130,130]
    if os.path.exists(p):
        c=re.search(r"^\s*color\s*=\s*\{\s*(\d+)\s+(\d+)\s+(\d+)",rd(p),re.M)
        if c: col=[int(c.group(i)) for i in (1,2,3)]
    COU[tag]={"name":tag,"color":col,"prim":"","acc":[]}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b=os.path.basename(f)[:-4]
    if " - " not in b: continue
    tag,nm=b.split(" - ",1); tag=tag.strip()
    if tag not in COU: continue
    head=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",rd(f))[0]
    COU[tag]["name"]=nm.strip()
    pm=re.search(r"primary_culture\s*=\s*([a-z_0-9]+)",head)
    if pm: COU[tag]["prim"]=pm.group(1)
    COU[tag]["acc"]=sorted(set(re.findall(r"^\s*culture\s*=\s*([a-z_0-9]+)",head,re.M)))

# ---- provinces
prov={}
files={}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid=int(re.match(r"(\d+)",os.path.basename(f)).group(1)); files[pid]=f
for pid,f in files.items():
    o=OLD["prov"].get(str(pid))
    if not o: continue
    head=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",rd(f))[0]
    g=lambda k,d="": (re.search(rf"^\s*{k}\s*=\s*([A-Za-z_0-9]+)",head,re.M) or [None,d])[1] \
        if re.search(rf"^\s*{k}\s*=\s*([A-Za-z_0-9]+)",head,re.M) else d
    gi=lambda k: int(re.search(rf"^\s*{k}\s*=\s*(\d+)",head,re.M).group(1)) if re.search(rf"^\s*{k}\s*=\s*(\d+)",head,re.M) else 0
    prov[pid]={"n":o["n"],"rg":o["rg"],"ct":o["ct"],"px":o["px"],
               "o":g("owner"),"c":g("controller"),
               "cr":sorted(set(re.findall(r"^\s*add_core\s*=\s*([A-Z]{3})",head,re.M))),
               "g":g("trade_goods"),"lr":gi("life_rating"),"col":gi("colonial"),
               "nb":gi("naval_base"),"ft":gi("fort"),"rr":gi("railroad")}

# ---- pops
PT=OLD["pop_types"]
allc=sorted(set(cgroup)); ci={c:i for i,c in enumerate(allc)}
ri={r:i for i,r in enumerate(religions)}; ti={t:i for i,t in enumerate(PT)}
pops=[]
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s=rd(f)
    for pm in re.finditer(r"^(\d+)\s*=\s*\{",s,re.M):
        pid=int(pm.group(1)); i=pm.end(); d=1
        while i<len(s) and d:
            if s[i]=="{": d+=1
            elif s[i]=="}": d-=1
            i+=1
        for em in re.finditer(r"\b([a-z_]+)\s*=\s*\{\s*culture\s*=\s*([a-z_0-9]+)\s*religion\s*=\s*([a-z_0-9]+)\s*size\s*=\s*(\d+)",
                              re.sub(r"\s+"," ",s[pm.end():i-1])):
            t,c,r,sz=em.groups()
            if t in ti and c in ci and r in ri: pops.append([pid,ti[t],ci[c],ri[r],int(sz)])

# overlord relationships, read back out of the diplomacy file we wrote
dips=sorted(glob.glob(f"{MOD}/history/diplomacy/1800_*.txt"))
INV={"vassal":"colony","substate":"substate","union":"personal_union"}
for dip in dips:
    for m in re.finditer(r"(vassal|substate|union)\s*=\s*\{[^}]*?first\s*=\s*([A-Z]{3})[^}]*?second\s*=\s*([A-Z]{3})",rd(dip),re.S):
        k,first,second=m.groups()
        if second in COU:
            COU[second]["over"]=first; COU[second]["rel"]=INV.get(k,"colony")
try:
    META=json.load(open(f"{W}/world_meta.json"))
except Exception:
    META={}
for tag,v in META.items():
    if tag in COU:
        COU[tag]["becomes"]=v.get("becomes","")
        COU[tag]["iprim"]=v.get("independence_primary","")
        COU[tag]["iacc"]=v.get("independence_accepted",[])

payload=dict(w=OLD["w"],h=OLD["h"],cultures=allc,culture_group=cgroup,culture_color=ccolor,
             religions=religions,pop_types=PT,goods=OLD["goods"],pops=pops,
             prov={str(k):v for k,v in prov.items()},countries=COU,sea=OLD["sea"],
             index_png=OLD["index_png"],border_png=OLD["border_png"])
js=json.dumps(payload,separators=(",",":"))
open(f"{W}/world_live.json","w").write(js)
print(f"  cultures {len(allc)}  colours {len(ccolor)}  countries {len(COU)}")
print(f"  provinces {len(prov)}  pops {len(pops)}  religions {len(religions)}")
print(f"  payload {round(len(js)/1024/1024,2)} MB")
