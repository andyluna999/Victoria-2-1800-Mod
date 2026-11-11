"""Event pictures for the Mexican chain.

Victoria II wants 521 x 203 — a wide, shallow letterbox. None of the source paintings
is that shape: the Bastin lithograph of Iturbide's entry is nearly 5,000 pixels wide,
the Alhondiga is a small canvas, and the coronation is almost square.

Fitting them by squashing would ruin all three, so each is cropped rather than scaled:
the image is enlarged until it covers the frame and then a band is taken out of it. The
band is not always the middle. In the entry into Mexico City the interest is the line
of horsemen across the upper third, and in the coronation it is Iturbide's head and the
crown above it, so those are offset upward.

  **The Army of the Three Guarantees** -- Bastin's lithograph of Iturbide riding into
  Mexico City on 27 September 1821 with the generals of the new army behind him, most
  of whom had spent the previous decade fighting for the King. Santa Anna is in the
  index along the bottom.

  **The Alhondiga de Granaditas** -- Guanajuato, 28 September 1810. The granary where
  the Spanish and creole families of the town barricaded themselves, and where everyone
  inside was killed when Hidalgo's people got the door open.

  **The coronation** -- Iturbide crowned emperor in July 1822, the throne having been
  offered to Ferdinand VII and refused.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import os, collections
from PIL import Image

MOD = _BUILD
SRC = f"{_TOOLS}/eventart"
W, H = 521, 203
log = collections.Counter()

# source file -> (output name, vertical anchor 0.0 top .. 1.0 bottom)
ART = {
    "three_guarantees.png":    ("1821_three_guarantees", 0.42),
    "grito_alhondiga.png":     ("1810_grito_de_dolores", 0.50),
    "iturbide_crowned.png":    ("1822_iturbide_crowned", 0.30),
    # The swearing of the Constitution at Cadiz: the dais, the deputies and the crowd
    # all sit across the middle of the canvas.
    "cadiz_constitution.png":  ("1812_cadiz_constitution", 0.48),
    # A portrait-shaped canvas, so the band has to be taken high enough to catch the
    # faces rather than the boots.
    "bolivar.png":             ("1819_bolivar", 0.32),
    # San Martin on the white horse, with the column behind him.
    "san_martin.png":          ("1817_san_martin", 0.46),
    # Iturrigaray with his wife and children, painted while he was viceroy.
    "iturrigaray.png":         ("1808_iturrigaray", 0.38),
}

os.makedirs(f"{MOD}/gfx/pictures/events", exist_ok=True)
for src, (name, anchor) in ART.items():
    p = os.path.join(SRC, src)
    if not os.path.exists(p): continue
    im = Image.open(p).convert("RGB")
    # cover the frame, then take a band out of it
    sc = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * sc)), max(H, round(im.height * sc))),
                   Image.LANCZOS)
    left = (im.width - W) // 2
    top = int(round((im.height - H) * anchor))
    top = max(0, min(im.height - H, top))
    im = im.crop((left, top, left + W, top + H))
    im.save(f"{MOD}/gfx/pictures/events/{name}.tga")
    log["event pictures"] += 1

# point the events at them
EDITS = [
    ("events/1800_Civil_Wars.txt", "9101700", "1810_grito_de_dolores"),
    ("decisions/1800_Autonomy.txt", "the_plan_of_iguala", "1821_three_guarantees"),
    ("events/1800_Constitutional.txt", "9100802", "1812_cadiz_constitution"),
    ("events/1800_Constitutional.txt", "9100804", "1812_cadiz_constitution"),
    ("events/1800_Iturrigaray.txt", "9101100", "1808_iturrigaray"),
    ("events/1800_Yermo.txt", "9101115", "1808_iturrigaray"),
    ("events/1800_Haiti_After.txt", "9101310", "1819_bolivar"),
    ("events/1800_Haiti_After.txt", "9101311", "1819_bolivar"),
    ("events/1800_Civil_Wars.txt", "9101712", "1819_bolivar"),
    ("events/1800_Civil_Wars.txt", "9101718", "1817_san_martin"),
    ("events/1800_Civil_Wars.txt", "9101724", "1817_san_martin"),
    ("decisions/1800_Autonomy.txt", "the_protectorate_of_san_martin", "1817_san_martin"),
    ("decisions/1800_Autonomy.txt", "the_treaty_of_trujillo", "1819_bolivar"),
    ("decisions/1800_Autonomy.txt", "the_congress_of_tucuman", "1817_san_martin"),
    ("decisions/1800_Constitutional.txt", "accept_the_constitution_of_cadiz",
     "1812_cadiz_constitution"),
    ("decisions/1800_Constitutional.txt", "refuse_the_constitution_of_cadiz",
     "1812_cadiz_constitution"),
    ("decisions/1800_Yermo.txt", "garrison_the_palace", "1808_iturrigaray"),
    # the coronation event names its own picture at creation, so nothing to rewrite
]
for rel, key, pic in EDITS:
    f = f"{MOD}/{rel}"
    if not os.path.exists(f): continue
    s = open(f, encoding="cp1252", errors="replace").read()
    i = s.find(key)
    if i < 0: continue
    j = s.find("picture", i)
    k = s.find("\n", j)
    if j < 0 or j - i > 900: continue
    s = s[:j] + f'picture = "{pic}"' + s[k:]
    open(f, "w", encoding="cp1252", errors="replace", newline="\n").write(s)
    log["events repictured"] += 1

for k, v in sorted(log.items()): print(f"  {k:<22}{v}")
