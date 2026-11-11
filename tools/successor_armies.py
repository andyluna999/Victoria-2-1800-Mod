"""The republics spawn fighting.

Victoria II reads every order-of-battle file at the start of the game, including those
of countries that do not exist yet, and hands a country its army when it comes into
being. HPM relies on this: Mexico, Colombia, Argentina, Chile and Peru all ship with
small orders of battle despite holding nothing in 1836.

Our own `oob_relocate` pass strips formations from landless countries -- written to
clear out the hundred-odd dead tags whose armies sat on other people's soil -- and it
took these with them. Pristine Mexico had six regiments; ours had none. So the republic
was born into a war it could not fight, and had to mobilise from scratch while the
viceroyalty's standing army walked in. Quelling the rising was trivial, which is the
opposite of the problem the whole system exists to create.

They are exempt now, and they get armies worth the name: the host each rising actually
put into the field in its first season, in the units it actually had.

  **Mexico.** Hidalgo came out of the Bajio with something between sixty and eighty
  thousand people, almost none of them soldiers, armed with machetes, slings, lances
  and perhaps a thousand muskets. In Victoria II that is a great many irregulars and
  very little else, and it is why the royalists beat them at Calderon and why it took
  eleven years anyway.

  **Buenos Aires, Santiago, Bogota.** Smaller, better: militia regiments with creole
  officers, some artillery out of the arsenals, and cavalry from the estates. The
  Army of the Andes was six thousand men and it was the best thing in the hemisphere.

  **Peru.** Smallest of all. Cuzco raised the sierra and the sierra had no muskets.
"""
import re, os, glob, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# successor: (name of its army, provinces it is born holding, infantry, cavalry,
#             artillery, irregulars, general)
ARMIES = {
 "MEX": ("Ejercito Insurgente", [2167, 2166, 2158, 2170, 2160, 2169],
         2, 3, 1, 22, "Miguel Hidalgo"),
 "CLM": ("Ejercito Libertador", [2247, 2249, 2248, 2250],
         5, 3, 2, 6, "Antonio Narino"),
 "ARG": ("Ejercito del Norte", [2348, 2361, 2362, 2360, 2379],
         6, 4, 2, 5, "Manuel Belgrano"),
 "CHL": ("Ejercito de Chile", [2324, 2325, 2326, 2327, 2331],
         4, 3, 1, 5, "Jose Miguel Carrera"),
 "PEU": ("Ejercito del Sur", [2302, 2303, 2304, 2299],
         2, 2, 0, 9, "Mateo Pumacahua", 1814),
}

for tag, row in ARMIES.items():
    name, prov, inf, cav, art, irr, gen = row[:7]
    born = row[7] if len(row) > 7 else 1810
    regs, k = [], 0
    for ty, n in (("infantry", inf), ("cavalry", cav),
                  ("artillery", art), ("irregular", irr)):
        for i in range(n):
            regs.append(f'\tregiment = {{\n\t\tname = "{i+1}. {ty.title()}"\n'
                        f'\t\ttype = {ty}\n\t\thome = {prov[k % len(prov)]}\n\t}}')
            k += 1
    body = (f"# {name}. Read at the start of the game and handed to this country when\n"
            f"# it comes into being, which is how Victoria II arms a nation that does\n"
            f"# not exist yet.\n\n"
            f'leader = {{\n\tname = "{gen}"\n\tdate = {born}.1.1\n\ttype = land\n'
            f'\tpersonality = inspiring\n\tbackground = amateur\n\tprestige = 0.4\n}}\n\n'
            f'army = {{\n\tname = "{name}"\n\tlocation = {prov[0]}\n'
            + "\n".join(regs) + "\n}\n")
    wr(f"{MOD}/history/units/{tag}_oob.txt", body)
    log["republics armed"] += 1
    log["regiments"] += len(regs)

# and stop the relocation pass from taking them away again
p = "tools/oob_relocate.py"
s = open(p).read()
if "SPAWNS_LATER" not in s:
    s = s.replace('''    if not owned.get(tag):''',
'''    # Countries our own content brings into being later keep their orders of battle.
    # Victoria II reads these at the start of the game and hands them over when the
    # country appears; clearing them as "landless" left every republic born into a war
    # with nothing to fight it with.
    SPAWNS_LATER = {"MEX", "CLM", "ARG", "CHL", "PEU", "VNZ", "ECU", "BOL", "URU",
                    "PRG", "CUB", "PRI", "BRZ", "TEX", "HAI", "ALD", "TUN", "TRI"}
    if not owned.get(tag) and tag not in SPAWNS_LATER:''')
    open(p, "w").write(s)
    log["tags exempted from stripping"] = 18

for k, v in sorted(log.items()): print(f"  {k:<30}{v}")
