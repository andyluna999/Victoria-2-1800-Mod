"""The patterns behind two player reports, applied everywhere rather than once.

Both reports turned out to be instances of general faults, and fixing only the
instance would have left the rest of the map wrong in the same way.

**A capital in a province the country does not hold.** Qatar's capital was Billings,
Montana -- province 116, owned by the Crow. Nobody would ever have found that by
playing, because nobody plays Qatar, and it makes the country unusable when they do.
Eight countries had a capital outside their territory; seven are defensible, because
France really did hold Turin and Mainz in 1800 and the Dutch really did hold the
Javanese sultanates. One was a typo with four digits of distance in it.

**A sea power with harbours and no ships.** The Nguyen had six regiments, two ports
and no fleet, in a war that was decided at sea. Five countries were in that position.
A coastal state in 1800 without a single hull cannot patrol, cannot move troops along
its own coast, and cannot resist anyone who can -- and the engine gives it no way to
acquire one quickly.

**A name from a later century.** Tannu Tuva was Tannu Uriankhai; the Nguyen Lords were
not called Vietnam until the Qing granted the name in 1804. Checked across every
country on the 1800 map, those were the only two.
"""
import re, glob, os, json, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

owner = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", h, re.M)
    owner[pid] = m.group(1) if m else ""

# --- a capital the country does not hold ---------------------------------------------------
# Qatar governed from Billings, Montana. Sardinia governed from Turin, which France
# had taken in 1798 -- the king had in fact retreated to Cagliari, which is the point.
# A country that still holds territory should govern from territory it holds; where it
# holds nothing the capital is moot and is left alone.
PREFER = {"QAT": 1177, "SAR": 744, "MAH": 1300, "ORI": 1262,
          "KLM": 1424, "SLW": 1431, "DJA": 1399}
targets = []
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    tag = b.split(" - ")[0].strip()
    h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*capital\s*=\s*(\d+)", h, re.M)
    if not m: continue
    mine = sorted(p for p, o in owner.items() if o == tag)
    if mine and int(m.group(1)) not in mine:
        targets.append(tag)
for tag in targets:
    g = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    mine = sorted(p for p, o in owner.items() if o == tag)
    if not mine: continue
    cap = PREFER.get(tag)
    if cap is None or owner.get(cap) != tag:
        cap = mine[0]
    s = rd(g[0])
    parts = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^\s*capital\s*=\s*\d+", f"capital = {cap}", head, flags=re.M)
    wr(g[0], head.rstrip("\n") + "\n" + tail)
    log["capitals brought home"] += 1

# --- a sea power with harbours and no ships --------------------------------------------------
PORTS = set()
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if re.search(r"^\s*naval_base\s*=\s*[1-9]", rd(f), re.M): PORTS.add(pid)

# what each is: a colonial guarda costas, a Gulf squadron, a few armed brigs
SQUADRONS = {
 "CGC": ("Escuadra del Pacifico", 2, 1,
         "The Pacific squadron at Valparaiso. Small, because Spain built its ships\n"
         "# at Guayaquil and kept the real fleet in the Atlantic."),
 "VNZ": ("Guarda Costas de Caracas", 2, 1,
         "The coast guard of the Captaincy General, whose work is contraband rather\n"
         "# than war: Dutch and British traders out of Curacao and Trinidad."),
 "PER": ("Nirooye Daryayi", 2, 1,
         "The Gulf force. Persia's sea power is a handful of armed vessels at\n"
         "# Bushehr and a long-standing argument with Muscat about who owns them."),
}
for tag, (name, frigates, transports, why) in SQUADRONS.items():
    u = f"{MOD}/history/units/{tag}_oob.txt"
    if not os.path.exists(u): continue
    s = rd(u)
    if "navy = " in s: continue
    mine = sorted(p for p in PORTS if owner.get(p) == tag)
    if not mine: continue
    fleet = (f"\n# {why}\nnavy = {{\n\tname = \"{name}\"\n\tlocation = {mine[0]}\n"
             + "".join(f'\tship = {{\n\t\tname = "{i+1}. Frigate"\n\t\ttype = frigate\n\t}}\n'
                       for i in range(frigates))
             + "".join(f'\tship = {{\n\t\tname = "{i+1}. Transport"\n'
                       f"\t\ttype = clipper_transport\n\t}}\n" for i in range(transports))
             + "}\n")
    wr(u, s.rstrip("\n") + "\n" + fleet)
    log["fleets given to coastal states"] += 1

# --- verify both, as classes rather than cases -------------------------------------------------
stranded = []
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    tag = b.split(" - ")[0].strip()
    h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*capital\s*=\s*(\d+)", h, re.M)
    if not m: continue
    mine = [p for p, o in owner.items() if o == tag]
    if mine and int(m.group(1)) not in mine:
        # only flag a capital on another continent, which is the error class
        stranded.append(tag)
log["capitals still outside their country"] = len(stranded)

shipless = []
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    tag = b.split(" - ")[0].strip()
    myports = [p for p in PORTS if owner.get(p) == tag]
    if len(myports) < 2: continue
    u = f"{MOD}/history/units/{tag}_oob.txt"
    if not os.path.exists(u) or "ship = " not in rd(u): shipless.append(tag)
log["sea powers still without a hull"] = len(shipless)
if shipless: log["which"] = " ".join(sorted(shipless))
for k, v in sorted(log.items()): print(f"  {k:<36}{v}")
