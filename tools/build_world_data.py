import numpy as np, json, re, os, glob, base64, io, collections
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
MOD = "/home/claude/hpm/HPM - Copy"; W = "/home/claude/work"

meta = json.load(open(f"{W}/pops_1836.json"))
stats = {int(k): v for k, v in json.load(open(f"{W}/prov_stats.json")).items()}
sea = set(meta["sea"])

# ---------- province history ----------
FIELDS = ["owner","controller","trade_goods","life_rating","terrain","colonial",
          "naval_base","fort","railroad","is_slave"]
P = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    m = re.match(r"(\d+)", os.path.basename(f))
    if not m: continue
    pid = int(m.group(1))
    s = re.sub(r"#.*", "", open(f, encoding="latin-1", errors="replace").read())
    head = re.split(r"\n\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=", s)[0]
    d = {}
    for k in FIELDS:
        mm = re.search(r"\b" + k + r"\s*=\s*([A-Za-z_0-9]+)", head)
        if mm: d[k] = mm.group(1)
    d["cores"] = sorted(set(re.findall(r"\badd_core\s*=\s*([A-Z]{3})", head)))
    P[pid] = d
print("province history files:", len(P))

# ---------- countries ----------
reg = re.sub(r"#.*", "", open(f"{MOD}/common/countries.txt", encoding="latin-1").read())
tagfile = {}
for m in re.finditer(r"^\s*([A-Z]{3})\s*=\s*\"?([^\"\n]+?)\"?\s*$", reg, re.M):
    tagfile[m.group(1)] = m.group(2).strip()
names = {}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)[:-4]
    if " - " in b:
        t, n = b.split(" - ", 1); names[t.strip()] = n.strip()
# primary and accepted cultures live in history/countries, not common/countries
prim, acc = {}, {}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)[:-4]
    if " - " not in b: continue
    tag = b.split(" - ", 1)[0].strip()
    txt = re.sub(r"#.*", "", open(f, encoding="latin-1", errors="replace").read())
    head = re.split(r"\n\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=", txt)[0]
    m = re.search(r"\bprimary_culture\s*=\s*([a-z_0-9]+)", head)
    if m: prim[tag] = m.group(1)
    acc[tag] = sorted(set(re.findall(r"^\s*culture\s*=\s*([a-z_0-9]+)", head, re.M)))
print("tags with a primary culture:", len(prim), " with accepted cultures:",
      sum(1 for v in acc.values() if v))

COU = {}
for tag, rel in tagfile.items():
    p = os.path.join(MOD, "common", rel)
    col = None
    if os.path.exists(p):
        c = re.search(r"^\s*color\s*=\s*\{\s*(\d+)\s+(\d+)\s+(\d+)",
                      open(p, encoding="latin-1", errors="replace").read(), re.M)
        if c: col = [int(c.group(i)) for i in (1, 2, 3)]
    COU[tag] = {"name": names.get(tag, rel.split("/")[-1][:-4]), "color": col or [130, 130, 130],
                "prim": prim.get(tag, ""), "acc": acc.get(tag, [])}
print("countries:", len(COU))

# ---------- goods ----------
g = re.sub(r"#.*", "", open(f"{MOD}/common/goods.txt", encoding="latin-1").read())
goods, depth, cur = [], 0, None
for m in re.finditer(r"([a-z_0-9]+)\s*=\s*\{|\{|\}", g):
    t = m.group(0)
    if t == "}": depth -= 1
    elif t == "{": depth += 1
    else:
        if depth == 1 and m.group(1) != "color": goods.append(m.group(1))
        depth += 1
goods = sorted(set(goods))
print("goods:", len(goods))

# ---------- cultures ----------
cu = re.sub(r"#.*", "", open(f"{MOD}/common/cultures.txt", encoding="latin-1").read())
cgroup, depth, cur = {}, 0, None
for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}", cu):
    t = m.group(0)
    if t == "}": depth -= 1
    elif t == "{": depth += 1
    else:
        n = m.group(1)
        if depth == 0: cur = n
        elif depth == 1 and n not in ("color","leader","unit","union","is_overseas"): cgroup[n] = cur
        depth += 1
religions = sorted(set(p[3] for p in meta["pops"]))
cultures = sorted(set(list(cgroup) + [p[2] for p in meta["pops"]]))
for c in cultures: cgroup.setdefault(c, "unassigned")
PT = meta["pop_types"]
ci = {c:i for i,c in enumerate(cultures)}; ri = {r:i for i,r in enumerate(religions)}
ti = {t:i for i,t in enumerate(PT)}
pops = [[p[0], ti[p[1]], ci[p[2]], ri[p[3]], p[4]] for p in meta["pops"]]
print("cultures", len(cultures), "religions", len(religions), "pops", len(pops))

# ---------- province payload ----------
prov = {}
for p in meta["land"]:
    s = stats[p]; h = P.get(p, {})
    prov[p] = {
        "n": s["name"], "rg": meta["region"].get(str(p), ""), "ct": meta["continent"].get(str(p), ""),
        "px": s["n"],
        "o": h.get("owner", ""), "c": h.get("controller", ""), "cr": h.get("cores", []),
        "g": h.get("trade_goods", ""), "lr": int(h.get("life_rating", 0) or 0),
        "tr": h.get("terrain", ""), "col": 1 if h.get("colonial") not in (None, "0") else 0,
        "nb": int(h.get("naval_base", 0) or 0), "ft": int(h.get("fort", 0) or 0),
        "rr": int(h.get("railroad", 0) or 0),
    }
print("provinces:", len(prov), "with owner:", sum(1 for v in prov.values() if v["o"]))

payload = dict(
    w=0, h=0, cultures=cultures, culture_group=cgroup, religions=religions, pop_types=PT,
    goods=goods, pops=pops, prov=prov, countries=COU, sea=sorted(sea),
)
# reuse rasters built earlier
small = json.load(open(f"{W}/app_data.json"))
payload["w"], payload["h"] = small["w"], small["h"]
payload["index_png"] = small["index_png"]; payload["border_png"] = small["border_png"]
js = json.dumps(payload, separators=(",", ":"))
open(f"{W}/world_data.json", "w").write(js)
print("payload:", round(len(js)/1024/1024, 2), "MB")
