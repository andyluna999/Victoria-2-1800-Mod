"""A technology tree that starts when the game does, and a French military lead.

**The tree begins in 1836.** Every one of the hundred and fifty technologies carries
`year = 1836` or later, which in Victoria II governs what it costs to research: before
a technology's year the price climbs steeply, and thirty-six years early it is
effectively out of reach. So the research screen in 1800 shows a tree nobody can climb,
and the powers sit on their four starting army technologies for a generation.

The fix is to move the tree to meet the start date. The game now runs 1800 to 1936 --
a hundred and thirty-six years where vanilla had a hundred -- so each technology's year
is mapped proportionally:

    new = 1800 + (old - 1836) x 1.36

which puts the first tier at 1800, the 1850 tier at about 1819, and leaves 1936 where
it is. The pacing of the tree is preserved and stretched over the longer game rather
than compressed against one end of it.

**And France should lead.** On the start date every great power holds the same four
army technologies, which is not what 1800 looked like. France had spent a decade
inventing modern war: the Gribeauval artillery system of standardised calibres and
interchangeable carriages, the division and then the corps as permanent combined-arms
formations, a general staff under Berthier, and conscription on a scale nobody else
attempted. Its officers were promoted on performance because the old ones had emigrated.

So France gets `army_professionalism`, `military_plans` and `iron_muzzle_loaded_artillery`
on top of what everyone has. Prussia and Austria get one each, because their reforms
are reactions to being beaten and have not happened yet. Britain gets the naval lead
instead, which is where it actually was.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# --- move the tree to meet the start date -------------------------------------------
START, OLD_START, OLD_END, END = 1800, 1836, 1936, 1936
SCALE = (END - START) / (OLD_END - OLD_START)
moved = []
for f in glob.glob(f"{MOD}/technologies/*.txt"):
    s = rd(f)
    def shift(m):
        old = int(m.group(1))
        new = int(round(START + (old - OLD_START) * SCALE))
        new = max(START, min(END, new))
        if new != old: moved.append((old, new))
        return m.group(0).replace(m.group(1), str(new))
    ns = re.sub(r"(?<=\byear\s=\s)(\d{4})", shift, s)
    ns = re.sub(r"\byear\s*=\s*(\d{4})", lambda m: shift(m), s)
    if ns != s:
        wr(f, ns); log["technology files rescaled"] += 1
log["technology years moved"] = len(moved)
if moved:
    log["earliest year now"] = min(n for _, n in moved)

# --- the French military lead ---------------------------------------------------------
EXTRA = {
    # France invented modern war in the decade before this one.
    "FRA": ["army_professionalism", "military_plans", "iron_muzzle_loaded_artillery"],
    # Prussia's reforms are a reaction to Jena and have not happened yet.
    "PRU": ["military_plans"],
    # Austria rebuilt under the Archduke after 1801, slowly.
    "AUS": ["army_professionalism"],
    # Russia has mass and Suvorov's doctrine, little else.
    "RUS": ["army_professionalism"],
    # Britain's lead is at sea, and it is enormous.
    "ENG": ["naval_professionalism", "post_nelsonian_thought", "naval_plans",
            "the_command_principle", "battleship_column_doctrine"],
    # the second and third naval powers of the age
    "FRA_navy": [],
    "SPA": ["naval_professionalism"],
    "NET": ["naval_professionalism"],
    "DEN": ["naval_professionalism"],
    "SWE": ["naval_professionalism"],
    "USA": ["naval_professionalism"],
}
for tag, techs in EXTRA.items():
    if tag.endswith("_navy") or not techs: continue
    g = glob.glob(f"{MOD}/history/countries/{tag} - *.txt")
    if not g: continue
    s = rd(g[0])
    parts = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    add = ""
    for t in techs:
        if not re.search(rf"^\s*{t}\s*=\s*1\s*$", head, re.M):
            add += f"{t} = 1\n"
            log["technologies granted"] += 1
    if add:
        head = re.sub(r"(^\s*civilized\s*=.*\n)", r"\1" + add, head, count=1, flags=re.M)
        wr(g[0], head.rstrip("\n") + "\n" + tail)

for k, v in sorted(log.items()): print(f"  {k:<32}{v}")
