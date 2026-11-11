"""Literacy and political awareness for 1800.

HPM's figures are 1836's, and a hundred and seven countries read above forty per cent
literacy with fifty-one above sixty. Those numbers describe a world after three decades
of state schooling, Sunday schools, cheap print and the Lancasterian monitorial system.
In 1800 almost none of that has happened.

The anchors below are the standard estimates of adult literacy around 1800. The pattern
they make is not the one a 1836 map suggests: the most literate countries in Europe are
Sweden, Denmark and Prussia, because the Lutheran churches had spent two centuries
requiring people to read the catechism before they could marry, and they are poorer and
less industrial than the countries they beat. England is behind Scotland. France, at
roughly a third, is behind both.

Plurality -- Victoria II's measure of political awareness -- is scaled hard. A hundred
and thirty-six countries sit above five, which is a world of newspapers and public
meetings. In 1800 the Combination Acts are in force in Britain, most of Europe is under
censorship, and the franchise barely exists.

Governments are left alone. All nine democracies that hold land in 1800 are real
republics -- Liguria, the Batavian and Helvetic Republics, Ragusa, the United States and
the four free imperial cities -- which is a better showing than I expected.
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
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# adult literacy around 1800, where an estimate exists
LIT = {
 "SWE": .75, "DEN": .70, "FIN": .70, "ICL": .80, "NOR": .65,
 "PRU": .60, "SAX": .55, "HAN": .50, "MEC": .45, "OLD": .45, "BRU": .50,
 "HAM": .60, "LUB": .60, "BRE": .60, "FRM": .55, "ANH": .50, "LIP": .48,
 "NET": .60, "SWI": .55, "SCO": .65,
 "ENG": .48, "IRE": .28, "FRA": .37, "BEL": .40,
 "AUS": .30, "BOH": .35, "HUN": .20, "BAV": .40, "WUR": .45, "BAD": .45,
 "HES": .45, "HEK": .45, "NAS": .45,
 "SPA": .20, "POR": .18, "SAR": .22, "TUS": .25, "PAP": .20, "SIC": .12,
 "LOM": .28, "VEN": .25, "MOD": .25, "PAR": .25, "LUC": .25, "LIG": .30,
 "RUS": .07, "POL": .15, "GRE": .08, "SER": .04, "TUR": .03, "RAG": .35,
 "USA": .55, "HAI": .05, "NSP": .10, "VPE": .08, "VNG": .08, "RDP": .10,
 "CGC": .10, "EBR": .08, "CBA": .12, "PTR": .10,
 "JAP": .30, "QNG": .18, "KOR": .15, "PER": .05, "MAR": .05, "PNJ": .05,
 "EGY": .04, "MOR": .05, "ETH": .03, "SIA": .08, "BUR": .10, "DAI": .12,
}
# everything unlisted takes a continental scale against its 1836 figure
BY_CONT_SCALE = 0.55
PLURALITY = 0.30          # 1836 political awareness, scaled to 1800

changed = collections.Counter()
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    b = os.path.basename(f)
    if " - " not in b: continue
    tag = b.split(" - ")[0].strip()
    s = rd(f)
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    before = head

    m = re.search(r"^\s*literacy\s*=\s*([\d.]+)", head, re.M)
    if m:
        old = float(m.group(1))
        new = LIT.get(tag, round(old * BY_CONT_SCALE, 3))
        new = max(0.01, min(0.80, new))
        if abs(new - old) > 0.001:
            head = re.sub(r"^\s*literacy\s*=.*$", f"literacy = {new}", head, count=1, flags=re.M)
            changed["literacy"] += 1
            if old >= 0.40: changed["literacy above 40% corrected"] += 1
    # the non-state-culture figure follows, never above the state one
    m = re.search(r"^\s*non_state_culture_literacy\s*=\s*([\d.]+)", head, re.M)
    if m:
        base = float(re.search(r"^\s*literacy\s*=\s*([\d.]+)", head, re.M).group(1))
        new = max(0.01, round(min(float(m.group(1)) * BY_CONT_SCALE, base * 0.5), 3))
        head = re.sub(r"^\s*non_state_culture_literacy\s*=.*$",
                      f"non_state_culture_literacy = {new}", head, count=1, flags=re.M)

    m = re.search(r"^\s*plurality\s*=\s*([\d.]+)", head, re.M)
    if m:
        old = float(m.group(1))
        new = round(old * PLURALITY, 2)
        if abs(new - old) > 0.01:
            head = re.sub(r"^\s*plurality\s*=.*$", f"plurality = {new}", head, count=1, flags=re.M)
            changed["plurality"] += 1

    if head != before:
        wr(f, head + tail); log["country files adjusted"] += 1

for k, v in changed.items(): print(f"  {k:<34}{v}")
for k, v in log.items(): print(f"  {k:<34}{v}")
