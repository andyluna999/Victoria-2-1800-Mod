"""Audit HPM's own events against an 1800 start.

Three thousand events were written for a game beginning in 1836. Moving the start back
thirty-six years does not break them loudly -- Victoria II will load every one -- but
some now describe a world that no longer exists, and they will fire anyway.

Four things go wrong, in rising order of how badly:

1. **An event fires before its premise.** Anything gated only on a date between 1836
   and the end is unreachable now, which is harmless. Anything gated on a year we have
   already passed, or on no year at all, can fire in 1801 on an assumption from 1836.
2. **An event names a country that does not exist yet.** Belgium, Greece, Germany,
   Italy. HPM guards most of these with `exists`, but not all.
3. **An event names a province somebody else now owns.** Our map moved 600-odd
   provinces; an event that gives Lombardy to Austria is about to give Austria
   something it already holds.
4. **An event depends on a technology nobody has.** We stripped 1,227 anachronistic
   grants, so a trigger on `post_napoleonic_thought` will not fire for anyone until
   somebody researches it.

This reports; it does not rewrite. The point is to know the size of the problem.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, json, collections, sys

MOD = _BUILD; W = _WORK
L = json.load(open(f"{W}/world_live.json"))
P = {int(k): v for k, v in L["prov"].items()}
owned = collections.defaultdict(list)
for pid, v in P.items():
    if v["o"]: owned[v["o"]].append(pid)
def rd(p): return re.sub(r"#.*", "", open(p, encoding="cp1252", errors="replace").read())

reg = rd(f"{MOD}/common/countries.txt")
TAGS = set(re.findall(r"^\s*([A-Z]{3})\s*=", reg, re.M))
src = rd(f"{MOD}/common/cultures.txt")
CULT, depth, cur = set(), 0, None
for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\{|\}", src):
    t = m.group(0)
    if t == "}": depth -= 1
    elif t == "{": depth += 1
    else:
        if depth == 1 and m.group(1) not in ("color","leader","unit","union","is_overseas","primary"):
            CULT.add(m.group(1))
        depth += 1
TECH = set()
for f in glob.glob(f"{MOD}/technologies/*.txt"):
    TECH |= set(re.findall(r"^([a-z_0-9]+)\s*=\s*\{", rd(f), re.M))
# which technologies does anybody actually start with?
START_TECH = collections.Counter()
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", rd(f))[0]
    for m in re.finditer(r"^\s*([a-z_]+)\s*=\s*1\s*$", head, re.M):
        if m.group(1) in TECH: START_TECH[m.group(1)] += 1

OURS = {os.path.basename(f) for f in glob.glob(f"{MOD}/events/1800_*.txt")}
events, byfile = [], collections.Counter()
for f in sorted(glob.glob(f"{MOD}/events/*.txt")):
    nm = os.path.basename(f)
    if nm in OURS: continue
    s = rd(f)
    # Anchor to the start of a line. Without this the scan also matches the
    # `country_event` inside an effect block, producing overlapping bodies, duplicate
    # ids, and events that look unguarded because their body is a fragment.
    for m in re.finditer(r"^(country_event|province_event)\s*=\s*\{", s, re.M):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        body = s[m.end():i-1]
        eid = re.search(r"\bid\s*=\s*(\d+)", body)
        events.append((nm, eid.group(1) if eid else "?", body))
        byfile[nm] += 1
print(f"  HPM events scanned                {len(events)} across {len(byfile)} files\n")

def trigger_of(body):
    m = re.search(r"\btrigger\s*=\s*\{", body)
    if not m: return ""
    i = m.end(); d = 1
    while i < len(body) and d:
        if body[i] == "{": d += 1
        elif body[i] == "}": d -= 1
        i += 1
    return body[m.end():i-1]

reachable, unreachable, undated = [], [], []
ghost_tag, ghost_prov, dead_tech = collections.Counter(), collections.Counter(), collections.Counter()
for nm, eid, body in events:
    trg = trigger_of(body)
    yrs = [int(y) for y in re.findall(r"\byear\s*=\s*(\d{4})", trg)]
    if not yrs: undated.append((nm, eid))
    elif max(yrs) < 1836: reachable.append((nm, eid, max(yrs)))
    else: unreachable.append((nm, eid))
    for t in set(re.findall(r"\b(?:tag|exists|owned_by|controlled_by|vassal_of|war_with|is_our_vassal)\s*=\s*([A-Z]{3})\b", trg)):
        if t in TAGS and not owned.get(t): ghost_tag[t] += 1
    for pid in set(int(x) for x in re.findall(r"\bowns\s*=\s*(\d+)", trg)):
        if pid in P and not P[pid]["o"]: ghost_prov[pid] += 1
    for tk in set(re.findall(r"^\s*([a-z_]+)\s*=\s*1\s*$", trg, re.M)):
        if tk in TECH and not START_TECH.get(tk): dead_tech[tk] += 1

print(f"  [1] events that can now fire BEFORE 1836   {len(reachable)}")
print(f"      (gated on a year we pass on the way to 1836)")
for nm, eid, y in sorted(reachable, key=lambda x: x[2])[:8]:
    print(f"        {y}  {nm} #{eid}")
print(f"\n  [2] events with NO year gate at all        {len(undated)}")
print(f"      (these are the ones that can fire in 1801 on an 1836 premise)")
print(f"\n  [3] triggers naming a country that holds nothing in 1800")
for t, n in ghost_tag.most_common(10):
    print(f"        {t} referenced in {n} triggers")
print(f"\n  [4] triggers requiring a province nobody owns")
for pid, n in ghost_prov.most_common(6):
    print(f"        {pid} {P[pid]['n']} in {n} triggers")
print(f"\n  [5] triggers on a technology nobody starts with")
for tk, n in dead_tech.most_common(8):
    print(f"        {tk} in {n} triggers")
# Refine [2]. An undated event is only dangerous if it can fire by itself: one that
# is `is_triggered_only` waits to be called by another event, and if that chain starts
# somewhere unreachable it never runs at all.
self_firing, triggered_only, no_guard = 0, 0, []
# Any condition at all counts as a guard. The first version of this list named only
# countries, provinces and flags, and so reported sixty-two events as unguarded that
# were in fact gated on `civilized`, `colonial_nation` or `has_country_modifier` --
# perfectly good systemic events that work at any date.
GUARDS = ("exists", "owns", "tag =", "has_country_flag", "has_global_flag",
          "vassal_of", "is_vassal", "war =", "revolt_percentage", "ai =",
          "civilized", "government", "is_greater_power", "primary_culture",
          "controlled_by", "owned_by", "nationalvalue", "is_culture_group",
          "religion", "capital", "has_pop_type", "badboy", "prestige",
          "literacy", "money", "part_of_sphere", "is_sphere_leader_of",
          "colonial_nation", "has_country_modifier", "has_province_modifier",
          "any_owned_province", "average_consciousness", "average_militancy",
          "invention", "technology", "is_culture", "unemployment", "rank",
          "ruling_party_ideology", "upper_house", "poor_strata", "middle_strata",
          "rich_strata", "constructing_cb", "is_disarmed", "crisis", "NOT =",
          "OR =", "AND =", "year", "month", "substate_of", "neighbour",
          "num_of_cities", "total_pops", "military_score", "industrial_score")
for nm, eid, body in events:
    trg = trigger_of(body)
    if re.search(r"\bis_triggered_only\s*=\s*yes", body):
        triggered_only += 1; continue
    if re.findall(r"\byear\s*=\s*(\d{4})", trg): continue
    self_firing += 1
    if not any(g in trg for g in GUARDS):
        no_guard.append((nm, eid, len(trg.strip())))
print(f"\n  of the {len(undated)} undated events:")
print(f"      {triggered_only} are is_triggered_only and wait to be called")
print(f"      {self_firing} can fire on their own")
print(f"      {len(no_guard)} of those have no country, province or flag guard at all")
for nm, eid, ln in sorted(no_guard, key=lambda x: x[2])[:10]:
    print(f"        {nm} #{eid}  trigger {ln} chars")

# The class the first playtest found. An event guarded only by country, with a short
# mean time to happen and no year, fires on day one. At a 1836 start that is correct
# -- the Carlist War had already begun. At 1800 it puts Carlist Spain on the map in
# 1804. The earlier version of this audit counted `tag = SPA` as a guard and missed
# all of them.
fires_at_start = []
for nm, eid, body in events:
    if re.search(r"is_triggered_only\s*=\s*yes", body): continue
    trg = trigger_of(body)
    if re.search(r"\byear\s*=\s*\d{4}", trg): continue
    # An event naming one country and carrying no date is 1836 flavour, whatever its
    # timer. The long-trigger ones matter as much as the short: 'Return of the
    # Carlists' has a trigger of several hundred characters, every clause true in
    # 1800, and it changed Spain's tag in 1804 -- which made the whole Peninsular War
    # chain, keyed to `tag = SPA`, unreachable.
    bare = bool(re.search(r"^\s*tag\s*=\s*[A-Z]{3}\s*$", trg, re.M))
    mt = re.search(r"mean_time_to_happen\s*=\s*\{([^}]*)\}", body, re.S)
    g = mt.group(1) if mt else ""
    dm = re.search(r"\bdays\s*=\s*(\d+)", g); mm = re.search(r"\bmonths\s*=\s*(\d+)", g)
    days = int(dm.group(1)) if dm else (int(mm.group(1)) * 30 if mm else 99999)
    if bare or (mt and len(trg.strip()) <= 150 and days <= 90):
        fires_at_start.append((nm, eid, days))
print(f"\n  [6] events that fire at game start with no date gate   {len(fires_at_start)}")
print("      (short trigger, timer under 90 days: these run in 1800)")
for nm, eid, dd in sorted(fires_at_start, key=lambda x: x[2])[:6]:
    print(f"        {dd:>3}d  {nm} #{eid}")

print(f"\n  events unreachable before 1836 (harmless) {len(unreachable)}")
print()
print("  " + "-" * 66)
print("  The 1800-1836 window")
print("  " + "-" * 66)
print(f"  HPM has {len(reachable)} events gated to fire in it.")
print("  Everything HPM wrote is dated 1836 or later, so the first thirty-six years")
print("  of this scenario contain no historical content but ours. That is not a bug")
print("  to fix; it is the size of the gap the narrative layer has to fill.")
