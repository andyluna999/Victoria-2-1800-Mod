"""Prestige for 1800 rather than 1836.

Victoria II gives only Great Powers a sphere of influence. Spain and Portugal carry
HPM's 1836 prestige, set after they had lost their empires -- Portugal sits at 10.
In 1800 both still held the Americas. Without this, Spain is unlikely to make the
eight and Portugal certainly cannot, so neither could ever sphere its own colonies.
"""
import re, glob
MOD="/home/claude/build/HPM"
# 1800 standing: Britain and France first, then Russia and Austria, then Prussia,
# Spain and the Ottomans. The United States was a minor power, not a near-peer.
P1800={"ENG":130,"FRA":125,"RUS":115,"AUS":100,"SPA":95,"TUR":80,"PRU":75,
       "POR":55,"NET":40,"SWE":30,"DEN":25,"USA":20,"SAR":20,"TUS":10}
done=[]
for tag,val in P1800.items():
    g=glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s=open(g[0],encoding="cp1252",errors="replace").read()
    parts=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",s)
    head,tail=parts[0],("\n"+"\n".join(parts[1:]) if len(parts)>1 else "")
    if re.search(r"^\s*prestige\s*=",head,re.M):
        head=re.sub(r"^\s*prestige\s*=.*$",f"prestige = {val}",head,count=1,flags=re.M)
    else:
        head=re.sub(r"(^\s*civilized\s*=.*\n)",r"\1"+f"prestige = {val}\n",head,count=1,flags=re.M)
    open(g[0],"w",encoding="cp1252",errors="replace",newline="\n").write(head+tail)
    done.append(f"{tag}={val}")
print("  1800 prestige set                   "+", ".join(done))
