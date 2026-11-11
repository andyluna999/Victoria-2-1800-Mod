"""Can every event we wrote actually fire?

Playtesting found the last four bugs, and each took a full run to surface. The Carlist
one took two. Every one of them was a *reachability* failure that was visible in the
files: an event keyed to a tag that stops existing, a chain whose second link waits on
a flag nothing sets, a country-scoped effect on land the country does not own.

This checks the chains as a graph instead of as a playthrough.

  **Orphan requirements.** An event gated on `has_global_flag = X` where nothing in
  the mod ever sets X. The chain is dead from that link on, silently.

  **Orphan events.** A `country_event = N` that calls an id nothing defines, or an
  `is_triggered_only` event that nothing calls. Both are halves of a broken chain.

  **Tag survival.** An event keyed to `tag = SPA` in 1807 assumes Spain is still SPA
  in 1807. Anything that can change or annex that tag earlier breaks every event after
  it. This is what made the whole Peninsular War unreachable.

  **Window arithmetic.** An event with a mean time to happen longer than the window its
  year gate allows will often simply not fire. San Ildefonso had a nine-month mean in a
  twelve-month window: about a one-in-four chance of never happening.

It reports; it does not rewrite.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, glob, os, collections, sys

MOD = _BUILD
def rd(p): return re.sub(r"#.*", "", open(p, encoding="cp1252", errors="replace").read())

OURS = sorted(glob.glob(f"{MOD}/events/1800_*.txt"))
ALL = sorted(glob.glob(f"{MOD}/events/*.txt"))
findings = []

def top_of(block, name):
    """The named sub-block's text, and only its depth-zero lines.

    A nested `tag = TUR` inside some other country's scope is not what the event is
    keyed to. Reading it as such reported the Porte and three treasury events as
    unreachable when they are fine.
    """
    m = re.search(rf"\b{name}\s*=\s*\{{", block)
    if not m: return ""
    i = m.end(); d = 1
    while i < len(block) and d:
        if block[i] == "{": d += 1
        elif block[i] == "}": d -= 1
        i += 1
    inner = block[m.end():i-1]
    out, depth = [], 0
    for line in inner.split("\n"):
        if depth == 0: out.append(line)
        depth += line.count("{") - line.count("}")
    return "\n".join(out)

def blocks(text):
    for m in re.finditer(r"^(?:country|province)_event\s*=\s*\{", text, re.M):
        i = m.end(); d = 1
        while i < len(text) and d:
            if text[i] == "{": d += 1
            elif text[i] == "}": d -= 1
            i += 1
        yield text[m.end():i-1]

ours, every = {}, {}
for f in ALL:
    mine = os.path.basename(f).startswith("1800_")
    for b in blocks(rd(f)):
        m = re.search(r"\bid\s*=\s*(\d+)", b)
        if not m: continue
        every[m.group(1)] = (os.path.basename(f), b)
        if mine: ours[m.group(1)] = (os.path.basename(f), b)

# also read decisions, which set and test flags too
dec_text = "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/*.txt"))
all_text = "\n".join(rd(f) for f in ALL) + dec_text

# --- 1. flags required but never set ------------------------------------------------
set_flags = set(re.findall(r"set_(?:global|country)_flag\s*=\s*(\w+)", all_text))
orphan = collections.Counter()
for eid, (f, b) in ours.items():
    for fl in re.findall(r"has_(?:global|country)_flag\s*=\s*(\w+)", b):
        if fl not in set_flags: orphan[f"{f} #{eid} waits on {fl}"] += 1
if orphan:
    findings.append(("HIGH", "events waiting on a flag nothing sets", list(orphan)[:8]))

# --- 2. calls to events that do not exist, and events nothing calls -------------------
missing, uncalled = [], []
called = set(re.findall(r"country_event\s*=\s*(?:\{\s*id\s*=\s*)?(\d+)", all_text))
called |= set(re.findall(r"province_event\s*=\s*(?:\{\s*id\s*=\s*)?(\d+)", all_text))
for eid, (f, b) in ours.items():
    for c in re.findall(r"(?:country|province)_event\s*=\s*(?:\{\s*id\s*=\s*)?(\d+)", b):
        if c not in every: missing.append(f"{f} #{eid} calls #{c}")
    if re.search(r"is_triggered_only\s*=\s*yes", b) and eid not in called:
        uncalled.append(f"{f} #{eid}")
if missing:
    findings.append(("HIGH", "events calling an id that does not exist", missing[:8]))
if uncalled:
    findings.append(("HIGH", "is_triggered_only events that nothing calls", uncalled[:8]))

# --- 3. does the tag survive to the date? ---------------------------------------------
# Anything that can turn tag X into something else before our event's year.
becomes = collections.defaultdict(list)
for f in ALL + glob.glob(f"{MOD}/decisions/*.txt"):
    t = rd(f)
    for m in re.finditer(r"^(?:country|province)_event\s*=\s*\{", t, re.M):
        i = m.end(); d = 1
        while i < len(t) and d:
            if t[i] == "{": d += 1
            elif t[i] == "}": d -= 1
            i += 1
        b = t[m.end():i-1]
        tg = re.search(r"^\s*tag\s*=\s*([A-Z]{3})\s*$", top_of(b, "trigger"), re.M)
        if not tg: continue
        if not re.search(r"\b(change_tag|annex_to)\s*=", b): continue
        yr = re.findall(r"\byear\s*=\s*(\d{4})", b)
        becomes[tg.group(1)].append((min(map(int, yr)) if yr else 0,
                                     os.path.basename(f)))
risky = []
for eid, (f, b) in ours.items():
    trg = top_of(b, "trigger")
    tg = re.search(r"^\s*tag\s*=\s*([A-Z]{3})\s*$", trg, re.M)
    yr = re.search(r"\byear\s*=\s*(\d{4})", trg)
    if not tg or not yr: continue
    # An event that guards on independence is not orphaned by an earlier tag change:
    # if the country already went its own way, the question is moot and the event is
    # meant not to fire. The 1820 crisis is exactly that.
    if "h18c_independent" in trg: continue
    for when, src in becomes.get(tg.group(1), []):
        if when < int(yr.group(1)):
            risky.append(f"{f} #{eid} needs {tg.group(1)} in {yr.group(1)}, "
                         f"but {src} can change that tag from {when or 'any year'}")
if risky:
    findings.append(("HIGH", "our events keyed to a tag that can disappear first",
                     sorted(set(risky))[:8]))

# --- 4. will it fire inside its window? -------------------------------------------------
thin = []
for eid, (f, b) in ours.items():
    yrs = [int(y) for y in re.findall(r"\byear\s*=\s*(\d{4})", b)]
    if len(yrs) < 2: continue
    months = (max(yrs) - min(yrs)) * 12
    mt = re.search(r"mean_time_to_happen\s*=\s*\{([^}]*)\}", b, re.S)
    if not mt: continue
    g = mt.group(1)
    mm = re.search(r"\bmonths\s*=\s*(\d+)", g); dm = re.search(r"\bdays\s*=\s*(\d+)", g)
    mean = int(mm.group(1)) if mm else (int(dm.group(1)) / 30 if dm else 0)
    if mean and months and mean > months * 0.5:
        miss = (1 - 1 / mean) ** months if mean > 1 else 0
        thin.append(f"{f} #{eid}: mean {mean:g} months in a {months}-month window "
                    f"(~{round(miss*100)}% chance it never fires)")
if thin:
    findings.append(("MED", "events that may not fire inside their own window", thin[:8]))

# --- 5. do the wars we declare name things the game knows? ----------------------------
cbs = set(re.findall(r"^\t?([a-z_]+)\s*=\s*\{",
                     rd(f"{MOD}/common/cb_types.txt"), re.M))
tags = set(re.findall(r"^\s*([A-Z]{3})\s*=", rd(f"{MOD}/common/countries.txt"), re.M))
badwar = []
for eid, (f, b) in ours.items():
    for cb in re.findall(r"casus_belli\s*=\s*(\w+)", b):
        if cb not in cbs: badwar.append(f"{f} #{eid} uses casus belli {cb}")
    # THIS, FROM and PREV are scope keywords, not country tags
    for tgt in re.findall(r"target\s*=\s*([A-Z]{3,4})\b", b):
        if tgt in ("THIS", "FROM", "PREV", "THI"): continue
        if tgt not in tags: badwar.append(f"{f} #{eid} declares war on {tgt}")
if badwar:
    findings.append(("HIGH", "wars naming a casus belli or country the game lacks",
                     sorted(set(badwar))[:8]))

# --- 6. a nation released by event must be born in defined territory -----------------
# `release_vassal` hands over every province the successor has a core on. For Mexico
# that is seventy-nine, including Mexico City, Veracruz, California and Guatemala,
# which turns a civil war into a handover. Our risings name the provinces each one
# actually held instead.
born = []
for eid, (f, b) in ours.items():
    # `release_vassal = THIS` frees the country in scope from its overlord; it does
    # not create a nation, and it is how a viceroyalty stops being Madrid's satellite
    # when its own republic rises.
    for tg in re.findall(r"release_vassal\s*=\s*([A-Z]{3,4})", b):
        if tg in ("THIS", "FROM", "PREV"): continue
        born.append(f"{f} #{eid} releases {tg} with all its cores")
if born:
    findings.append(("MED", "nations released with every province they core",
                     sorted(set(born))[:6]))

# --- 7. every viceroyalty has the same four roads out --------------------------------
# Colony, junta, autonomous kingdom, independence -- and a negotiated road as well as a
# violent one. Mexico had Iguala for two patches before the others had their own, which
# made New Spain the only viceroyalty worth playing.
VICEROYALTIES = {"NSP", "VPE", "VNG", "RDP", "CGC"}
# Three of the four roads are events now rather than menu items, so this reads both.
dec_text = "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/1800_*.txt")
                     + glob.glob(f"{MOD}/events/1800_Four_Moments.txt")
                     + glob.glob(f"{MOD}/events/1800_Autonomous_Kingdom.txt"))
roads = collections.defaultdict(set)
# Decisions are indented blocks; events are whole `country_event = {` blocks with the
# tag in the trigger and the flag in an option. Scan for both shapes.
_blocks = []
for _m in re.finditer(r"^[ \t]+([a-z_0-9]+)\s*=\s*\{|^country_event\s*=\s*\{",
                      dec_text, re.M):
    _i = _m.end(); _d = 1
    while _i < len(dec_text) and _d:
        if dec_text[_i] == "{": _d += 1
        elif dec_text[_i] == "}": _d -= 1
        _i += 1
    _blocks.append(dec_text[_m.end():_i-1])
for b in _blocks:
    for tg in VICEROYALTIES:
        if not re.search(rf"\btag = {tg}\b", b): continue
        if "h18c_junta_governs" in b and "set_country_flag" in b: roads[tg].add("junta")
        if "h18c_autonomous" in b and "set_country_flag" in b: roads[tg].add("autonomy")
        if "h18_an_american_republic" in b: roads[tg].add("republic")
        if "h18_plan_de_iguala" in b: roads[tg].add("negotiated")
short = [f"{t} lacks {sorted({'junta','autonomy','republic','negotiated'} - roads[t])}"
         for t in sorted(VICEROYALTIES)
         if {"junta", "autonomy", "republic", "negotiated"} - roads[t]]
if short:
    findings.append(("MED", "viceroyalties without every road out", short))

# --- 8. no chain may die because one roll was missed ----------------------------------
# The Mutiny at Aranjuez had a window of exactly 1808 and never came up, and Bayonne,
# the colonies learning the King was a prisoner, Iturrigaray and the French invasion of
# Spain all died with it. An event something else waits on needs room to be late.
narrow = []
for eid, (f, b) in ours.items():
    if re.search(r"is_triggered_only\s*=\s*yes", b): continue
    yrs = [int(y) for y in re.findall(r"year\s*=\s*(\d{4})", b)]
    if len(yrs) < 2: continue
    sets = set(re.findall(r"set_(?:global|country)_flag\s*=\s*(\w+)", b))
    waited_on = any(f"has_global_flag = {fl}" in "".join(x[1] for x in ours.values())
                    or f"has_country_flag = {fl}" in "".join(x[1] for x in ours.values())
                    for fl in sets)
    if waited_on and (max(yrs) - min(yrs)) < 5:
        narrow.append(f"{f} #{eid}: {min(yrs)}-{max(yrs)}, and other events wait on it")
if narrow:
    findings.append(("MED", "chained events with too little room to be late",
                     sorted(set(narrow))[:6]))

# --- 9. no peaceful shortcut out of the empire ----------------------------------------
# ai_will_do is a weight, not a gate: the AI takes any decision whose `allow` is met,
# whatever the weight says. Five negotiated-independence decisions were gated only by
# weight, so whole viceroyalties converted with no war at all -- Colombia, Peru and
# Argentina in one run. A decision that change_tags a viceroyalty and declares no war
# must require the country to have already broken with Madrid.
dec_all = "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/1800_*.txt"))
shortcut = []
for m in re.finditer(r"^\t([a-z_0-9]+)\s*=\s*\{", dec_all, re.M):
    i = m.end(); d = 1
    while i < len(dec_all) and d:
        if dec_all[i] == "{": d += 1
        elif dec_all[i] == "}": d -= 1
        i += 1
    b = dec_all[m.end():i-1]
    if "change_tag" not in b: continue
    if "war = {" in b: continue            # it fights for it, fine
    am = re.search(r"allow\s*=\s*\{", b)
    if not am: continue
    j = am.end(); dd = 1
    while j < len(b) and dd:
        if b[j] == "{": dd += 1
        elif b[j] == "}": dd -= 1
        j += 1
    allow = b[am.end():j-1]
    if not any(k in allow for k in ("h18c_junta_governs", "h18c_autonomous",
                                    "h18c_civil_war")):
        shortcut.append(m.group(1))
if shortcut:
    findings.append(("HIGH", "decisions that convert a viceroyalty with no war and "
                     "no prior break with Madrid", sorted(set(shortcut))[:6]))

# --- 10. the period must end ----------------------------------------------------------
# A beginning and a middle and no end is not a scenario. Whatever happens to Napoleon
# there has to be a Congress: Vienna if he loses, Paris if he wins, and a peace of
# exhaustion if neither. The last is the one that matters -- it is the backstop for
# every timeline where the wars simply petered out.
arc = "\n".join(rd(f) for f in glob.glob(f"{MOD}/events/1800_Napoleonic*.txt"))
endings = len(re.findall(r"set_global_flag = h18_the_congress_has_met", arc))
backstop = bool(re.search(r"year = 182\d", arc))
if endings < 3:
    findings.append(("HIGH", "the Napoleonic period has fewer than three endings",
                     [f"{endings} found; needs victory, defeat and exhaustion"]))
if not backstop:
    findings.append(("HIGH", "the period has no late backstop ending",
                     ["nothing fires if the wars peter out"]))

# --- 11. the AI must fight for it ------------------------------------------------------
# A decision that change_tags an entire viceroyalty converts the whole territory at a
# stroke. For a player that is a legitimate choice -- the viceroy declaring for the
# republic. For the AI it skips the civil war entirely, which is why whole viceroyalties
# kept turning into republics with no fighting over three playtests. Such a decision
# must carry ai_will_do = 0, or be gated on a prior break AND fight for it.
whole = []
for m in re.finditer(r"^\t([a-z_0-9]+)\s*=\s*\{", dec_all, re.M):
    i = m.end(); d = 1
    while i < len(dec_all) and d:
        if dec_all[i] == "{": d += 1
        elif dec_all[i] == "}": d -= 1
        i += 1
    b = dec_all[m.end():i-1]
    if "change_tag" not in b: continue
    if not re.search(r"\btag = (NSP|VPE|VNG|RDP|CGC|CBA|PTR)\b", b): continue
    aw = re.search(r"ai_will_do\s*=\s*\{\s*factor\s*=\s*([\d.]+)", b)
    if aw and float(aw.group(1)) == 0: continue          # player only, fine
    # otherwise it must be earned: a prior break AND Spain unable to answer
    if all(k in b for k in ("h18c_junta_governs", "h18_riego_cancels_the_expedition")):
        continue
    whole.append(m.group(1))
if whole:
    findings.append(("HIGH", "the AI can convert a whole viceroyalty without fighting",
                     sorted(set(whole))[:6]))

# --- 12. one event per moment ----------------------------------------------------------
# Two Grito de Dolores fired in one playthrough, one with the painting and one without,
# because the rising and the civil war were written as separate events with the same
# title. Variants of one event scoped to different countries are fine -- only one can
# fire per country -- so this looks for two events with the same title that the SAME
# country could see.
bytitle = collections.defaultdict(list)
locall = "\n".join(rd(f) for f in glob.glob(f"{MOD}/localisation/2*.csv"))
names = dict(re.findall(r"^(EVTNAME\d+);([^;]*)", locall, re.M))
for eid, (f, b) in ours.items():
    t = names.get(f"EVTNAME{eid}")
    if not t: continue
    # a triggered-only event has exactly one caller, so five variants of one title
    # are five different countries' copies and nobody sees two
    if re.search(r"is_triggered_only\s*=\s*yes", b): continue
    tg = re.search(r"^\s*tag = ([A-Z]{3})\s*$", top_of(b, "trigger"), re.M)
    bytitle[(t, tg.group(1) if tg else "any")].append(eid)
twice = [f"{t} ({tg}): {ids}" for (t, tg), ids in bytitle.items() if len(ids) > 1]
if twice:
    findings.append(("MED", "one country can see the same event title twice",
                     sorted(twice)[:6]))

# --- 13. no single event may gate the whole ending --------------------------------
# Every road to a Congress ran through the Russian campaign, and the Russian campaign
# required France to be at peace in 1812 -- which it never is. A run reached 1817 with
# Austerlitz, Pressburg, Jena, Tilsit and Schonbrunn all fired and no settlement of any
# kind, because one unreachable event stood in front of all three endings.
arc2 = "\n".join(rd(f) for f in glob.glob(f"{MOD}/events/1800_Napoleonic*.txt"))
ends = []
for m in re.finditer(r"id = (\d+)(.*?)(?:mean_time|is_triggered)", arc2, re.S):
    if "h18_the_congress_has_met" not in m.group(2): continue
    # a flag inside a NOT is how each ending excludes the others, not a prerequisite
    body = re.sub(r"NOT\s*=\s*\{[^{}]*\}", "", m.group(2))
    ends.append(set(re.findall(r"has_global_flag = (\w+)", body)))
if ends:
    common = set.intersection(*ends) if len(ends) > 1 else set()
    if common:
        findings.append(("HIGH", "every ending waits on the same flag",
                         [f"all {len(ends)} endings require {sorted(common)}"]))

# --- 14. a settler rises only for a nation whose primary culture is his -------------
# `nationalist_rebels` carries `independence = culture`. Texas was primary mestizo, so
# the Anglo settlers the filibuster chain spends forty years delivering had no nation
# to rise for and the whole thing ended in nothing.
fil = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil):
    releases = set(re.findall(r"set_global_flag = h18_(\w+)_declared", rd(fil)))
    wrong = []
    for tg in sorted(x.upper() for x in releases):
        g = glob.glob(f"{MOD}/history/countries/{tg} - *.txt")
        if not g: continue
        h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(g[0]))[0]
        p_ = re.search(r"^primary_culture\s*=\s*(\w+)", h, re.M)
        if not p_ or p_.group(1) not in ("yankee", "dixie", "texan"):
            wrong.append(f"{tg} primary is {p_.group(1) if p_ else '?'}")
    if wrong:
        findings.append(("HIGH", "a filibuster republic its settlers cannot rise for",
                         wrong))

# --- 15. a migration wave needs people at its source ----------------------------------
# move_pop walks a pop from one province to another, so a wave whose source province
# has no settlers of the right culture moves nothing. The whole frontier chain is a
# relay: each band draws from the one behind it, and an empty link breaks everything
# downstream of it.
fil = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil):
    txt = rd(fil)
    seeded = set()
    for _f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
        _t = re.sub(r"#.*", "", rd(_f))
        for _pm in re.finditer(r"^(\d+)\s*=\s*\{", _t, re.M):
            _i = _pm.end(); _d = 1
            while _i < len(_t) and _d:
                if _t[_i] == "{": _d += 1
                elif _t[_i] == "}": _d -= 1
                _i += 1
            if re.search(r"culture = (dixie|yankee)", _t[_pm.end():_i-1]):
                seeded.add(int(_pm.group(1)))
    # the first link of the relay must be seeded; later links are fed by earlier waves
    fed = set(int(x) for x in re.findall(r"move_pop = (\d+)", txt))
    dry = []
    for m in re.finditer(r"(\d+) = \{\s*random_pop", txt):
        src = int(m.group(1))
        if src not in seeded and src not in fed:
            dry.append(str(src))
    if dry:
        findings.append(("HIGH", "a migration wave draws from a province with no settlers",
                         sorted(set(dry))[:8]))
    # a band that draws from itself walks people out of a province and back into it
    selfmove = []
    for m in re.finditer(r"(\d+) = \{\s*random_pop.*?move_pop = (\d+)", txt, re.S):
        if m.group(1) == m.group(2):
            selfmove.append(m.group(1))
    if selfmove:
        findings.append(("HIGH", "a migration wave moves a pop into its own province",
                         sorted(set(selfmove))[:8]))

# --- 16. a viceroyalty must be beaten, not merely born against -----------------------
# Colombia was born holding Bogota, which is New Granada's capital, so the test for
# "the republic holds the viceregal capital" was true the instant the republic
# existed. New Granada dissolved nine weeks after the rising, without a battle.
war_f = f"{MOD}/events/1800_Independence_War.txt"
civ_f = f"{MOD}/events/1800_Civil_Wars.txt"
if os.path.exists(war_f) and os.path.exists(civ_f):
    civ = rd(civ_f)
    bornwith = collections.defaultdict(set)
    for m in re.finditer(r"(\d+) = \{ secede_province = ([A-Z]{3}) add_core", civ):
        bornwith[m.group(2)].add(int(m.group(1)))
    wt = re.sub(r"#.*", "", rd(war_f))
    clashes = []
    for m in re.finditer(r"id = \d+(.*?)mean_time", wt, re.S):
        tg = re.search(r"tag = ([A-Z]{3})", m.group(1))
        if not tg: continue
        need = {int(x) for x in re.findall(r"(\d+) = \{ controlled_by = THIS \}", m.group(1))}
        overlap = need & bornwith.get(tg.group(1), set())
        if overlap:
            clashes.append(f"{tg.group(1)} is handed {sorted(overlap)} and must take it")
    if clashes:
        findings.append(("HIGH", "a republic wins by holding what it was given", clashes))

# --- 17. a defender goal must not be an annexation ----------------------------------
# A defender goal in Victoria II applies against the war LEADER. With `call_ally` the
# leader becomes the overlord, so `annex_core_country` -- which carries po_annex --
# made the republics' war aim the annexation of Spain itself. Chile conquered the
# peninsula, and Peru and Chile never resolved at all, because a war on those terms
# cannot be concluded.
annexgoal = []
for eid, (f, b) in ours.items():
    for m in re.finditer(r"defender_goal\s*=\s*\{\s*casus_belli\s*=\s*(\w+)", b):
        if "annex" in m.group(1) or "conquest" in m.group(1):
            annexgoal.append(f"{f} #{eid} defends with {m.group(1)}")
dec_all2 = "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/1800_*.txt"))
for m in re.finditer(r"defender_goal\s*=\s*\{\s*casus_belli\s*=\s*(\w+)", dec_all2):
    if "annex" in m.group(1) or "conquest" in m.group(1):
        annexgoal.append(f"a decision defends with {m.group(1)}")
if annexgoal:
    findings.append(("HIGH", "a defender goal that annexes the war leader",
                     sorted(set(annexgoal))[:6]))

# --- 18. a viceroyalty that becomes a country stops claiming as a viceroyalty --------
# The defeat path cleared the old tag's cores; the transition decisions did not, so a
# New Spain that took the Plan of Iguala left its cores on every province -- a dead
# claim belonging to an administration nobody could restore, and a lever for any great
# power that wanted to release it.
dec_t = "\n".join(re.sub(r"#.*", "", rd(f)) for f in glob.glob(f"{MOD}/decisions/1800_*.txt"))
keep = []
for m in re.finditer(r"^[ \t]+([a-z_0-9]+)\s*=\s*\{", dec_t, re.M):
    i = m.end(); d = 1
    while i < len(dec_t) and d:
        if dec_t[i] == "{": d += 1
        elif dec_t[i] == "}": d -= 1
        i += 1
    b = dec_t[m.end():i]
    if "change_tag" not in b: continue
    if not re.search(r"all_core = \{ remove_core = [A-Z]{3} \}", b):
        keep.append(m.group(1))
if keep:
    findings.append(("HIGH", "a transition that leaves the old country's cores behind",
                     sorted(set(keep))[:8]))

# --- 19. Hispaniola is not part of Louisiana -----------------------------------------
# The Purchase was written as "every French-cored province in North America", and
# Victoria II counts the Caribbean as North America. France owns Saint-Domingue in
# 1800, so the United States bought the island along with Louisiana and HPM granted it
# statehood in 1803 -- which is why Haiti never appeared in a single playthrough.
lou = f"{MOD}/events/1800_Louisiana.txt"
if os.path.exists(lou):
    lt = re.sub(r"#.*", "", rd(lou))
    m = re.search(r"any_owned\s*=\s*\{(.*?)secede_province = USA", lt, re.S)
    if m and not all(f"province_id = {p}" in m.group(1) for p in (2213, 2214, 2215, 2216)):
        findings.append(("HIGH", "the Louisiana Purchase can take Hispaniola",
                         ["Saint-Domingue and Santo Domingo are not excluded"]))

# --- 20. a migration must use the idiom HPM proves works -----------------------------
# HPM writes move_pop exactly one way, forty-four times: any_pop with a limit and
# nothing else. Pairing it with reduce_pop or putting it inside random_pop appears
# nowhere in three thousand events, and our waves were doing both -- so the American
# tide fired for fifty years and very likely moved nobody at all.
fil2 = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil2):
    ft = re.sub(r"#.*", "", rd(fil2))
    odd = []
    if re.search(r"reduce_pop[^{}]*move_pop", ft, re.S):
        odd.append("reduce_pop paired with move_pop")
    if re.search(r"random_pop\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*move_pop", ft, re.S):
        odd.append("move_pop inside random_pop")
    if odd:
        findings.append(("HIGH", "a migration written in an idiom HPM never uses", odd))

# --- 21. no one decision may close every frontier band ------------------------------
# Every band carried NOT = { has_country_modifier = the_border_arranged }, and that
# modifier lands on both signatories of Adams-Onis. One AI decision in 1819 therefore
# shut down the American tide for the rest of the game -- on both roads, including the
# northern one through Kansas and Oregon, which the treaty had nothing to do with.
fil3 = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil3):
    ft3 = re.sub(r"#.*", "", rd(fil3))
    bands = re.findall(r"id = (\d+)(?:(?!country_event).)*?h18_band_(\d{4})", ft3, re.S)
    blockers = collections.Counter()
    for m in re.finditer(r"id = \d+(.*?)mean_time", ft3, re.S):
        if "h18_band_" not in m.group(1): continue
        for mod in re.findall(r"NOT = \{ has_country_modifier = (\w+) \}", m.group(1)):
            blockers[mod] += 1
    shut = [f"{m} blocks {n} of the bands" for m, n in blockers.items() if n >= 4]
    if shut:
        findings.append(("HIGH", "one modifier can close every frontier band", shut))

print("=" * 74)
print("CHAIN AUDIT — can what we wrote actually happen?")
# --- 5. do the wars we declare name things the game knows? ----------------------------
cbs = set(re.findall(r"^\t?([a-z_]+)\s*=\s*\{",
                     rd(f"{MOD}/common/cb_types.txt"), re.M))
tags = set(re.findall(r"^\s*([A-Z]{3})\s*=", rd(f"{MOD}/common/countries.txt"), re.M))
badwar = []
for eid, (f, b) in ours.items():
    for cb in re.findall(r"casus_belli\s*=\s*(\w+)", b):
        if cb not in cbs: badwar.append(f"{f} #{eid} uses casus belli {cb}")
    # THIS, FROM and PREV are scope keywords, not country tags
    for tgt in re.findall(r"target\s*=\s*([A-Z]{3,4})\b", b):
        if tgt in ("THIS", "FROM", "PREV", "THI"): continue
        if tgt not in tags: badwar.append(f"{f} #{eid} declares war on {tgt}")
if badwar:
    findings.append(("HIGH", "wars naming a casus belli or country the game lacks",
                     sorted(set(badwar))[:8]))

# --- 6. a nation released by event must be born in defined territory -----------------
# `release_vassal` hands over every province the successor has a core on. For Mexico
# that is seventy-nine, including Mexico City, Veracruz, California and Guatemala,
# which turns a civil war into a handover. Our risings name the provinces each one
# actually held instead.
born = []
for eid, (f, b) in ours.items():
    # `release_vassal = THIS` frees the country in scope from its overlord; it does
    # not create a nation, and it is how a viceroyalty stops being Madrid's satellite
    # when its own republic rises.
    for tg in re.findall(r"release_vassal\s*=\s*([A-Z]{3,4})", b):
        if tg in ("THIS", "FROM", "PREV"): continue
        born.append(f"{f} #{eid} releases {tg} with all its cores")
if born:
    findings.append(("MED", "nations released with every province they core",
                     sorted(set(born))[:6]))

# --- 7. every viceroyalty has the same four roads out --------------------------------
# Colony, junta, autonomous kingdom, independence -- and a negotiated road as well as a
# violent one. Mexico had Iguala for two patches before the others had their own, which
# made New Spain the only viceroyalty worth playing.
VICEROYALTIES = {"NSP", "VPE", "VNG", "RDP", "CGC"}
# Three of the four roads are events now rather than menu items, so this reads both.
dec_text = "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/1800_*.txt")
                     + glob.glob(f"{MOD}/events/1800_Four_Moments.txt")
                     + glob.glob(f"{MOD}/events/1800_Autonomous_Kingdom.txt"))
roads = collections.defaultdict(set)
# Decisions are indented blocks; events are whole `country_event = {` blocks with the
# tag in the trigger and the flag in an option. Scan for both shapes.
_blocks = []
for _m in re.finditer(r"^[ \t]+([a-z_0-9]+)\s*=\s*\{|^country_event\s*=\s*\{",
                      dec_text, re.M):
    _i = _m.end(); _d = 1
    while _i < len(dec_text) and _d:
        if dec_text[_i] == "{": _d += 1
        elif dec_text[_i] == "}": _d -= 1
        _i += 1
    _blocks.append(dec_text[_m.end():_i-1])
for b in _blocks:
    for tg in VICEROYALTIES:
        if not re.search(rf"\btag = {tg}\b", b): continue
        if "h18c_junta_governs" in b and "set_country_flag" in b: roads[tg].add("junta")
        if "h18c_autonomous" in b and "set_country_flag" in b: roads[tg].add("autonomy")
        if "h18_an_american_republic" in b: roads[tg].add("republic")
        if "h18_plan_de_iguala" in b: roads[tg].add("negotiated")
short = [f"{t} lacks {sorted({'junta','autonomy','republic','negotiated'} - roads[t])}"
         for t in sorted(VICEROYALTIES)
         if {"junta", "autonomy", "republic", "negotiated"} - roads[t]]
if short:
    findings.append(("MED", "viceroyalties without every road out", short))

# --- 8. no chain may die because one roll was missed ----------------------------------
# The Mutiny at Aranjuez had a window of exactly 1808 and never came up, and Bayonne,
# the colonies learning the King was a prisoner, Iturrigaray and the French invasion of
# Spain all died with it. An event something else waits on needs room to be late.
narrow = []
for eid, (f, b) in ours.items():
    if re.search(r"is_triggered_only\s*=\s*yes", b): continue
    yrs = [int(y) for y in re.findall(r"year\s*=\s*(\d{4})", b)]
    if len(yrs) < 2: continue
    sets = set(re.findall(r"set_(?:global|country)_flag\s*=\s*(\w+)", b))
    waited_on = any(f"has_global_flag = {fl}" in "".join(x[1] for x in ours.values())
                    or f"has_country_flag = {fl}" in "".join(x[1] for x in ours.values())
                    for fl in sets)
    if waited_on and (max(yrs) - min(yrs)) < 5:
        narrow.append(f"{f} #{eid}: {min(yrs)}-{max(yrs)}, and other events wait on it")
if narrow:
    findings.append(("MED", "chained events with too little room to be late",
                     sorted(set(narrow))[:6]))

# --- 9. no peaceful shortcut out of the empire ----------------------------------------
# ai_will_do is a weight, not a gate: the AI takes any decision whose `allow` is met,
# whatever the weight says. Five negotiated-independence decisions were gated only by
# weight, so whole viceroyalties converted with no war at all -- Colombia, Peru and
# Argentina in one run. A decision that change_tags a viceroyalty and declares no war
# must require the country to have already broken with Madrid.
dec_all = "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/1800_*.txt"))
shortcut = []
for m in re.finditer(r"^\t([a-z_0-9]+)\s*=\s*\{", dec_all, re.M):
    i = m.end(); d = 1
    while i < len(dec_all) and d:
        if dec_all[i] == "{": d += 1
        elif dec_all[i] == "}": d -= 1
        i += 1
    b = dec_all[m.end():i-1]
    if "change_tag" not in b: continue
    if "war = {" in b: continue            # it fights for it, fine
    am = re.search(r"allow\s*=\s*\{", b)
    if not am: continue
    j = am.end(); dd = 1
    while j < len(b) and dd:
        if b[j] == "{": dd += 1
        elif b[j] == "}": dd -= 1
        j += 1
    allow = b[am.end():j-1]
    if not any(k in allow for k in ("h18c_junta_governs", "h18c_autonomous",
                                    "h18c_civil_war")):
        shortcut.append(m.group(1))
if shortcut:
    findings.append(("HIGH", "decisions that convert a viceroyalty with no war and "
                     "no prior break with Madrid", sorted(set(shortcut))[:6]))

# --- 10. the period must end ----------------------------------------------------------
# A beginning and a middle and no end is not a scenario. Whatever happens to Napoleon
# there has to be a Congress: Vienna if he loses, Paris if he wins, and a peace of
# exhaustion if neither. The last is the one that matters -- it is the backstop for
# every timeline where the wars simply petered out.
arc = "\n".join(rd(f) for f in glob.glob(f"{MOD}/events/1800_Napoleonic*.txt"))
endings = len(re.findall(r"set_global_flag = h18_the_congress_has_met", arc))
backstop = bool(re.search(r"year = 182\d", arc))
if endings < 3:
    findings.append(("HIGH", "the Napoleonic period has fewer than three endings",
                     [f"{endings} found; needs victory, defeat and exhaustion"]))
if not backstop:
    findings.append(("HIGH", "the period has no late backstop ending",
                     ["nothing fires if the wars peter out"]))

# --- 11. the AI must fight for it ------------------------------------------------------
# A decision that change_tags an entire viceroyalty converts the whole territory at a
# stroke. For a player that is a legitimate choice -- the viceroy declaring for the
# republic. For the AI it skips the civil war entirely, which is why whole viceroyalties
# kept turning into republics with no fighting over three playtests. Such a decision
# must carry ai_will_do = 0, or be gated on a prior break AND fight for it.
whole = []
for m in re.finditer(r"^\t([a-z_0-9]+)\s*=\s*\{", dec_all, re.M):
    i = m.end(); d = 1
    while i < len(dec_all) and d:
        if dec_all[i] == "{": d += 1
        elif dec_all[i] == "}": d -= 1
        i += 1
    b = dec_all[m.end():i-1]
    if "change_tag" not in b: continue
    if not re.search(r"\btag = (NSP|VPE|VNG|RDP|CGC|CBA|PTR)\b", b): continue
    aw = re.search(r"ai_will_do\s*=\s*\{\s*factor\s*=\s*([\d.]+)", b)
    if aw and float(aw.group(1)) == 0: continue          # player only, fine
    # otherwise it must be earned: a prior break AND Spain unable to answer
    if all(k in b for k in ("h18c_junta_governs", "h18_riego_cancels_the_expedition")):
        continue
    whole.append(m.group(1))
if whole:
    findings.append(("HIGH", "the AI can convert a whole viceroyalty without fighting",
                     sorted(set(whole))[:6]))

# --- 12. one event per moment ----------------------------------------------------------
# Two Grito de Dolores fired in one playthrough, one with the painting and one without,
# because the rising and the civil war were written as separate events with the same
# title. Variants of one event scoped to different countries are fine -- only one can
# fire per country -- so this looks for two events with the same title that the SAME
# country could see.
bytitle = collections.defaultdict(list)
locall = "\n".join(rd(f) for f in glob.glob(f"{MOD}/localisation/2*.csv"))
names = dict(re.findall(r"^(EVTNAME\d+);([^;]*)", locall, re.M))
for eid, (f, b) in ours.items():
    t = names.get(f"EVTNAME{eid}")
    if not t: continue
    # a triggered-only event has exactly one caller, so five variants of one title
    # are five different countries' copies and nobody sees two
    if re.search(r"is_triggered_only\s*=\s*yes", b): continue
    tg = re.search(r"^\s*tag = ([A-Z]{3})\s*$", top_of(b, "trigger"), re.M)
    bytitle[(t, tg.group(1) if tg else "any")].append(eid)
twice = [f"{t} ({tg}): {ids}" for (t, tg), ids in bytitle.items() if len(ids) > 1]
if twice:
    findings.append(("MED", "one country can see the same event title twice",
                     sorted(twice)[:6]))

# --- 13. no single event may gate the whole ending --------------------------------
# Every road to a Congress ran through the Russian campaign, and the Russian campaign
# required France to be at peace in 1812 -- which it never is. A run reached 1817 with
# Austerlitz, Pressburg, Jena, Tilsit and Schonbrunn all fired and no settlement of any
# kind, because one unreachable event stood in front of all three endings.
arc2 = "\n".join(rd(f) for f in glob.glob(f"{MOD}/events/1800_Napoleonic*.txt"))
ends = []
for m in re.finditer(r"id = (\d+)(.*?)(?:mean_time|is_triggered)", arc2, re.S):
    if "h18_the_congress_has_met" not in m.group(2): continue
    # a flag inside a NOT is how each ending excludes the others, not a prerequisite
    body = re.sub(r"NOT\s*=\s*\{[^{}]*\}", "", m.group(2))
    ends.append(set(re.findall(r"has_global_flag = (\w+)", body)))
if ends:
    common = set.intersection(*ends) if len(ends) > 1 else set()
    if common:
        findings.append(("HIGH", "every ending waits on the same flag",
                         [f"all {len(ends)} endings require {sorted(common)}"]))

# --- 14. a settler rises only for a nation whose primary culture is his -------------
# `nationalist_rebels` carries `independence = culture`. Texas was primary mestizo, so
# the Anglo settlers the filibuster chain spends forty years delivering had no nation
# to rise for and the whole thing ended in nothing.
fil = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil):
    releases = set(re.findall(r"set_global_flag = h18_(\w+)_declared", rd(fil)))
    wrong = []
    for tg in sorted(x.upper() for x in releases):
        g = glob.glob(f"{MOD}/history/countries/{tg} - *.txt")
        if not g: continue
        h = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", rd(g[0]))[0]
        p_ = re.search(r"^primary_culture\s*=\s*(\w+)", h, re.M)
        if not p_ or p_.group(1) not in ("yankee", "dixie", "texan"):
            wrong.append(f"{tg} primary is {p_.group(1) if p_ else '?'}")
    if wrong:
        findings.append(("HIGH", "a filibuster republic its settlers cannot rise for",
                         wrong))

# --- 15. a migration wave needs people at its source ----------------------------------
# move_pop walks a pop from one province to another, so a wave whose source province
# has no settlers of the right culture moves nothing. The whole frontier chain is a
# relay: each band draws from the one behind it, and an empty link breaks everything
# downstream of it.
fil = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil):
    txt = rd(fil)
    seeded = set()
    for _f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
        _t = re.sub(r"#.*", "", rd(_f))
        for _pm in re.finditer(r"^(\d+)\s*=\s*\{", _t, re.M):
            _i = _pm.end(); _d = 1
            while _i < len(_t) and _d:
                if _t[_i] == "{": _d += 1
                elif _t[_i] == "}": _d -= 1
                _i += 1
            if re.search(r"culture = (dixie|yankee)", _t[_pm.end():_i-1]):
                seeded.add(int(_pm.group(1)))
    # the first link of the relay must be seeded; later links are fed by earlier waves
    fed = set(int(x) for x in re.findall(r"move_pop = (\d+)", txt))
    dry = []
    for m in re.finditer(r"(\d+) = \{\s*random_pop", txt):
        src = int(m.group(1))
        if src not in seeded and src not in fed:
            dry.append(str(src))
    if dry:
        findings.append(("HIGH", "a migration wave draws from a province with no settlers",
                         sorted(set(dry))[:8]))
    # a band that draws from itself walks people out of a province and back into it
    selfmove = []
    for m in re.finditer(r"(\d+) = \{\s*random_pop.*?move_pop = (\d+)", txt, re.S):
        if m.group(1) == m.group(2):
            selfmove.append(m.group(1))
    if selfmove:
        findings.append(("HIGH", "a migration wave moves a pop into its own province",
                         sorted(set(selfmove))[:8]))

# --- 16. a viceroyalty must be beaten, not merely born against -----------------------
# Colombia was born holding Bogota, which is New Granada's capital, so the test for
# "the republic holds the viceregal capital" was true the instant the republic
# existed. New Granada dissolved nine weeks after the rising, without a battle.
war_f = f"{MOD}/events/1800_Independence_War.txt"
civ_f = f"{MOD}/events/1800_Civil_Wars.txt"
if os.path.exists(war_f) and os.path.exists(civ_f):
    civ = rd(civ_f)
    bornwith = collections.defaultdict(set)
    for m in re.finditer(r"(\d+) = \{ secede_province = ([A-Z]{3}) add_core", civ):
        bornwith[m.group(2)].add(int(m.group(1)))
    wt = re.sub(r"#.*", "", rd(war_f))
    clashes = []
    for m in re.finditer(r"id = \d+(.*?)mean_time", wt, re.S):
        tg = re.search(r"tag = ([A-Z]{3})", m.group(1))
        if not tg: continue
        need = {int(x) for x in re.findall(r"(\d+) = \{ controlled_by = THIS \}", m.group(1))}
        overlap = need & bornwith.get(tg.group(1), set())
        if overlap:
            clashes.append(f"{tg.group(1)} is handed {sorted(overlap)} and must take it")
    if clashes:
        findings.append(("HIGH", "a republic wins by holding what it was given", clashes))

# --- 17. a defender goal must not be an annexation ----------------------------------
# A defender goal in Victoria II applies against the war LEADER. With `call_ally` the
# leader becomes the overlord, so `annex_core_country` -- which carries po_annex --
# made the republics' war aim the annexation of Spain itself. Chile conquered the
# peninsula, and Peru and Chile never resolved at all, because a war on those terms
# cannot be concluded.
annexgoal = []
for eid, (f, b) in ours.items():
    for m in re.finditer(r"defender_goal\s*=\s*\{\s*casus_belli\s*=\s*(\w+)", b):
        if "annex" in m.group(1) or "conquest" in m.group(1):
            annexgoal.append(f"{f} #{eid} defends with {m.group(1)}")
dec_all2 = "\n".join(rd(f) for f in glob.glob(f"{MOD}/decisions/1800_*.txt"))
for m in re.finditer(r"defender_goal\s*=\s*\{\s*casus_belli\s*=\s*(\w+)", dec_all2):
    if "annex" in m.group(1) or "conquest" in m.group(1):
        annexgoal.append(f"a decision defends with {m.group(1)}")
if annexgoal:
    findings.append(("HIGH", "a defender goal that annexes the war leader",
                     sorted(set(annexgoal))[:6]))

# --- 18. a viceroyalty that becomes a country stops claiming as a viceroyalty --------
# The defeat path cleared the old tag's cores; the transition decisions did not, so a
# New Spain that took the Plan of Iguala left its cores on every province -- a dead
# claim belonging to an administration nobody could restore, and a lever for any great
# power that wanted to release it.
dec_t = "\n".join(re.sub(r"#.*", "", rd(f)) for f in glob.glob(f"{MOD}/decisions/1800_*.txt"))
keep = []
for m in re.finditer(r"^[ \t]+([a-z_0-9]+)\s*=\s*\{", dec_t, re.M):
    i = m.end(); d = 1
    while i < len(dec_t) and d:
        if dec_t[i] == "{": d += 1
        elif dec_t[i] == "}": d -= 1
        i += 1
    b = dec_t[m.end():i]
    if "change_tag" not in b: continue
    if not re.search(r"all_core = \{ remove_core = [A-Z]{3} \}", b):
        keep.append(m.group(1))
if keep:
    findings.append(("HIGH", "a transition that leaves the old country's cores behind",
                     sorted(set(keep))[:8]))

# --- 19. Hispaniola is not part of Louisiana -----------------------------------------
# The Purchase was written as "every French-cored province in North America", and
# Victoria II counts the Caribbean as North America. France owns Saint-Domingue in
# 1800, so the United States bought the island along with Louisiana and HPM granted it
# statehood in 1803 -- which is why Haiti never appeared in a single playthrough.
lou = f"{MOD}/events/1800_Louisiana.txt"
if os.path.exists(lou):
    lt = re.sub(r"#.*", "", rd(lou))
    m = re.search(r"any_owned\s*=\s*\{(.*?)secede_province = USA", lt, re.S)
    if m and not all(f"province_id = {p}" in m.group(1) for p in (2213, 2214, 2215, 2216)):
        findings.append(("HIGH", "the Louisiana Purchase can take Hispaniola",
                         ["Saint-Domingue and Santo Domingo are not excluded"]))

# --- 20. a migration must use the idiom HPM proves works -----------------------------
# HPM writes move_pop exactly one way, forty-four times: any_pop with a limit and
# nothing else. Pairing it with reduce_pop or putting it inside random_pop appears
# nowhere in three thousand events, and our waves were doing both -- so the American
# tide fired for fifty years and very likely moved nobody at all.
fil2 = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil2):
    ft = re.sub(r"#.*", "", rd(fil2))
    odd = []
    if re.search(r"reduce_pop[^{}]*move_pop", ft, re.S):
        odd.append("reduce_pop paired with move_pop")
    if re.search(r"random_pop\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*move_pop", ft, re.S):
        odd.append("move_pop inside random_pop")
    if odd:
        findings.append(("HIGH", "a migration written in an idiom HPM never uses", odd))

# --- 21. no one decision may close every frontier band ------------------------------
# Every band carried NOT = { has_country_modifier = the_border_arranged }, and that
# modifier lands on both signatories of Adams-Onis. One AI decision in 1819 therefore
# shut down the American tide for the rest of the game -- on both roads, including the
# northern one through Kansas and Oregon, which the treaty had nothing to do with.
fil3 = f"{MOD}/events/1800_Filibusters.txt"
if os.path.exists(fil3):
    ft3 = re.sub(r"#.*", "", rd(fil3))
    bands = re.findall(r"id = (\d+)(?:(?!country_event).)*?h18_band_(\d{4})", ft3, re.S)
    blockers = collections.Counter()
    for m in re.finditer(r"id = \d+(.*?)mean_time", ft3, re.S):
        if "h18_band_" not in m.group(1): continue
        for mod in re.findall(r"NOT = \{ has_country_modifier = (\w+) \}", m.group(1)):
            blockers[mod] += 1
    shut = [f"{m} blocks {n} of the bands" for m, n in blockers.items() if n >= 4]
    if shut:
        findings.append(("HIGH", "one modifier can close every frontier band", shut))

print("=" * 74)
if not findings:
    print("\n  no findings\n")
for sev, title, items in findings:
    print(f"\n[{sev}] {title}")
    for i in items: print(f"      {i}")
_ourflags = set()
for _f, _b in ours.values():
    _ourflags |= set(re.findall(r"set_(?:global|country)_flag\s*=\s*(\w+)", _b))
print(f"\n  our events: {len(ours)}   flags they set: {len(_ourflags)}")
sys.exit(0)
