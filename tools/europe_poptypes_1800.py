"""Occupational structure for 1800.

HPM's pop types describe 1836. Britain comes out 57% labourers and 10% craftsmen --
Victoria II's craftsmen are factory workers, and in 1800 mechanised industry barely
existed anywhere. Russia and Austria show almost no serfs where serfdom was still the
basis of the rural economy.

Culture, religion and every province total are left exactly as they are. Only the
split between occupations moves, and it moves by scaling each type toward the national
target, so the relative differences HPM has between provinces survive.
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
L = json.load(open(f"{W}/world_live.json"))
ALL = {"europe","asia","africa","oceania","australia_new_zealand","polynesia","north_america","south_america"}
EU = {int(k) for k, v in L["prov"].items() if v["ct"] in ("europe","asia","africa","oceania","australia_new_zealand","polynesia")}
CONT = {int(k): v["ct"] for k, v in L["prov"].items()}

# 1800 occupational structure, as shares. Britain: agriculture ~36% of the workforce,
# manufacture largely handicraft rather than factory. The serf economies east of the
# Elbe: unfree labour is the rural base, not peasant proprietorship.
COMMERCIAL = {"farmers":.34,"artisans":.27,"labourers":.16,"craftsmen":.05,"soldiers":.03,
              "aristocrats":.025,"clerks":.02,"clergymen":.015,"bureaucrats":.015,
              "capitalists":.01,"officers":.005,"serfs":0.0}
WESTERN    = {"farmers":.68,"artisans":.16,"labourers":.05,"soldiers":.03,"clergymen":.022,
              "aristocrats":.022,"craftsmen":.012,"bureaucrats":.01,"clerks":.006,
              "capitalists":.004,"officers":.004,"serfs":0.0}
SERF       = {"serfs":.62,"farmers":.14,"artisans":.11,"labourers":.03,"soldiers":.035,
              "aristocrats":.025,"clergymen":.02,"bureaucrats":.008,"craftsmen":.006,
              "officers":.004,"clerks":.003,"capitalists":.001}
OTTOMAN    = {"farmers":.74,"artisans":.12,"labourers":.03,"soldiers":.04,"clergymen":.022,
              "aristocrats":.022,"craftsmen":.008,"bureaucrats":.008,"officers":.005,
              "clerks":.003,"capitalists":.002,"serfs":0.0}

# the rest of the world. A Chinese county and a Bengali district are not a French
# department: the artisan and scholar-official layers are large, the factory worker
# does not exist, and in much of Africa and Arabia slavery is part of the structure.
CONFUCIAN  = {"farmers":.78,"artisans":.13,"soldiers":.03,"bureaucrats":.018,
              "aristocrats":.018,"clergymen":.012,"labourers":.008,"clerks":.004,
              "craftsmen":.002,"officers":.002,"capitalists":.001,"serfs":0.0}
SAMURAI    = {"farmers":.76,"artisans":.11,"soldiers":.055,"aristocrats":.03,
              "clergymen":.02,"labourers":.01,"bureaucrats":.008,"clerks":.004,
              "officers":.002,"craftsmen":.001,"capitalists":.001,"serfs":0.0}
INDIAN     = {"farmers":.70,"artisans":.17,"soldiers":.04,"clergymen":.032,
              "aristocrats":.028,"labourers":.02,"bureaucrats":.006,"clerks":.004,
              "craftsmen":.002,"officers":.002,"capitalists":.001,"serfs":0.0}
TRADITIONAL= {"farmers":.80,"artisans":.10,"soldiers":.04,"clergymen":.022,
              "aristocrats":.022,"labourers":.01,"slaves":0.0,"bureaucrats":.005,
              "clerks":.003,"craftsmen":.002,"officers":.002,"capitalists":.001,"serfs":0.0}
SLAVEHOLD  = {"farmers":.66,"slaves":.14,"artisans":.09,"soldiers":.05,"clergymen":.025,
              "aristocrats":.025,"labourers":.008,"bureaucrats":.004,"clerks":.002,
              "craftsmen":.001,"officers":.002,"capitalists":.001,"serfs":0.0}
BY_CONT = {"asia":TRADITIONAL,"africa":SLAVEHOLD,"oceania":TRADITIONAL,
           "australia_new_zealand":TRADITIONAL,"polynesia":TRADITIONAL,"europe":WESTERN}

TARGET = collections.defaultdict(lambda: WESTERN)
for t in ("ENG","NET"): TARGET[t] = COMMERCIAL
for t in ("RUS","PRU","AUS","MOL","WAL"): TARGET[t] = SERF
for t in ("TUR",): TARGET[t] = OTTOMAN
for t in ("QNG","KOR","TKG","MGL","TIB"): TARGET[t] = CONFUCIAN
for t in ("JAP",): TARGET[t] = SAMURAI
for t in ("ENG","NET","POR","FRA","SPA","DEN"): pass   # set by their European entry
for t in ("PNJ","NEP","BHU","SIK","HYD","MYS","AWA","GWA","IND","NAG","BER","BHO",
          "TRA","KAS","ORI","RAJ","JOD","MEW","BIK","MUG"): TARGET[t] = INDIAN
for t in ("PER","AFG","KHI","BUK","KOK","OMA","NEJ","HDJ","YEM","MOR","TUN","TRI",
          "ALD","EGY","ETH","SOK","OYO","ASH","DAH","SEG","ZAN","MAD"): TARGET[t] = TRADITIONAL

owner = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid not in EU: continue
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                    open(f, encoding="cp1252", errors="replace").read())[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    owner[pid] = m.group(1) if m else "-"

POPRE = re.compile(r"\t([a-z_]+) = \{\n\t\tculture = ([a-z_0-9]+)\n\t\treligion = ([a-z_0-9]+)\n\t\tsize = (\d+)\n\t\}\n")

# pass 1: what each country's mix is now
cur = collections.defaultdict(collections.Counter)
files = {}
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s = open(f, encoding="cp1252", errors="replace").read(); files[f] = s
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1))
        if pid not in EU: continue
        i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        for ty, cu, rl, sz in POPRE.findall(s[pm.end():i-1]):
            cur[owner[pid]][ty] += int(sz)

fac = {}
for tag, c in cur.items():
    tot = sum(c.values()) or 1
    t = TARGET[tag]
    fac[tag] = {ty: (t.get(ty, 0.0) / (c[ty]/tot)) if c[ty] else 0.0 for ty in c}

# pass 2: redistribute each culture-and-religion group across the target occupations.
# Scaling alone cannot fix Britain, because its industrial provinces hold no farmer pops
# at all and a factor of two on zero is still zero. Types therefore have to be created.
# The mix is blended -- most of the way to the national target, part of the way kept
# local -- so a mining province still reads differently from a cathedral city.
BLEND = 0.80
changed = created = 0
for f, s in files.items():
    blocks = []
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        if pid in EU: blocks.append((pm.end(), i-1, pid))
    if not blocks: continue
    out, pos = [], 0
    for a, b, pid in blocks:
        body = s[a:b]; tag = owner[pid]
        # a European power's African or Asian provinces take the local structure,
        # not the metropole's: Bengal under the Company is not Lancashire
        ct = CONT.get(pid, "europe")
        tgt = TARGET[tag] if ct == "europe" else (
              TARGET[tag] if tag in ("QNG","JAP","KOR","TUR","PER") else BY_CONT.get(ct, TRADITIONAL))
        rows = POPRE.findall(body)
        if not rows: continue
        groups = collections.OrderedDict()
        local = collections.Counter()
        for ty, cu, rl, sz in rows:
            groups.setdefault((cu, rl), collections.Counter())[ty] += int(sz)
            local[ty] += int(sz)
        ltot = sum(local.values()) or 1
        mix = {}
        # sorted, not set order: Python's set iteration varies with the hash seed, so
        # two builds of the same input were producing the same pops in a different
        # order and the build was not byte-reproducible
        for ty in sorted(set(list(tgt) + list(local))):
            share = BLEND * tgt.get(ty, 0.0) + (1 - BLEND) * (local[ty] / ltot)
            if share > 0: mix[ty] = share
        msum = sum(mix.values()) or 1
        mix = {k: v / msum for k, v in mix.items()}
        txt = ""
        for (cu, rl), c in groups.items():
            total = sum(c.values())
            order = sorted(mix, key=lambda t: (-mix[t], t))   # name breaks ties
            placed = 0
            for k, ty in enumerate(order):
                n = int(round(total * mix[ty])) if k < len(order)-1 else total - placed
                if n < 1: continue
                placed += n
                if ty not in c: created += 1
                txt += f"\t{ty} = {{\n\t\tculture = {cu}\n\t\treligion = {rl}\n\t\tsize = {n}\n\t}}\n"
        out.append(s[pos:a]); out.append(txt); pos = b
        changed += 1
    out.append(s[pos:])
    open(f, "w", encoding="cp1252", errors="replace", newline="\n").write("".join(out))

print(f"  provinces restructured            {changed}")
print(f"  occupations created where absent  {created:,}")
