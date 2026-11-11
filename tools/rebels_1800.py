"""Rebel movements have to wait for their century.

Not one of HPM's twenty-three rebel types carries a date. At a 1836 start that is
mostly harmless, because the ideologies that drive them are gated by technology and
literacy anyway. At 1800 it is not: Carlist rebels took Spain in June 1806, twenty-seven
years before Don Carlos had a claim to press, and because that changed Spain's tag the
entire Peninsular War chain -- keyed to `tag = SPA` -- became unreachable. Napoleon
never invaded, Bayonne never happened, and Iturrigaray was never asked who governs.

The events were gated twice and it kept happening, because this was never an event. A
rebel faction winning a revolt replaces the government, and no amount of auditing
event files finds it.

The dates below are when each movement could first have existed:

  * **Carlists and Cristinos, 1833.** Ferdinand VII dies and his brother disputes his
    daughter's succession. Before that there is nothing to be a Carlist about.
  * **Pan-nationalists, 1848.** Plain nationalists are deliberately NOT dated: they
    are how a culture wins its independence, and in this period that is Caracas,
    Buenos Aires and Dolores.
  * **Socialists, 1848. Anarcho-liberals, 1848.** The year the movements became ones.
  * **Communists, 1871.** The Commune.
  * **Red Shirts, 1860.** Garibaldi sails for Sicily.
  * **Sepoys, 1857. Indian nationalists, 1885.** The Mutiny, then Congress.
  * **Boxers, 1899. Young Turks, 1908. Fascists, 1919. Partisans, 1914.**

Left alone: reactionaries, liberals, separatists, independence movements, slave
revolts and the native risings. All of those are entirely at home in 1800 -- the
French Revolution had already happened, and so had Haiti.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import re, collections

MOD = _BUILD
log = collections.Counter()
PATH = f"{MOD}/common/rebel_types.txt"

WAIT = {
    "carlist_rebels": 1833, "christino_rebels": 1833,
    # nationalist_rebels is the only type carrying `independence = culture` -- the one
    # that actually releases a nation. Gating it to 1830 would have killed Spanish
    # American independence outright, which runs from 1810 to 1826 and IS nationalist
    # rebellion. Pan-nationalism stays at 1848, because pan-Germanism and pan-Slavism
    # genuinely are later.
    "pan_nationalist_rebels": 1848,
    "socialist_rebels": 1848, "anarcho_liberal_rebels": 1848,
    "communist_rebels": 1871, "red_shirts": 1860,
    "indian_sepoys": 1857, "indian_nationalists": 1885,
    "boxer_rebels": 1899, "turkish_nationalist_rebels": 1908,
    "fascist_rebels": 1919, "partisan_rebels": 1914,
}

s = open(PATH, encoding="cp1252", errors="replace").read()
out, pos = [], 0
for m in re.finditer(r"^([a-z_]+)\s*=\s*\{", s, re.M):
    name = m.group(1)
    if name not in WAIT: continue
    i = m.end(); d = 1
    while i < len(s) and d:
        if s[i] == "{": d += 1
        elif s[i] == "}": d -= 1
        i += 1
    body = s[m.end():i-1]
    sp = re.search(r"spawn_chance\s*=\s*\{", body)
    if not sp: continue
    if "# waits for its century" in body: continue
    yr = WAIT[name]
    # The same shape the file already uses for its country conditions.
    add = (f"\n        # waits for its century\n"
           f"        modifier = {{\n            factor = 0\n"
           f"            country = {{ NOT = {{ year = {yr} }} }}\n        }}\n")
    nb = body[:sp.end()] + add + body[sp.end():]
    out.append(s[pos:m.end()]); out.append(nb); out.append("}")
    pos = i
    log["rebel types dated"] += 1
out.append(s[pos:])
if log["rebel types dated"]:
    open(PATH, "w", encoding="cp1252", errors="replace",
         newline="\n").write("".join(out))

for k, v in sorted(log.items()): print(f"  {k:<28}{v}")
print(f"  earliest now allowed            {min(WAIT.values())} (nationalists)")
