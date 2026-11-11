import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import numpy as np, csv, json, os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

MOD = _SRC
OUT = _WORK
os.makedirs(OUT, exist_ok=True)

# --- definition.csv: colour -> province id, name
rows = []
with open(f"{MOD}/map/definition.csv", encoding="latin-1") as f:
    r = csv.reader(f, delimiter=";")
    next(r)
    for row in r:
        if not row or not row[0].strip().isdigit():
            continue
        def num(s):
            d = "".join(ch for ch in s if ch.isdigit())
            return int(d) if d else 0
        pid = int(row[0]); rgb = (num(row[1]), num(row[2]), num(row[3]))
        name = row[4] if len(row) > 4 else ""
        rows.append((pid, rgb, name))
print("definition rows:", len(rows), "max id:", max(r[0] for r in rows))

names = {pid: nm for pid, rgb, nm in rows}
colour_of = {pid: rgb for pid, rgb, nm in rows}

# duplicate colours?
seen = {}
dups = []
for pid, rgb, nm in rows:
    if rgb in seen:
        dups.append((seen[rgb], pid, rgb))
    seen[rgb] = pid
print("duplicate colours:", len(dups), dups[:5])

im = Image.open(f"{MOD}/map/provinces.bmp").convert("RGB")
a = np.asarray(im, dtype=np.uint8)
# Victoria II stores the province bitmap bottom-up: row 0 of the decoded image is the
# SOUTH edge of the map, which is also why positions.txt measures y from the bottom.
# Flip here so every downstream raster, label anchor and exported PNG has north up.
a = np.flipud(a).copy()
H, W, _ = a.shape
print("bmp:", W, H)

key = (a[:, :, 0].astype(np.uint32) << 16) | (a[:, :, 1].astype(np.uint32) << 8) | a[:, :, 2].astype(np.uint32)

lut = np.zeros(1 << 24, dtype=np.uint16)  # 0 = unknown/sea-unmapped
for pid, rgb, nm in rows:
    lut[(rgb[0] << 16) | (rgb[1] << 8) | rgb[2]] = pid
idx = lut[key]  # H x W of province ids

uniq, counts = np.unique(idx, return_counts=True)
present = set(int(u) for u in uniq if u != 0)
defined = set(names)
print("ids painted on map:", len(present))
print("defined but not painted:", sorted(defined - present)[:20], "count", len(defined - present))
print("painted but not defined (unmapped colours):", int(counts[uniq == 0][0]) if 0 in uniq else 0, "pixels")

np.save(f"{OUT}/idx.npy", idx)

# --- per province stats
stats = {}
ys, xs = np.nonzero(idx)
ids = idx[ys, xs]
order = np.argsort(ids, kind="stable")
ids_s, ys_s, xs_s = ids[order], ys[order], xs[order]
bounds = np.searchsorted(ids_s, np.arange(1, ids_s.max() + 2))
for pid in sorted(present):
    s, e = bounds[pid - 1], bounds[pid]
    py, px = ys_s[s:e], xs_s[s:e]
    cy, cx = py.mean(), px.mean()
    d = (py - cy) ** 2 + (px - cx) ** 2
    k = int(np.argmin(d))
    stats[pid] = dict(
        n=int(e - s), x0=int(px.min()), x1=int(px.max()), y0=int(py.min()), y1=int(py.max()),
        lx=int(px[k]), ly=int(py[k]), name=names.get(pid, ""))
json.dump(stats, open(f"{OUT}/prov_stats.json", "w"))

sizes = sorted((v["n"], k) for k, v in stats.items())
print("smallest provinces:", sizes[:5])
print("median px:", sizes[len(sizes)//2][0])
print("provinces under 100px:", sum(1 for n, _ in sizes if n < 100))
