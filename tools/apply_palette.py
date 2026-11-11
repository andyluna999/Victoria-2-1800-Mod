"""Rewrite culture colours in common/cultures.txt from work/palette.json.

Handles both the cultures this project created and HPM's own, so a restyled family
is consistent whether or not the culture predates us.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re
MOD=_BUILD
PAL=json.load(open(f"{_WORK}/palette.json"))
# colours edited in the World Builder win over the generated scheme, and they are
# already keyed by engine name so no translation is needed
try:
    USER=json.load(open(f"{_WORK}/palette_user.json"))
except Exception:
    USER={}
f=f"{MOD}/common/cultures.txt"
s=open(f,encoding="cp1252",errors="replace").read()
def key(c): return re.sub(r"(?<!^)(?=[A-Z])","_",c).lower().replace("__","_")
done=missing=0
MERGED={key(c):rgb for c,rgb in PAL.items()}
MERGED.update(USER)
for k,rgb in MERGED.items():
    # some cultures carry a key before the colour (breton has primary = BRT), so allow
    # any lines in between rather than demanding colour be first
    pat=re.compile(rf"(\n\s+{re.escape(k)}\s*=\s*\{{(?:\s*\n\s*[a-z_]+\s*=\s*[A-Za-z_0-9]+)*\s*\n\s*color\s*=\s*\{{\s*)\d+\s+\d+\s+\d+(\s*\}})")
    s,n=pat.subn(lambda m: f"{m.group(1)}{rgb[0]} {rgb[1]} {rgb[2]}{m.group(2)}", s, count=1)
    if n: done+=1
    else: missing+=1
open(f,"w",encoding="cp1252",errors="replace",newline="\n").write(s)
print(f"  culture colours rewritten       {done}")
if missing: print(f"  palette entries with no culture  {missing}")
