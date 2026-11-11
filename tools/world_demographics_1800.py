"""Demographic corrections found by the audit.

**Occitania.** The largest single error left in the world. Every province from Bordeaux
to Nice was filed 100% `french`, and the `occitan` culture existed holding nobody at
all -- the same shape as Scotland. The Abbe Gregoire's survey of 1794 found that of
28 million French subjects only about 3 million spoke French well; the langue d'oc was
the mother tongue of the whole Midi.

**Galicia, Sardinia, Corsica.** Three more peoples filed under a neighbour's name:
Galicia as Castilian, Sardinia as south Italian, Corsica as north Italian. Sardinia is
the sharpest case, because the Kingdom of Sardinia's primary culture pointed at a
culture that held nobody on the island.

**Hawaii.** `hawaiian` existed holding nobody while the islands were filed as generic
Polynesian, in the year Kamehameha was finishing their unification.

**Siberia.** Twenty-three provinces came out 90-100% Russian. In 1800 Siberia held
roughly 575,000 Russians against some 500,000 indigenous people -- Siberian Tatars,
Khanty and Mansi, Buryats, Yakuts, Evenks. The Russian share here is the 1890s, after
the Trans-Siberian.
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
SCALE = 0.25
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# ---------------------------------------------------------------- new cultures
NEW = {
 "galician":  ("french", [72, 150, 112],
   ["Afonso","Breogan","Xoan","Manoel","Pedro","Rosalia","Anton","Xurxo","Lois"],
   ["Castelao","Pondal","Curros","Fernandez","Pereira","Carballo","Quiroga","Losada"]),
 "sardinian": ("italian", [176, 140, 72],
   ["Antoni","Bachis","Efisio","Gavinu","Juanne","Predu","Salvadore","Tziu"],
   ["Angioy","Carboni","Deledda","Manca","Pinna","Satta","Serra","Zedda"]),
 "corsican":  ("italian", [138, 110, 150],
   ["Pasquale","Sampieru","Ghjuvanni","Matteu","Carlu","Anton","Natale"],
   ["Paoli","Gaffori","Ornano","Colonna","Casabianca","Pozzo di Borgo","Peretti"]),
}
src = rd(f"{MOD}/common/cultures.txt")
def group_anchor(grp, fallback):
    m = re.search(rf"\n[ \t]+{fallback}[ \t]*=[ \t]*\{{", src)
    return m
added = ""
for c, (grp, col, first, last) in NEW.items():
    if re.search(rf"\n[ \t]+{c}[ \t]*=[ \t]*\{{", src): continue
    added += (f"        {c} = {{\n            color = {{ {col[0]} {col[1]} {col[2]} }}\n"
              f"            first_names = {{ {' '.join(first)} }}\n"
              f"            last_names = {{ {' '.join(last)} }}\n        }}\n")
    log["cultures added"] += 1
if added:
    a = re.search(r"\n[ \t]+french[ \t]*=[ \t]*\{", src)
    src = src[:a.start()+1] + added + src[a.start()+1:]
    wr(f"{MOD}/common/cultures.txt", src)

# ------------------------------------------------- how much of each province changes
# province: {culture it comes from: {culture it becomes: share of that culture}}
SHIFT = {}
def shift(pid, frm, to, share): SHIFT.setdefault(pid, []).append((frm, to, share))

# --- Occitania. Shares are of the province's French-filed population.
CORE_OC = [455, 456, 463, 457, 462, 450, 449, 461, 447, 445, 459]   # the heart of the Midi
HIGH_OC = [458, 448, 453, 469, 467, 470, 471, 468]                   # Gascony to Provence
for p in CORE_OC: shift(p, "french", "occitan", 0.92)
for p in HIGH_OC: shift(p, "french", "occitan", 0.80)
shift(460, "french", "occitan", 0.85)        # Bearn, beside the Basque country
shift(454, "french", "occitan", 0.55)        # Dauphine, the Franco-Provencal march
shift(452, "french", "occitan", 0.55)        # Forez
shift(444, "french", "occitan", 0.45)        # Angoumois, on the oc-oil line
shift(451, "french", "occitan", 0.30)        # Lyonnais: Franco-Provencal
shift(431, "french", "occitan", 0.30)        # Maconnais
shift(472, "french", "occitan", 0.45)        # the Nicois hinterland

# --- Corsica, Sardinia, Galicia
shift(473, "north_italian", "corsican", 0.95)
shift(765, "south_italian", "sardinian", 0.97)
shift(766, "south_italian", "sardinian", 0.95)
for p in (474, 476): shift(p, "spanish", "galician", 0.92)   # La Coruna, Vigo
shift(475, "spanish", "galician", 0.25)                       # Asturias, the Galician edge

# --- Hawaii, in the year Kamehameha finishes the conquest
shift(658, "polynesian", "hawaiian", 0.98)

# --- Siberia and the Urals. Indigenous peoples, not a Russian monoculture.
# Khanty and Mansi on the Ob, Siberian Tatars through the forest-steppe, Buryats
# around Baikal, Yakuts on the Lena, Evenks across the taiga.
SIB = {
 1058: [("russian","tatar",0.38),("russian","ugrian",0.06)],      # Ekaterinburg: Bashkir country
 1059: [("russian","tatar",0.48)], 1060: [("russian","tatar",0.55)],
 1061: [("russian","tatar",0.30),("russian","ugrian",0.10)],
 1063: [("russian","siberian",0.38),("russian","tatar",0.14)],
 1064: [("russian","tatar",0.34),("russian","siberian",0.16)],
 1066: [("russian","ugrian",0.30),("russian","tatar",0.12)],
 1067: [("russian","siberian",0.42),("russian","tatar",0.12)],
 1070: [("russian","siberian",0.55)], 1076: [("russian","siberian",0.60)],
 1075: [("russian","mongol",0.42)],                                # Irkutsk: Buryat
 1077: [("russian","siberian",0.42),("russian","tatar",0.14)],
 1079: [("russian","mongol",0.35),("russian","siberian",0.15)],
 2614: [("russian","ugrian",0.45),("russian","siberian",0.15)],
 2658: [("russian","siberian",0.60),("russian","yakut",0.15)],
 2670: [("russian","yakut",0.55)], 2671: [("russian","yakut",0.50)],
 2683: [("russian","ugrian",0.50),("russian","siberian",0.20)],
 2685: [("russian","ugrian",0.65),("russian","siberian",0.15)],
 2686: [("russian","tatar",0.35),("russian","ugrian",0.15)],
 2691: [("russian","siberian",0.35),("russian","tatar",0.10)],
 2698: [("russian","tatar",0.30),("russian","siberian",0.12)],
 2701: [("russian","siberian",0.65)],
}
for pid, lst in SIB.items():
    for frm, to, sh in lst: shift(pid, frm, to, sh)

REL = {"occitan":"catholic","galician":"catholic","sardinian":"catholic",
       "corsican":"catholic","hawaiian":"animist","tatar":"sunni","ugrian":"animist",
       "siberian":"animist","yakut":"animist","mongol":"gelugpa"}

# ------------------------------------------------- rewrite, preserving province totals
files = {f: rd(f) for f in glob.glob(f"{MOD}/history/pops/*/*.txt")}
POPRE = re.compile(r"\t([a-z_]+) = \{\n\t\tculture = ([a-z_0-9]+)\n\t\treligion = ([a-z_0-9]+)\n\t\tsize = (\d+)\n\t\}\n")
moved = collections.Counter()
for f, s in files.items():
    blocks = []
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        if pid in SHIFT: blocks.append((pm.end(), i-1, pid))
    if not blocks: continue
    out, pos = [], 0
    for a, b, pid in blocks:
        body = s[a:b]; rows = POPRE.findall(body)
        if not rows: continue
        rules = SHIFT[pid]
        new = []
        for ty, cu, rl, sz in rows:
            sz = int(sz); taken = 0
            for frm, to, share in rules:
                if cu != frm: continue
                n = int(round(sz * share))
                if n >= 5:
                    new.append((ty, to, REL.get(to, rl), n)); taken += n; moved[to] += n
            rest = sz - taken
            if rest >= 5: new.append((ty, cu, rl, rest))
            elif rest > 0 and new: new[-1] = (*new[-1][:3], new[-1][3] + rest)
        txt = "".join(f"\t{ty} = {{\n\t\tculture = {cu}\n\t\treligion = {rl}\n\t\tsize = {n}\n\t}}\n"
                      for ty, cu, rl, n in new)
        out.append(s[pos:a]); out.append(txt); pos = b
    out.append(s[pos:])
    wr(f, "".join(out))

# Two countries whose primary culture names a people who barely live there. Xinjiang
# is Uighur and the northwest marches are Tibetan; filing both under the north Chinese
# is the Qing administrative fiction, not the population.
for tag, prim in (("XIN", "uighur"), ("XBI", "tibetan")):
    for f in glob.glob(f"{MOD}/history/countries/{tag} - *.txt"):
        t = rd(f)
        t = re.sub(r"^\s*primary_culture\s*=.*$", f"primary_culture = {prim}", t,
                   count=1, flags=re.M)
        # the new primary must not also sit in the accepted list
        t = re.sub(rf"^\s*culture\s*=\s*{prim}\s*\n", "", t, flags=re.M)
        if not re.search(r"^\s*culture\s*=\s*beifaren\s*$", t, re.M):
            t = re.sub(r"(^primary_culture\s*=.*\n)", r"\1culture = beifaren\n", t,
                       count=1, flags=re.M)
        wr(f, t); log["primary cultures corrected"] += 1

# Sardinia's kingdom should name a culture that lives on the island
for f in glob.glob(f"{MOD}/history/countries/SAR - *.txt"):
    t = rd(f)
    t = re.sub(r"^\s*primary_culture\s*=.*$", "primary_culture = sardinian", t, count=1, flags=re.M)
    if not re.search(r"^\s*culture\s*=\s*north_italian\s*$", t, re.M):
        t = re.sub(r"(^primary_culture\s*=.*\n)", r"\1culture = north_italian\n", t, count=1, flags=re.M)
    wr(f, t); log["Sardinia's primary culture set"] = 1
# France and Spain accept their own regional peoples
for tag, cults in (("FRA", ["occitan", "corsican"]), ("SPA", ["galician"]),
                   ("HAW", ["hawaiian"])):
    for f in glob.glob(f"{MOD}/history/countries/{tag} - *.txt"):
        t = rd(f)
        head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", t)[0]
        want = [c for c in cults if not re.search(rf"^\s*culture\s*=\s*{c}\s*$", head, re.M)]
        if tag == "HAW":
            t = re.sub(r"^\s*primary_culture\s*=.*$", "primary_culture = hawaiian", t, count=1, flags=re.M)
            want = []
        if want:
            t = re.sub(r"(^\s*primary_culture\s*=.*\n)", r"\1" + "".join(f"culture = {c}\n" for c in want),
                       t, count=1, flags=re.M)
        wr(f, t)
log["accepted cultures updated"] = 4

print(f"  provinces adjusted                {len(SHIFT)}")
for c, v in moved.most_common():
    print(f"    {c:<12}{int(v/SCALE):>11,} real")
for k, v in log.items(): print(f"  {k:<34}{v}")
