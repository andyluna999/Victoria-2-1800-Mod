"""Africa, Asia, the Middle East and Oceania in 1800.

Same method as Europe: national totals anchored where estimates exist, scaled inside
each polity's own territory so the internal distribution survives, then the occupational
structure rebuilt for 1800.

The growth rates differ sharply and a single factor would be wrong everywhere. China
went from roughly 300 million to 400 million over the period -- the Qing demographic
surge is the largest single population movement of the age. Most of Africa barely moved.
Japan under the Tokugawa was almost flat.
"""
import json, re, glob, os, collections

MOD = "/home/claude/build/HPM"; W = "/home/claude/work"
L = json.load(open(f"{W}/world_live.json"))
SCALE = 0.25
CONTS = {"asia", "africa", "oceania", "australia_new_zealand", "polynesia"}
REST = {int(k): v for k, v in L["prov"].items() if v["ct"] in CONTS}

# real population in 1800 where a usable estimate exists
T1800 = {
 "QNG": 330_000_000,   # estimates for 1800 run 295-350M; the Qing surge is already well advanced
 "JAP":  30_000_000,   # Tokugawa Japan was close to flat for a century
 "KOR":  13_000_000,   # census-based estimates run 7M, corrected estimates far higher
 "PER":   6_000_000,   # Qajar Persia
 "SIA":   3_000_000,
 "BUR":   4_000_000,   # Konbaung at its height
 "DAI":   7_000_000,   # Vietnam, unified under Gia Long in 1802
 "MOR":   3_000_000,
 "ETH":   4_000_000,   # the Zemene Mesafint
 "OMA":   1_000_000,
 "AFG":   5_000_000,   # the Durrani realm, fragmenting
 "NEP":   2_000_000,
 "TKG":   1_500_000,
 "MGL":   1_000_000,
}
# otherwise by continent, from the standard series
DEFAULT = {"asia": 0.89, "africa": 0.92, "oceania": 0.90,
           "australia_new_zealand": 0.92, "polynesia": 0.95}

owner = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid not in REST: continue
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                    open(f, encoding="cp1252", errors="replace").read())[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    owner[pid] = m.group(1) if m else "-"

files = {f: open(f, encoding="cp1252", errors="replace").read()
         for f in glob.glob(f"{MOD}/history/pops/*/*.txt")}

def blocks(s):
    for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
        pid = int(pm.group(1)); i = pm.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        yield pm.start(), pm.end(), i, pid

cur = collections.Counter()
for s in files.values():
    for a, bo, b, pid in blocks(s):
        if pid in REST:
            cur[owner[pid]] += sum(int(x) for x in re.findall(r"size\s*=\s*(\d+)", s[bo:b-1]))

fac = {}
for tag, total in cur.items():
    if not total: continue
    if tag in T1800:
        fac[tag] = T1800[tag] * SCALE / total
    else:
        conts = collections.Counter(REST[p]["ct"] for p in owner if owner[p] == tag)
        fac[tag] = DEFAULT[conts.most_common(1)[0][0]] if conts else 0.88

before = after = 0
for f, s in files.items():
    out, pos, touched = [], 0, False
    for a, bo, b, pid in blocks(s):
        if pid not in REST: continue
        k = fac.get(owner[pid], 0.88)
        def shrink(m):
            global before, after
            v = int(m.group(1)); n = max(1, int(round(v * k)))
            before += v; after += n
            return f"size = {n}"
        out.append(s[pos:bo]); out.append(re.sub(r"size\s*=\s*(\d+)", shrink, s[bo:b-1]))
        pos = b-1; touched = True
    if touched:
        out.append(s[pos:])
        open(f, "w", encoding="cp1252", errors="replace", newline="\n").write("".join(out))

print(f"  rest of the world {before:,} -> {after:,}")
print(f"    = {int(before/SCALE):,} -> {int(after/SCALE):,} real")
for tag in sorted(fac, key=lambda t: -cur[t])[:8]:
    if cur[tag] < 200000: continue
    print(f"    {tag:<5}{int(cur[tag]/SCALE):>13,} -> {int(cur[tag]*fac[tag]/SCALE):>13,}  x{fac[tag]:.2f}"
          + ("" if tag in T1800 else "   (continental default)"))
