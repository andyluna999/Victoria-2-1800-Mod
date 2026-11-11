"""1800 province variables for North America: railroads, forts, naval bases, RGOs."""
import json
W="/home/claude/work"
D=json.load(open(f"{W}/world_data.json"))
NA={int(k):v for k,v in D["prov"].items() if v["ct"]=="north_america"}
byname={}
for p,v in NA.items(): byname.setdefault(v["n"],[]).append(p)
def pid(n,i=0): return byname[n][i]

V={}
def setv(p,**kw): V.setdefault(p,{}).update(kw)

# --- railroads: the first railway anywhere opened in 1825. None exist in 1800.
rails=[p for p,v in NA.items() if v["rr"]>0]
for p in rails: setv(p, railroad=0)

# --- forts, rebuilt for 1800
for p,v in NA.items():
    if v["ft"]>0: setv(p, fort=0)
FORTS={"Halifax":1,"Bermuda":1,"Quebec City":1,"Havana":2,"Puerto Rico":1,
       "Veracruz":1,"San Antonio":1,"New York":1,"St Augustine":1}
for n,l in FORTS.items():
    if n in byname: setv(pid(n), fort=l)

# --- naval bases, rebuilt for 1800
for p,v in NA.items():
    if v["nb"]>0: setv(p, naval_base=0)
NAVAL={"Halifax":2,"Bermuda":2,"Jamaica":2,"Havana":2,"Antigua":1,"Barbados":1,
       "Martinique":1,"Guadeloupe":1,"Quebec City":1,"Boston":1,"New York":1,
       "Norfolk":1,"Philadelphia":1,"Baltimore":1,"New Orleans":1,"Port Au Prince":1,
       "Puerto Rico":1,"Veracruz":1,"Trinidad":1}
for n,l in NAVAL.items():
    if n in byname: setv(pid(n), naval_base=l)

# --- trade goods. Victoria II has no sugar, and fruit is the established stand-in
# (it feeds liquor the way sugar fed rum). Jamaica, the greatest sugar island on
# earth in 1800, was set to sulphur.
SUGAR=["Jamaica","Barbados","Saint Kitts","Antigua","Martinique","Saint Lucia",
       "Grenada","Saint Vincent","Tobago","Trinidad","Cap Haitien","Tortola",
       "Montserrat","Dominica","Jagua","Camaguey"]
for n in SUGAR:
    if n in byname: setv(pid(n), trade_goods="fruit")
# minerals and chemicals that were not mined anywhere near these places in 1800
RGO={"Salt Lake City":"cattle","Cody":"cattle","Bismarck":"cattle","Dupree":"cattle",
     "Minot":"cattle","Carson City":"cattle","Elko":"wool","Las Vegas":"cattle",
     "Flagstaff":"wool","Lubbock":"cattle","Lake Charles":"timber","Shreveport":"timber",
     "Fort MacLeod":"cattle","Sudbury":"timber","Vancouver Island":"timber","Banff":"timber",
     "Millertown":"fish","El Paso":"cattle","Loa":"cattle","Moab":"cattle","Grand Junction":"cattle"}
for n,g in RGO.items():
    if n in byname: setv(pid(n), trade_goods=g)

print(f"{len(V)} provinces changed")
print(f"  railroads cleared : {len(rails)}")
print(f"  forts             : {sum(1 for v in V.values() if v.get('fort'))} set, "
      f"{sum(1 for v in V.values() if v.get('fort')==0)} cleared")
print(f"  naval bases       : {sum(1 for v in V.values() if v.get('naval_base'))} set, "
      f"{sum(1 for v in V.values() if v.get('naval_base')==0)} cleared")
print(f"  trade goods       : {sum(1 for v in V.values() if 'trade_goods' in v)}")
missing=[n for n in list(FORTS)+list(NAVAL)+SUGAR+list(RGO) if n not in byname]
print("  names not found on the map:", sorted(set(missing)) or "none")
json.dump({str(k):v for k,v in V.items()}, open(f"{W}/na_province_vars.json","w"))
