"""The British Isles, 1800.

The totals were already close -- Ireland 5,000,004 and England and Wales 8,932,156
against the 1801 census's 8,895,000. What was wrong was who those people were. Wales
was filed entirely as `british`, and Ireland's Protestants were filed as `british` too,
in a single undifferentiated block that put Belfast at 77% British.

Three cultures added.

**welsh.** Wales held 587,000 people in 1801 and something like seven in ten of them
spoke Welsh, concentrated in the north and west. The anglicised parts are real and
specific: Monmouthshire, the Vale of Glamorgan, the border, and south Pembrokeshire,
which has been English-speaking since the twelfth century and was called Little England
Beyond Wales for it.

**ulster_scot** and **anglo_irish**, rather than one name for both, because they were
two different peoples who disliked each other almost as much as they disliked the
Catholics. The Ulster Scots are Presbyterian, descended from the seventeenth-century
Scottish plantation, concentrated in Antrim and Down, excluded from office by the Test
Act, and about to supply a large part of the United Irishmen in 1798 and a very large
part of the emigration to America. The Anglo-Irish are Church of Ireland, the
landowning interest, holding the Parliament that is being dissolved this year by the
Act of Union. Collapsing them into one culture would lose both 1798 and 1801.

Denominational shares are from the 1834 religious census, the first reliable count,
applied to a 1800 population of five million.
"""
import json, re, glob, os, collections

MOD = "/home/claude/build/HPM"; W = "/home/claude/work"
SCALE = 0.25
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

CULTURES = {
 "welsh": ([46, 126, 86],
   ["Dafydd","Gruffudd","Hywel","Ieuan","Llywelyn","Madog","Owain","Rhys","Emrys",
    "Gwilym","Iestyn","Cadwaladr","Meredydd","Tudur","Idris","Caradog"],
   ["Ap Rhys","Ap Hywel","Llewelyn","Morgan","Vaughan","Price","Lloyd","Gwynne",
    "Bevan","Meyrick","Mostyn","Wynn","Herbert","Trevor"]),
 "ulster_scot": ([86, 150, 170],
   ["Andrew","Archibald","David","Ebenezer","Hamilton","Hugh","James","John","Robert",
    "Samuel","Thomas","William","Alexander","Francis"],
   ["Boyd","Crawford","Dunlop","Ferguson","Hamilton","Johnston","Kennedy","Logan",
    "McCrea","Montgomery","Orr","Porter","Stewart","Wallace"]),
 "anglo_irish": ([178, 118, 196],
   ["Arthur","Castlereagh","Charles","Edward","Frederick","Henry","John","Richard",
    "Robert","Thomas","William","Lionel","Augustus"],
   ["Beresford","Boyle","Butler","Colclough","Fitzgibbon","Grattan","Hely-Hutchinson",
    "Ponsonby","Parsons","Shelburne","Tighe","Wellesley","Yelverton"]),
}
src = rd(f"{MOD}/common/cultures.txt")
anchor = re.search(r"\n[ \t]+scottish[ \t]*=[ \t]*\{", src)
add = ""
for c, (col, first, last) in CULTURES.items():
    if re.search(rf"\n[ \t]+{c}[ \t]*=[ \t]*\{{", src): continue
    add += (f"        {c} = {{\n            color = {{ {col[0]} {col[1]} {col[2]} }}\n"
            f"            first_names = {{ {' '.join(first)} }}\n"
            f"            last_names = {{ {' '.join(last)} }}\n        }}\n")
    log["cultures added"] += 1
if add:
    src = src[:anchor.start()+1] + add + src[anchor.start()+1:]
    wr(f"{MOD}/common/cultures.txt", src)

# --- Wales: province, 1801 population, Welsh-speaking share ----------------------
WALES = {
 276: (145_940, 0.95, "Anglesey, Caernarfon, Merioneth -- Welsh almost to a person"),
 274: (107_268, 0.85, "Cardigan, Carmarthen, Pembroke -- less the English south"),
 275: (110_672, 0.80, "Powys and the march, anglicised along the border"),
 273: (233_748, 0.58, "Glamorgan and Monmouth, the most English part of Wales"),
}
# --- Ireland: province, population, and the 1834 denominational shares ------------
# Catholic, Presbyterian (Ulster Scots), Church of Ireland (Anglo-Irish)
IRELAND = {
 254: (372_760, .35, .45, .20, "Antrim and Down: the Presbyterian heartland"),
 255: (361_724, .48, .30, .22, "Londonderry and Tyrone"),
 256: (189_272, .55, .20, .25, "Armagh, Monaghan, Cavan"),
 257: (350_408, .75, .12, .13, "Donegal and the north-west"),
 258: (378_008, .95, .005, .045, "Connacht: Galway and Mayo"),
 259: (530_032, .95, .005, .045, "Sligo, Roscommon, Leitrim"),
 260: (618_332, .93, .005, .065, "Cork"),
 261: (564_528, .93, .005, .065, "Limerick, Clare, Kerry"),
 262: (370_004, .93, .005, .065, "Waterford and Tipperary"),
 263: (593_912, .85, .015, .135, "Dublin: the Ascendancy's own city"),
 264: (366_968, .88, .01, .11, "Kildare and the midlands"),
 265: (304_056, .89, .01, .10, "Wexford, Carlow, Wicklow"),
}
LOWLAND  = {"farmers":.52,"artisans":.24,"labourers":.11,"clergymen":.032,
            "aristocrats":.028,"clerks":.022,"soldiers":.02,"bureaucrats":.016,
            "craftsmen":.008,"capitalists":.003,"officers":.001}
TENANT   = {"farmers":.74,"labourers":.16,"artisans":.06,"clergymen":.02,
            "aristocrats":.012,"soldiers":.006,"clerks":.002}
GENTRY   = {"aristocrats":.26,"farmers":.30,"clergymen":.11,"bureaucrats":.09,
            "artisans":.08,"officers":.06,"clerks":.05,"soldiers":.03,"capitalists":.02}
ARCH = {"welsh": TENANT, "british": LOWLAND, "irish": TENANT,
        "ulster_scot": LOWLAND, "anglo_irish": GENTRY}
REL  = {"welsh": "protestant", "british": "protestant", "irish": "catholic",
        "ulster_scot": "protestant", "anglo_irish": "protestant"}

alloc = collections.defaultdict(dict)
for pid, (pop, share, why) in WALES.items():
    alloc[pid]["welsh"] = pop * share
    alloc[pid]["british"] = pop * (1 - share)
for pid, (pop, cath, pres, angl, why) in IRELAND.items():
    alloc[pid]["irish"] = pop * cath
    if pop * pres >= 400: alloc[pid]["ulster_scot"] = pop * pres
    alloc[pid]["anglo_irish"] = pop * angl

rows, summary = [], collections.Counter()
for pid, mix in alloc.items():
    for c, real in mix.items():
        n = int(round(real * SCALE))
        if n < 10: continue
        arch = ARCH[c]; placed = 0
        items = sorted(arch.items(), key=lambda x: (-x[1], x[0]))
        for i, (ty, fr) in enumerate(items):
            sz = int(round(n * fr)) if i < len(items) - 1 else n - placed
            placed += sz
            if sz < 5: continue
            rows.append((pid, ty, c, REL[c], sz)); summary[c] += sz

files = {f: rd(f) for f in glob.glob(f"{MOD}/history/pops/*/*.txt")}
target = next(f for f in files if os.path.basename(f) == "united kingdom.txt")
s = files[target]; keep = []
for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
    pid = int(pm.group(1)); i = pm.end(); d = 1
    while i < len(s) and d:
        if s[i] == "{": d += 1
        elif s[i] == "}": d -= 1
        i += 1
    if pid not in alloc: keep.append(s[pm.start():i])
by = collections.defaultdict(list)
for pid, ty, c, rel, sz in rows: by[pid].append((ty, c, rel, sz))
txt = ""
for pid in sorted(by):
    txt += f"{pid} = {{\n"
    for ty, c, rel, sz in by[pid]:
        txt += f"\t{ty} = {{\n\t\tculture = {c}\n\t\treligion = {rel}\n\t\tsize = {sz}\n\t}}\n"
    txt += "}\n"
wr(target, ("\n".join(keep) + "\n\n" if keep else "") + txt)

# Britain accepts the Welsh and the two Irish Protestant groups; it does not accept
# the Catholic Irish, which is the whole political question of the next thirty years.
for f in glob.glob(f"{MOD}/history/countries/ENG - *.txt"):
    t = rd(f)
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", t)[0]
    want = [c for c in ("welsh", "ulster_scot", "anglo_irish")
            if not re.search(rf"^\s*culture\s*=\s*{c}\s*$", head, re.M)]
    if want:
        t = re.sub(r"(^\s*primary_culture\s*=.*\n)", r"\1" + "".join(f"culture = {c}\n" for c in want),
                   t, count=1, flags=re.M)
        wr(f, t); log["accepted by Britain"] = len(want)
    # Britain does not accept the Catholic Irish in 1800. The Test and Penal Acts are
    # still in force, Catholics cannot sit in Parliament, and Pitt's promise of
    # Emancipation alongside the Union is about to be vetoed by the King. HPM's
    # accepted status is the post-1829 settlement, twenty-nine years early.
    t = rd(f)
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", t)[0]
    if re.search(r"^\s*culture\s*=\s*irish\s*$", head, re.M):
        head = re.sub(r"^\s*culture\s*=\s*irish\s*\n", "", head, count=1, flags=re.M)
        rest = t[len(re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", t)[0]):]
        wr(f, head + rest); log["Catholic Irish no longer accepted by Britain"] = 1
for f in glob.glob(f"{MOD}/history/countries/IRE - *.txt"):
    t = rd(f)
    t = re.sub(r"^\s*primary_culture\s*=.*$", "primary_culture = irish", t, count=1, flags=re.M)
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", t)[0]
    want = [c for c in ("anglo_irish", "ulster_scot")
            if not re.search(rf"^\s*culture\s*=\s*{c}\s*$", head, re.M)]
    if want:
        t = re.sub(r"(^\s*primary_culture\s*=.*\n)", r"\1" + "".join(f"culture = {c}\n" for c in want),
                   t, count=1, flags=re.M)
    wr(f, t); log["Ireland's cultures set"] = 1

tot = sum(summary.values())
print(f"  provinces written                 {len(by)}")
print(f"  Wales and Ireland                 {int(tot/SCALE):,} real")
for c, v in summary.most_common():
    print(f"    {c:<14}{int(v/SCALE):>10,} real")
print(f"  Welsh speakers                    {int(summary['welsh']/SCALE):,}  "
      f"(about seven in ten of 587,000)")
for k, v in log.items(): print(f"  {k:<34}{v}")
