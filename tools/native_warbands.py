"""The plains and woodland nations get war parties, raised where their people live.

Three generic passes had been deciding these armies between them and all three were
wrong for the job. The re-homing sorted a country's provinces by raw soldier count and
sent the Haudenosaunee to recruit in New York -- ten thousand Yankees and ninety
Haudenosaunee -- so they fielded nothing. The disbanding pass applied a European bar
of nine hundred men per regiment to nations of four thousand people and cut every one
of them to a single token unit. And the mustering pass had no idea that a soldier of
the wrong culture is no soldier at all.

So these are written directly instead. Each nation raises irregular war parties from
the provinces it actually holds, sized to the people who actually live there, and
homed only where its own culture has soldiers. The numbers are small on purpose: the
Comanche were perhaps twenty thousand people and fielded a few thousand warriors, and
that is what made them formidable on the southern plains and doomed against a
continental state.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
PER = 260          # soldier pop units behind one war party, at our 0.25 scale
MAXBANDS = 8
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

NATIONS = {
 "SIO": "Oceti Sakowin", "COM": "Comanche War Parties", "PAW": "Pawnee Scouts",
 "OSA": "Osage War Parties", "APA": "Apache Rancherias", "NAV": "Navajo Riders",
 "CRA": "Crow War Parties", "BLA": "Blackfoot Confederacy", "ARI": "Mandan Villages",
 "CRK": "Cherokee Regiment", "CHA": "Chickasaw Levy", "SEM": "Seminole Bands",
 "CCY": "Creek Towns", "CAW": "Choctaw Levy", "NEZ": "Nez Perce Bands",
 "AAA": "Shoshone Bands", "ANI": "Anishinaabe Levy", "IRO": "Haudenosaunee Levy",
 "COA": "Coast Salish", "COK": "Chinook Bands", "SAL": "Salish Bands",
 "MAP": "Mapuche Malones", "TLI": "Tlingit Clans", "CHE": "Cheyenne Dog Soldiers",
}

owner = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", h, re.M)
    owner[pid] = m.group(1) if m else ""

solcul = collections.defaultdict(collections.Counter)
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    t = re.sub(r"#.*", "", rd(f))
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", t, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(t) and d:
            if t[i] == "{": d += 1
            elif t[i] == "}": d -= 1
            i += 1
        for m in re.finditer(r"\bsoldiers = \{\n\t\tculture = (\w+)\n\t\t"
                             r"religion = \w+\n\t\tsize = (\d+)", t[pm.end():i-1]):
            solcul[pid][m.group(1)] += int(m.group(2))

for tag, name in NATIONS.items():
    g = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    head = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(g[0]))[0]
    pm = re.search(r"^\s*primary_culture\s*=\s*(\w+)", head, re.M)
    if not pm: continue
    acc = {pm.group(1)} | set(re.findall(r"^\s*culture\s*=\s*(\w+)", head, re.M))
    mine = [p for p, o in owner.items() if o == tag]
    if not mine: continue
    # only provinces where this nation's own people are under arms
    home = sorted(((p, sum(v for c, v in solcul[p].items() if c in acc)) for p in mine),
                  key=lambda x: -x[1])
    home = [(p, n) for p, n in home if n >= 60]
    if not home:
        # nobody under arms anywhere: give it one band at its capital regardless
        cap = re.search(r"^\s*capital\s*=\s*(\d+)", head, re.M)
        home = [(int(cap.group(1)), PER)] if cap else [(mine[0], PER)]
        log["nations with no armed population"] += 1
    total = sum(n for _, n in home)
    bands = max(1, min(MAXBANDS, total // PER))
    regs, k = [], 0
    for i in range(bands):
        p = home[i % len(home)][0]
        ty = "cavalry" if tag in ("COM", "SIO", "CRA", "BLA", "NAV", "CHE", "AAA") and i % 3 == 0 else "irregular"
        regs.append(f'\tregiment = {{\n\t\tname = "{i+1}. {name}"\n'
                    f'\t\ttype = {ty}\n\t\thome = {p}\n\t}}')
    body = (f"# {name}. Raised from the people who actually live here: the generic\n"
            f"# passes were homing these on provinces full of settlers and cutting them\n"
            f"# to a single token unit against a bar set for European armies.\n\n"
            f'army = {{\n\tname = "{name}"\n\tlocation = {home[0][0]}\n'
            + "\n".join(regs) + "\n}\n")
    wr(f"{MOD}/history/units/{tag}_oob.txt", body)
    log["nations armed"] += 1
    log["war parties"] += bands

for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
