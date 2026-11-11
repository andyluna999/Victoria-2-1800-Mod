"""Spanish Louisiana and the Floridas were never Mexican claims.

Spain held Louisiana from 1762 and the Floridas from 1783; both passed to France and
then the United States without ever being Mexican. New Mexico, Texas, Arizona, the
Californias and the Great Basin keep their Mexican cores, because those did become
Mexico. Runs on the split export, before it is compiled.
"""
import json
W=json.load(open("/home/claude/work/world_data.json"))["prov"]
F="/home/claude/work/export_split.json"
d=json.load(open(F)); P=d["provinces"]
LOUISIANA={"USA_139","USA_148","USA_144","USA_151","USA_124","USA_126","USA_121",
           "USA_118","USA_158","USA_129","USA_116","USA_111","USA_194","USA_196","USA_200"}
n=0
for k,v in P.items():
    if W[k]["rg"] in LOUISIANA and "MEX" in v["cores"]:
        v["cores"]=sorted((set(v["cores"])-{"MEX"})|{"NSP"}); n+=1
json.dump(d,open(F,"w"))
kept=sum(1 for v in P.values() if "MEX" in v["cores"])
print(f"  Louisiana cores MEX -> NSP      {n}")
print(f"  provinces still claimed by MEX  {kept}")
