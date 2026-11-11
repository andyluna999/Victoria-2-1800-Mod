"""A country only gets the army its own file names.

New Spain shipped with thirty-six regiments in a valid, well-formed, correctly-homed
order of battle, and put nothing on the map through four rounds of diagnosis -- unit
types, brace balance, province ownership, soldier pops, accepted cultures. None of
those were the cause. Victoria II loads `history/units/TAG_oob.txt` only when the
country's own history file declares it:

    oob = "SPA_oob.txt"

Two hundred and twenty-seven of HPM's country files carry that line. The eight tags we
invented for the colonial system carried none, so the engine never opened their orders
of battle at all.
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
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

for f in sorted(glob.glob(f"{MOD}/history/countries/*.txt")):
    b = os.path.basename(f)
    if " - " not in b: continue
    tag = b.split(" - ")[0].strip()
    if not os.path.exists(f"{MOD}/history/units/{tag}_oob.txt"): continue
    s = rd(f)
    if re.search(r'^\s*oob\s*=', s, re.M): continue
    parts = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"(^\s*capital\s*=.*\n)", r"\1" + f'oob = "{tag}_oob.txt"\n',
                  head, count=1, flags=re.M)
    wr(f, head.rstrip("\n") + "\n" + tail)
    log["armies the game will now read"] += 1
    log["tags"] = log.get("tags", "") + tag + " "
for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
