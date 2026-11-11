"""WP-12. A country whose parties all begin after the start date has no ruling party
and therefore no government. 281 of 546 HPM country files are in that state at 1800."""
# A party whose start_date equals the game's start date is not yet active on day one:
# Victoria II wants it to have begun strictly earlier. Dating 1,523 parties to
# 1800.1.1 left 448 countries, France among them, with a ruling party the game would
# not recognise and therefore no ideology at all. They start the year before.
import re, glob, os
MOD="/home/claude/build/HPM"; START=1800
fixed=cnt=0; clamped=[]
for f in glob.glob(f"{MOD}/common/countries/*.txt"):
    s=open(f,encoding="cp1252",errors="replace").read()
    ds=[int(x) for x in re.findall(r"start_date\s*=\s*(\d{4})",s)]
    if not ds: continue
    cnt+=1
    if min(ds)<=START: continue
    # pull every party that begins before 1848 back to the start date, so each country
    # keeps a conservative/reactionary option at 1800 without inventing new parties
    def back(m):
        y=int(m.group(1))
        return f"start_date = {START-1}.1.1" if y<1848 else m.group(0)
    ns=re.sub(r"start_date\s*=\s*(\d{4})\.\d+\.\d+", back, s)
    if ns==s:  # nothing under 1848: pull only the earliest
        e=min(ds)
        ns=re.sub(rf"start_date\s*=\s*{e}\.\d+\.\d+", f"start_date = {START-1}.1.1", s, count=1)
    open(f,"w",encoding="cp1252",errors="replace",newline="\n").write(ns)
    fixed+=1; clamped.append(os.path.basename(f)[:-4])
print(f"  party dates: {fixed} of {cnt} country files clamped back to {START}")
# verify
bad=[]
for f in glob.glob(f"{MOD}/common/countries/*.txt"):
    s=open(f,encoding="cp1252",errors="replace").read()
    ds=[int(x) for x in re.findall(r"start_date\s*=\s*(\d{4})",s)]
    if ds and min(ds)>START: bad.append(os.path.basename(f))
print(f"  countries still with no party at {START}: {len(bad)} {bad[:5]}")

# A second pass over the result: any party a country actually rules with must be
# active on day one, whatever its original date. The first pass only moved parties
# whose start_date was before 1848, which left 283 ruling parties stranded -- some at
# 1800.1.1 exactly, some as late as 1913 because the country's earlier parties had
# been dropped. Victoria II wants the ruling party to have begun strictly before the
# current date, so they are dated to the year before the start.
import glob as _glob, os as _os, re as _re
_MOD = MOD if "MOD" in dir() else "/home/claude/build/HPM"
_ruling = {}
for _f in _glob.glob(f"{_MOD}/history/countries/*.txt"):
    _b = _os.path.basename(_f)
    if " - " not in _b: continue
    _h = _re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)",
                   open(_f, encoding="cp1252", errors="replace").read())[0]
    _m = _re.search(r"^\s*ruling_party\s*=\s*(\S+)", _h, _re.M)
    if _m: _ruling[_m.group(1)] = True
_fixed = 0
for _g in _glob.glob(f"{_MOD}/common/countries/*.txt"):
    _s = open(_g, encoding="cp1252", errors="replace").read()
    _out, _pos, _n = [], 0, 0
    for _m in _re.finditer(r"party\s*=\s*\{", _s):
        _i = _m.end(); _d = 1
        while _i < len(_s) and _d:
            if _s[_i] == "{": _d += 1
            elif _s[_i] == "}": _d -= 1
            _i += 1
        _b2 = _s[_m.start():_i]
        _nm = _re.search(r'name\s*=\s*"([^"]*)"', _b2)
        if not _nm or _nm.group(1) not in _ruling:
            continue
        _sd = _re.search(r"start_date\s*=\s*(\d{4})\.\d+\.\d+", _b2)
        if not _sd or int(_sd.group(1)) < START:
            continue
        _nb = _re.sub(r"start_date\s*=\s*\d{4}\.\d+\.\d+",
                      f"start_date = {START-1}.1.1", _b2, count=1)
        _out.append(_s[_pos:_m.start()]); _out.append(_nb); _pos = _i; _n += 1
    if _n:
        _out.append(_s[_pos:])
        open(_g, "w", encoding="cp1252", errors="replace",
             newline="\n").write("".join(_out))
        _fixed += _n
print(f"  ruling parties made active at start   {_fixed}")
