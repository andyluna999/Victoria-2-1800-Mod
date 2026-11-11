"""Apply the second World Builder export: owner changes, and the cores that are real.

The export unowns the Saharan interior and gives Cyrenaica to the Karamanlis, both
correct. It also adds a Karamanli core to every province in Australia and New Zealand,
which is a box-select that caught the wrong continent. Those 35 are skipped.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, re, glob, os, collections
MOD = _BUILD; W = _WORK
E = json.load(open("/mnt/user-data/uploads/hpm_world_1800_1.json"))
L = json.load(open(f"{W}/world_live.json"))
P = L["prov"]   # used only for the continent of each province, never for its state
prov = {}
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    prov[int(re.match(r"(\d+)", os.path.basename(f)).group(1))] = f
log = collections.Counter()
intended = {}   # what this pass is responsible for, checked later by the sweep
for k, v in E["provinces"].items():
    pid = int(k); base = P[k]; f = prov.get(pid)
    if not f: continue
    want_owner = v["owner"] or ""
    want_cores = set(v["cores"])
    # a Karamanli core in the Pacific is a mis-click, not a claim
    if base["ct"] == "australia_new_zealand":
        want_cores -= {"KRM"}
    # Norfolk Island was settled in March 1788, six weeks after Sydney, and held as a
    # penal station until 1814. It is one of the two original colonies, not empty land.
    if pid == 2508:
        want_owner = "ENG"; want_cores |= {"ENG", "AST"}
    # Read the current state from the file we are about to edit. world_live.json is
    # regenerated AFTER a build, so on a second run it already shows the result and
    # every write would be skipped while the rebuilt files still hold the old values.
    s = open(f, encoding="cp1252", errors="replace").read()
    cur_head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", cur_head, re.M)
    cur_owner = m.group(1) if m else ""
    cur_cores = set(re.findall(r"^\s*add_core\s*=\s*([A-Z]{3})", cur_head, re.M))
    intended[str(pid)] = {"owner": want_owner, "cores": sorted(want_cores)}
    if want_owner == cur_owner and want_cores == cur_cores:
        continue
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^\s*owner\s*=.*\n", "", head, flags=re.M)
    head = re.sub(r"^\s*controller\s*=.*\n", "", head, flags=re.M)
    head = re.sub(r"^\s*add_core\s*=.*\n", "", head, flags=re.M)
    pre = (f"owner = {want_owner}\ncontroller = {want_owner}\n" if want_owner else "")
    pre += "".join(f"add_core = {c}\n" for c in sorted(want_cores))
    open(f, "w", encoding="cp1252", errors="replace", newline="\n").write(
        pre + head.lstrip("\n").rstrip("\n") + "\n" + tail)
    if want_owner != cur_owner: log["owners changed"] += 1
    if want_cores != cur_cores: log["core sets changed"] += 1
log["australian cores skipped"] = sum(
    1 for k, v in E["provinces"].items()
    if P[k]["ct"] == "australia_new_zealand" and "KRM" in v["cores"])
# Re-read every file we wrote. The bug this guards against is subtle: comparing
# against world_live.json, which is regenerated after the build, made this pass skip
# its own writes on a rebuild and Britain kept thirty-seven Australian provinces.
missed = []
for k, v in intended.items():
    f = prov.get(int(k))
    if not f: continue
    head = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)",
                    open(f, encoding="cp1252", errors="replace").read())[0]
    m = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", head, re.M)
    got_o = m.group(1) if m else ""
    got_c = set(re.findall(r"^\s*add_core\s*=\s*([A-Z]{3})", head, re.M))
    if got_o != v["owner"] or got_c != set(v["cores"]): missed.append(k)
log["writes verified"] = len(intended) - len(missed)
if missed:
    raise SystemExit(f"  apply_export2 FAILED to apply {len(missed)} provinces: {missed[:6]}")
json.dump(intended, open(f"{W}/export_intent.json", "w"))
log["provinces this pass owns"] = len(intended)
for k, v in log.items(): print(f"  {k:<30}{v}")
