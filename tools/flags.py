"""Flags for the forty-six tags this project created.

Drawn rather than collected. Images off the web are modern copyrighted renderings at
whatever size and style their author chose; these designs are simple enough to render
from their historical descriptions, which keeps the set consistent, reproducible inside
the build, and free of anyone else's artwork.

Each entry below says what the design is based on. Three categories:

**Attested.** The Cross of Burgundy flew over Spanish America until 1843 and is the
right flag for every viceroyalty. The Bhagwa Dhwaj, the saffron swallowtail, is the
Maratha standard. Genoa's red cross on white is the Ligurian Republic's. Tunis under
the Husainids used the red field with a white disc. These are drawn as described.

**Differenced.** The Spanish viceroyalties all flew the same colours, which is useless
in a game where you must tell Peru from Mexico at a glance. They share the Cross of
Burgundy and are differenced by a canton. The canton is a game device and is not
historical; the cross is.

**Abstract.** The twenty-six Indigenous nations of North America did not use flags, and
the tribal flags that exist today are twentieth-century designs. Inventing
pseudo-historical ones would be worse than useless, so these are plain geometric
devices built from each nation's culture colour -- an identifier, not a claim.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import os, math, collections
from PIL import Image, ImageDraw

MOD = _BUILD
W, H = 93, 64
log = collections.Counter()

def new(bg): return Image.new("RGB", (W, H), bg)

def save_tga(im, path):
    """Write the flag the way HPM writes its own: 32 bits with an alpha channel.

    Ours were 24-bit with no alpha. Victoria II redraws country flags when the map
    mode changes, and a flag in a format the engine does not expect is a plausible
    reason for a hang at exactly that moment. Matching HPM byte-for-byte in format
    costs nothing and removes the question.
    """
    im.convert("RGBA").save(path)

def cross(im, col, t=10, ox=0):
    d = ImageDraw.Draw(im)
    d.rectangle([0, H//2 - t//2, W, H//2 + t//2 - 1], fill=col)
    d.rectangle([W//2 - t//2 + ox, 0, W//2 + t//2 - 1 + ox, H], fill=col)

def saltire_raguly(im, col, t=8):
    """The Cross of Burgundy: a saltire of two ragged, lopped branches.

    The ragged stubs are the whole point of the design -- it is a pair of pruned
    tree limbs crossed, not a plain St Andrew's cross -- so they are drawn as short
    spurs set perpendicular to each arm.
    """
    d = ImageDraw.Draw(im)
    for (ax, ay), (bx, by) in (((0, 0), (W, H)), ((0, H), (W, 0))):
        d.line([(ax, ay), (bx, by)], fill=col, width=t)
        dx, dy = (bx - ax), (by - ay)
        ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln
        px, py = -uy, ux                      # perpendicular
        for k in range(1, 9):                 # spurs along the limb
            cx, cy = ax + dx * k / 9, ay + dy * k / 9
            for sgn in (1, -1):
                d.line([(cx, cy),
                        (cx + px * 9 * sgn + ux * 4, cy + py * 9 * sgn + uy * 4)],
                       fill=col, width=4)

def canton(im, col, w=34, h=24):
    ImageDraw.Draw(im).rectangle([0, 0, w, h], fill=col)

def bands(im, cols, horizontal=True):
    d = ImageDraw.Draw(im); n = len(cols)
    for i, c in enumerate(cols):
        if horizontal: d.rectangle([0, H*i//n, W, H*(i+1)//n - 1], fill=c)
        else: d.rectangle([W*i//n, 0, W*(i+1)//n - 1, H], fill=c)

def crescent(im, col, cx=46, cy=32, r=17, off=7, bg=None):
    """The bite must be cut in whatever lies behind the crescent, which is not always
    the colour of the corner pixel -- on Tunis it sits on a white disc, not the red
    field, and reading the corner erased the whole device."""
    d = ImageDraw.Draw(im)
    if bg is None: bg = im.getpixel((cx, cy))
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    d.ellipse([cx-r+off, cy-r+2, cx+r+off, cy+r-2], fill=bg)

def star(im, col, cx, cy, r):
    pts = []
    for i in range(10):
        a = math.pi/2 + i*math.pi/5
        rr = r if i % 2 == 0 else r*0.42
        pts.append((cx + rr*math.cos(a), cy - rr*math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=col)

def disc(im, col, cx=46, cy=32, r=20):
    ImageDraw.Draw(im).ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)

def swallowtail(im, bg):
    d = ImageDraw.Draw(im)
    d.polygon([(W, 0), (W, H), (W-26, H//2)], fill=bg)

def diag(im, col, w=14):
    ImageDraw.Draw(im).line([(0, H), (W, 0)], fill=col, width=w)

def border(im, col, t=4):
    d = ImageDraw.Draw(im)
    for i in range(t):
        d.rectangle([i, i, W-1-i, H-1-i], outline=col)

WHITE=(242,242,238); RED=(186,28,36); GOLD=(240,190,40); GREEN=(28,112,64)
BLUE=(30,62,140); BLACK=(26,26,28); SAFFRON=(232,135,30); CRIM=(140,22,32)
SKY=(90,160,210); MAROON=(110,34,44); SAND=(214,186,132); TEAL=(42,118,126)

def spanish_colony(cant):
    """Cross of Burgundy, differenced by a canton for legibility."""
    im = new(WHITE); saltire_raguly(im, RED)
    if cant: canton(im, cant, 30, 21)
    return im

# --- supplied artwork -------------------------------------------------------------
# Real flags, already at 93x64. These take precedence over anything drawn here.
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flagart")
def art(name):
    """Load supplied artwork at whatever size it arrives and fit it to 93x64.

    Flags off Wikimedia come as SVG renders at 1200x800, 2560x1707, anything. Rather
    than asking for them pre-sized, take what is given: scale to cover, centre, crop.
    Cover rather than fit, because a letterboxed flag with bars down the side is a
    worse lie than a few pixels trimmed off a field of solid colour.
    """
    im = Image.open(os.path.join(ART, name)).convert("RGB")
    if im.size == (W, H): return im
    sc = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * sc)), max(H, round(im.height * sc))),
                   Image.LANCZOS)
    left, top = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((left, top, left + W, top + H))

FLAGS = {}
# --- the Spanish Americas ----------------------------------------------------------
# Every viceroyalty and captaincy-general flew the same Cross of Burgundy. They are
# not differenced here: they were not differenced in life, and a player can tell Peru
# from Mexico by where it is on the map.
SPANISH_COLONIES = ("NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR")
for _t in SPANISH_COLONIES:
    FLAGS[_t] = lambda: art("new_spain.png")

# The Viceroyalty of Brazil takes HPM's own Brazilian flag, copied per government
# type, rather than anything drawn here.
HPM_COPY = {"EBR": "BRZ"}

# --- the Mediterranean republics --------------------------------------------------
def lig():
    """Genoa's cross of St George, with the republican canton of 1797."""
    im = new(WHITE); cross(im, RED, 12); canton(im, GREEN, 30, 21); return im
FLAGS["LIG"] = lig
def rag():
    """Ragusa: the LIBERTAS banner, a blue band on white."""
    im = new(WHITE); d = ImageDraw.Draw(im)
    d.rectangle([0, 24, W, 40], fill=BLUE)
    d.rectangle([0, 24, W, 27], fill=GOLD); d.rectangle([0, 37, W, 40], fill=GOLD)
    return im
FLAGS["RAG"] = rag

# --- the Barbary regencies ----------------------------------------------------------
def rga():
    """Algiers: the Ottoman regency, crescent on red."""
    im = new(RED); crescent(im, WHITE, bg=RED); return im
FLAGS["RGA"] = rga
def btn():
    """Tunis under the Husainids: a white disc on red, crescent and star within."""
    im = new(RED); disc(im, WHITE, 46, 32, 23)
    crescent(im, RED, 43, 32, 15, 7, bg=WHITE)
    star(im, RED, 55, 32, 7); return im
FLAGS["BTN"] = btn
def krm():
    """Tripoli under the Karamanli: crescent on green."""
    im = new(GREEN); crescent(im, WHITE, bg=GREEN); return im
FLAGS["KRM"] = krm

# --- India and south-east Asia -------------------------------------------------------
def mar():
    """The Bhagwa Dhwaj, the saffron swallowtail standard of the Marathas."""
    im = new(SAFFRON); swallowtail(im, WHITE); return im
FLAGS["MAR"] = mar
def crn():
    """The Nawab of the Carnatic: crescent on green, in the Mughal manner."""
    im = new(GREEN); crescent(im, GOLD, 44, 32, 16, 6, bg=GREEN)
    border(im, GOLD, 3); return im
FLAGS["CRN"] = crn
def tys():
    """Tay Son: the red banner of the rising, with a gold border."""
    im = new(RED); border(im, GOLD, 5); disc(im, GOLD, 46, 32, 13); return im
FLAGS["TYS"] = tys

# --- the Caucasus ---------------------------------------------------------------------
def geo():
    """Kartli-Kakheti: the five-cross banner of the Georgian kings."""
    im = new(WHITE); cross(im, RED, 11)
    for cx, cy in ((22, 16), (70, 16), (22, 48), (70, 48)):
        d = ImageDraw.Draw(im)
        d.rectangle([cx-7, cy-2, cx+7, cy+2], fill=RED)
        d.rectangle([cx-2, cy-7, cx+2, cy+7], fill=RED)
    return im
FLAGS["GEO"] = geo
def ime():
    """Imereti: the Georgian cross with the blue of the western kingdom."""
    im = new(WHITE); cross(im, RED, 11); canton(im, BLUE, 28, 20); return im
FLAGS["IME"] = ime
# the Muslim khanates of the Araxes, Persian vassals: reconstructions, not attested
# The khanates of the Araxes left no flags, so they get plain banners rather than
# invented devices: a colour each, and no claim to a design nobody recorded.
FLAGS["YER"] = lambda: new(GREEN)
FLAGS["GAN"] = lambda: new(CRIM)
FLAGS["BAK"] = lambda: new(TEAL)

# --- west Africa -----------------------------------------------------------------------
def hau():
    """The Hausa city-states: a reconstruction in the colours of the Sahel."""
    im = new(GREEN); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 26, H], fill=SAND)
    crescent(im, SAND, 58, 32, 15, 6, bg=GREEN); return im
FLAGS["HAU"] = hau

# --- the Indigenous nations of North America -------------------------------------------
# Abstract devices from each nation's culture colour. These nations did not use flags
# and the tribal flags that exist today are modern; these are identifiers, not claims.
NATIVE = {
 "COM": (176,88,39), "CRK": (178,50,69), "CCY": (166,54,60), "CAW": (154,58,56),
 "CHA": (170,52,64), "IRO": (150,56,52), "ANI": (196,52,58), "OSA": (140,92,38),
 "PAW": (152,100,42), "SIO": (127,88,67), "ARI": (208,62,42), "BLA": (65,23,11),
 "BCY": (65,23,11), "CRA": (186,66,40), "SAL": (150,62,52), "NEZ": (168,60,56),
 "COK": (140,70,58), "COA": (146,66,54), "APA": (133,40,0), "NAV": (133,40,0),
 "TLI": (120,74,62), "YUP": (146,120,96), "AAA": (158,76,50), "SEM": (119,53,44),
 "MAP": (66,111,128),
}
def native(col, style):
    im = new(col); d = ImageDraw.Draw(im)
    light = tuple(min(255, int(c*1.0) + 70) for c in col)
    dark = tuple(max(0, int(c*0.55)) for c in col)
    if style == 0:
        d.rectangle([0, H//3, W, 2*H//3 - 1], fill=light)
    elif style == 1:
        d.polygon([(0,0),(34,H//2),(0,H)], fill=light)
    elif style == 2:
        d.rectangle([0, 0, W, H//4], fill=light); d.rectangle([0, 3*H//4, W, H], fill=light)
    elif style == 3:
        disc(im, light, 46, 32, 18)
    elif style == 4:
        diag(im, light, 16)
    elif style == 5:
        d.rectangle([W//3, 0, 2*W//3 - 1, H], fill=light)
    for i in range(0, W, 12):
        d.rectangle([i, H-6, i+5, H], fill=dark)
    return im
for i, (tag, col) in enumerate(sorted(NATIVE.items())):
    FLAGS[tag] = (lambda c=col, s=i % 6: native(c, s))

# --- write them out ---------------------------------------------------------------------
GOV = ("", "_communist", "_fascist", "_monarchy", "_republic")

SRC_FLAGS = f"{_SRC}/gfx/flags"
for _dst, _src in HPM_COPY.items():
    for _g in GOV:
        _f = os.path.join(SRC_FLAGS, f"{_src}{_g}.tga")
        if not os.path.exists(_f): _f = os.path.join(SRC_FLAGS, f"{_src}.tga")
        if os.path.exists(_f):
            Image.open(_f).convert("RGBA").save(f"{MOD}/gfx/flags/{_dst}{_g}.tga")
            log["copied from HPM"] += 1

# Specific files for specific government types, from the supplied artwork.
# Mexico gets a complete set spanning its first decade of existence: the flag the
# Army of the Three Guarantees carried into Mexico City in September 1821, Iturbide's
# empire, the federal republic, Hidalgo's Guadalupe banner for the popular revolution
# -- which is the branch our capital-flight chain turns on -- and the Cristero banner
# for a clerical reaction.
OVERRIDE = {
 # --- the viceroyalties ------------------------------------------------------------
 # Victoria II picks a flag from the government's flagType, and absolute_monarchy maps
 # to `monarchy`. The colonies are absolute monarchies, so `_monarchy` is the flag
 # they actually fly day to day -- it must be the plain Cross of Burgundy, the same
 # for every one of them. Putting the regency flags there had them flying the arms of
 # a self-governing junta while obediently paying tribute to Madrid, and the Cross of
 # Burgundy would never have appeared on screen at all.
 #
 # The regency is what happens when the viceroy or governor seizes self-rule in the
 # King's name -- Iturrigaray in Mexico in 1808, deposed by the peninsular faction for
 # exactly that. A junta is not a monarchy, so it belongs on `_republic`: the moment a
 # colony stops being governed from Madrid and starts governing itself, the arms of
 # its own viceroyalty go up in place of the bare Burgundian cross.
 ("NSP", "_republic"): "new_spain-independent-regency.png",
 ("VPE", "_republic"): "viceroyalty_of_peru_-_independent_regency.png",
 ("VNG", "_republic"): "viceroyalty_of_new_granada_-_independent_regency.png",
 ("RDP", "_republic"): "viceroyalty_of_rio_de_la_plata_-_independent_regency.png",
 ("CBA", "_republic"): "captaincy_general_of_cuba_-_independent_regency_flag.png",

 # --- supplied historical flags ------------------------------------------------------
 ("MAR", ""): "maratha_bhagwa_dhwaj.png",
 ("MAR", "_monarchy"): "maratha_bhagwa_dhwaj.png",
 ("MAR", "_republic"): "maratha_bhagwa_dhwaj.png",
 ("MAR", "_communist"): "maratha_bhagwa_dhwaj.png",
 ("MAR", "_fascist"): "maratha_bhagwa_dhwaj.png",
 ("RAG", ""): "ragusa_st_blaise.png",
 ("RAG", "_monarchy"): "ragusa_st_blaise.png",
 ("RAG", "_republic"): "ragusa_st_blaise.png",
 ("RAG", "_communist"): "ragusa_st_blaise.png",
 ("RAG", "_fascist"): "ragusa_st_blaise.png",
 ("LIG", ""): "liguria_genoese_arms.png",
 ("LIG", "_monarchy"): "liguria_genoese_arms.png",
 ("LIG", "_republic"): "liguria_genoese_arms.png",
 ("LIG", "_communist"): "liguria_genoese_arms.png",
 ("LIG", "_fascist"): "liguria_genoese_arms.png",
 ("RGA", ""): "algiers_regency.png",
 ("RGA", "_monarchy"): "algiers_regency.png",
 ("RGA", "_republic"): "algiers_regency.png",
 ("RGA", "_communist"): "algiers_regency.png",
 ("RGA", "_fascist"): "algiers_regency.png",
 ("KRM", ""): "tripoli_karamanli.png",
 ("KRM", "_monarchy"): "tripoli_karamanli.png",
 ("KRM", "_republic"): "tripoli_karamanli.png",
 ("KRM", "_communist"): "tripoli_karamanli.png",
 ("KRM", "_fascist"): "tripoli_karamanli.png",
 ("GEO", ""): "kartli_kakheti.png",
 ("GEO", "_monarchy"): "kartli_kakheti.png",
 ("GEO", "_republic"): "kartli_kakheti.png",
 ("GEO", "_communist"): "kartli_kakheti.png",
 ("GEO", "_fascist"): "kartli_kakheti.png",
 ("IME", ""): "imereti.png",
 ("IME", "_monarchy"): "imereti.png",
 ("IME", "_republic"): "imereti.png",
 ("IME", "_communist"): "imereti.png",
 ("IME", "_fascist"): "imereti.png",
 ("TYS", ""): "tay_son.png",
 ("TYS", "_monarchy"): "tay_son.png",
 ("TYS", "_republic"): "tay_son.png",
 ("TYS", "_communist"): "tay_son.png",
 ("TYS", "_fascist"): "tay_son.png",
 ("CRN", ""): "carnatic_sultanate.png",
 ("CRN", "_monarchy"): "carnatic_sultanate.png",
 ("CRN", "_republic"): "carnatic_sultanate.png",
 ("CRN", "_communist"): "carnatic_sultanate.png",
 ("CRN", "_fascist"): "carnatic_sultanate.png",
 ("PTR", "_republic"): "captaincy_general_of_puerto_rico_-_independent_regency_flag.png",

 # --- and the republics they became ------------------------------------------------
 # Belgrano's light blue and white, first raised on the Parana in February 1812.
 ("ARG", ""):          "Argentina_flag_1812.png",
 ("ARG", "_republic"): "Argentina_flag_1812.png",
 # The Patria Vieja flag of 1812, Chile's first, which O'Higgins flew until Rancagua.
 ("CHL", ""):          "chilean_independence_1812_flag.png",
 ("CHL", "_republic"): "chilean_independence_1812_flag.png",
 # Miranda's tricolour, carried from Haiti to Venezuela in 1806 and the ancestor of
 # the Colombian, Venezuelan and Ecuadorean flags alike -- so it belongs to the whole
 # Bolivarian succession, not to one of them.
 ("CLM", ""):          "Francisco_de_Miranda_s_tricolour.png",
 ("CLM", "_republic"): "Francisco_de_Miranda_s_tricolour.png",
 ("VNZ", ""):          "Francisco_de_Miranda_s_tricolour.png",
 ("VNZ", "_republic"): "Francisco_de_Miranda_s_tricolour.png",
 ("ECU", ""):          "Francisco_de_Miranda_s_tricolour.png",
 ("MEX", ""):          "mexico-three-guarantees-rebels.png",
 ("MEX", "_monarchy"): "mexico-first-mexican-empire.png",
 ("MEX", "_communist"):"mexico-hidalgo-revolt.png",
 ("MEX", "_fascist"):  "mexico-cristero-rebellion.png",
}
# The Nguyen dynasty, which the Gia Long proclamation creates. Three red bands on
# yellow -- the long tinh, the court's own flag.
OVERRIDE[("VNM", "")]           = "VNM.png"
OVERRIDE[("VNM", "_monarchy")]  = "VNM_monarchy.png"
OVERRIDE[("VNM", "_republic")]  = "VNM_republic.png"
OVERRIDE[("VNM", "_communist")] = "VNM_communist.png"
OVERRIDE[("VNM", "_fascist")]   = "VNM_fascist.png"

# The Jarai of the Central Highlands. A brass gong on forest green: the gong sets
# the Jarai apart from every neighbour that kept an army, because what they kept
# instead was a king who could not give orders.
OVERRIDE[("JRI", "")]           = "JRI.png"
OVERRIDE[("JRI", "_monarchy")]  = "JRI_monarchy.png"
OVERRIDE[("JRI", "_republic")]  = "JRI_republic.png"
OVERRIDE[("JRI", "_communist")] = "JRI_communist.png"
OVERRIDE[("JRI", "_fascist")]   = "JRI_fascist.png"

for (_tg, _g), _fn in OVERRIDE.items():
    if _tg not in FLAGS: FLAGS[_tg] = (lambda f=_fn: art(f))
for tag, fn in FLAGS.items():
    if tag in HPM_COPY: continue
    base = fn()
    for sfx in GOV:
        if (tag, sfx) in OVERRIDE:
            save_tga(art(OVERRIDE[(tag, sfx)]), f"{MOD}/gfx/flags/{tag}{sfx}.tga")
            log["flag files written"] += 1; log["supplied artwork used"] += 1
            continue
        # tags that exist only to receive supplied artwork keep HPM's own files for
        # any government type we were not given a flag for
        if tag in ("MEX", "ARG", "CHL", "CLM", "VNZ", "ECU"): continue
        # The Spanish colonies fly one flag under the Crown whatever the government
        # type is called, so the little corner markers that distinguish the drawn
        # flags must not be stamped on them -- a Cross of Burgundy with a gold corner
        # is not a Cross of Burgundy.
        if tag in SPANISH_COLONIES:
            save_tga(base, f"{MOD}/gfx/flags/{tag}{sfx}.tga")  # overrides handled above
            log["flag files written"] += 1
            continue
        im = base.copy()
        if sfx == "_communist":
            d = ImageDraw.Draw(im); d.rectangle([0, 0, 22, 16], fill=(150, 20, 24))
        elif sfx == "_fascist":
            d = ImageDraw.Draw(im); d.rectangle([0, 0, 22, 16], fill=(60, 60, 62))
        elif sfx == "_monarchy":
            d = ImageDraw.Draw(im); d.rectangle([W-24, 0, W, 16], fill=GOLD)
        elif sfx == "_republic":
            d = ImageDraw.Draw(im); d.rectangle([W-24, H-16, W, H], fill=(235, 235, 232))
        save_tga(im, f"{MOD}/gfx/flags/{tag}{sfx}.tga")
        log["flag files written"] += 1
    log["flags drawn"] += 1

print(f"  flags drawn                       {log['flags drawn']}")
print(f"  files written                     {log['flag files written']}")
