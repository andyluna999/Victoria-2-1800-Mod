"""Factories and social legislation for 1800.

Two classes of 1836 content that survived every pass so far because nothing was
looking for them.

**Factories.** Seventy-six `state_building` blocks across ninety-two provinces: steel
mills, ammunition works, canned-food plants, glassworks. Victoria II's factory is a
mechanised plant with a capitalist owner and a wage-earning workforce, and in 1800
there were perhaps a few dozen such things on earth, all of them textile mills in
Lancashire and none of them represented by these buildings. The ammunition factory in
particular is an artifact of a world with interchangeable parts, which is 1810s at the
earliest. All of them go.

**Social legislation.** The reform columns are mostly at their minimum already, but a
scattering are not, and every one of them is decades early:

  * eighteen countries limit working hours. The first Factory Act is 1802, applies
    only to pauper apprentices, and is unenforced for thirty years.
  * forty-one permit trade unions. Combination was criminal in Britain under the Acts
    of 1799 and 1800, and in France under the Loi Le Chapelier of 1791.
  * pensions, health care, unemployment subsidies, safety regulation and minimum
    wages all appear in small numbers. Bismarck's pension law is 1889.

Schooling is left alone: Prussia and a few others really did have state schools in
1800, and `low_schools` is a fair description of them.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections

MOD = _BUILD
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t):
    open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# --- factories -------------------------------------------------------------------
removed = collections.Counter()
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    s = rd(f)
    if "state_building" not in s: continue
    out, pos = [], 0
    for m in re.finditer(r"[ \t]*state_building[ \t]*=[ \t]*\{", s):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        while i < len(s) and s[i] in "\r\n": i += 1
        b = re.search(r"building\s*=\s*([a-z_]+)", s[m.end():i])
        removed[b.group(1) if b else "?"] += 1
        out.append(s[pos:m.start()]); pos = i
    out.append(s[pos:])
    wr(f, "".join(out)); log["province files cleared of factories"] += 1
log["factories removed"] = sum(removed.values())

# --- social legislation ------------------------------------------------------------
# reform: the only value that describes 1800
FLOOR = {
 "wage_reform": "no_minimum_wage",
 "work_hours": "no_work_hour_limit",
 "safety_regulations": "no_safety",
 "health_care": "no_health_care",
 "unemployment_subsidies": "no_subsidies",
 "pensions": "no_pensions",
 "trade_unions": "no_trade_unions",
}
changed = collections.Counter()
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    before = head
    for k, floor in FLOOR.items():
        m = re.search(rf"^\s*{k}\s*=\s*(\w+)", head, re.M)
        if m and m.group(1) != floor:
            changed[f"{k}: {m.group(1)}"] += 1
            head = re.sub(rf"^\s*{k}\s*=.*$", f"{k} = {floor}", head, count=1, flags=re.M)
    if head != before:
        wr(f, head + tail); log["countries rolled back"] += 1
log["reform settings changed"] = sum(changed.values())

print(f"  factories removed                 {log['factories removed']}")
for b, n in removed.most_common(6):
    print(f"    {b:<24}{n}")
print(f"  province files cleared            {log['province files cleared of factories']}")
print(f"  countries rolled back             {log['countries rolled back']}")
for k, n in changed.most_common(8):
    print(f"    {k:<34}{n}")
