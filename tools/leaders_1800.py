"""The commanders of 1800.

Two hundred and forty-nine of HPM's two hundred and seventy-eight leaders are dated
after our start, a hundred and forty-eight of them in the 1830s, so on 1 January 1800
almost no country has a general at all. The existing roster is left alone -- a
commander appearing in 1817 or 1833 is correct and welcome -- and the generation that
was actually in the field is added alongside it.

Everyone here held a command in or around 1800. A few notes on the ones that need them:

  * Suvorov is included although he dies in May. He is in the file for four months,
    which is right: the greatest soldier in Europe is alive on the start date and
    about to be unavailable, and that is a fact the player should have to live with.
  * Desaix and Kleber both die in 1800 too, and both are here for the same reason.
  * Toussaint Louverture, Dessalines and Christophe are governing Saint-Domingue in
    the Republic's name on this date, which is why they are under HAI rather than FRA.
  * Bonaparte is First Consul, not a field commander, but he takes an army over the
    Alps in May and anyone playing France should be able to.
  * Cezzar Ahmed Pasha held Acre against that army the year before, which is the
    single reason the French are still in Egypt rather than Syria.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"
log = collections.Counter()
def rd(p): return open(p, encoding="cp1252", errors="replace").read()
def wr(p, t): open(p, "w", encoding="cp1252", errors="replace", newline="\n").write(t)

# tag: [(name, land|sea, personality, background, prestige)]
L = {
 # Napoleon takes the best combination Victoria II has: au_fait is the highest-attack
 # personality in the game (+3 attack, +15% organisation) and the bayonet school adds
 # +2 attack, +1 defence and +10% speed. Five points of attack with no offsetting
 # penalty is the ceiling for a leader, and it sits on top of the Grande Armee
 # modifier -- +20% attack and +25% organisation for every French army.
 #
 # A custom trait would go further, but traits.txt has no weighting: anything added to
 # the pool is handed out to randomly generated generals everywhere, so a Napoleonic
 # trait would turn up on Bavarian brigadiers.
 "FRA": [("Napoleon Bonaparte","land","au_fait","school_of_the_bayonet",1.0),
         ("Jean Victor Moreau","land","coolminded","war_college",0.6),
         ("Andre Massena","land","defiant","school_of_the_bayonet",0.7),
         ("Louis Desaix","land","gallant","engineer",0.6),
         ("Jean-Baptiste Kleber","land","inspiring","drillmaster",0.5),
         ("Jean Lannes","land","impetuous","exranker",0.5),
         ("Michel Ney","land","chivalrous","school_of_offense",0.6),
         # Davout never lost a battle, and beat the main Prussian army at Auerstedt
         # with one corps against twice his numbers.
         ("Louis-Nicolas Davout","land","implacable","school_of_defense",0.7),
         # The chief of staff who made the corps system work on paper.
         ("Louis-Alexandre Berthier","land","expert","gifted_administrator",0.5),
         ("Joachim Murat","land","vainglorious","cavalry_school",0.4),
         ("Toussaint Louverture","land","inspiring","exranker",0.9),
         ("Pierre de Villeneuve","sea","cautious","aristocrat",0.2),
         ("Latouche Treville","sea","aggressive","war_college",0.4)],
 "ENG": [("Horatio Nelson","sea","audacious","natural_born_leader",1.0),
         ("John Jervis","sea","relentless","drillmaster",0.7),
         ("Cuthbert Collingwood","sea","coolminded","innovative_tactician",0.6),
         ("George Elphinstone","sea","cautious","aristocrat",0.4),
         ("Ralph Abercromby","land","earnest","war_college",0.6),
         ("John Moore","land","inspiring","drillmaster",0.6),
         ("Arthur Wellesley","land","defiant","school_of_defense",0.8),
         ("Charles Cornwallis","land","balanced_p","aristocrat",0.5)],
 # The only man to beat Napoleon in the field before 1812, at Aspern-Essling.
 "AUS": [("Archduke Charles","land","au_fait","school_of_defense",0.9),
         ("Michael von Melas","land","cautious","aristocrat",0.5),
         ("Paul Kray","land","persistant","exranker",0.5),
         ("Heinrich von Bellegarde","land","balanced_p","aristocrat",0.4),
         ("Johann von Klenau","land","aggressive","cavalry_school",0.4)],
 # Sixty-three battles and no defeats, and four months left to live.
 "RUS": [("Alexander Suvorov","land","implacable","school_of_the_bayonet",1.0),
         ("Mikhail Kutuzov","land","cautious","war_college",0.7),
         ("Pyotr Bagration","land","gallant","exranker",0.6),
         ("Barclay de Tolly","land","coolminded","war_college",0.5),
         ("Fyodor Ushakov","sea","audacious","innovative_tactician",0.7),
         ("Dmitry Senyavin","sea","earnest","rising_star",0.4)],
 "PRU": [("Gebhard von Blucher","land","aggressive","cavalry_school",0.6),
         ("Duke of Brunswick","land","cautious","aristocrat",0.4),
         ("Gerhard von Scharnhorst","land","earnest","engineer",0.5),
         ("Prince Hohenlohe","land","arrogant","aristocrat",0.3)],
 "SPA": [("Federico Gravina","sea","gallant","aristocrat",0.5),
         ("Jose de Mazarredo","sea","coolminded","professor",0.5),
         ("Gregorio de la Cuesta","land","persistant","aristocrat",0.3),
         ("Francisco Castanos","land","balanced_p","war_college",0.4)],
 "TUR": [("Cezzar Ahmed Pasha","land","brutish","exranker",0.6),
         ("Huseyin Kucuk Pasha","land","cautious","aristocrat",0.4),
         ("Kaptan Hasan Bey","sea","earnest","exranker",0.3)],
 "SIC": [("Karl Mack von Leiberich","land","pessimist","armchair_general",0.2),
         ("Cardinal Ruffo","land","inspiring","amateur",0.4)],
 "NET": [("Herman Daendels","land","aggressive","exranker",0.4),
         ("Jan de Winter","sea","earnest","exranker",0.4)],
 "POR": [("Marquis of Alorna","land","balanced_p","aristocrat",0.3)],
 "USA": [("Thomas Truxtun","sea","aggressive","expert_raider",0.5),
         ("James Wilkinson","land","unsound","adventurer",0.2),
         ("Alexander Hamilton","land","earnest","amateur",0.4)],
 "DEN": [("Olfert Fischer","sea","persistant","school_of_defense",0.4)],
 "SWE": [("Carl Olof Cronstedt","sea","cautious","school_of_defense",0.3)],
 # Toussaint is a French general in 1800 and belongs on France's roster, not Haiti's.
 # He is governor-general of Saint-Domingue by commission of the Republic, he has just
 # beaten Rigaud in its name, and he dies in a French prison in April 1803 -- nine
 # months before Haiti exists. Listing him under HAI meant the best commander in the
 # Caribbean never appeared in the game at all.
 #
 # Dessalines and Christophe were French officers too, but they outlive the colony,
 # so they wait for the country they make.
 "HAI": [("Jean-Jacques Dessalines","land","merciless","exranker",0.7),
         ("Henri Christophe","land","relentless","exranker",0.5)],
 "MAR": [("Yashwantrao Holkar","land","audacious","cavalry_school",0.6),
         ("Pierre Cuillier-Perron","land","persistant","drillmaster",0.5),
         ("Daulat Rao Sindhia","land","arrogant","aristocrat",0.4)],
 "PER": [("Abbas Mirza","land","earnest","aristocrat",0.5)],
 "NEJ": [("Saud ibn Abd al-Aziz","land","relentless","adventurer",0.7)],
 "EBR": [("Conde de Linhares","land","balanced_p","aristocrat",0.3)],
 # Massena is besieged in Genoa from April and the Republic has its own officers
 "LIG": [("Girolamo Durazzo","land","earnest","aristocrat",0.3),
         ("Giacomo Mazzini","sea","cautious","expert_raider",0.2)],
 "NSP": [("Felix Calleja","land","merciless","drillmaster",0.5)],
 "VPE": [("Jose de Abascal","land","cautious","bureaucrat_speed",0.4)],
 "RDP": [("Santiago de Liniers","land","gallant","adventurer",0.4)],
 "TYS": [("Nguyen Van Truong","land","persistant","exranker",0.4)],
 "QNG": [("Eldemboo","land","relentless","aristocrat",0.5),
         ("Nayancheng","land","balanced_p","bureaucrat_speed",0.3)],
 "RGA": [("Mustapha Pasha","sea","brutish","adventurer",0.4)],
 "MOR": [("Moulay Slimane","land","bigoted","aristocrat",0.3)],
 "ETH": [("Ras Wolde Selassie","land","persistant","aristocrat",0.3)],
 "BUR": [("Maha Bandula","land","aggressive","exranker",0.5)],
 "SIA": [("Chao Phraya Kalahom","land","balanced_p","aristocrat",0.3)],
 "JAP": [("Matsudaira Sadanobu","land","earnest","bureaucrat_speed",0.3)],
 "AFG": [("Fateh Khan","land","audacious","adventurer",0.4)],
 "PNJ": [("Ranjit Singh","land","audacious","cavalry_school",0.8),
         ("Hari Singh Nalwa","land","relentless","exranker",0.5)],
}

# traits must exist, or Victoria II drops the leader silently
tr = re.sub(r"#.*", "", rd(f"{MOD}/common/traits.txt"))
depth, cur, PERS, BACK = 0, None, set(), set()
for m in re.finditer(r"([a-z_]+)\s*=\s*\{|\{|\}", tr):
    t = m.group(0)
    if t == "}": depth -= 1
    elif t == "{": depth += 1
    else:
        n = m.group(1)
        if depth == 0: cur = n
        elif depth == 1: (PERS if cur == "personality" else BACK).add(n)
        depth += 1
fixed = 0
for tag, rows in L.items():
    out = []
    for nm, ty, per, bak, pr in rows:
        if per not in PERS: per = "balanced_p"; fixed += 1
        if bak not in BACK: bak = "war_college" if ty == "land" else "natural_born_leader"; fixed += 1
        if bak not in BACK: bak = "no_background"
        out.append((nm, ty, per, bak, pr))
    L[tag] = out
log["traits corrected to valid names"] = fixed

for tag, rows in L.items():
    f = f"{MOD}/history/units/{tag}_oob.txt"
    body = rd(f) if os.path.exists(f) else ""
    have = set(re.findall(r'leader\s*=\s*\{[^}]*?name\s*=\s*"([^"]*)"', body, re.S))
    block = []
    for nm, ty, per, bak, pr in rows:
        if nm in have: continue
        # Haiti's commanders date from independence; everyone else from the start.
        when = "1804.1.1" if tag == "HAI" else "1799.1.1"
        block.append(f'leader = {{\n\tname = "{nm}"\n\tdate = {when}\n\ttype = {ty}\n'
                     f'\tpersonality = {per}\n\tbackground = {bak}\n\tprestige = {pr}\n}}')
        log["leaders added"] += 1
        log["admirals" if ty == "sea" else "generals"] += 1
    if not block: continue
    head = "# Commanders in the field on the start date.\n\n" + "\n".join(block) + "\n\n"
    # after the relation blocks, before the formations
    m = re.search(r"^(?=[ \t]*(army|navy|leader)[ \t]*=)", body, re.M)
    if m: body = body[:m.start()] + head + body[m.start():]
    else: body = body + "\n" + head
    wr(f, body)
    log["countries given commanders"] += 1

for k, v in sorted(log.items()): print(f"  {k:<36}{v}")
