"""Venezuela was not governed from Bogota, and had not been since 1777.

Reported by a player, and correct. The mod had Caracas, Maracaibo, Cumana and the
whole of the Venezuelan provinces owned by the Viceroyalty of New Granada, which is
the arrangement as it stood before 1777 and not as it stood in 1800.

The Captaincy General of Venezuela was created in 1777, separating Caracas, Maracaibo,
Cumana, Guayana, Margarita and Trinidad from New Granada and placing them under a
captain general answering directly to Madrid. It got its own audiencia at Caracas in
1786 and its own intendancy in 1776, which between them meant the three things that
actually constitute a government: its own courts, its own revenue and its own army.
By 1800 Bogota had no jurisdiction there at all.

This is not a map detail. It is the reason the Venezuelan revolution was a separate
revolution with its own junta in April 1810, its own declaration in July 1811 -- the
first anywhere in Spanish America -- its own first and second republics and its own
catastrophe under Boves. And it is the reason Gran Colombia was a *union* of Venezuela
and New Granada rather than New Granada growing: Bolivar spent 1819 to 1821 joining
two countries that had never been one in living memory, and it came apart in 1830
along precisely the line drawn in 1777.

So the Captaincy General exists, holds its own provinces, raises its own army, and
gets the same roads out that the viceroyalties have.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# the Captaincy General as it stood in 1800
VENEZUELA = [2264, 2265, 2266, 2267, 2268, 2269, 2270, 2271, 2272,
             2273, 2274, 2275, 2276, 2277, 2278]

for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid not in VENEZUELA: continue
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    if not re.search(r"^\s*owner\s*=\s*VNG", head, re.M):
        continue
    head = re.sub(r"^\s*owner\s*=\s*VNG", "owner = VNZ", head, flags=re.M)
    head = re.sub(r"^\s*controller\s*=\s*VNG", "controller = VNZ", head, flags=re.M)
    # New Granada keeps no claim on country it has not governed since 1777
    head = re.sub(r"^\s*add_core\s*=\s*VNG\s*\n", "", head, flags=re.M)
    if "add_core = VNZ" not in head:
        head = head.rstrip("\n") + "\nadd_core = VNZ\n"
    wr(f, head.rstrip("\n") + "\n" + tail)
    log["provinces moved to the Captaincy General"] += 1

# the country itself, modelled on the viceroyalties it is not part of
g = glob.glob(f"{MOD}/history/countries/VNZ - *.txt")
if g:
    s = rd(g[0])
    parts = re.split(r"\n(?=\s*\d{4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    head = re.sub(r"^\s*capital\s*=\s*\d+", "capital = 2264", head, flags=re.M)
    head = re.sub(r"^\s*government\s*=\s*\w+", "government = absolute_monarchy",
                  head, flags=re.M)
    head = re.sub(r"^\s*primary_culture\s*=\s*\w+", "primary_culture = spanish",
                  head, flags=re.M)
    for c in ("criollo", "mestizo", "afro_caribbean"):
        if f"culture = {c}" not in head:
            head = re.sub(r"(^primary_culture\s*=.*\n)", r"\1" + f"culture = {c}\n",
                          head, count=1, flags=re.M)
    if not re.search(r"^\s*prestige\s*=", head, re.M):
        head = head.rstrip("\n") + "\nprestige = 4\n"
    else:
        head = re.sub(r"^\s*prestige\s*=\s*[\d.]+", "prestige = 4", head, flags=re.M)
    if not re.search(r"^\s*oob\s*=", head, re.M):
        head = re.sub(r"(^\s*capital\s*=.*\n)", r"\1" + 'oob = "VNZ_oob.txt"\n',
                      head, count=1, flags=re.M)
    wr(g[0], head.rstrip("\n") + "\n" + tail)
    log["the Captaincy General governs itself"] = 1

# cacao, cattle and the llanero cavalry that beat the first two republics
wr(f"{MOD}/history/units/VNZ_oob.txt",
   "# The army of the Captaincy General. Small, as it was: the captain general's\n"
   "# regular force was a few battalions, and what actually decided the wars here\n"
   "# was the llanero cavalry of the plains, which fought for whoever offered the\n"
   "# herds -- royalist under Boves, republican under Paez.\n\n"
   'leader = {\n\tname = "Juan de Casas"\n\tdate = 1799.1.1\n\ttype = land\n'
   "\tpersonality = cautious\n\tbackground = aristocrat\n\tprestige = 0.2\n}\n\n"
   'army = {\n\tname = "Ejercito de Venezuela"\n\tlocation = 2264\n'
   + "".join(f'\tregiment = {{\n\t\tname = "{i+1}. Infantry"\n\t\ttype = infantry\n'
             f"\t\thome = {p}\n\t}}\n"
             for i, p in enumerate([2264, 2270, 2267, 2272, 2273]))
   + "".join(f'\tregiment = {{\n\t\tname = "{i+1}. Llaneros"\n\t\ttype = cavalry\n'
             f"\t\thome = {p}\n\t}}\n"
             for i, p in enumerate([2266, 2274, 2275]))
   + "}\n")
log["regiments"] = 8

# Spain's possession, like the rest
f = f"{MOD}/history/diplomacy/1800_colonial_rule.txt"
if os.path.exists(f):
    s = rd(f)
    if "second = VNZ" not in s:
        wr(f, s.rstrip() + "\n\nvassal = {\n\tfirst = SPA\n\tsecond = VNZ\n"
                           "\tstart_date = 1777.2.8\n\tend_date = 1836.1.1\n}\n"
                           "\nsphere = {\n\tfirst = SPA\n\tsecond = VNZ\n"
                           "\tstart_date = 1777.2.8\n\tend_date = 1836.1.1\n}\n")
        log["a possession of Spain, like the rest"] = 1

left = []
for f in glob.glob(f"{MOD}/history/provinces/*/*.txt"):
    pid = int(re.match(r"(\d+)", os.path.basename(f)).group(1))
    if pid in VENEZUELA and re.search(r"^\s*owner\s*=\s*VNG", rd(f), re.M):
        left.append(pid)
log["still governed from Bogota"] = len(left)
for k, v in sorted(log.items()): print(f"  {k:<42}{v}")
