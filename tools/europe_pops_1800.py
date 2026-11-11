"""Europe's population on 1 January 1800.

HPM's figures are 1836's, and Europe grew very unevenly over those 36 years: Britain
and Ireland roughly doubled, France grew about a sixth, the Habsburg lands a quarter.
Applying one continental factor would get the total right and every country wrong.

Cultures are not touched -- HPM's 64 European cultures are correct for 1800. What
changes is how many people each polity holds, scaled within its own territory so the
internal distribution HPM already has is preserved.
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
EU = {int(k): v for k, v in L["prov"].items() if v["ct"] == "europe"}

# real population in 1800, by the polity that holds the land on the start date.
# Census years where they exist: Britain and Ireland 1801, France 1801, Sweden 1800,
# Spain 1797, Denmark 1801. The rest are standard historical-demography estimates.
T1800 = {
 "FRA": 34_300_000,   # France 1801 census 27.35M, plus Belgium, the left bank, Piedmont, Savoy
 "RUS": 34_000_000,   # European Russia including Lithuania, Belarus, Ukraine, the Baltic
 "AUS": 23_500_000,   # the Habsburg monarchy with Lombardy, Venetia and Galicia
 "ENG": 10_500_000,   # 1801 census: England and Wales 8.9M, Scotland 1.6M
 "SPA": 10_600_000,   # 1797 census
 "PRU":  9_500_000,   # Prussia with South Prussia and New East Prussia
 "TUR":  8_500_000,   # the Ottoman Balkans and Thrace
 "SIC":  5_600_000,   # Naples 4.0M, Sicily 1.6M
 "IRE":  5_000_000,
 "SWE":  3_300_000,   # Sweden 2.35M, Finland 0.83M, Pomerania 0.11M
 "POR":  3_000_000,
 "DEN":  2_450_000,   # Denmark, Norway, Schleswig-Holstein, Iceland
 "PAP":  2_300_000,
 "NET":  2_100_000,   # the Batavian Republic
 "SAX":  2_000_000,
 "BAV":  2_400_000,   # Bavaria with Franconia, which HPM files under BAV
 "SWI":  1_700_000,   # the Helvetic Republic
 "TUS":  1_100_000,
 "WAL":  1_000_000,
 "HAN":    900_000,
 "WUR":    650_000,
 "MOL":    600_000,
 "BAD":    600_000,
 "LIG":    500_000,
 "SAR":    500_000,   # the island alone
 "HEK":    450_000,
 "MEC":    400_000,
 "MOD":    350_000,
 "PAR":    350_000,
 "HES":    300_000,
 "ION":    200_000,
 "OLD":    150_000,
 "LUC":    120_000,
 "MON":    100_000,
 "NEH":     50_000,
}
# everything unlisted -- the smaller German states, the Caucasus, the free cities --
# takes the continental ratio: Europe went from roughly 190M to 230M over the period
DEFAULT = 0.88   # 190/230 left the continent light once the named targets were summed

# Read current totals out of the mod's own pop files, not world_live.json. That file
# is regenerated after the build, so on a second run it would already hold the rescaled
# figures and the shrink would compound.
prov_owner_pre = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid not in EU: continue
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                    open(f, encoding="cp1252", errors="replace").read())[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    prov_owner_pre[pid] = m.group(1) if m else "-"
cur = collections.Counter()
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s_ = open(f, encoding="cp1252", errors="replace").read()
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s_, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(s_) and d:
            if s_[i] == "{": d += 1
            elif s_[i] == "}": d -= 1
            i += 1
        if pid in EU:
            cur[prov_owner_pre.get(pid, "-")] += sum(int(x) for x in re.findall(r"size\s*=\s*(\d+)", s_[pm.end():i-1]))
factor = {}
for tag, total in cur.items():
    if not total: continue
    tgt = T1800.get(tag)
    factor[tag] = (tgt * SCALE / total) if tgt else DEFAULT

prov_owner = prov_owner_pre
files = {}
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    files[f] = open(f, encoding="cp1252", errors="replace").read()

written = 0; before = after = 0
for f, s in files.items():
    out = []; last = 0; touched = False
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        if pid not in EU:
            continue
        fac = factor.get(prov_owner[pid], DEFAULT)
        block = s[pm.start():i]
        def shrink(m):
            global before, after
            v = int(m.group(1)); n = max(1, int(round(v * fac)))
            before += v; after += n
            return f"size = {n}"
        nb = re.sub(r"size\s*=\s*(\d+)", shrink, block)
        out.append((pm.start(), i, nb)); touched = True
    if touched:
        res = []; pos = 0
        for a, b, nb in out:
            res.append(s[pos:a]); res.append(nb); pos = b
        res.append(s[pos:])
        open(f, "w", encoding="cp1252", errors="replace", newline="\n").write("".join(res))
        written += 1

print(f"  pop files rewritten               {written}")
print(f"  Europe {before:,} -> {after:,}  ({int(before/SCALE):,} -> {int(after/SCALE):,} real)")
print("\n  the largest changes:")
for tag in sorted(factor, key=lambda t: -cur[t])[:12]:
    if cur[tag] < 50000: continue
    print(f"    {tag:<5}{int(cur[tag]/SCALE):>12,} -> {int(cur[tag]*factor[tag]/SCALE):>12,} real"
          f"   x{factor[tag]:.2f}" + ("" if tag in T1800 else "   (continental default)"))
