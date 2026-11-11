"""Scotland, 1800.

Every Scottish province was filed as `british`, so a country with its own law, church,
universities and two languages did not appear on the culture map at all. The `scottish`
culture already existed and was already in use in North America -- the diaspora was on
the map and the homeland was not.

Two things to get right province by province.

**The totals.** The 1801 census counted 1,608,420 people in Scotland, and we are
holding 1,496,380 distributed on HPM's 1836 shape. That shape is wrong for 1800 in a
specific way: Glasgow and the southwest boomed between the two dates, so the industrial
west is over-weighted and the Highlands under-weighted. In 1801 Inverness-shire, Ross,
Sutherland, Caithness, Argyll and the Isles together held more people than Lanarkshire.

**The language line.** Roughly 300,000 people spoke Gaelic in 1800, almost all of them
north and west of the Highland line, and the Clearances are about to begin. Filing them
as Lowland Scots would erase the single most consequential fact about Scotland in this
period. They get their own culture, `highlander`.

County figures below are from the 1801 census, grouped to HPM's seven provinces.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, collections

MOD = _BUILD; W = _WORK
SCALE = 0.25
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# province: (1801 population, counties it stands for, scottish, highlander, irish)
SCOTLAND = {
 269: (200_000, "Edinburgh, Haddington, Linlithgow, Peebles, Selkirk, Roxburgh",
       197_000,       0,  3_000),
 271: (300_000, "Lanark, Renfrew, Ayr, Dunbarton, Bute",
       286_000,   2_000, 12_000),
 270: (190_000, "Stirling, Clackmannan, Fife, Kinross",
       185_000,   5_000,      0),
 268: (230_000, "Angus, Perthshire -- the Highland line runs through this one",
       205_000,  25_000,      0),
 266: (230_000, "Aberdeen, Banff, Moray, Kincardine",
       215_000,  15_000,      0),
 267: (310_000, "Inverness, Ross, Sutherland, Caithness, Argyll, the Isles",
        57_000, 253_000,      0),
 272: (148_420, "Dumfries, Kirkcudbright, Wigtown, Berwick",
       148_420,       0,      0),
}
GAELIC = sum(v[3] for v in SCOTLAND.values())

# --- the culture --------------------------------------------------------------
NAMES = {"first": ["Alasdair","Aonghas","Calum","Domhnall","Eachann","Fearghas","Iain",
                   "Lachlann","Murchadh","Niall","Raonull","Seumas","Somhairle","Tormod"],
         "last":  ["MacDhomhnaill","MacLeoid","Caimbeul","MacGriogair","MacNeacail",
                   "MacCoinnich","Camshron","Granndach","MacPhearsain","Friseal",
                   "MacMhathain","Dòmhnallach","Rothach","Siosal"]}
src = rd(f"{MOD}/common/cultures.txt")
if not re.search(r"\n[ \t]+highlander[ \t]*=[ \t]*\{", src):
    m = re.search(r"\n[ \t]+scottish[ \t]*=[ \t]*\{", src)
    blk = ("        highlander = {\n            color = { 46 104 126 }\n"
           f"            first_names = {{ {' '.join(NAMES['first'])} }}\n"
           f"            last_names = {{ {' '.join(NAMES['last'])} }}\n        }}\n")
    src = src[:m.start()+1] + blk + src[m.start()+1:]
    wr(f"{MOD}/common/cultures.txt", src)
    log["cultures added"] = 1

# --- the pops -------------------------------------------------------------------
# Lowland Scotland was commercial and proto-industrial; the Highlands were crofting
# townships with a tacksman layer and a very large Presbyterian clergy for the size.
LOWLAND  = {"farmers":.52,"artisans":.24,"labourers":.11,"clergymen":.032,
            "aristocrats":.028,"clerks":.022,"soldiers":.02,"bureaucrats":.016,
            "craftsmen":.008,"capitalists":.003,"officers":.001}
HIGHLAND = {"farmers":.82,"artisans":.075,"soldiers":.045,"labourers":.02,
            "clergymen":.018,"aristocrats":.018,"officers":.003,"bureaucrats":.001}
ARCH = {"scottish": LOWLAND, "highlander": HIGHLAND, "irish": LOWLAND}
# the Kirk in the Lowlands; the Highlands keep Catholic pockets in Lochaber,
# the Uists and Barra that survived the penal laws
REL = {("scottish", "protestant"): 1.0, ("irish", "catholic"): 1.0}

rows, summary = [], collections.Counter()
for pid, (total, counties, sc, hl, ir) in SCOTLAND.items():
    for cult, real in (("scottish", sc), ("highlander", hl), ("irish", ir)):
        if real <= 0: continue
        n = int(round(real * SCALE))
        groups = [(cult, "catholic" if cult == "irish" else "protestant", n)]
        if cult == "highlander":                       # about a sixth stayed Catholic
            cath = int(round(n * 0.16))
            groups = [(cult, "protestant", n - cath), (cult, "catholic", cath)]
        for c, rel, size in groups:
            arch = ARCH[c]; placed = 0
            items = sorted(arch.items(), key=lambda x: (-x[1], x[0]))
            for i, (ty, fr) in enumerate(items):
                sz = int(round(size * fr)) if i < len(items) - 1 else size - placed
                placed += sz
                if sz < 5: continue
                rows.append((pid, ty, c, rel, sz)); summary[c] += sz

files = {f: rd(f) for f in glob.glob(f"{MOD}/history/pops/*/*.txt")}
target = next((f for f in files if os.path.basename(f) == "united kingdom.txt"), None)
if target is None:
    target = next(f for f, s in files.items()
                  if {int(m.group(1)) for m in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M)} & set(SCOTLAND))
s = files[target]
keep = []
for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
    pid = int(pm.group(1)); i = pm.end(); d = 1
    while i < len(s) and d:
        if s[i] == "{": d += 1
        elif s[i] == "}": d -= 1
        i += 1
    if pid not in SCOTLAND: keep.append(s[pm.start():i])
by = collections.defaultdict(list)
for pid, ty, c, rel, sz in rows: by[pid].append((ty, c, rel, sz))
txt = ""
for pid in sorted(by):
    txt += f"{pid} = {{\n"
    for ty, c, rel, sz in by[pid]:
        txt += f"\t{ty} = {{\n\t\tculture = {c}\n\t\treligion = {rel}\n\t\tsize = {sz}\n\t}}\n"
    txt += "}\n"
wr(target, ("\n".join(keep) + "\n\n" if keep else "") + txt)

# Britain accepts both: Scots sat in the Commons and officered the army and the Company
for f in glob.glob(f"{MOD}/history/countries/ENG - *.txt"):
    t = rd(f)
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", t)[0]
    add = [c for c in ("scottish", "highlander")
           if not re.search(rf"^\s*culture\s*=\s*{c}\s*$", head, re.M)]
    if add:
        t = re.sub(r"(^\s*primary_culture\s*=.*\n)", r"\1" + "".join(f"culture = {c}\n" for c in add),
                   t, count=1, flags=re.M)
        wr(f, t); log["accepted cultures added to Britain"] = len(add)

tot = sum(summary.values())
print(f"  provinces written                 {len(by)}")
print(f"  Scotland                          {tot:,} pops = {int(tot/SCALE):,} real"
      f"   (the 1801 census counted 1,608,420)")
for c, v in summary.most_common():
    print(f"    {c:<12}{v:>8,} = {int(v/SCALE):>9,} real")
print(f"  Gaelic speakers                   {GAELIC:,}   (about 300,000 in 1800)")
for k, v in log.items(): print(f"  {k:<34}{v}")
