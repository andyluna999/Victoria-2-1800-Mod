import json, colorsys
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
L=json.load(open('/mnt/user-data/outputs/HPM_NA_1800_cultures_pops.json'))
N=json.load(open(_os.path.join(_TOOLS, 'names_source.json')))
ALIAS={"AfroAmerican":"afro_american","AfroCaribbean":"afro_caribbean","AngloCanadian":"anglo_canadian",
 "FrenchCanadian":"french_canadian","FrenchCreole":"french_creole","CaliforniaNations":"california_nations",
 "MandanArikara":"mandan_arikara","NezPerce":"nez_perce","TainoRemnant":"taino_remnant"}
G=sorted(set(L['culture_groups'].values())); GH={g:i*360/len(G) for i,g in enumerate(G)}
out={}
for c,g in L['culture_groups'].items():
    mem=sorted([x for x in L['culture_groups'] if L['culture_groups'][x]==g])
    i=mem.index(c); k=max(1,len(mem))
    h=((GH[g]+(i-(k-1)/2)*min(13,105/k))/360)%1
    rr,gg,bb=colorsys.hls_to_rgb(h,0.42+0.06*(i%4),0.58)
    key=ALIAS.get(c,c); s=N.get(key)
    out[c]={"color":[int(rr*255),int(gg*255),int(bb*255)],
            "first":(s or N["_fallback"])["first"],"last":(s or N["_fallback"])["last"],
            "sourced":bool(s)}
out["_fallback"]={"color":[130,130,130],**N["_fallback"],"sourced":False}
json.dump(out,open(_os.path.join(_WORK, 'culture_names.json'),'w'))
pre={'british','cree','dixie','french','irish','metis','north_german','portuguese','russian','scottish','spanish','yankee'}
left=[c for c,v in out.items() if not v["sourced"] and c!="_fallback" and c not in pre]
print(f"{len(out)-1} cultures; new ones still on fallback names:", left or "none")
