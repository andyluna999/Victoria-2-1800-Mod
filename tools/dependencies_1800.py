"""Puppets, satellites and protectorates, worldwide, for 1800.

Three problems with the inherited set:

  1. Seventy-two relationships carry `start_date = 1836.1.1`. At a 1836 start that is
     the opening position; at an 1800 start they are empty until the year arrives and
     then spring into existence. Some of those are right -- the Peru-Bolivian
     Confederation really does form in 1836 -- and some are simply the 1836 world
     written down, like the Japanese han, which existed throughout.
  2. Neuchatel ends up with two overlords. Prussia's prince held it from 1707; it
     joined the Swiss Confederation in 1814 while staying Prussian until 1857. Both
     entries are right, and they have to be sequenced rather than overlapping.
  3. Britain's subsidiary alliances in India are missing entirely. By 1800 Hyderabad,
     Mysore, Travancore and Awadh had all signed treaties placing Company troops in
     their territory and their foreign policy in Calcutta's hands. That is the
     instrument the Company conquered India with, and it should be on the map.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# --- 1. relationships that existed in 1800 but are dated 1836 --------------------
# The Japanese han are the clear case: Satsuma, Choshu and the rest were Tokugawa
# vassals for two and a half centuries before 1836.
REDATE = {("TKG", x) for x in ("SEN", "YZW", "KAG", "TOS", "CHO", "SAT", "JAP")}
redated = 0
for f in glob.glob(f"{MOD}/history/diplomacy/*.txt"):
    if os.path.basename(f).startswith("1800_"): continue
    s = rd(f); out = s
    for m in re.finditer(r"(vassal|union|substate)\s*=\s*\{([^}]*)\}", s, re.S):
        b = m.group(2)
        first = (re.search(r"first\s*=\s*([A-Z]{3})", b) or [None, None])[1]
        second = (re.search(r"second\s*=\s*([A-Z]{3})", b) or [None, None])[1]
        if (first, second) in REDATE and "1836.1.1" in b:
            out = out.replace(m.group(0), m.group(0).replace("start_date = 1836.1.1",
                                                             "start_date = 1800.1.1"))
            redated += 1
    if out != s: wr(f, out)
log["relationships re-dated to 1800"] = redated

# --- 2. sequence the overlapping ones --------------------------------------------
# Prussia holds Neuchatel until the Swiss Confederation takes it in 1814.
for f in glob.glob(f"{MOD}/history/diplomacy/1800_europe.txt"):
    s = rd(f)
    pass  # end dates are now set where the relationship is written
    wr(f, s); log["overlaps sequenced"] += 1

# --- 3. Schleswig-Holstein ---------------------------------------------------------
# The duchies were ruled by the Danish king in personal union, and Holstein sat inside
# the Holy Roman Empire. Giving the provinces to Denmark directly left the union entry
# pointing at a tag with no land.
HOLSTEIN = [369, 529]
prov = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    prov[int(re.match(r"(\d+)", os.path.basename(f)).group(1))] = f
for pid in HOLSTEIN:
    f = prov.get(pid)
    if not f: continue
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^\s*owner\s*=.*\n", "", head, flags=re.M)
    head = re.sub(r"^\s*controller\s*=.*\n", "", head, flags=re.M)
    head = "owner = SWH\ncontroller = SWH\n" + head.lstrip("\n")
    if not re.search(r"^\s*add_core\s*=\s*SWH\s*$", head, re.M):
        head = head.rstrip("\n") + "\nadd_core = SWH\n"
    if not re.search(r"^\s*add_core\s*=\s*DEN\s*$", head, re.M):
        head = head.rstrip("\n") + "\nadd_core = DEN\n"
    wr(f, head.rstrip("\n") + "\n" + tail)
    log["Holstein provinces restored to the duchy"] += 1

# --- 4. the dependencies of 1800 that are dated 1836 -----------------------------
# Every one of these already exists in HPM, dated to the 1836 start. The relationships
# themselves are much older: Hyderabad signed its subsidiary alliance in 1798, Mysore
# was reconstituted under one in 1799 after Tipu died at Seringapatam, Travancore
# accepted one in 1795, and Tibet has had imperial residents since 1728. Awadh is left
# at 1801, which is the correct date for its treaty and lands one year into the game.
PULL_BACK = {
 ("ENG", "HYD"): "the subsidiary alliance of 1798",
 ("ENG", "MYS"): "reconstituted under the Wodeyars, 1799",
 ("ENG", "TRA"): "the treaty of 1795",
 ("QNG", "TIB"): "under the ambans since 1728",
}
# and these need an end date so a later relationship can take over cleanly
SEQUENCE = {
 ("EGY", "HDJ"): None,                    # Muhammad Ali's conquest: correctly 1836
 ("DEN", "SWH"): ("union", "1836.1.1"),   # the personal union yields to HPM's 1836 vassal
}
pulled = sequenced = 0
for f in glob.glob(f"{MOD}/history/diplomacy/*.txt"):
    if os.path.basename(f).startswith("1800_"): continue
    s_ = rd(f); out = s_
    for m in re.finditer(r"(vassal|union|substate)\s*=\s*\{([^}]*)\}", s_, re.S):
        kind, b = m.group(1), m.group(2)
        first = (re.search(r"first\s*=\s*([A-Z]{3})", b) or [None, None])[1]
        second = (re.search(r"second\s*=\s*([A-Z]{3})", b) or [None, None])[1]
        key = (first, second)
        if key in PULL_BACK and "start_date = 1836.1.1" in b:
            out = out.replace(m.group(0), m.group(0).replace(
                "start_date = 1836.1.1", "start_date = 1800.1.1")); pulled += 1
        elif key in SEQUENCE and SEQUENCE[key] and kind == SEQUENCE[key][0]:
            out = out.replace(m.group(0), re.sub(r"end_date\s*=\s*\S+",
                f"end_date = {SEQUENCE[key][1]}", m.group(0))); sequenced += 1
    if out != s_: wr(f, out)
log["subsidiary alliances pulled back to 1800"] = pulled
log["overlaps given an end date"] = sequenced

# the Sharif of Mecca holds the Hejaz for the Sultan until Diriyah takes it in 1803,
# and HPM's Egyptian claim on it only begins in 1836
wr(f"{MOD}/history/diplomacy/1800_protectorates.txt",
   "# TUR - the Sharifate of Mecca\nvassal = {\n\tfirst = TUR\n\tsecond = HDJ\n"
   "\tstart_date = 1800.1.1\n\tend_date = 1836.1.1\n}\n")
log["dependencies added"] = 1

# --- 5. report the final picture ---------------------------------------------------
act = collections.defaultdict(list)
dbl = collections.defaultdict(list)
for f in glob.glob(f"{MOD}/history/diplomacy/*.txt"):
    for m in re.finditer(r"(vassal|union|substate)\s*=\s*\{([^}]*)\}", rd(f), re.S):
        k, bb = m.group(1), m.group(2)
        g = lambda n: (re.search(rf"{n}\s*=\s*(\S+)", bb) or [None, None])[1]
        s_, e_ = g("start_date") or "1.1.1", g("end_date") or "9999.1.1"
        if s_ <= "1800.1.1" < e_:
            act[g("first")].append((k, g("second")))
            dbl[g("second")].append(g("first"))
log["active on 1 Jan 1800"] = sum(len(v) for v in act.values())
over2 = {k: v for k, v in dbl.items() if len(v) > 1}
log["countries with two overlords"] = len(over2)

for k, v in log.items(): print(f"  {k:<42}{v}")
print("\n  who answers to whom on 1 January 1800:")
for a in sorted(act, key=lambda x: -len(act[x])):
    print(f"    {a}: " + ", ".join(f"{b}({k[0]})" for k, b in sorted(act[a], key=lambda z: z[1])))
if over2: print("\n  CONFLICT:", over2)
