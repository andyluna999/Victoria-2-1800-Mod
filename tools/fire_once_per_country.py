"""`fire_only_once` on a shared event fires it once for the world, not once each.

"There Is Nobody to Obey" has a trigger covering seven viceroyalties and
`fire_only_once = yes`. It fired for New Granada in April 1810 and for nobody else
ever -- so six viceroyalties never got the interim flag, Spain's demand in 1814 reached
two of them, and the player's own country was not among them.

Nineteen of our events were built that way, and six of them are the separatism drivers.
Bayonne, the Consolidacion, Ferdinand's revocation, the junta and the militia were each
adjusting one viceroyalty's figure and leaving the other six untouched, which is why
the system behaved differently in every playtest and why no amount of tuning the
numbers made it consistent.

The repair is the idiom the engine actually wants: drop `fire_only_once`, have the
event set a flag of its own, and have its trigger exclude countries that already
carry it. That is once per country, which is what every one of these meant.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

for f in sorted(glob.glob(f"{MOD}/events/1800_*.txt")):
    s = rd(f)
    out, pos, n = [], 0, 0
    for m in re.finditer(r"^country_event\s*=\s*\{", s, re.M):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        b = s[m.end():i-1]
        if "fire_only_once = yes" not in b or "is_triggered_only" in b:
            continue
        tm = re.search(r"trigger\s*=\s*\{", b)
        if not tm: continue
        j = tm.end(); dd = 1
        while j < len(b) and dd:
            if b[j] == "{": dd += 1
            elif b[j] == "}": dd -= 1
            j += 1
        trig = b[tm.end():j-1]
        # Count only tags the event is scoped TO, not tags it merely inspects: the
        # Congress events test `FRA = { ... }` inside an AUS trigger and are correctly
        # once-for-the-world, since there is only one Congress.
        top = re.sub(r"[A-Z]{3}\s*=\s*\{[^{}]*\}", "", trig)
        if len(set(re.findall(r"\btag = ([A-Z]{3})", top))) < 2:
            continue
        eid = re.search(r"id = (\d+)", b).group(1)
        flat = " ".join(trig.split())
        sets = re.findall(r"set_country_flag = (\w+)", b)
        # a modifier works as a guard just as well as a flag -- capital flight uses one
        mods = re.findall(r"add_country_modifier = \{ name = (\w+)", b)
        guard = next((x for x in sets
                      if f"NOT = {{ has_country_flag = {x} }}" in flat), None)
        if not guard:
            guard = next((x for x in mods
                          if f"NOT = {{ has_country_modifier = {x} }}" in flat), None)
        nb = b.replace("    fire_only_once = yes\n", "")
        if not guard:
            guard = f"h18_seen_{eid}"
            nb = nb.replace(f"trigger = {{\n", f"trigger = {{\n"
                            f"        NOT = {{ has_country_flag = {guard} }}\n", 1)
            om = re.search(r"option = \{\n(\s*)name = \"[^\"]*\"\n", nb)
            if om:
                nb = nb[:om.end()] + f"{om.group(1)}set_country_flag = {guard}\n" + nb[om.end():]
            log["given a per-country guard"] += 1
        else:
            log["already self-guarded"] += 1
        out.append(s[pos:m.end()]); out.append(nb); pos = i - 1; n += 1
    if n:
        out.append(s[pos:]); wr(f, "".join(out)); log["files rewritten"] += 1

# verify
left = []
for f in glob.glob(f"{MOD}/events/1800_*.txt"):
    s = re.sub(r"#.*", "", rd(f))
    for m in re.finditer(r"^country_event\s*=\s*\{", s, re.M):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        b = s[m.end():i-1]
        if "fire_only_once = yes" in b and "is_triggered_only" not in b:
            tm = re.search(r"trigger\s*=\s*\{", b)
            if tm and len(set(re.findall(r"\btag = ([A-Z]{3})", b[tm.end():]))) > 1:
                left.append(re.search(r"id = (\d+)", b).group(1))
log["shared events still fire-once"] = len(left)
for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
