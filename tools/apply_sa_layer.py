"""Apply the South America 1800 layer to the built mod: cultures, pops, country cultures."""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, collections
MOD=_BUILD; W=_WORK
SA=json.load(open(f"{W}/sa1800.json"))
PAL=json.load(open(f"{W}/palette.json"))
NAMES=json.load(open(f"{_TOOLS}/names_source.json"))
L=json.load(open(f"{W}/world_live.json"))
def rd(p): return open(p,encoding="cp1252",errors="replace").read()
def wr(p,t):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,"w",encoding="cp1252",errors="replace",newline="\n").write(t)
def key(c): return re.sub(r"(?<!^)(?=[A-Z])","_",c).lower().replace("__","_")
log=collections.Counter()

GROUPS_NEW={"andean":"nativeamerican","amazonian_peoples":"nativeamerican","southern_cone":"nativeamerican"}
src=rd(f"{MOD}/common/cultures.txt")
have,depth=set(),0
for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}",re.sub(r"#.*","",src)):
    t=m.group(0)
    if t=="}": depth-=1
    elif t=="{": depth+=1
    else:
        if depth==1 and m.group(1) not in ("color","leader","unit","union","is_overseas","primary"):
            have.add(m.group(1))
        depth+=1
bygroup=collections.defaultdict(list)
for c,g in SA["culture_groups"].items():
    if key(c) not in have: bygroup[g].append(c)
out=src.rstrip()+"\n"
for g,ms in sorted(bygroup.items()):
    blocks=""
    for c in sorted(ms):
        n=NAMES.get(key(c),NAMES["_fallback"]); col=PAL.get(c,[130,130,130])
        blocks+=(f"\t\t{key(c)} = {{\n\t\t\tcolor = {{ {col[0]} {col[1]} {col[2]} }}\n"
                 f"\t\t\tfirst_names = {{ {' '.join(n['first'])} }}\n"
                 f"\t\t\tlast_names = {{ {' '.join(n['last'])} }}\n\t\t}}\n")
        log["cultures added"]+=1
    if re.search(rf"^{g}\s*=\s*\{{",out,re.M):
        m=re.search(rf"^{g}\s*=\s*\{{",out,re.M); i,d=m.end(),1
        while i<len(out) and d:
            if out[i]=="{": d+=1
            elif out[i]=="}": d-=1
            i+=1
        out=out[:i-1]+blocks+out[i-1:]
    else:
        out+=f"\n{g} = {{\n\tleader = {GROUPS_NEW.get(g,'european')}\n\tis_overseas = no\n\tunit = NativeGC\n{blocks}}}\n"
wr(f"{MOD}/common/cultures.txt",out)

# ---- pops: replace every South American province
files={}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    files[int(re.match(r"(\d+)",os.path.basename(f)).group(1))]=f
saset={int(k) for k,v in L["prov"].items() if v["ct"]=="south_america"}
keep=collections.defaultdict(list)
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s=rd(f); stem=os.path.basename(f)
    for pm in re.finditer(r"^(\d+)\s*=\s*\{",s,re.M):
        pid=int(pm.group(1)); i=pm.end(); d=1
        while i<len(s) and d:
            if s[i]=="{": d+=1
            elif s[i]=="}": d-=1
            i+=1
        if pid not in saset: keep[stem].append((pid,s[pm.start():i]))
new=collections.defaultdict(list)
for p in SA["pops"]:
    pid=int(p["province"]); f=files.get(pid)
    if not f: continue
    new[os.path.basename(os.path.dirname(f))+".txt"].append(p)
for stem,rows in new.items():
    by=collections.defaultdict(list)
    for p in rows: by[int(p["province"])].append(p)
    txt=""
    for pid in sorted(by):
        txt+=f"{pid} = {{\n"
        for p in by[pid]:
            txt+=(f"\t{p['type']} = {{\n\t\tculture = {key(p['culture'])}\n"
                  f"\t\treligion = {p['religion']}\n\t\tsize = {p['size']}\n\t}}\n")
        txt+="}\n"
        log["sa provinces written"]+=1
    old="\n".join(b for _,b in sorted(keep.get(stem,[])))
    wr(f"{MOD}/history/pops/1800.1.1/{stem}",(old+"\n\n" if old else "")+txt)

# ---- country cultures
CC={"EBR":("portuguese",["brasileiro"]),"BRZ":("brasileiro",["afro_brazilian","portuguese"]),
 "VPE":("spanish",["criollo"]),"PEU":("mestizo",["criollo","quechua","aymara"]),
 "VNG":("spanish",["criollo"]),"CLM":("mestizo",["criollo","chibcha"]),
 "VNZ":("mestizo",["criollo"]),"ECU":("mestizo",["criollo","quechua"]),
 "CGC":("spanish",["criollo"]),"CHL":("criollo",["mestizo"]),
 "RDP":("spanish",["criollo"]),"ARG":("criollo",["mestizo"]),
 "BOL":("mestizo",["criollo","quechua","aymara"]),"PRG":("guarani",["mestizo","criollo"]),
 "URU":("criollo",["mestizo"]),"MAP":("mapuche",[]),"POR":("portuguese",["brasileiro"]),
 "LPL":("criollo",["mestizo"]),"PBC":("mestizo",["criollo","quechua","aymara"]),
 "SPU":("mestizo",["criollo","quechua"]),"GUY":("afro_caribbean",["british"])}
for tag,(prim,acc) in CC.items():
    g=glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s=rd(g[0])
    parts=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",s)
    head,tail=parts[0],("\n"+"\n".join(parts[1:]) if len(parts)>1 else "")
    head=re.sub(r"^\s*culture\s*=\s*[A-Za-z_0-9]+\s*\n","",head,flags=re.M)
    head=re.sub(r"^\s*primary_culture\s*=.*$",f"primary_culture = {key(prim)}",head,count=1,flags=re.M)
    head=re.sub(r"(^primary_culture\s*=.*\n)",r"\1"+"".join(f"culture = {key(a)}\n" for a in acc),
                head,count=1,flags=re.M)
    wr(g[0],head+tail); log["country cultures set"]+=1
for k,v in log.items(): print(f"  {k:<32}{v}")
