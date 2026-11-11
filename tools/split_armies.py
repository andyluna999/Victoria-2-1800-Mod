"""No army larger than a corps.

Selecting New Spain crashed the game the moment its order of battle was read for the
first time. Everything in the file was valid -- the provinces existed, the pops were
there, the cultures were accepted, the unit types were fieldable, setup.log showed the
whole mod loading without a complaint.

What was wrong was the shape. HPM's largest single army anywhere is twelve regiments.
Ours had thirty-six for New Spain, forty-two for France and two hundred in a single
Qing stack, because the war-footing passes grew existing armies in place rather than
raising new ones. Nothing in the files says that is illegal and the parser accepts it
happily; the engine then tries to build a formation several times larger than anything
the game was designed around.

So armies are split into corps of at most twelve, which is both safe and better
history: a Napoleonic army was a collection of corps, not one enormous column. The
first keeps the original name and location, the rest are numbered after it and stand
in the same place.
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
MAX = 12
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

def blocks(text, kw):
    out = []
    for m in re.finditer(rf"[ \t]*{kw}[ \t]*=[ \t]*\{{", text):
        i = m.end(); d = 1
        while i < len(text) and d:
            if text[i] == "{": d += 1
            elif text[i] == "}": d -= 1
            i += 1
        out.append((m.start(), i, text[m.start():i]))
    return out

for f in sorted(glob.glob(f"{MOD}/history/units/*.txt")):
    s = rd(f)
    pieces, pos, split = [], 0, 0
    for a, b, body in blocks(s, "army"):
        regs = [r for _, _, r in blocks(body, "regiment")]
        if len(regs) <= MAX:
            continue
        name = re.search(r'name\s*=\s*"([^"]*)"', body)
        locm = re.search(r"location\s*=\s*(\d+)", body)
        base = name.group(1) if name else "Army"
        loc = locm.group(1) if locm else None
        chunks = [regs[i:i+MAX] for i in range(0, len(regs), MAX)]
        made = []
        for n, chunk in enumerate(chunks):
            nm = base if n == 0 else f"{n+1}. {base}"
            head = f'army = {{\n\tname = "{nm}"\n'
            if loc: head += f"\tlocation = {loc}\n"
            made.append(head + "\n".join(r.strip("\n") for r in chunk) + "\n}")
        pieces.append(s[pos:a]); pieces.append("\n\n".join(made)); pos = b
        split += 1
        log["armies split"] += 1
        log["corps created"] += len(chunks) - 1
    if split:
        pieces.append(s[pos:]); wr(f, "".join(pieces)); log["files rewritten"] += 1

worst = 0
for f in glob.glob(f"{MOD}/history/units/*.txt"):
    for _, _, body in blocks(rd(f), "army"):
        worst = max(worst, len(blocks(body, "regiment")))
log["largest army now"] = worst
for k, v in sorted(log.items()): print(f"  {k:<24}{v}")
