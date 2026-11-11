import re, json, os, glob, collections

MOD = "/home/claude/hpm/HPM - Copy"
OUT = "/home/claude/work"

# --- land / sea
txt = open(f"{MOD}/map/default.map", encoding="latin-1").read()
sea = set(int(x) for x in re.search(r"sea_starts\s*=\s*\{(.*?)\}", txt, re.S).group(1).split())
maxp = int(re.search(r"max_provinces\s*=\s*(\d+)", txt).group(1))
land = [p for p in range(1, maxp) if p not in sea]
print("max_provinces", maxp, "sea", len(sea), "land", len(land))

# --- regions
reg = {}
for m in re.finditer(r"^([A-Za-z0-9_]+)\s*=\s*\{([^}]*)\}", open(f"{MOD}/map/region.txt", encoding="latin-1").read(), re.M):
    for p in m.group(2).split():
        if p.isdigit():
            reg[int(p)] = m.group(1)
print("provinces with region:", len(reg))

# --- continents
cont = {}
for m in re.finditer(r"^([a-z_]+)\s*=\s*\{(.*?)\n\}", open(f"{MOD}/map/continent.txt", encoding="latin-1").read(), re.S | re.M):
    body = re.search(r"provinces\s*=\s*\{(.*?)\}", m.group(2), re.S)
    if body:
        for p in body.group(1).split():
            if p.isdigit():
                cont[int(p)] = m.group(1)
print("provinces with continent:", len(cont))

# --- owner / controller / cores from history/provinces
own, cores = {}, collections.defaultdict(list)
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    base = os.path.basename(f)
    m = re.match(r"(\d+)", base)
    if not m:
        continue
    pid = int(m.group(1))
    s = open(f, encoding="latin-1", errors="replace").read()
    s = re.sub(r"#.*", "", s)
    # only the header block (before any dated block)
    head = re.split(r"\n\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=", s)[0]
    o = re.search(r"\bowner\s*=\s*([A-Z]{3})", head)
    if o:
        own[pid] = o.group(1)
    for c in re.finditer(r"\badd_core\s*=\s*([A-Z]{3})", head):
        cores[pid].append(c.group(1))
print("provinces with owner:", len(own))

# --- pops
POP_TYPES = ["aristocrats","artisans","bureaucrats","capitalists","clergymen","clerks",
             "craftsmen","farmers","labourers","officers","serfs","slaves","soldiers"]
pt_re = "|".join(POP_TYPES)
pops = []   # (prov, type, culture, religion, size)
files = sorted(glob.glob(f"{MOD}/history/pops/1836.1.1/*.txt"))
for f in files:
    s = open(f, encoding="latin-1", errors="replace").read()
    s = re.sub(r"#.*", "", s)
    for pm in re.finditer(r"(\d+)\s*=\s*\{", s):
        pid = int(pm.group(1))
        # find matching close brace
        i = pm.end(); depth = 1
        while i < len(s) and depth:
            if s[i] == "{": depth += 1
            elif s[i] == "}": depth -= 1
            i += 1
        body = s[pm.end():i-1]
        for em in re.finditer(r"\b(" + pt_re + r")\s*=\s*\{(.*?)\}", body, re.S):
            b = em.group(2)
            cu = re.search(r"culture\s*=\s*([a-z_]+)", b)
            re_ = re.search(r"religion\s*=\s*([a-z_]+)", b)
            sz = re.search(r"size\s*=\s*(\d+)", b)
            if cu and re_ and sz:
                pops.append([pid, em.group(1), cu.group(1), re_.group(1), int(sz.group(1))])

print("pop entries:", len(pops), "from", len(files), "files")
print("total pop size:", sum(p[4] for p in pops))
provs = set(p[0] for p in pops)
print("provinces with pops:", len(provs))
print("land provinces WITHOUT pops:", len([p for p in land if p not in provs]))
print("sea/other provinces WITH pops:", sorted(p for p in provs if p in sea)[:10])
cults = collections.Counter(p[2] for p in pops)
rels = collections.Counter(p[3] for p in pops)
print("cultures used:", len(cults), cults.most_common(8))
print("religions used:", len(rels), rels.most_common())

json.dump(dict(sea=sorted(sea), land=land, maxp=maxp, region=reg, continent=cont,
               owner=own, cores=cores, pops=pops, pop_types=POP_TYPES),
          open(f"{OUT}/pops_1836.json", "w"))
print("written")
