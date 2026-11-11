"""Re-apply the curated 1800 province variables AFTER the export is compiled.

write_export rewrites province files from the World Builder export, and that export
predates the 1800 province-variable pass -- so running it later silently restored
Jamaica's sulphur and ten railroads twenty-five years early. This runs last.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os
MOD=_BUILD
V={int(k):v for k,v in json.load(open(f"{_WORK}/na_province_vars.json")).items()}
files={}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    files[int(re.match(r"(\d+)",os.path.basename(f)).group(1))]=f
n=0
for pid,vals in V.items():
    f=files.get(pid)
    if not f: continue
    s=open(f,encoding="cp1252",errors="replace").read()
    parts=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",s)
    head,tail=parts[0],("\n"+"\n".join(parts[1:]) if len(parts)>1 else "")
    for key,val in vals.items():
        head=re.sub(rf"^\s*{key}\s*=.*\n?","",head,flags=re.M)
        if val not in (0,"0"):
            head=head.rstrip("\n")+f"\n{key} = {val}\n"
    open(f,"w",encoding="cp1252",errors="replace",newline="\n").write(head.rstrip("\n")+"\n"+tail)
    n+=1
# the colonial level must survive this too
ORIG={}
for f in glob.glob(f"{_SRC}/history/provinces/*/*.txt"):
    pid=int(re.match(r"(\d+)",os.path.basename(f)).group(1))
    m=re.search(r"^\s*colonial\s*=\s*(\d+)",
                re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                         re.sub(r"#.*","",open(f,encoding="cp1252",errors="replace").read()))[0],re.M)
    if m: ORIG[pid]=int(m.group(1))
fixed=0
for pid,f in files.items():
    s=open(f,encoding="cp1252",errors="replace").read()
    m=re.search(r"^\s*colonial\s*=\s*(\d+)",s,re.M)
    if m and ORIG.get(pid,0)>int(m.group(1)):
        s=re.sub(r"^\s*colonial\s*=\s*\d+",f"colonial = {ORIG[pid]}",s,count=1,flags=re.M)
        open(f,"w",encoding="cp1252",errors="replace",newline="\n").write(s); fixed+=1
# no railway existed anywhere on earth before 1825, so this is global, not regional
rr=0
for pid,f in files.items():
    s_=open(f,encoding="cp1252",errors="replace").read()
    parts=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",s_)
    head,tail=parts[0],("\n"+"\n".join(parts[1:]) if len(parts)>1 else "")
    if re.search(r"^\s*railroad\s*=\s*[1-9]",head,re.M):
        head=re.sub(r"^\s*railroad\s*=.*\n?","",head,flags=re.M)
        open(f,"w",encoding="cp1252",errors="replace",newline="\n").write(head.rstrip("\n")+"\n"+tail)
        rr+=1
print(f"  railroads cleared worldwide          {rr}")
print(f"  1800 province variables re-applied   {n}")
print(f"  colonial levels restored             {fixed}")
