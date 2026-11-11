"""A sweep aimed at what we changed, rather than at HPM in general."""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, json, csv, collections

SRC = _SRC
MOD = os.environ.get("SWEEP_TARGET", _BUILD)
BF = f"{_TOOLS}/sweep_baseline.json"
BASE_FIND = json.load(open(BF)) if (os.path.exists(BF) and not os.environ.get("SWEEP_RECORD")) else {}
REC = {}
def rd(p): return re.sub(r"#.*", "", open(p, encoding="cp1252", errors="replace").read())
def raw(p): return open(p, encoding="cp1252", errors="replace").read()
bad = 0
def chk(name, ok, detail=""):
    """Fail only on what we introduced. HPM has findings of its own, recorded once."""
    global bad
    d = str(detail); REC[name] = d
    if ok:
        print("  ok    " + name + (f"  -> {d}" if d else "")); return
    b = BASE_FIND.get(name)
    try:
        import ast
        cur, bl = ast.literal_eval(d), ast.literal_eval(b) if b else None
        if isinstance(cur, list) and isinstance(bl, list) and set(cur) <= set(bl):
            print("  known " + name + "  -> pre-existing in HPM: " + d); return
    except Exception:
        pass
    if b == d:
        print("  known " + name + "  -> pre-existing in HPM: " + d); return
    print("  BUG   " + name + (f"  -> {d}" if d else "")); bad += 1

reg = rd(f"{MOD}/common/countries.txt")
TAGS = set(re.findall(r"^\s*([A-Z]{3})\s*=", reg, re.M))
BASE = set(re.findall(r"^\s*([A-Z]{3})\s*=", rd(f"{SRC}/common/countries.txt"), re.M))
NEW = sorted(TAGS - BASE)
print(f"sweeping {len(TAGS)} tags, {len(NEW)} of them ours\n")

# ---- cultures and religions in scope
src = rd(f"{MOD}/common/cultures.txt"); CULT = set(); d = 0
for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}", src):
    t = m.group(0)
    if t == "}": d -= 1
    elif t == "{": d += 1
    else:
        if d == 1 and m.group(1) not in ("color","leader","unit","union","is_overseas","primary"):
            CULT.add(m.group(1))
        d += 1
RELS = set(re.findall(r"^\s{1,8}([a-z_0-9]+)\s*=\s*\{", rd(f"{MOD}/common/religion.txt"), re.M))
MODS = set(re.findall(r"^([a-z_0-9]+)\s*=\s*\{", rd(f"{MOD}/common/event_modifiers.txt"), re.M))
DEFN = {int(r[0]) for r in csv.reader(open(f"{MOD}/map/definition.csv", encoding="latin-1"),
        delimiter=";") if r and r[0].isdigit()}

# ---- province state
owner, controller, cores, provfile = {}, {}, {}, {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1)); provfile[pid] = f
    h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    o = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", h, re.M)
    c = re.search(r"^\s*controller\s*=\s*([A-Z]{3})", h, re.M)
    owner[pid] = o.group(1) if o else None
    controller[pid] = c.group(1) if c else None
    cores[pid] = re.findall(r"^\s*add_core\s*=\s*([A-Z]{3})", h, re.M)

chk("every owner is a registered tag",
    not [p for p, t in owner.items() if t and t not in TAGS],
    sorted({t for t in owner.values() if t and t not in TAGS})[:5])
chk("every controller is a registered tag",
    not [p for p, t in controller.items() if t and t not in TAGS],
    sorted({t for t in controller.values() if t and t not in TAGS})[:5])
chk("every core is a registered tag",
    not [t for cs in cores.values() for t in cs if t not in TAGS],
    sorted({t for cs in cores.values() for t in cs if t not in TAGS})[:5])
chk("no province is owned without a controller",
    not [p for p in owner if owner[p] and not controller[p]],
    [f"{p}:{owner[p]}" for p in owner if owner[p] and not controller[p]][:5])
chk("no province is controlled without an owner",
    not [p for p in owner if controller[p] and not owner[p]],
    [p for p in owner if controller[p] and not owner[p]][:5])
chk("no duplicate cores on one province",
    not [p for p, cs in cores.items() if len(cs) != len(set(cs))],
    [p for p, cs in cores.items() if len(cs) != len(set(cs))][:5])

# ---- country files
caps, prim, parties = {}, {}, {}
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    tag = b.split(" - ")[0].strip()
    h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*capital\s*=\s*(\d+)", h, re.M); caps[tag] = int(m.group(1)) if m else None
    m = re.search(r"^\s*primary_culture\s*=\s*([a-z_0-9]+)", h, re.M); prim[tag] = m.group(1) if m else None
    m = re.search(r"^\s*ruling_party\s*=\s*(\S+)", h, re.M); parties[tag] = m.group(1) if m else None

held = collections.defaultdict(list)
for p, t in owner.items():
    if t: held[t].append(p)
chk("every country with land has a capital it owns",
    not [t for t in held if caps.get(t) and caps[t] not in held[t]],
    [f"{t}:{caps[t]}" for t in held if caps.get(t) and caps[t] not in held[t]][:6])
chk("every capital is a real province",
    not [t for t, c in caps.items() if c and c not in DEFN],
    [f"{t}:{c}" for t, c in caps.items() if c and c not in DEFN][:5])
chk("our tags all have a primary culture that exists",
    not [t for t in NEW if not prim.get(t) or prim[t] not in CULT],
    [f"{t}:{prim.get(t)}" for t in NEW if not prim.get(t) or prim[t] not in CULT][:6])
chk("our tags all have a flag",
    not [t for t in NEW if not os.path.exists(f"{MOD}/gfx/flags/{t}.tga")],
    [t for t in NEW if not os.path.exists(f"{MOD}/gfx/flags/{t}.tga")])

# ruling party must be defined in that country's own file
badp = []
for tag, want in parties.items():
    m = re.search(rf'^\s*{tag}\s*=\s*"?([^"\n]+?)"?\s*$', reg, re.M)
    if not (m and want): continue
    cf = os.path.join(MOD, "common", m.group(1).strip())
    if os.path.exists(cf) and f'"{want}"' not in raw(cf): badp.append(f"{tag}:{want}")
chk("every ruling party is defined in its own country file", not badp, badp[:6])

# ---- diplomacy
dip = []
for f in glob.glob(f"{MOD}/history/diplomacy/1800_*.txt"):
    for m in re.finditer(r"(vassal|union|substate)\s*=\s*\{[^}]*?first\s*=\s*([A-Z]{3})[^}]*?second\s*=\s*([A-Z]{3})", rd(f), re.S):
        dip.append(m.groups())
chk("every dependency names registered tags",
    not [d for d in dip if d[1] not in TAGS or d[2] not in TAGS],
    [d for d in dip if d[1] not in TAGS or d[2] not in TAGS][:5])
seconds = collections.Counter(d[2] for d in dip)
chk("no country has two overlords", not [t for t, n in seconds.items() if n > 1],
    [t for t, n in seconds.items() if n > 1])
chk("no country is its own overlord", not [d for d in dip if d[1] == d[2]],
    [d for d in dip if d[1] == d[2]])
chk("every dependency actually holds land",
    not [d for d in dip if not held.get(d[2])],
    [f"{d[1]}->{d[2]}" for d in dip if not held.get(d[2])])
chk("every overlord actually holds land",
    not [d for d in dip if not held.get(d[1])],
    [f"{d[1]}->{d[2]}" for d in dip if not held.get(d[1])])

# ---- dependencies across the whole timeline, not just the start date.
# A relationship dated 1836 is invisible at an 1800 start and then springs into
# existence mid-game; two that overlap give a country two overlords at once.
allrel = []
for f in glob.glob(f"{MOD}/history/diplomacy/*.txt"):
    for m in re.finditer(r"(vassal|union|substate)\s*=\s*\{([^}]*)\}", rd(f), re.S):
        b = m.group(2)
        g = lambda n: (re.search(rf"{n}\s*=\s*(\S+)", b) or [None, None])[1]
        def ymd(x, d):
            try: return tuple(int(v) for v in (x or d).split("."))
            except Exception: return tuple(int(v) for v in d.split("."))
        allrel.append((m.group(1), g("first"), g("second"),
                       ymd(g("start_date"), "1.1.1"), ymd(g("end_date"), "9999.1.1")))
clash = []
bysec = collections.defaultdict(list)
for k, a, b_, s_, e_ in allrel: bysec[b_].append((a, s_, e_, k))
for sec, rs in bysec.items():
    for i in range(len(rs)):
        for j in range(i + 1, len(rs)):
            if rs[i][0] == rs[j][0]: continue
            if rs[i][1] < rs[j][2] and rs[j][1] < rs[i][2]:
                clash.append(f"{sec}: {rs[i][0]} and {rs[j][0]}")
chk("no country ever has two overlords at once", not clash, sorted(set(clash))[:6])
chk("every dependency names a tag that exists",
    not [r for r in allrel if r[1] not in TAGS or r[2] not in TAGS],
    [f"{r[1]}->{r[2]}" for r in allrel if r[1] not in TAGS or r[2] not in TAGS][:6])
active = [r for r in allrel if r[3] <= (1800, 1, 1) < r[4]]
chk("every dependency active at the start holds land",
    not [r for r in active if not held.get(r[2])],
    [f"{r[1]}->{r[2]}" for r in active if not held.get(r[2])][:6])
chk("every overlord active at the start holds land",
    not [r for r in active if not held.get(r[1])],
    [f"{r[1]}->{r[2]}" for r in active if not held.get(r[1])][:6])

# ---- the build must match what the export pass said it would do.
# A script that reads current state from world_live.json rather than from the file it
# is editing will silently skip its own writes on a rebuild, because world_live.json is
# regenerated after the build. That is how Britain kept 37 Australian provinces.
INTENT = f"{_WORK}/export_intent.json"
# apply_export2 now runs immediately after the export is compiled and verifies its own
# writes before the historical passes that follow it. Those passes deliberately
# override it -- Spain's claim on Fernando Po is not in the export -- so this checks
# that the file was produced, not that every value survived to the end of the build.
chk("the export pass ran and verified its own writes", os.path.exists(INTENT),
    f"{len(json.load(open(INTENT))) if os.path.exists(INTENT) else 0} provinces recorded")

# ---- flags
# Victoria II needs a flag per government type. A missing one shows as a blank square
# in the diplomacy screen rather than failing loudly.
GOVS = ("", "_communist", "_fascist", "_monarchy", "_republic")
# Only the tags this project added. HPM ships flags only where it overrides vanilla,
# so a missing file for an HPM tag means Victoria II supplies it, not that it is broken.
missing_flag, badsize = [], []
for tg in sorted(NEW):
    for g in GOVS:
        fp = f"{MOD}/gfx/flags/{tg}{g}.tga"
        if not os.path.exists(fp):
            missing_flag.append(f"{tg}{g}")
            continue
        with open(fp, "rb") as fh: hd = fh.read(18)
        if len(hd) < 18: badsize.append(f"{tg}{g} truncated"); continue
        w_ = hd[12] + hd[13]*256; h_ = hd[14] + hd[15]*256
        if (w_, h_) != (93, 64): badsize.append(f"{tg}{g} {w_}x{h_}")
chk("every tag we added has all five flags", not missing_flag, missing_flag[:8])
chk("every flag we drew is 93x64", not badsize, badsize[:6])

# ---- effects must run where they can take effect
# Spain retroceded Louisiana on 25 October 1800 and the map never changed, because the
# event ran `secede_province` on provinces Spain did not own -- they belong to New
# Spain. A province effect issued from a country that does not own the province does
# nothing, silently. Every secede_province we write must be issued by the owner.
powner = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    powner[pid] = m.group(1) if m else ""
wrongscope = []
for f in glob.glob(f"{MOD}/events/1800_*.txt"):
    t = re.sub(r"#.*", "", rd(f))
    for em in re.finditer(r"^country_event\s*=\s*\{", t, re.M):
        i = em.end(); d = 1
        while i < len(t) and d:
            if t[i] == "{": d += 1
            elif t[i] == "}": d -= 1
            i += 1
        b = t[em.end():i-1]
        tg = re.search(r"\btag\s*=\s*([A-Z]{3})", b)
        if not tg: continue          # is_triggered_only: scope comes from the caller
        # `secede_province = THIS` is the acquire idiom: the scoped country takes the
        # province whoever holds it, which is fine. `secede_province = SOMEONE_ELSE`
        # is giving away land, and only the owner can do that.
        for sm in re.finditer(r"(\d+)\s*=\s*\{\s*secede_province\s*=\s*(\w+)", b):
            pid, dest = int(sm.group(1)), sm.group(2)
            if dest == "THIS": continue
            if powner.get(pid) and powner[pid] != tg.group(1):
                wrongscope.append(f"{os.path.basename(f)} {tg.group(1)} gives away {pid} "
                                  f"(owned by {powner[pid]})")
chk("a province is only seceded by the country that owns it", not wrongscope,
    wrongscope[:5])

# ---- the staleness trap
# Three separate bugs came from a build script reading ownership out of
# work/world_live.json, which is written AFTER a build and so describes the previous
# run. Europe was nearly halved twice, Britain kept thirty-seven Australian provinces,
# and Norfolk Island changed hands on alternate builds. A script that decides anything
# from current state must read the mod; tools/livestate.py does that.
OWN_KEYS = ('["o"]', "['o']", '["c"]', "['c']", '["cr"]', "['cr']")
offenders = []
for _f in sorted(glob.glob(f"{_TOOLS}/*.py")):
    _nm = os.path.basename(_f)
    # read-only tools are exempt: they report, they never write into the mod
    if _nm in ("build_live_data.py", "demographic_audit.py", "sweep.py",
               "livestate.py", "build_sa_1800.py", "event_audit.py",
               "lint.py", "deep_audit.py"): continue
    _src = open(_f).read()
    if "world_live.json" not in _src: continue
    if not any(k in _src for k in OWN_KEYS): continue
    if "/history/" not in _src: continue
    offenders.append(_nm)
chk("no build script reads ownership from world_live.json", not offenders,
    ", ".join(offenders))

# ---- 1836 content that survives in history files.
# Restored after an index-range splice deleted this whole section. The sweep went on
# reporting NO NEW BUGS for several builds because the checks were not running at all,
# which is a worse failure than any single bug they look for.
fac = 0
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    fac += len(re.findall(r"state_building\s*=\s*\{", rd(f)))
chk("no factories anywhere in 1800", fac == 0, f"{fac} state_building blocks")

FLOOR_1800 = {"wage_reform": "no_minimum_wage", "work_hours": "no_work_hour_limit",
              "safety_regulations": "no_safety", "health_care": "no_health_care",
              "unemployment_subsidies": "no_subsidies", "pensions": "no_pensions",
              "trade_unions": "no_trade_unions"}
above = []
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    for k, floor in FLOOR_1800.items():
        m = re.search(rf"^\s*{k}\s*=\s*(\w+)", head, re.M)
        if m and m.group(1) != floor:
            above.append(f"{os.path.basename(f)[:3]} {k}={m.group(1)}")
chk("no social legislation ahead of 1800", not above, sorted(set(above))[:6])

tre = f"{MOD}/events/1800_Treasuries.txt"
if os.path.exists(tre):
    t = rd(tre); bad = []
    for m in re.finditer(r"country_event\s*=\s*\{\s*id\s*=\s*(\d+)(.*?)\n\}", t, re.S):
        eid, body = int(m.group(1)), m.group(2)
        if not (9100001 <= eid <= 9100024): continue
        if re.search(r"\n\s+[A-Z]{3} = \{ treasury", body): continue
        if re.search(r"\btreasury\s*=\s*\d", body) and "money = 1000000" not in body:
            bad.append(str(eid))
    chk("every opening treasury is drained before it is set", not bad, ", ".join(bad[:5]))

# ---- the order of battle
# Countries our own content brings into being later are armed in advance: Victoria II
# reads every order of battle at the start of the game and hands one over when the
# country appears. Their units sit on ground they do not hold yet, which is the point.
SPAWNS_LATER = {"MEX", "CLM", "ARG", "CHL", "PEU", "ECU", "BOL", "URU",
                "PRG", "CUB", "PRI", "BRZ", "TEX", "CAL", "HAI", "ALD", "TUN", "TRI"}
stranded, armyless = [], []
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    tg = os.path.basename(f)[:3]
    if tg in SPAWNS_LATER: continue
    t = rd(f)
    # A garrison may stand on ground its country holds without owning: Spain
    # administers Santo Domingo, which France has owned on paper since Basel in 1795.
    # Recruitment is different -- a regiment's home must be owned, or it cannot
    # reinforce from a population that is not yours.
    for m in re.finditer(r"\blocation\s*=\s*(\d+)", t):
        pid = int(m.group(1))
        o, c = owner.get(pid), controller.get(pid) or owner.get(pid)
        if o and tg not in (o, c):
            stranded.append(f"{tg} stands on {pid}, held by {c}")
    for m in re.finditer(r"\bhome\s*=\s*(\d+)", t):
        o = owner.get(int(m.group(1)))
        if o and o != tg: stranded.append(f"{tg} recruits from {m.group(1)}, {o}'s")
chk("every unit stands on its own country's soil", not stranded,
    sorted(set(stranded))[:4])
for tg in sorted(held):
    f = f"{MOD}/history/units/{tg}_oob.txt"
    if not os.path.exists(f) or "regiment" not in rd(f): armyless.append(tg)
chk("every country holding land has an army", not armyless, armyless[:8])

# HPM's largest single army anywhere is twelve regiments. Ours grew to two hundred in
# one Qing stack and thirty-six for New Spain, because the war-footing passes added
# regiments to existing armies instead of raising new ones -- and selecting New Spain
# crashed the game the first time its order of battle was ever read.
_huge = []
for _f in glob.glob(f"{MOD}/history/units/*.txt"):
    _t = re.sub(r"#.*", "", rd(_f))
    for _m in re.finditer(r"[ \t]*army[ \t]*=[ \t]*\{", _t):
        _i = _m.end(); _d = 1
        while _i < len(_t) and _d:
            if _t[_i] == "{": _d += 1
            elif _t[_i] == "}": _d -= 1
            _i += 1
        _n = len(re.findall(r"regiment\s*=\s*\{", _t[_m.end():_i]))
        if _n > 12:
            _huge.append(f"{os.path.basename(_f)[:3]} has an army of {_n}")
chk("no army is larger than a corps", not _huge, sorted(set(_huge))[:6])

# France began the game with no armies on the map because almost every regiment in its
# order of battle was a type it had no technology for. The Garde Royale is `guard`,
# which Victoria II unlocks with breech-loaded rifles -- an 1860s technology -- and
# after the rollback France did not have it. 243 units across 39 countries, all
# silently absent, which is why France lost every war after 1806.
_act = {}
for _f in glob.glob(f"{MOD}/technologies/*.txt") + glob.glob(f"{MOD}/inventions/*.txt"):
    _t = re.sub(r"#.*", "", rd(_f))
    for _m in re.finditer(r"^([a-z_0-9]+)\s*=\s*\{", _t, re.M):
        _i = _m.end(); _d = 1
        while _i < len(_t) and _d:
            if _t[_i] == "{": _d += 1
            elif _t[_i] == "}": _d -= 1
            _i += 1
        for _u in re.findall(r"activate_unit\s*=\s*(\w+)", _t[_m.end():_i]):
            _act[_u] = _m.group(1)
_startech = {}
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(_f))[0]
    _startech[_b.split(" - ")[0].strip()] = set(
        re.findall(r"^\s*([a-z_]+)\s*=\s*1\s*$", _h, re.M))
_unfieldable = []
for _f in glob.glob(f"{MOD}/history/units/*.txt"):
    _tg = os.path.basename(_f)[:3]
    for _u in set(re.findall(r"type\s*=\s*(\w+)", re.sub(r"#.*", "", rd(_f)))):
        if _u in ("land", "sea"): continue
        _need = _act.get(_u)
        if _need and _need not in _startech.get(_tg, set()):
            _unfieldable.append(f"{_tg} has {_u}, needs {_need}")
chk("no country fields a unit it has no technology for", not _unfieldable,
    sorted(set(_unfieldable))[:6])

# The shape of every colonial war: Spain beats any one viceroyalty, cannot beat them
# all at once, and loses to France. If these drift the whole period stops working.
def _regs(tg):
    f = f"{MOD}/history/units/{tg}_oob.txt"
    return len(re.findall(r"regiment\s*=\s*\{", re.sub(r"#.*", "", rd(f)))) \
        if os.path.exists(f) else 0
_spa = _regs("SPA")
_biggest = max(_regs(t) for t in ("NSP", "VPE", "VNG", "RDP", "CGC"))
# The viceroyalties are garrisons; the republics are the belligerents. Spain's real
# test is whether it can face the countries the risings produce, all at once.
_all = sum(_regs(t) for t in ("MEX", "PEU", "CLM", "ARG", "CHL"))
_fra = _regs("FRA")
chk("Spain outnumbers its largest colony", _spa > _biggest * 1.5,
    f"Spain {_spa} vs {_biggest}")
chk("Spain cannot face every republic at once", _spa < _all,
    f"Spain {_spa} vs {_all} together")
chk("Spain is outmatched by France", _spa * 2 < _fra, f"Spain {_spa} vs France {_fra}")
# A regiment is filled from the soldier pop of its home province. New Spain had
# thirty-six regiments drawing on soldier pops of seven, fifteen and twenty-nine, and
# put nothing at all on the map -- for four patches, while I looked at unit types,
# brace counts and province ownership.
_sol = collections.Counter()
for _f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    _t = re.sub(r"#.*", "", rd(_f))
    for _pm in re.finditer(r"^(\d+)\s*=\s*\{", _t, re.M):
        _pid = int(_pm.group(1)); _i = _pm.end(); _d = 1
        while _i < len(_t) and _d:
            if _t[_i] == "{": _d += 1
            elif _t[_i] == "}": _d -= 1
            _i += 1
        for _m in re.finditer(r"\bsoldiers = \{\n\t\tculture = \w+\n\t\t"
                              r"religion = \w+\n\t\tsize = (\d+)", _t[_pm.end():_i-1]):
            _sol[_pid] += int(_m.group(1))
# A nation of four thousand people does not raise a European regiment. Its warriors
# are irregulars drawn from a whole people rather than a professional soldier class,
# so the bar for them is a few hundred rather than nine hundred -- which is the whole
# reason the plains nations could field anything at all and still lose.
_SMALL = {"SIO", "COM", "PAW", "OSA", "APA", "NAV", "CRA", "BLA", "ARI", "CHE",
          "CRK", "CHA", "SEM", "CCY", "CAW", "NEZ", "AAA", "ANI", "IRO", "COA",
          "COK", "SAL", "BCY", "MAP", "TLI", "YUP", "CHY", "ARA", "KAN", "OTO"}
_unmanned = []
for _f in glob.glob(f"{MOD}/history/units/*.txt"):
    _tg = os.path.basename(_f)[:3]
    if _tg in SPAWNS_LATER: continue
    _n = len(re.findall(r"regiment\s*=\s*\{", re.sub(r"#.*", "", rd(_f))))
    if _n < 2: continue
    _bar = 260 if _tg in _SMALL else 900
    _cap = sum(_sol.get(p, 0) for p, o in owner.items() if o == _tg) // _bar
    if _cap < _n:
        _unmanned.append(f"{_tg}: {_n} regiments, manpower for {_cap}")
chk("every army has the soldiers to fill it", not _unmanned, sorted(_unmanned)[:6])

chk("Spain can carry an army across the Atlantic",
    "clipper_transport" in rd(f"{MOD}/history/units/SPA_oob.txt"), "no transports")

# A party whose start_date equals the game's start date is not active on day one:
# Victoria II wants it to have begun strictly earlier. 1,523 parties were dated to
# 1800.1.1 and 448 countries, France among them, had a ruling party the game would not
# recognise -- and therefore no ideology at all.
_pstart = {}
for _g in glob.glob(f"{MOD}/common/countries/*.txt"):
    _t = rd(_g)
    for _m in re.finditer(r"party\s*=\s*\{(.*?)\n\}", _t, re.S):
        _n = re.search(r'name\s*=\s*"([^"]*)"', _m.group(1))
        _sd = re.search(r"start_date\s*=\s*(\S+)", _m.group(1))
        if _n: _pstart[_n.group(1)] = _sd.group(1) if _sd else None
_inactive = []
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(_f))[0]
    _m = re.search(r"^\s*ruling_party\s*=\s*(\S+)", _h, re.M)
    if not _m: continue
    _sd = _pstart.get(_m.group(1))
    if _sd is None: continue          # defined in another country's file: HPM's own
    if _sd >= "1800.1.1" and not _sd.startswith("179"):
        _inactive.append(f"{_b.split(' - ')[0]}:{_m.group(1)} starts {_sd}")
chk("every ruling party is active on the start date", not _inactive, _inactive[:6])

# ---- leaders
tr = re.sub(r"#.*", "", rd(f"{MOD}/common/traits.txt"))
_d, _cur, PERS, BACK = 0, None, set(), set()
for m in re.finditer(r"([a-z_]+)\s*=\s*\{|\{|\}", tr):
    t_ = m.group(0)
    if t_ == "}": _d -= 1
    elif t_ == "{": _d += 1
    else:
        n = m.group(1)
        if _d == 0: _cur = n
        elif _d == 1: (PERS if _cur == "personality" else BACK).add(n)
        _d += 1
badtrait, atstart = [], set()
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    tg = os.path.basename(f)[:3]
    for blk in re.findall(r"leader\s*=\s*\{([^}]*)\}", rd(f), re.S):
        p_ = re.search(r"personality\s*=\s*(\w+)", blk)
        b_ = re.search(r"background\s*=\s*(\w+)", blk)
        if p_ and p_.group(1) not in PERS: badtrait.append(f"{tg} {p_.group(1)}")
        if b_ and b_.group(1) not in BACK: badtrait.append(f"{tg} {b_.group(1)}")
        y = re.search(r"date\s*=\s*(\d{4})", blk)
        if y and int(y.group(1)) <= 1800: atstart.add(tg)
chk("every leader trait exists", not badtrait, sorted(set(badtrait))[:6])
WARRING = {"FRA","ENG","AUS","TUR","SIC","POR","NET","LIG","SPA"}
chk("every country at war has a commander on day one",
    not (WARRING - atstart), sorted(WARRING - atstart))

# A leader dated before the country that holds him exists never appears at all.
# Toussaint sat on Haiti's roster from 1799; Haiti is founded in 1804 and he died in a
# French prison in 1803, so the best commander in the Caribbean was in the files and
# never in the game.
# The earliest our own content can bring each country into being, which is its
# rising, not its historical independence: the civil wars create Mexico, Colombia,
# Argentina and Chile in 1810 and Peru in 1814.
BORN_WITH = {"HAI": 1804, "MEX": 1810, "ARG": 1810, "CHL": 1810, "CLM": 1810,
             "PEU": 1814, "BRZ": 1822, "VNZ": 1777, "ECU": 1830, "BOL": 1825,
             "URU": 1828, "PRG": 1811}
early = []
for tg, born in BORN_WITH.items():
    f = f"{MOD}/history/units/{tg}_oob.txt"
    if not os.path.exists(f): continue
    for blk in re.findall(r"leader\s*=\s*\{([^}]*)\}", rd(f), re.S):
        d_ = re.search(r"date\s*=\s*(\d{4})", blk)
        n_ = re.search(r'name\s*=\s*"([^"]*)"', blk)
        if d_ and int(d_.group(1)) < born:
            early.append(f"{tg} {n_.group(1) if n_ else '?'} dated {d_.group(1)}, "
                         f"country exists {born}")
chk("no leader waits on a country founded after him", not early, early[:5])

# ---- spheres of influence
GP1800 = {"ENG", "FRA", "RUS", "AUS", "SPA", "TUR", "PRU"}
badsph, ghost = [], []
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    tg = os.path.basename(f)[:3]
    for other, blk in re.findall(r"^([A-Z]{3})[ \t]*=[ \t]*\{([^}]*)\}", rd(f), re.M):
        if other not in TAGS: ghost.append(f"{tg}->{other}")
        if re.search(r"level\s*=\s*5", blk):
            if tg not in GP1800: badsph.append(f"{tg} spheres {other}")
            elif not held.get(other): ghost.append(f"{tg} spheres landless {other}")
chk("only Great Powers hold a sphere", not badsph, sorted(set(badsph))[:6])
chk("every sphere and relation names a country that exists and holds land",
    not ghost, sorted(set(ghost))[:6])

# ---- our events and decisions
ours = glob.glob(f"{MOD}/events/1800_*.txt") + glob.glob(f"{MOD}/decisions/1800_*.txt")
loc = "\n"
for f in glob.glob(f"{MOD}/localisation/*.csv"): loc += raw(f)
ids = collections.Counter()
for f in glob.glob(f"{MOD}/events/*.txt"):
    for m in re.finditer(r"^\s*id\s*=\s*(\d+)", rd(f), re.M): ids[m.group(1)] += 1
chk("no duplicate event ids anywhere", not [k for k, v in ids.items() if v > 1],
    [k for k, v in ids.items() if v > 1][:5])

reftag, refprov, refcult, refmod, reftrig = set(), set(), set(), set(), set()
for f in ours:
    t = rd(f)
    reftag |= set(re.findall(r"\b(?:tag|vassal_of|war_with|release|target)\s*=\s*([A-Z]{3})\b", t))
    reftag |= set(re.findall(r"^\s*([A-Z]{3})\s*=\s*\{", t, re.M))
    refprov |= {int(x) for x in re.findall(r"^\s*(\d+)\s*=\s*\{", t, re.M)}
    refprov |= {int(x) for x in re.findall(r"state_province_id\s*=\s*(\d+)", t)}
    refcult |= set(re.findall(r"(?:has_pop_culture|add_accepted_culture|primary_culture)\s*=\s*([A-Za-z_0-9]+)", t))
    refmod |= set(re.findall(r"(?:name = |remove_country_modifier = )([a-z_0-9]+)", t))
reftag -= {"THIS", "FROM", "OR", "AND", "NOT"}
chk("our content references only registered tags", not (reftag - TAGS), sorted(reftag - TAGS)[:8])
chk("our content references only real provinces", not (refprov - DEFN), sorted(refprov - DEFN)[:8])
chk("our content references only defined cultures", not (refcult - CULT), sorted(refcult - CULT)[:8])
chk("our content references only defined modifiers", not (refmod - MODS), sorted(refmod - MODS)[:8])

# every option in our events/decisions has a name, and every name is localised
missing = []
for f in ours:
    t = rd(f)
    # `define_general` and `define_admiral` take the commander's actual name as a
    # literal, exactly as HPM writes them ("Umar Tall"). They are not localisation keys.
    t = re.sub(r'define_(?:general|admiral)\s*=\s*\{[^}]*\}', '', t)
    for m in re.finditer(r'name\s*=\s*"([^"]+)"', t):
        if f"\n{m.group(1)};" not in loc: missing.append(m.group(1))
    for m in re.finditer(r'(?:title|desc)\s*=\s*"([^"]+)"', t):
        if f"\n{m.group(1)};" not in loc: missing.append(m.group(1))
chk("every string our content shows is localised", not missing, sorted(set(missing))[:6])

# random_list weights must be positive integers
badw = []
for f in ours:
    for m in re.finditer(r"random_list\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", rd(f), re.S):
        ws = [int(x) for x in re.findall(r"^\s*(\d+)\s*=\s*\{", m.group(1), re.M)]
        if not ws or any(w <= 0 for w in ws): badw.append(ws)
chk("every random_list has positive weights", not badw, badw[:4])

# ---- pops
popprov = collections.Counter(); zero = 0; badc = set(); badr = set(); badt = set()
PT = {os.path.basename(x)[:-4] for x in glob.glob(f"{MOD}/poptypes/*.txt")}
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    s = rd(f)
    for m in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M): popprov[int(m.group(1))] += 1
    for ty, cu, rl, sz in re.findall(r"\t([a-z_]+) = \{\s*culture = ([a-z_0-9]+)\s*religion = ([a-z_0-9]+)\s*size = (\d+)", re.sub(r"\s+", " ", s).replace(" ", " ")):
        pass
    for m in re.finditer(r"size\s*=\s*(\d+)", s):
        if int(m.group(1)) <= 0: zero += 1
    badc |= set(re.findall(r"culture\s*=\s*([a-z_0-9]+)", s)) - CULT
    badr |= set(re.findall(r"religion\s*=\s*([a-z_0-9]+)", s)) - RELS
    badt |= set(re.findall(r"^\s*([a-z_]+)\s*=\s*\{\s*$", s, re.M)) - PT
chk("no province appears in two pop files", not [p for p, n in popprov.items() if n > 1],
    [p for p, n in popprov.items() if n > 1][:5])
chk("no zero-size pops", zero == 0, zero)
chk("every pop culture is defined", not badc, sorted(badc)[:6])
chk("every pop religion is defined", not badr, sorted(badr)[:6])
chk("every owned land province has pops",
    not [p for p, t in owner.items() if t and p not in popprov and p in DEFN],
    [f"{p}:{owner[p]}" for p, t in owner.items() if t and p not in popprov][:6])

# ---- culture colours should be distinguishable
colmap = collections.defaultdict(list)
for m in re.finditer(r"\n\s+([a-z_0-9]+)\s*=\s*\{(?:\s*\n\s*[a-z_]+\s*=\s*\S+)*\s*\n\s*color\s*=\s*\{\s*(\d+)\s+(\d+)\s+(\d+)", src):
    colmap[(m.group(2), m.group(3), m.group(4))].append(m.group(1))
dupcol = {k: v for k, v in colmap.items() if len(v) > 1}
chk("no two cultures share a colour", not dupcol, list(dupcol.values())[:4])

if os.environ.get("SWEEP_RECORD"):
    json.dump(REC, open(BF, "w"), indent=1); print("\nbaseline recorded")
print(f"\n{'NO NEW BUGS' if not bad else str(bad) + ' NEW BUG(S)'}")
