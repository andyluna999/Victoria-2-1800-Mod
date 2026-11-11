"""Remove the disabled 1861 start: a full duplicate world state for a commented-out
bookmark that would be meaningless once the 1800 timeline diverges."""
import shutil, os, re, glob
MOD="/home/claude/build/HPM"
n=0
d=f"{MOD}/history/pops/1861.4.14"
if os.path.isdir(d):
    n=len(os.listdir(d)); shutil.rmtree(d)
blocks=0
for pat in ("history/provinces/*/*.txt","history/countries/*.txt"):
    for f in glob.glob(f"{MOD}/{pat}"):
        s=open(f,encoding="cp1252",errors="replace").read()
        out,depth,keep,i,changed=[],0,True,0,False
        lines=s.split("\n"); res=[]; skip=0
        for ln in lines:
            if skip>0:
                skip+= ln.count("{")-ln.count("}")
                if skip<=0: skip=0
                continue
            if re.match(r"^\s*186[01]\.\d+\.\d+\s*=\s*\{", ln):
                skip=ln.count("{")-ln.count("}"); blocks+=1; changed=True
                if skip<=0: skip=0
                continue
            res.append(ln)
        if changed:
            open(f,"w",encoding="cp1252",errors="replace",newline="\n").write("\n".join(res))
print(f"  1861 pop files removed: {n}")
print(f"  1860/61 dated blocks removed: {blocks}")
