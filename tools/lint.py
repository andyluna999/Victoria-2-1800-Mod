"""Static checks on the built mod. Every one of these has caught a real defect."""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, collections, glob, os, csv, collections, sys
import json
MOD=os.environ.get("LINT_TARGET",_BUILD)
BASEFILE=f"{_TOOLS}/lint_baseline.json"
BASE=json.load(open(BASEFILE)) if os.path.exists(BASEFILE) and not os.environ.get("LINT_RECORD") else {}
RECORD={}
fails=0
def chk(name, ok, detail=""):
    """Fail only on defects we introduced. HPM ships with a few of its own; those are
    recorded once against pristine HPM and reported as KNOWN rather than failing."""
    global fails
    d=str(detail)
    RECORD[name]=d
    if ok:
        print("  PASS "+name+("  -> "+d if d else "")); return
    b=BASE.get(name)
    if b==d:
        print("  KNOWN "+name+"  -> pre-existing in HPM: "+d); return
    # a finding that has shrunk is an improvement, not a regression
    try:
        import ast
        cur_l, base_l = ast.literal_eval(d), ast.literal_eval(b) if b else None
        if isinstance(cur_l, list) and isinstance(base_l, list) and set(cur_l) <= set(base_l):
            fixed = sorted(set(base_l) - set(cur_l))
            print("  KNOWN "+name+"  -> pre-existing in HPM: "+d
                  + ("   (we fixed: "+", ".join(map(str, fixed))+")" if fixed else "")); return
    except Exception:
        pass
    print("  FAIL "+name+("  -> "+d if d else "")); fails+=1

# 1. encoding + line endings
bad_enc=[]; bad_eol=[]
for f in glob.glob(f"{MOD}/**/*.txt",recursive=True)+glob.glob(f"{MOD}/**/*.csv",recursive=True):
    b=open(f,"rb").read()
    if b.startswith(b"\xef\xbb\xbf"): bad_enc.append(f)
    if b"\r\n" in b: bad_eol.append(f)
chk("no UTF-8 BOM anywhere", not bad_enc, bad_enc[:3])
chk("no CRLF line endings", not bad_eol, [os.path.basename(x) for x in bad_eol[:3]])

# 2. brace balance
imb=[]
for f in glob.glob(f"{MOD}/**/*.txt",recursive=True):
    s=re.sub(r"#.*","",open(f,encoding="cp1252",errors="replace").read())
    if s.count("{")!=s.count("}"): imb.append(os.path.relpath(f,MOD))
chk("braces balanced in every file", not imb, imb[:5])

# 3. cultures
src=open(f"{MOD}/common/cultures.txt",encoding="cp1252",errors="replace").read()
src=re.sub(r"#.*","",src)
cults=[];depth=0
for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}",src):
    t=m.group(0)
    if t=="}":depth-=1
    elif t=="{":depth+=1
    else:
        if depth==1 and m.group(1) not in("color","leader","unit","union","is_overseas"):cults.append(m.group(1))
        depth+=1
dup=[k for k,v in collections.Counter(cults).items() if v>1]
chk("no duplicate culture definitions", not dup, dup[:8])
chk("culture count", len(cults)>280, len(cults))

# 4. every culture used by a pop is defined
used=set()
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    used|=set(re.findall(r"culture\s*=\s*([a-z_0-9]+)",open(f,encoding="cp1252",errors="replace").read()))
chk("every pop culture is defined", used<=set(cults), sorted(used-set(cults))[:8])

# 5. tags
reg=open(f"{MOD}/common/countries.txt",encoding="cp1252",errors="replace").read()
tags=set(re.findall(r"^\s*([A-Z]{3})\s*=",re.sub(r"#.*","",reg),re.M))
missing=[]
for t in tags:
    rel=re.search(rf"^\s*{t}\s*=\s*\"?([^\"\n]+?)\"?\s*$",reg,re.M)
    if rel and not os.path.exists(os.path.join(MOD,"common",rel.group(1).strip())): missing.append(t)
chk("every tag has a country definition file", not missing, sorted(missing)[:6])
# primary cultures resolve
badpc=[]
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    s=re.sub(r"#.*","",open(f,encoding="cp1252",errors="replace").read())
    m=re.search(r"primary_culture\s*=\s*([a-z_0-9]+)",s)
    if m and m.group(1) not in cults: badpc.append((os.path.basename(f)[:3],m.group(1)))
chk("every primary_culture resolves", not badpc, badpc[:6])

# 5b. exactly one history file per tag
seen=collections.defaultdict(list)
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b=os.path.basename(f)
    if " - " in b: seen[b.split(" - ")[0]].append(b)
dups={k:v for k,v in seen.items() if len(v)>1}
chk("one history file per tag", not dups, list(dups.items())[:3])

# 5c. no tag may be a Windows reserved device name -- its flag file cannot exist
RESERVED={"CON","PRN","AUX","NUL"}|{f"COM{i}" for i in range(1,10)}|{f"LPT{i}" for i in range(1,10)}
res=[t for t in tags if t.upper() in RESERVED]
chk("no tag is a Windows reserved device name", not res, res)

# 5d. every filename must be creatable on Windows
BADCH=set('<>:"/\\|?*')
illegal=[]
for f in glob.glob(f"{MOD}/**/*",recursive=True):
    b=os.path.basename(f)
    stem=b.split(".")[0].upper()
    if set(b) & BADCH or stem in RESERVED or b.rstrip() != b or b.endswith("."):
        illegal.append(os.path.relpath(f,MOD))
chk("every filename is legal on Windows", not illegal, illegal[:5])

# 5e. every decision and event we add must have its localisation and its modifiers
ours_dec=glob.glob(f"{MOD}/decisions/1800_*.txt")
ours_ev=glob.glob(f"{MOD}/events/1800_*.txt")
loc_all="\n"
for f in glob.glob(f"{MOD}/localisation/*.csv"):
    loc_all+=open(f,encoding="cp1252",errors="replace").read()
em=open(f"{MOD}/common/event_modifiers.txt",encoding="cp1252",errors="replace").read()
miss_loc, miss_mod = [], []
SKIP={"trigger","option","mean_time_to_happen","effect","allow","potential","ai_will_do",
      "modifier","limit","any_owned","any_pop","any_country"}
# Read brace depth, not indentation. A decision is a block at depth one inside
# political_decisions; `war = {` and `relation = {` sitting inside an effect block are
# not decisions, and matching on four spaces reported them as unlocalised.
def _decision_names(text):
    text = re.sub(r"#.*", "", text)
    pm = re.search(r"political_decisions\s*=\s*\{", text)
    if not pm: return
    i, depth = pm.end(), 1
    while i < len(text) and depth:
        if text[i] == "{": depth += 1
        elif text[i] == "}": depth -= 1
        elif depth == 1:
            nm = re.match(r"\s*([a-z_0-9]+)\s*=\s*\{", text[i:])
            if nm:
                yield nm.group(1)
                j, d2 = i + nm.end(), 1
                while j < len(text) and d2:
                    if text[j] == "{": d2 += 1
                    elif text[j] == "}": d2 -= 1
                    j += 1
                i = j
                continue
        i += 1

for f in ours_dec:
    t=open(f,encoding="cp1252",errors="replace").read()
    for n in _decision_names(t):
        if n in SKIP: continue
        # Victoria II keys a decision's title as <name>_title, not <name>. This
        # check looked for the bare name and so passed every decision whose title was
        # missing while failing the ones that had it.
        if f"\n{n}_title;" not in loc_all: miss_loc.append(n + "_title")
        if f"\n{n}_desc;" not in loc_all: miss_loc.append(n + "_desc")
for f in ours_dec+ours_ev:
    t=open(f,encoding="cp1252",errors="replace").read()
    for n in set(re.findall(r"EVTNAME(\d+)",t)):
        if f"\nEVTNAME{n};" not in loc_all: miss_loc.append("EVTNAME"+n)
    for m in set(re.findall(r"(?:name = |remove_country_modifier = )([a-z_0-9]+)",t)):
        if not re.search(rf"^{m} = \{{",em,re.M): miss_mod.append(m)
chk("our decisions and events are localised", not miss_loc, sorted(set(miss_loc))[:6])
chk("every modifier we reference is defined", not miss_mod, sorted(set(miss_mod))[:6])

# A picture that is not on disk shows as a blank panel in the event window.
_pics = set()
for _f in ours_dec + ours_ev:
    _pics |= set(re.findall(r'picture\s*=\s*"([A-Za-z0-9_]+)"',
                            open(_f, encoding="cp1252", errors="replace").read()))
# A picture may live in HPM's own folder or in the base game's, which is not visible
# from here. Anything HPM's own events already use is known good.
_hpmpics = set()
for _f in glob.glob(f"{MOD}/events/*.txt"):
    if os.path.basename(_f).startswith("1800_"): continue
    _hpmpics |= set(re.findall(r'picture\s*=\s*"?([A-Za-z0-9_]+)"?',
                               open(_f, encoding="cp1252", errors="replace").read()))
_nopic = [p for p in _pics
          if not os.path.exists(f"{MOD}/gfx/pictures/events/{p}.tga")
          and p not in _hpmpics]
chk("every event picture we name exists", not _nopic, sorted(_nopic)[:6])

# 6. every country has a party valid at the start
start=int(re.search(r"start_date\s*=\s*'(\d{4})",open(f"{MOD}/common/defines.lua",encoding="cp1252",errors="replace").read()).group(1))
noparty=[]
for f in glob.glob(f"{MOD}/common/countries/*.txt"):
    ds=[int(x) for x in re.findall(r"start_date\s*=\s*(\d{4})",open(f,encoding="cp1252",errors="replace").read())]
    if ds and min(ds)>start: noparty.append(os.path.basename(f))
chk(f"every country has a party valid at {start}", not noparty, noparty[:5])

# 7. provinces referenced in pops exist
defn={int(r[0]) for r in csv.reader(open(f"{MOD}/map/definition.csv",encoding="latin-1"),delimiter=";") if r and r[0].isdigit()}
pp=set()
for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
    pp|={int(x) for x in re.findall(r"^(\d+)\s*=\s*\{",open(f,encoding="cp1252",errors="replace").read(),re.M)}
chk("every pop province exists on the map", pp<=defn, sorted(pp-defn)[:6])

# 8. duplicate event ids
ids=collections.Counter()
for f in glob.glob(f"{MOD}/events/*.txt"):
    s=re.sub(r"#.*","",open(f,encoding="cp1252",errors="replace").read())
    for m in re.finditer(r"^\s*id\s*=\s*(\d+)",s,re.M): ids[m.group(1)]+=1
d=[k for k,v in ids.items() if v>1]
chk("no duplicate event ids", not d, f"{len(d)} duplicated, e.g. {d[:5]}")

# 9. start date consistency
pops_dirs=[os.path.basename(x) for x in glob.glob(f"{MOD}/history/pops/*")]
bm=open(f"{MOD}/common/bookmarks.txt",encoding="cp1252",errors="replace").read()
chk("pops folder matches the start date", pops_dirs==[f"{start}.1.1"], pops_dirs)
chk("bookmark matches the start date", f"{start}.1.1" in bm)

# 10. the vocabulary checks.
# An unknown key makes the whole of common/event_modifiers.txt fail to parse, which
# does not announce itself. The first playtest of the decision shelf hung the game
# hard enough to need a reboot, and the power cycle took the logs with it. Four keys
# were wrong: factory_cost, defense and supply_range in the new modifiers, plus
# administrative_efficiency, which had been sitting in the Ottoman modifier since
# that pass and had never been exercised.
_src = re.sub(r"#.*", "", open(f"{_SRC}/common/event_modifiers.txt",
                               encoding="cp1252", errors="replace").read())
_valid = set(re.findall(r"^\s+([a-z_]+)\s*=\s*-?[\d.]+\s*$", _src, re.M))
_base = set(re.findall(r"^([a-z_0-9]+)\s*=\s*\{", _src, re.M))
_ours = re.sub(r"#.*", "", open(f"{MOD}/common/event_modifiers.txt",
                                encoding="cp1252", errors="replace").read())
# Brace counting, not a regex: a block whose closing brace is indented makes a
# non-greedy match run on into the next one and report a key from the wrong modifier.
def _blocks(text):
    for _m in re.finditer(r"^([a-z_0-9]+)\s*=\s*\{", text, re.M):
        _i = _m.end(); _d = 1
        while _i < len(text) and _d:
            if text[_i] == "{": _d += 1
            elif text[_i] == "}": _d -= 1
            _i += 1
        yield _m.group(1), text[_m.end():_i-1]
_bad = []
for _name, _body in _blocks(_ours):
    if _name in _base: continue
    for _k in re.findall(r"^\s+([a-z_]+)\s*=", _body, re.M):
        if _k != "icon" and _k not in _valid: _bad.append(f"{_name}.{_k}")
chk("every modifier key we add is one the game knows", not _bad, _bad[:6])

# A pop-scope limit takes pop triggers. `has_pop_type` is a country trigger and does
# not belong inside any_pop; HPM writes `type` there, two hundred and fifteen times.
_POPOK = {"has_pop_culture", "has_pop_religion", "type", "is_primary_culture",
          "is_accepted_culture", "is_culture_group", "location", "literacy",
          "is_core", "is_colonial", "province_id", "is_state_religion"}
_bp = []
for _f in glob.glob(f"{MOD}/events/1800_*.txt") + glob.glob(f"{MOD}/decisions/1800_*.txt"):
    _t = open(_f, encoding="cp1252", errors="replace").read()
    for _m in re.finditer(r"any_pop\s*=\s*\{\s*limit\s*=\s*\{([^}]*)\}", _t):
        for _k in re.findall(r"([a-z_]+)\s*=", _m.group(1)):
            if _k not in _POPOK: _bp.append(_k)
chk("every pop-scope trigger is a pop trigger", not _bp, sorted(set(_bp)))

# Braces must balance in every file we touch. The malformed event_modifiers.txt that
# caused the hang was off by exactly one, and nothing else would have noticed.
_unb = []
for _f in (glob.glob(f"{MOD}/common/*.txt") + glob.glob(f"{MOD}/events/1800_*.txt")
           + glob.glob(f"{MOD}/decisions/1800_*.txt") + glob.glob(f"{MOD}/history/wars/*.txt")):
    _t = re.sub(r"#.*", "", open(_f, encoding="cp1252", errors="replace").read())
    _t = re.sub(r'"[^"]*"', '""', _t)
    if _t.count("{") != _t.count("}"):
        _unb.append(f"{os.path.basename(_f)} {_t.count('{')}/{_t.count('}')}")
chk("braces balance in every file we write", not _unb, _unb[:6])

# `change_tag = X` tells a country to become X. If X is already a live country, two
# countries end up holding one tag and Victoria II hangs -- no crash, no log line, the
# process just stops responding. The Carnatic was told to become Britain and froze the
# game on 30 June 1801; Tay Son -> DAI had the same fault waiting in 1802. A live tag
# must be annexed into with annex_to or inherit, never become.
_live = set()
for _f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    _h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                  open(_f, encoding="cp1252", errors="replace").read())[0]
    _m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", _h, re.M)
    if _m: _live.add(_m.group(1))
_ct = []
for _f in glob.glob(f"{MOD}/events/1800_*.txt") + glob.glob(f"{MOD}/decisions/1800_*.txt"):
    _t = re.sub(r"#.*", "", open(_f, encoding="cp1252", errors="replace").read())
    for _m in re.finditer(r"change_tag\s*=\s*([A-Z]{3})", _t):
        if _m.group(1) in _live:
            _ct.append(f"{os.path.basename(_f)} -> {_m.group(1)}")
chk("change_tag never targets a country that already exists", not _ct, _ct[:6])

# A decision that forms, annexes or releases a nation and carries no year fires the
# moment its conditions happen to be met. On our map that meant Romania annexing
# Wallachia on 1 January 1800, fifty-nine years early.
_FORMS = re.compile(r"\b(change_tag|inherit|annex_to|release_vassal|"
                    r"change_tag_no_core_switch)\s*=")
_ud = []
for _f in glob.glob(f"{MOD}/decisions/*.txt"):
    if os.path.basename(_f).startswith("1800_"): continue
    _t = re.sub(r"#.*", "", open(_f, encoding="cp1252", errors="replace").read())
    for _m in re.finditer(r"^[ \t]+([a-z_0-9]+)\s*=\s*\{", _t, re.M):
        _i = _m.end(); _d = 1
        while _i < len(_t) and _d:
            if _t[_i] == "{": _d += 1
            elif _t[_i] == "}": _d -= 1
            _i += 1
        _b = _t[_m.end():_i-1]
        if "potential" not in _b or "effect" not in _b: continue
        _pm = re.search(r"potential\s*=\s*\{", _b)
        if not _pm: continue
        _j = _pm.end(); _dd = 1
        while _j < len(_b) and _dd:
            if _b[_j] == "{": _dd += 1
            elif _b[_j] == "}": _dd -= 1
            _j += 1
        if re.search(r"\byear\s*=\s*\d{4}", _b[_pm.end():_j-1]): continue
        if _FORMS.search(_b[_j:]): _ud.append(f"{os.path.basename(_f)}:{_m.group(1)}")
chk("every nation-forming decision carries a date", not _ud, _ud[:6])

# A rebel faction winning a revolt replaces the government, and no amount of auditing
# event files finds it. Carlist rebels took Spain in June 1806 -- twenty-seven years
# before there was anything to be a Carlist about -- and because that changed Spain's
# tag, the whole Peninsular War chain keyed to `tag = SPA` went unreachable. Twice.
_LATE = ("carlist_rebels", "christino_rebels", "pan_nationalist_rebels", "socialist_rebels", "anarcho_liberal_rebels",
         "communist_rebels", "red_shirts", "indian_sepoys", "indian_nationalists",
         "boxer_rebels", "turkish_nationalist_rebels", "fascist_rebels",
         "partisan_rebels")
_rt = re.sub(r"#.*", "", open(f"{MOD}/common/rebel_types.txt",
                              encoding="cp1252", errors="replace").read())
_undated = []
for _m in re.finditer(r"^([a-z_]+)\s*=\s*\{", _rt, re.M):
    if _m.group(1) not in _LATE: continue
    _i = _m.end(); _d = 1
    while _i < len(_rt) and _d:
        if _rt[_i] == "{": _d += 1
        elif _rt[_i] == "}": _d -= 1
        _i += 1
    _b = _rt[_m.end():_i-1]
    _sp = re.search(r"spawn_chance\s*=\s*\{", _b)
    if not _sp: continue
    _j = _sp.end(); _dd = 1
    while _j < len(_b) and _dd:
        if _b[_j] == "{": _dd += 1
        elif _b[_j] == "}": _dd -= 1
        _j += 1
    if not re.search(r"year\s*=\s*\d{4}", _b[_sp.end():_j-1]):
        _undated.append(_m.group(1))
chk("every late rebel movement waits for its century", not _undated, _undated[:6])

# Victoria II prices a technology against its `year`: researching one thirty-six years
# early is effectively impossible. HPM's tree begins in 1836, so at an 1800 start the
# whole of it was out of reach and the powers sat on their four starting army
# technologies for a generation. The first tier must meet the start date.
_ty = []
for _f in glob.glob(f"{MOD}/technologies/*.txt"):
    _ty += [int(_y) for _y in re.findall(r"\byear\s*=\s*(\d{4})",
                                         re.sub(r"#.*", "", open(_f, encoding="cp1252",
                                                                 errors="replace").read()))]
# Victoria II stops parsing a country history file at an unknown key and discards the
# rest of it. `add_country_modifier` is not valid there -- HPM uses it zero times in
# history/countries -- and one line of it on line 15 of France's file threw away its
# prestige, its technologies, its reforms and its ruling party. France loaded with
# nothing and lost every war for twenty-four years.
_vocab = set()
for _f in glob.glob(f"{_SRC}/history/countries/*.txt"):
    _t = re.sub(r"#.*", "", open(_f, encoding="cp1252", errors="replace").read())
    _vocab |= set(re.findall(r"^\s*([a-z_0-9]+)\s*=", _t, re.M))
_alien = []
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _t = re.sub(r"#.*", "", open(_f, encoding="cp1252", errors="replace").read())
    for _k in set(re.findall(r"^\s*([a-z_0-9]+)\s*=", _t, re.M)):
        if _k not in _vocab:
            _alien.append(f"{os.path.basename(_f)[:3]}:{_k}")
chk("country history files use only keys the game reads there", not _alien,
    sorted(set(_alien))[:6])

# And read each file the way the parser does, stopping at the first unknown key, to
# confirm the things that sit late in these files actually survive: prestige is around
# line 20, the ruling party around line 80. One alien key on line 15 lost both.
def _as_game(path):
    _t = re.sub(r"#.*", "", open(path, encoding="cp1252", errors="replace").read())
    _head = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", _t)[0]
    _got = {}
    for _line in _head.split("\n"):
        _m = re.match(r"([a-z_0-9]+)\s*=\s*(\S+)", _line)
        if not _m: continue
        if _m.group(1) not in _vocab: return _got, _m.group(1)
        _got.setdefault(_m.group(1), _m.group(2))
    return _got, None
_lost = []
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _got, _stop = _as_game(_f)
    if _stop:
        _lost.append(f"{_b[:3]} truncated at {_stop}")
    elif _got.get("capital") and not _got.get("ruling_party"):
        _lost.append(f"{_b[:3]} has no ruling party")
chk("every country file survives the parser to its ruling party", not _lost,
    sorted(set(_lost))[:6])

# A country only gets the army its own history file names. New Spain shipped with
# thirty-six regiments in a perfect order-of-battle file and put nothing on the map,
# through four rounds of diagnosis, because no line said `oob = "NSP_oob.txt"` and the
# engine therefore never opened it. Sixty-seven countries were in that state.
_undeclared = []
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _tag = _b.split(" - ")[0].strip()
    if not os.path.exists(f"{MOD}/history/units/{_tag}_oob.txt"): continue
    if not re.search(r'^\s*oob\s*=', open(_f, encoding="cp1252",
                                          errors="replace").read(), re.M):
        _undeclared.append(_tag)
# The mirror of the declaration bug. A country that names an order of battle it has
# no file for is pointing the engine at nothing -- VNM did, because it is created by
# change_tag and carries its army over rather than reading one.
_phantom = []
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _m = re.search(r'^\s*oob\s*=\s*"([^"]+)"',
                   open(_f, encoding="cp1252", errors="replace").read(), re.M)
    if _m and not os.path.exists(f"{MOD}/history/units/{_m.group(1)}"):
        _phantom.append(f"{_b.split(' - ')[0]} -> {_m.group(1)}")

chk("no country declares an order of battle that does not exist", not _phantom,
    sorted(_phantom)[:8])

chk("every order of battle is declared by its country", not _undeclared,
    sorted(_undeclared)[:8])

# A country needs a party for every ideology its Upper House can turn. The
# viceroyalties had two -- conservative and reactionary -- against the 262 countries
# in this mod that have seven, and a run died three days after the Upper House went
# liberal with no liberal party to form a government.
_thin = []
for _f in glob.glob(f"{MOD}/common/countries/*.txt"):
    _t = open(_f, encoding="cp1252", errors="replace").read()
    _by = collections.defaultdict(set)
    for _m in re.finditer(r"party\s*=\s*\{(.*?)\n\}", _t, re.S):
        _n = re.search(r'name\s*=\s*"([A-Z]{3})_', _m.group(1))
        _i = re.search(r"ideology\s*=\s*(\w+)", _m.group(1))
        if _n and _i: _by[_n.group(1)].add(_i.group(1))
    for _tg, _ids in _by.items():
        if _tg in ("NSP","VPE","VNG","RDP","CGC","CBA","PTR","EBR") and len(_ids) < 5:
            _thin.append(f"{_tg} has only {sorted(_ids)}")
chk("every viceroyalty has a party for each ideology", not _thin, sorted(_thin)[:6])

# A province takes add_province_modifier, not add_country_modifier. HPM uses the
# province form 874 times. Forty-four of ours were the country effect aimed at a
# province, which the engine accepts and silently does nothing with -- the whole
# frontier would have stayed shut.
_wrongscope = []
for _f in glob.glob(f"{MOD}/events/1800_*.txt") + glob.glob(f"{MOD}/decisions/1800_*.txt"):
    _t = re.sub(r"#.*", "", open(_f, encoding="cp1252", errors="replace").read())
    # `70 = { ... }` inside a random_list is a probability weight, not a province id
    _t = re.sub(r"random_list\s*=\s*\{", "RANDOMLIST {", _t)
    _depth, _inrand, _clean = 0, -1, []
    for _ch in _t:
        if _ch == "{": _depth += 1
        elif _ch == "}":
            _depth -= 1
            if _inrand >= 0 and _depth < _inrand: _inrand = -1
        _clean.append(" " if _inrand >= 0 else _ch)
        if _clean[-9:] == list("RANDOMLIST")[:9] or "".join(_clean[-10:]) == "RANDOMLIST":
            _inrand = _depth
    for _m in re.finditer(r"\b(\d{1,4})\s*=\s*\{[^{}]*?(add|remove)_country_modifier",
                          "".join(_clean)):
        _wrongscope.append(f"{os.path.basename(_f)} province {_m.group(1)}")
chk("a province gets a province modifier, not a country one", not _wrongscope,
    sorted(set(_wrongscope))[:6])

# Our province passes rewrite a file's head to change owners, cores and trade goods,
# and were dropping the naval_base line while they did it -- thirty-nine harbours HPM
# ships were simply gone, including Charleston, Bordeaux, Rotterdam and La Coruna.
_was = set()
for _f in glob.glob(f"{_SRC}/history/provinces/*/*.txt"):
    if re.search(r"^\s*naval_base\s*=\s*[1-9]",
                 open(_f, encoding="cp1252", errors="replace").read(), re.M):
        _was.add(int(re.match(r"(\d+)", os.path.basename(_f)).group(1)))
_now = set()
for _f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    if re.search(r"^\s*naval_base\s*=\s*[1-9]",
                 open(_f, encoding="cp1252", errors="replace").read(), re.M):
        _now.add(int(re.match(r"(\d+)", os.path.basename(_f)).group(1)))
chk("no harbour HPM shipped has been lost", not (_was - _now),
    sorted(_was - _now)[:8])

# The base game's Louisiana Purchase takes French-cored North American provinces, and
# Victoria II counts the Caribbean as North America -- so the United States annexed
# Haiti in every playthrough. That event is vanilla's and cannot be edited from this
# mod, so the defence is that France holds no core there to match on. It also happens
# to be true: Saint-Domingue had been in open revolt since 1791.
_hisp = []
for _p in (2213, 2214, 2215, 2216):
    for _f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
        if not os.path.basename(_f).startswith(f"{_p} "): continue
        if re.search(r"^\s*add_core\s*=\s*FRA\s*$",
                     open(_f, encoding="cp1252", errors="replace").read(), re.M):
            _hisp.append(_p)
chk("France holds no core on Hispaniola", not _hisp, _hisp)

# Victoria II keeps the first definition of a modifier it reads, so a second one with
# the same name is dead on arrival and silently so. `the_hundred_days` was defined
# twice and our version never applied.
_em = open(f"{MOD}/common/event_modifiers.txt", encoding="cp1252", errors="replace").read()
# silk_famine is duplicated in pristine HPM; we police only what we add.
_pris = open(f"{_SRC}/common/event_modifiers.txt",
             encoding="cp1252", errors="replace").read()
_prisdup = {k for k, v in collections.Counter(
    re.findall(r"^([a-z_0-9]+) = \{", _pris, re.M)).items() if v > 1}
_dupmod = [k for k, v in collections.Counter(
    re.findall(r"^([a-z_0-9]+) = \{", _em, re.M)).items()
    if v > 1 and k not in _prisdup]
chk("every modifier is defined exactly once", not _dupmod, sorted(_dupmod)[:8])

# Two player reports turned out to be instances of general faults, and the instance
# is worth much less than the class. Qatar governed from Billings, Montana; the Nguyen
# fought a war decided at sea with no ships at all.
_own = {}
for _f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    _pid = int(re.match(r"(\d+)", os.path.basename(_f)).group(1))
    _h = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                  open(_f, encoding="cp1252", errors="replace").read())[0]
    _m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", _h, re.M)
    _own[_pid] = _m.group(1) if _m else ""

_stranded = []
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _tag = _b.split(" - ")[0].strip()
    _h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)",
                  open(_f, encoding="cp1252", errors="replace").read())[0]
    _m = re.search(r"^\s*capital\s*=\s*(\d+)", _h, re.M)
    if not _m: continue
    _mine = [p for p, o in _own.items() if o == _tag]
    if _mine and int(_m.group(1)) not in _mine:
        _stranded.append(f"{_tag}:{_m.group(1)}")
chk("every country governs from land it holds", not _stranded, sorted(_stranded)[:8])

# Quy Nhon is 1379 and Pleiku is 1378, and one transposed digit had the Nguyen
# raising regiments on a plateau they did not govern. The re-homing pass moved them
# silently every build, so nothing ever complained.
_foreign = []
# A tag that does not exist at the start -- French Algeria, the successor republics --
# has its order of battle written against land it will hold when it is created, which
# is correct and not a fault.
_live = {t for t in _own.values() if t}
for _f in glob.glob(f"{MOD}/history/units/*.txt"):
    _tag = os.path.basename(_f)[:3]
    if _tag not in _live: continue
    for _m in re.finditer(r"\bhome\s*=\s*(\d+)",
                          open(_f, encoding="cp1252", errors="replace").read()):
        if _own.get(int(_m.group(1)), _tag) != _tag:
            _foreign.append(f"{_tag} raises in {_m.group(1)} "
                            f"(held by {_own.get(int(_m.group(1)))})")
chk("no country raises a regiment on another country's land", not _foreign,
    sorted(set(_foreign))[:8])

_ports = set()
for _f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    if re.search(r"^\s*naval_base\s*=\s*[1-9]",
                 open(_f, encoding="cp1252", errors="replace").read(), re.M):
        _ports.add(int(re.match(r"(\d+)", os.path.basename(_f)).group(1)))
_shipless = []
for _f in glob.glob(f"{MOD}/history/countries/*.txt"):
    _b = os.path.basename(_f)
    if " - " not in _b: continue
    _tag = _b.split(" - ")[0].strip()
    # This is about state navies. Ireland is dormant under Britain, and a people
    # who hold coastline without building seagoing ships -- the Mapuche, the coastal
    # nations of the Pacific north-west -- are not a gap in the data.
    if _tag in ("IRE", "MAP", "COA", "COK", "SAL", "TLI", "YUP", "BCY"): continue
    if len([p for p in _ports if _own.get(p) == _tag]) < 2: continue
    _u = f"{MOD}/history/units/{_tag}_oob.txt"
    if not os.path.exists(_u) or "ship = " not in open(
            _u, encoding="cp1252", errors="replace").read():
        _shipless.append(_tag)
chk("a country with harbours has something to put in them", not _shipless,
    sorted(_shipless)[:8])

chk("the technology tree is reachable from the start date",
    _ty and min(_ty) <= start, f"earliest technology year is {min(_ty) if _ty else '?'}")

if os.environ.get("LINT_RECORD"):
    json.dump(RECORD, open(BASEFILE,"w"), indent=1)
    print("\nbaseline recorded from "+MOD)
print(f"\n{'ALL CHECKS PASSED' if not fails else str(fails)+' NEW DEFECT(S)'}")
sys.exit(1 if fails else 0)
