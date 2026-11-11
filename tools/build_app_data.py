import numpy as np, json, re, os, base64, io, collections
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

MOD = "/home/claude/hpm/HPM - Copy"
W = "/home/claude/work"
idx = np.load(f"{W}/idx.npy")
meta = json.load(open(f"{W}/pops_1836.json"))
stats = {int(k): v for k, v in json.load(open(f"{W}/prov_stats.json")).items()}
sea = set(meta["sea"])
H, Wd = idx.shape

# ---- choose a downscale: mode of each block so small provinces survive
def downscale(idx, f):
    h, w = H // f, Wd // f
    blocks = idx[:h*f, :w*f].reshape(h, f, w, f).transpose(0, 2, 1, 3).reshape(h, w, f*f)
    blocks.sort(axis=2)
    # modal value per block
    out = np.zeros((h, w), dtype=idx.dtype)
    best = np.zeros((h, w), dtype=np.int32)
    cur = blocks[:, :, 0]; run = np.ones((h, w), dtype=np.int32)
    out[:] = cur; best[:] = 1
    for k in range(1, f*f):
        v = blocks[:, :, k]
        same = v == cur
        run = np.where(same, run + 1, 1)
        cur = v
        better = run > best
        best = np.where(better, run, best)
        out = np.where(better, cur, out)
    return out

land = [p for p in meta["land"]]
for f in (6, 4, 3):
    small = downscale(idx, f)
    present = set(np.unique(small).tolist())
    missing = [p for p in land if p not in present]
    print(f"factor {f}: {Wd//f}x{H//f}, land provinces missing: {len(missing)}")

F = 3
small = downscale(idx, F)
h, w = small.shape
print("chosen", w, h)

# nudge: paint any missing land province at its scaled anchor
present = set(np.unique(small).tolist())
for p in land:
    if p not in present:
        s = stats[p]
        y, x = min(s["ly"] // F, h - 1), min(s["lx"] // F, w - 1)
        small[y, x] = p
print("land missing after nudge:", len([p for p in land if p not in set(np.unique(small).tolist())]))

# ---- encode province id into RGB
rgb = np.zeros((h, w, 3), dtype=np.uint8)
rgb[:, :, 0] = (small >> 16) & 255
rgb[:, :, 1] = (small >> 8) & 255
rgb[:, :, 2] = small & 255
buf = io.BytesIO()
Image.fromarray(rgb).save(buf, format="PNG", optimize=True, compress_level=9)
png = buf.getvalue()
print("index png:", round(len(png)/1024), "KB ->", round(len(png)*4/3/1024), "KB base64")
open(f"{W}/index_small.png", "wb").write(png)

# ---- borders overlay (1-bit, drawn from the small index)
bb = np.zeros((h, w), dtype=bool)
d = small[:, :-1] != small[:, 1:]; bb[:, :-1] |= d
d = small[:-1, :] != small[1:, :]; bb[:-1, :] |= d
ov = np.zeros((h, w, 4), dtype=np.uint8)
ov[bb] = (0, 0, 0, 90)
buf = io.BytesIO(); Image.fromarray(ov).save(buf, format="PNG", optimize=True, compress_level=9)
border_png = buf.getvalue()
print("border png:", round(len(border_png)/1024), "KB")
open(f"{W}/border_small.png", "wb").write(border_png)

# ---- cultures.txt -> groups
cu = re.sub(r"#.*", "", open(f"{MOD}/common/cultures.txt", encoding="latin-1").read())
groups, cur = {}, None
depth = 0
cgroup = {}
i = 0
# simple brace walk
tok = re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}", cu)
stack = []
for m in tok:
    if m.group(0) == "}":
        if stack: stack.pop()
    elif m.group(0) == "{":
        stack.append(None)
    else:
        name = m.group(1)
        if len(stack) == 0:
            stack.append(("group", name)); cur = name; groups[name] = []
        elif len(stack) == 1 and name not in ("color", "leader", "unit", "union", "is_overseas"):
            stack.append(("cult", name)); groups[cur].append(name); cgroup[name] = cur
        else:
            stack.append(None)
print("culture groups:", len(groups), "cultures:", len(cgroup))

religions = sorted(set(p[3] for p in meta["pops"]))
used_cultures = sorted(set(p[2] for p in meta["pops"]))
all_cultures = sorted(set(list(cgroup) + used_cultures))
for c in all_cultures:
    cgroup.setdefault(c, "unassigned")
print("cultures total:", len(all_cultures), "unused in 1836:", len(set(cgroup) - set(used_cultures)))

PT = meta["pop_types"]
ci = {c: i for i, c in enumerate(all_cultures)}
ri = {r: i for i, r in enumerate(religions)}
ti = {t: i for i, t in enumerate(PT)}
pops = [[p[0], ti[p[1]], ci[p[2]], ri[p[3]], p[4]] for p in meta["pops"]]

prov = {}
for p in meta["land"]:
    s = stats[p]
    prov[p] = [s["name"], meta["region"].get(str(p), ""), meta["continent"].get(str(p), ""),
               meta["owner"].get(str(p), ""), s["n"]]

payload = dict(
    w=w, h=h, F=F,
    cultures=all_cultures,
    culture_group={c: cgroup[c] for c in all_cultures},
    religions=religions,
    pop_types=PT,
    pops=pops,
    prov=prov,
    sea=sorted(sea),
    index_png="data:image/png;base64," + base64.b64encode(png).decode(),
    border_png="data:image/png;base64," + base64.b64encode(border_png).decode(),
)
js = json.dumps(payload, separators=(",", ":"))
open(f"{W}/app_data.json", "w").write(js)
print("payload:", round(len(js)/1024/1024, 2), "MB")
