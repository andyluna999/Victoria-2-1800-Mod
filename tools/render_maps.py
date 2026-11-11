import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import numpy as np, json, re, os, glob
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None

MOD = _SRC
W, OUT = _WORK, "/mnt/user-data/outputs"
os.makedirs(OUT, exist_ok=True)

idx = np.load(f"{W}/idx.npy")
stats = {int(k): v for k, v in json.load(open(f"{W}/prov_stats.json")).items()}
meta = json.load(open(f"{W}/pops_1836.json"))
sea = set(meta["sea"]); owner = {int(k): v for k, v in meta["owner"].items()}
H, Wd = idx.shape

# ---- border mask: mark BOTH sides of every edge so fills can't leak
b = np.zeros_like(idx, dtype=bool)
d = idx[:, :-1] != idx[:, 1:]
b[:, :-1] |= d; b[:, 1:] |= d
d = idx[:-1, :] != idx[1:, :]
b[:-1, :] |= d; b[1:, :] |= d

is_sea = np.isin(idx, list(sea))

# ---- paint base
base = np.zeros((H, Wd, 3), dtype=np.uint8)
base[...] = (255, 255, 255)            # land: paintable white
base[is_sea] = (28, 52, 74)            # sea: do not paint
base[idx == 0] = (255, 0, 255)         # unmapped: magenta
base[b] = (0, 0, 0)                    # borders

# rescue provinces whose interior was eaten by the border
rescued = []
for pid, s in stats.items():
    if pid in sea:
        continue
    y0, y1, x0, x1 = s["y0"], s["y1"], s["x0"], s["x1"]
    sub = idx[y0:y1+1, x0:x1+1] == pid
    if not (sub & ~b[y0:y1+1, x0:x1+1]).any():
        base[s["ly"], s["lx"]] = (255, 255, 255)
        rescued.append(pid)
print("tiny provinces rescued:", len(rescued), rescued[:20])
Image.fromarray(base).save(f"{OUT}/HPM_paint_base.png", optimize=True)
print("paint base done")

# ---- numbered reference
font = None
for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
    if os.path.exists(p):
        font = ImageFont.truetype(p, 12); break
if font is None:
    font = ImageFont.load_default()

num = Image.fromarray(base.copy())
dr = ImageDraw.Draw(num)
for pid, s in sorted(stats.items()):
    t = str(pid)
    bb = dr.textbbox((0, 0), t, font=font)
    x = s["lx"] - (bb[2]-bb[0])//2; y = s["ly"] - (bb[3]-bb[1])//2 - 1
    dr.text((x, y), t, font=font, fill=(150, 170, 190) if pid in sea else (200, 30, 30))
num.save(f"{OUT}/HPM_provinces_numbered.png", optimize=True)
print("numbered done")

# ---- current ownership reference
reg = open(f"{MOD}/common/countries.txt", encoding="latin-1").read()
reg = re.sub(r"#.*", "", reg)
colmap = {}
for m in re.finditer(r"^\s*([A-Z]{3})\s*=\s*\"?([^\"\n]+?)\"?\s*$", reg, re.M):
    tag, rel = m.group(1), m.group(2).strip()
    f = os.path.join(MOD, "common", rel)
    if not os.path.exists(f):
        continue
    c = re.search(r"^\s*color\s*=\s*\{\s*(\d+)\s+(\d+)\s+(\d+)", open(f, encoding="latin-1", errors="replace").read(), re.M)
    if c:
        colmap[tag] = tuple(int(c.group(i)) for i in (1, 2, 3))
print("country colours:", len(colmap))

ow = np.zeros((H, Wd, 3), dtype=np.uint8)
ow[...] = (235, 232, 222)              # unowned land
ow[is_sea] = (28, 52, 74)
lut = np.zeros((idx.max()+1, 3), dtype=np.uint8)
lut[:] = (235, 232, 222)
for pid, tag in owner.items():
    lut[pid] = colmap.get(tag, (120, 120, 120))
m = (~is_sea) & (idx > 0)
ow[m] = lut[idx[m]]
ow[b] = (0, 0, 0)
Image.fromarray(ow).save(f"{OUT}/HPM_current_owners_1836.png", optimize=True)
print("owners done")

for f in ["HPM_paint_base.png", "HPM_provinces_numbered.png", "HPM_current_owners_1836.png"]:
    print(f, round(os.path.getsize(f"{OUT}/{f}")/1e6, 1), "MB")
