"""Fixes from the first playtest run, 1800-1809.

**1. HPM's 1836 setup events fire on day one.** The First Carlist War has
`trigger = { tag = SPA }` and a one-day mean time to happen, because at a 1836 start
the war had already begun and HPM wants it on the map immediately. At an 1800 start it
fires in 1800, which is how Carlist Spain appeared in 1804. Sixty-four events share
that shape: no year gate, a short trigger, and a timer under ninety days. Each gets a
`year = 1836` floor, which restores HPM's intended behaviour rather than suppressing it.

My event audit missed these because it counted `tag = SPA` as a guard. It is a country
guard, not a date guard, and an event guarded only by country with a one-day timer
fires immediately. The audit now asks the sharper question.

**2. Factories buildable in 1800.** Thirty-one of HPM's thirty-three buildings are
unlocked by a technology. Two are not: the liquor distillery and the glass factory.
They are meant as the starting industry of an 1836 world. Both now require
`mechanical_production`, so industrialisation is something to reach rather than
something you begin with -- and after the technology rollback only Britain, France,
the Batavian Republic and the United States hold it.

**3. The colonies are not in their metropole's war.** Victoria II does not drag a
vassal into its overlord's war automatically at game start; it has to be written into
the war. New Spain belongs in the Second Coalition on Spain's side, and so do the rest.

**4. Spain does not sphere its own colonies.** Vassalage and sphere membership are
separate in Victoria II. A colonial empire whose colonies sit outside its sphere is
not an empire.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# --- 1. give HPM's start-of-game events their historical date back -----------------
for f in sorted(glob.glob(f"{MOD}/events/*.txt")):
    if os.path.basename(f).startswith("1800_"): continue
    s = rd(f); out, pos, n = [], 0, 0
    # province_event as well as country_event: the Alternative ACW secession events
    # are province-scoped and were skipped entirely by the first version of this.
    for m in re.finditer(r"^(?:country|province)_event\s*=\s*\{", s, re.M):
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        b = s[m.start():i]
        if re.search(r"is_triggered_only\s*=\s*yes", b): continue
        tm = re.search(r"(trigger\s*=\s*\{)", b)
        if not tm: continue
        j = tm.end(); dd = 1
        while j < len(b) and dd:
            if b[j] == "{": dd += 1
            elif b[j] == "}": dd -= 1
            j += 1
        trg = b[tm.end():j-1]
        if re.search(r"\byear\s*=\s*\d{4}", trg): continue
        # Two shapes, and the second is the one the first playtest missed.
        #
        # A short trigger with a short timer fires at once: the First Carlist War is
        # `tag = SPA` with a one-day mean time, because at an 1836 start the war had
        # already begun.
        #
        # But a LONG trigger does too, if its conditions happen to hold. 'Return of the
        # Carlists' has a trigger of several hundred characters -- government type,
        # Basque or Catalan provinces, no existing sympathies -- and every clause of it
        # is true in 1800. It turned Spain into Carlist Spain in November 1804, and
        # because the tag changed, every event in the Peninsular War chain keyed to
        # `tag = SPA` became unreachable. Napoleon never invaded.
        #
        # So the rule is the plain one: an event naming a single country and carrying
        # no date is country flavour written for 1836, whatever its timer. There are
        # 281 of them -- the American Civil War, the Crimean War, the Berlin Congress,
        # the Great War -- and none belongs in our window.
        bare_tag = bool(re.search(r"^\s*tag\s*=\s*[A-Z]{3}\s*$", trg, re.M))
        mt = re.search(r"mean_time_to_happen\s*=\s*\{([^}]*)\}", b, re.S)
        g = mt.group(1) if mt else ""
        dm = re.search(r"\bdays\s*=\s*(\d+)", g); mm = re.search(r"\bmonths\s*=\s*(\d+)", g)
        days = int(dm.group(1)) if dm else (int(mm.group(1)) * 30 if mm else 99999)
        quick = mt and len(trg.strip()) <= 150 and days <= 90
        if not (bare_tag or quick): continue
        nb = b[:tm.end()] + "\n        year = 1836" + b[tm.end():]
        out.append(s[pos:m.start()]); out.append(nb); pos = i; n += 1
    if n:
        out.append(s[pos:]); wr(f, "".join(out))
        log["events given their 1836 date back"] += n
        log["event files touched"] += 1

# --- 1b. the same fault in HPM's decisions -----------------------------------------
# Events were only half of it. On the first clean run, Romania annexed Wallachia on
# 1 January 1800, fifty-nine years early, because `unite_moldavia_wallachia` has no
# date gate and our 1800 map -- Moldavia and Wallachia as separate Ottoman vassals,
# which is correct -- happens to satisfy it. A hundred and sixty-nine decisions that
# form, annex or release a nation have no year in their potential. They all get the
# 1836 floor HPM wrote them for; the period's own formations are ours to supply.
FORMS = re.compile(r"\b(change_tag|inherit|annex_to|release_vassal|"
                   r"change_tag_no_core_switch)\s*=")
for f in sorted(glob.glob(f"{MOD}/decisions/*.txt")):
    if os.path.basename(f).startswith("1800_"): continue
    s_ = rd(f); out, pos, n = [], 0, 0
    for m in re.finditer(r"^[ \t]+([a-z_0-9]+)\s*=\s*\{", s_, re.M):
        i = m.end(); d = 1
        while i < len(s_) and d:
            if s_[i] == "{": d += 1
            elif s_[i] == "}": d -= 1
            i += 1
        b = s_[m.end():i-1]
        if "potential" not in b or "effect" not in b: continue
        pm = re.search(r"potential\s*=\s*\{", b)
        if not pm: continue
        j = pm.end(); dd = 1
        while j < len(b) and dd:
            if b[j] == "{": dd += 1
            elif b[j] == "}": dd -= 1
            j += 1
        pot = b[pm.end():j-1]
        if re.search(r"\byear\s*=\s*\d{4}", pot): continue
        if not FORMS.search(b[j:]): continue
        nb = b[:pm.end()] + "\n\t\t\tyear = 1836" + b[pm.end():]
        out.append(s_[pos:m.end()]); out.append(nb); out.append("}")
        pos = i; n += 1
    if n:
        out.append(s_[pos:]); wr(f, "".join(out))
        log["decisions given their 1836 date back"] += n
        log["decision files touched"] += 1

# --- 2. a factory needs a technology ------------------------------------------------
# Both free buildings are attached to mechanical_production, the first tech that
# describes a mechanised works rather than a craft shop.
for f in glob.glob(f"{MOD}/technologies/*.txt"):
    s = rd(f)
    m = re.search(r"^(\s*mechanical_production\s*=\s*\{)", s, re.M)
    if not m: continue
    add = "\n        activate_building = liquor_distillery\n        activate_building = glass_factory"
    if "activate_building = liquor_distillery" in s: break
    wr(f, s[:m.end()] + add + s[m.end():])
    log["factories now needing technology"] = 2
    break

# --- 3. the colonies go to war with their metropole ---------------------------------
COLONIAL = [("SPA", ["NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR"]),
            ("NET", []), ("FRA", [])]
f = f"{MOD}/history/wars/SecondCoalition.txt"
if os.path.exists(f):
    s = rd(f)
    extra = [t for _, ts in COLONIAL for t in ts]
    add = "\n".join(f"    add_defender = {t}" for t in extra if f"add_defender = {t}" not in s)
    if add:
        s = s.replace("    add_defender = SPA",
                      "    add_defender = SPA\n"
                      "    # Spain's colonies are belligerents with her: Victoria II does not\n"
                      "    # bring a vassal into its overlord's war on its own.\n" + add)
        wr(f, s); log["colonies added to the war"] = len(extra)

# --- 4. Spain spheres its own colonies ----------------------------------------------
f = f"{MOD}/history/units/SPA_oob.txt"
if os.path.exists(f):
    s = rd(f)
    block = ""
    for t in ("NSP", "VPE", "VNG", "RDP", "CGC", "CBA", "PTR"):
        if re.search(rf"^{t}\s*=\s*\{{", s, re.M): continue
        block += (f"{t} = {{\n\tvalue = 200\n\tlevel = 5\n\tinfluence_value = 50\n"
                  f"\tmilitary_access = yes\n}}\n")
        log["colonies put in Spain's sphere"] += 1
    if block:
        wr(f, "# Spain's colonies are in her sphere. Vassalage and sphere membership are\n"
              "# separate things in Victoria II, and a colonial empire whose colonies sit\n"
              "# outside its sphere is not one.\n\n" + block + "\n" + s.lstrip("\n"))
# Portugal gets no sphere. Victoria II gives spheres only to Great Powers, and
# Portugal in 1800 is a British client, not a Great Power -- it is in Britain's own
# sphere. Brazil is already bound to it as a vassal in history/diplomacy, which is the
# relationship that actually describes the thing.

for k, v in sorted(log.items()): print(f"  {k:<40}{v}")
