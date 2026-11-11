"""Governments for 1 January 1800, per the Narrative & Event Plan section 3.

Several are still HPM's 1836 settings, which describe a world that has not happened:
France as the July Monarchy, the Netherlands as the Kingdom under Willem I, Spain and
Sweden as constitutional monarchies, Portugal under a liberal ministry.
"""
import re, glob
MOD="/home/claude/build/HPM"
# ruling party on the start date. The sister republics are liberal because that is
# what they were; Portugal is conservative because the liberal ministries are decades off.
PARTY={"FRA":"FRA_liberal","NET":"HOL_liberal","SWI":"SWI_liberal","LIG":"LIG_liberal",
       "POR":"POR_conservative","SPA":"SPA_conservative","SWE":"SWE_conservative",
       "IRE":"IRE_conservative","SIC":"SIC_conservative","TUS":"TUS_conservative"}
GOV={
 "FRA":("presidential_dictatorship","nv_liberty"),  # the Consulate, seven weeks old
 "NET":("democracy","nv_liberty"),                  # the Batavian Republic
 "SWI":("democracy","nv_liberty"),                  # the Helvetic Republic
 "LIG":("democracy","nv_liberty"),                  # the Ligurian Republic
 "SPA":("absolute_monarchy","nv_order"),            # Charles IV, Godoy dominant
 "POR":("absolute_monarchy","nv_order"),            # Maria I incapacitated, Prince Regent John
 "SWE":("absolute_monarchy","nv_order"),            # Gustav IV Adolf
 "IRE":("hms_government","nv_liberty"),             # a kingdom in union with Britain
}
done=[]
for tag,(gov,nv) in GOV.items():
    want=PARTY.get(tag)
    g=glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s=open(g[0],encoding="cp1252",errors="replace").read()
    parts=re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",s)
    head,tail=parts[0],("\n"+"\n".join(parts[1:]) if len(parts)>1 else "")
    before=head
    head=re.sub(r"^\s*government\s*=.*$",f"government = {gov}",head,count=1,flags=re.M)
    head=re.sub(r"^\s*nationalvalue\s*=.*$",f"nationalvalue = {nv}",head,count=1,flags=re.M)
    head=re.sub(r"^\s*last_election\s*=.*$","last_election = 1799.1.1",head,count=1,flags=re.M)
    if want:
        # only set it if that party really exists in this country's own file
        reg=open(f"{MOD}/common/countries.txt",encoding="cp1252",errors="replace").read()
        m=re.search(rf'^\s*{tag}\s*=\s*"?([^"\n]+?)"?\s*$',reg,re.M)
        if m:
            cf=f"{MOD}/common/"+m.group(1).strip()
            try:
                if f'"{want}"' in open(cf,encoding="cp1252",errors="replace").read():
                    head=re.sub(r"^\s*ruling_party\s*=.*$",f"ruling_party = {want}",head,count=1,flags=re.M)
            except Exception: pass
    if head!=before:
        open(g[0],"w",encoding="cp1252",errors="replace",newline="\n").write(head+tail)
        done.append(f"{tag}={gov}")
print("  1800 governments set              "+", ".join(done))
