"""Spain's right of reconquest, until 1830.

Spain did not accept the loss of the Americas when it happened, and no European power
asked it to. Ferdinand VII refused to recognise a single one of the new republics for
the rest of his life; the recognitions came one at a time under his daughter, from
Mexico in 1836 through to Honduras in 1894. Until then, from Madrid's point of view,
there were no republics -- only provinces in rebellion.

HPM already gives Spain a `colonial_reconquest_cb`, but only against Cuba, Puerto Rico
and the Philippines. The mainland successors are outside it, so once Mexico or Peru
existed Spain had no legal way to attack them and the AI simply accepted the loss. That
is backwards: those are exactly the wars Spain spent the 1820s trying to fight, and
Ferdinand was still planning an expedition against Mexico in 1829 -- Barradas actually
landed at Tampico with three thousand men and surrendered to the heat and Santa Anna.

So the casus belli is extended to every mainland successor, and it expires in 1830.
After that the republics are facts, Ferdinand is dying, and a Spain that wants them
back has to use the same justifications anyone else would.

The date is not arbitrary. Barradas was the last attempt, and after it the Cortes
stopped voting money for the Americas.
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
PATH = f"{MOD}/common/cb_types.txt"
log = collections.Counter()

SUCCESSORS = ["MEX", "PEU", "CLM", "ARG", "CHL", "VNZ", "ECU", "BOL",
              "URU", "PRG", "UCA", "CAM", "GUA", "SAL", "HON", "NIC", "COS"]

s = open(PATH, encoding="cp1252", errors="replace").read()
if "the mainland republics, until 1830" not in s:
    m = re.search(r"^colonial_reconquest_cb\s*=\s*\{", s, re.M)
    if m:
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        block = s[m.start():i]
        cu = re.search(r"can_use\s*=\s*\{\s*OR\s*=\s*\{", block)
        if cu:
            add = ("\n            # the mainland republics, until 1830. Ferdinand VII\n"
                   "            # recognised none of them and was still planning an\n"
                   "            # expedition against Mexico in 1829 -- Barradas landed\n"
                   "            # at Tampico with three thousand men and surrendered to\n"
                   "            # the heat and Santa Anna. After that the Cortes stopped\n"
                   "            # voting money for the Americas.\n"
                   "            AND = {\n"
                   "                THIS = { tag = SPA }\n"
                   "                NOT = { year = 1830 }\n"
                   "                OR = {\n"
                   + "".join(f"                    tag = {t}\n" for t in SUCCESSORS)
                   + "                }\n            }\n")
            nb = block[:cu.end()] + add + block[cu.end():]
            s = s[:m.start()] + nb + s[i:]
            open(PATH, "w", encoding="cp1252", errors="replace",
                 newline="\n").write(s)
            log["successors Spain may reconquer"] = len(SUCCESSORS)

# and the AI should actually want to, while Ferdinand is alive
t = re.sub(r"#.*", "", open(PATH, encoding="cp1252", errors="replace").read())
log["braces balance"] = t.count("{") == t.count("}")
for k, v in sorted(log.items()): print(f"  {k:<34}{v}")
