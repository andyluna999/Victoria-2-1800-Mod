"""Read the world's current state from the mod itself.

Three bugs in this project came from reading ownership or population out of
`work/world_live.json`. That file is regenerated *after* a build, so a script that
consults it is looking at the previous run: Europe was nearly halved twice, Britain
kept thirty-seven Australian provinces, and Norfolk Island changed hands on every
alternate build. Anything that makes a decision about the current state must read the
files it is about to edit, which is what this does.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"

def province_state():
    """owner, controller and cores per province id, read from history/provinces."""
    owner, controller, cores, path = {}, {}, {}, {}
    for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
        pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
        head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                        open(f, encoding="cp1252", errors="replace").read())[0]
        m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
        owner[pid] = m.group(1) if m else ""
        m = re.search(r"^\s*controller\s*=\s*([A-Z]{3})", head, re.M)
        controller[pid] = m.group(1) if m else ""
        cores[pid] = re.findall(r"^\s*add_core\s*=\s*([A-Z]{3})", head, re.M)
        path[pid] = f
    return owner, controller, cores, path

def population():
    """total pops per province id, read from history/pops."""
    tot = collections.Counter()
    for f in glob.glob(f"{MOD}/history/pops/*/*.txt"):
        s = re.sub(r"#.*", "", open(f, encoding="cp1252", errors="replace").read())
        for pm in re.finditer(r"^(\d+)\s*=\s*\{", s, re.M):
            pid = int(pm.group(1)); i = pm.end(); d = 1
            while i < len(s) and d:
                if s[i] == "{": d += 1
                elif s[i] == "}": d -= 1
                i += 1
            tot[pid] += sum(int(x) for x in re.findall(r"size\s*=\s*(\d+)", s[pm.end():i-1]))
    return tot
