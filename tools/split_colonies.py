"""Separate each Iberian colonial administration from the republic that succeeds it.

The export reuses successor tags for the colonies (MEX named "Viceroyalty of New
Spain"), which means the viceroyalty and the nation are one object: the name cannot
change at independence and the republic cannot be released by rebels. This moves the
territory onto a colonial tag and leaves the republic as a coreless claimant.
"""
import json, collections

EXP = "/mnt/user-data/uploads/hpm_world_1836.json"
OUT = "/home/claude/work/export_split.json"
d = json.load(open(EXP))
P, C = d["provinces"], d["countries"]

SPA_RED, POR_GRN = (170, 50, 50), (40, 110, 60)
def blend(a, b, t=0.45): return [int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)]

# colonial tag, viceroyalty name, successor tag, republic name, metropole, republic cultures
PAIRS = [
 ("NSP", "Viceroyalty of New Spain",        "MEX", "Mexico",    "SPA", "mestizo", ["criollo","nahua","maya"]),
 ("VNG", "Viceroyalty of New Granada",      "CLM", "Colombia",  "SPA", "mestizo", ["criollo"]),
 ("VPE", "Viceroyalty of Peru",             "PEU", "Peru",      "SPA", "mestizo", ["criollo"]),
 ("CGC", "General Captaincy of Chile",      "CHL", "Chile",     "SPA", "criollo", ["mestizo"]),
 ("EBR", "Viceroyalty of Brazil",           "BRZ", "Brazil",    "POR", "criollo", []),
]
# RDP already exists as its own colonial tag in the export; it only needs a successor
KEEP = {"RDP": ("ARG", "criollo", ["mestizo"])}

log = collections.Counter()
for col, vname, suc, rname, metro, iprim, iacc in PAIRS:
    owned = [k for k, v in P.items() if v["owner"] == suc]
    if not owned:
        log["pair skipped, successor holds nothing"] += 1
        continue
    base = C.get(suc, {}).get("color", [130, 130, 130])
    C[col] = {"name": vname,
              "color": blend(base, SPA_RED if metro == "SPA" else POR_GRN),
              "overlord": metro, "relationship": "colony",
              "primary_culture": "spanish" if metro == "SPA" else "portuguese",
              "accepted_cultures": ["criollo"],
              "becomes": suc,
              "on_independence": {"becomes": suc, "primary_culture": iprim,
                                  "accepted_cultures": iacc}}
    # the republic keeps its claims and its own identity, but holds nothing yet
    C[suc] = {"name": rname, "color": base, "overlord": "", "relationship": "puppet",
              "primary_culture": iprim, "accepted_cultures": iacc,
              "becomes": "", "on_independence": None}
    for k in owned:
        v = P[k]
        v["owner"] = col
        v["controller"] = col
        cores = set(v["cores"])
        cores.add(col)          # the viceroyalty is coherent as a state
        cores.add(suc)          # and the republic can be released from it
        v["cores"] = sorted(cores)
    log["colonies split"] += 1
    log["provinces moved"] += len(owned)

for col, (suc, iprim, iacc) in KEEP.items():
    if col not in C: continue
    C[col]["becomes"] = suc
    C[col]["primary_culture"] = "spanish"
    C[col]["accepted_cultures"] = ["criollo"]
    C[col]["overlord"] = C[col].get("overlord") or "SPA"
    C[col]["relationship"] = "colony"
    C[col]["on_independence"] = {"becomes": suc, "primary_culture": iprim,
                                 "accepted_cultures": iacc}
    if suc in C:
        C[suc]["primary_culture"] = iprim
        C[suc]["accepted_cultures"] = iacc
    for k, v in P.items():
        if v["owner"] == col and suc not in v["cores"]:
            v["cores"] = sorted(set(v["cores"]) | {suc})
            log["successor cores added"] += 1
    log["colonies kept as authored"] += 1

# --- Cuba and Puerto Rico were their own captaincies-general, answering to Madrid
# directly. They were never administered from Mexico, and the decisions and remittance
# events written for them referenced tags that the pruning step had removed.
ISLANDS = [
 ("CBA", "Captaincy General of Cuba", "CUB", [2209, 2210, 2211, 2212, 44],
  "criollo", ["afro_caribbean"]),
 ("PTR", "Puerto Rico",               "PRI", [2222], "criollo", ["afro_caribbean"]),
]
for col, vname, suc, ids, iprim, iacc in ISLANDS:
    base = C.get(suc, {}).get("color", [130, 130, 130])
    C[col] = {"name": vname, "color": blend(base, SPA_RED),
              "overlord": "SPA", "relationship": "colony",
              "primary_culture": "spanish", "accepted_cultures": ["criollo"],
              "becomes": suc,
              "on_independence": {"becomes": suc, "primary_culture": iprim,
                                  "accepted_cultures": iacc}}
    if suc in C:
        C[suc] = {"name": C[suc]["name"], "color": base, "overlord": "", "relationship": "puppet",
                  "primary_culture": iprim, "accepted_cultures": iacc,
                  "becomes": "", "on_independence": None}
    for k in map(str, ids):
        if k not in P: continue
        v = P[k]
        v["owner"] = col; v["controller"] = col
        v["cores"] = sorted(set(v["cores"]) | {col, suc})
        log["island provinces moved"] += 1
    log["island captaincies"] += 1

# --- Windows reserved device names -------------------------------------------
# CON, PRN, AUX, NUL, COM1-9 and LPT1-9 cannot be filenames on Windows, with or
# without an extension. A country tagged CON can never have CON.tga, so the flag
# copy fails outright. Bare COM and LPT are fine; only the numbered ones are taken.
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} \
         | {f"LPT{i}" for i in range(1, 10)}
def free_tag(seed, taken):
    import string
    for a in string.ascii_uppercase:
        for b in string.ascii_uppercase:
            for c in string.ascii_uppercase:
                t = a + b + c
                if t not in taken and t not in RESERVED:
                    return t
    raise SystemExit("no free tag")
for old in [t for t in list(C) if t.upper() in RESERVED]:
    new_t = {"CON": "CRK"}.get(old) or free_tag(old, set(C))
    if new_t in C: new_t = free_tag(old, set(C))
    C[new_t] = C.pop(old)
    for v in P.values():
        if v["owner"] == old: v["owner"] = new_t
        if v["controller"] == old: v["controller"] = new_t
        v["cores"] = sorted({new_t if x == old else x for x in v["cores"]})
    for k in C.values():
        if k.get("overlord") == old: k["overlord"] = new_t
        if k.get("becomes") == old: k["becomes"] = new_t
        oi = k.get("on_independence")
        if oi and oi.get("becomes") == old: oi["becomes"] = new_t
    log[f"reserved tag {old} renamed to {new_t}"] += 1

json.dump(d, open(OUT, "w"))
for k, v in log.items(): print(f"  {k:<36}{v}")
print("  colonial tags now on the map:",
      ", ".join(sorted({v["owner"] for v in P.values()
                        if v["owner"] in set(x[0] for x in PAIRS) | set(KEEP)})))
