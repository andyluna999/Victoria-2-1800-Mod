"""The United States will not take Haiti, and the reason is the interesting part.

The AI kept conquering Hispaniola. Nothing in the files told it to -- no cores, no
events, no decisions. It is simply doing what a Victoria II AI does with a small,
friendless, unrecognised neighbour that has no allies, and Haiti is friendless by
design: the `pariah_republic` modifier is the whole point of that country's position.

But the historical position is the opposite of tempting, and the reason is worth
modelling rather than patching around.

The United States refused to *recognise* Haiti until 1862. Not because it did not
notice -- American merchants traded there throughout -- but because recognition meant
receiving a Black ambassador in Washington, and annexation would have meant adding
half a million free Black citizens to a republic half of whose states were slave
states. Southern senators blocked recognition for sixty years precisely because
Haiti's existence was an argument they could not afford to have. Jefferson, who had
helped Leclerc, called it a danger to be quarantined. Calhoun said the quiet part.

So the thing that protected Haiti from the United States was American slavery, and the
protection ends when slavery does. That is a better mechanic than a scripted ban: the
restriction has a cause, the cause is visible in the game state, and when a player
abolishes slavery early they inherit the option along with it.
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

GUARD = """
            # The United States will not take Hispaniola while it is a slave republic.
            # Washington refused even to recognise Haiti until 1862: recognition meant
            # receiving a Black ambassador, and annexation would have meant half a
            # million free Black citizens in a union half of whose states were slave
            # states. Southern senators blocked it for sixty years. The protection
            # ends when slavery does.
            NOT = {
                AND = {
                    THIS = { tag = USA }
                    OR = {
                        tag = HAI
                        tag = DOM
                    }
                    OR = {
                        THIS = { slavery = yes_slavery }
                        NOT = { year = 1890 }
                    }
                }
            }
"""

s = open(PATH, encoding="cp1252", errors="replace").read()
if "while it is a slave republic" not in s:
    for name in ("conquest", "colonial_conquest", "colonial_conquest_full",
                 "annex_core_country", "humiliate", "conquest_any"):
        m = re.search(rf"^{name}\s*=\s*\{{", s, re.M)
        if not m: continue
        i = m.end(); d = 1
        while i < len(s) and d:
            if s[i] == "{": d += 1
            elif s[i] == "}": d -= 1
            i += 1
        block = s[m.start():i]
        cu = re.search(r"can_use\s*=\s*\{", block)
        if not cu: continue
        nb = block[:cu.end()] + GUARD + block[cu.end():]
        s = s[:m.start()] + nb + s[i:]
        log["casus belli guarded"] += 1
    open(PATH, "w", encoding="cp1252", errors="replace", newline="\n").write(s)

t = re.sub(r"#.*", "", open(PATH, encoding="cp1252", errors="replace").read())
log["braces balance"] = t.count("{") == t.count("}")
for k, v in sorted(log.items()): print(f"  {k:<26}{v}")
