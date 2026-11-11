"""Construct the 1800 North American culture + population layer for HPM.

Scale: HPM's 1836 data runs at ~0.25 of real population (US 1836 real 15.4M -> HPM 3.84M;
world real ~1.1bn -> HPM 266.8M). We keep 0.25 so North America stays commensurate with
the rest of the world, which is untouched.
"""
import os as _os
_ROOT = _os.environ.get("HPM1800_ROOT") or _os.path.dirname(
    _os.path.dirname(_os.path.abspath(__file__)))
_SRC = _os.environ.get("HPM1800_SRC") or _os.path.join(_ROOT, "hpm", "HPM - Copy")
_BUILD = _os.environ.get("HPM1800_BUILD") or _os.path.join(_ROOT, "build", "HPM")
_WORK = _os.environ.get("HPM1800_WORK") or _os.path.join(_ROOT, "work")
_TOOLS = _os.path.join(_ROOT, "tools")
import json, collections, math

W = _WORK
D = json.load(open(f"{W}/world_data.json"))
ST = {int(k): v for k, v in json.load(open(f"{W}/prov_stats.json")).items()}
SCALE = 0.25

NA = {int(p): v for p, v in D["prov"].items() if v["ct"] == "north_america"}
for p in NA: NA[p]["x"] = ST[p]["lx"]; NA[p]["y"] = ST[p]["ly"]

# ---------------------------------------------------------------- culture table
# group, religion, archetype, real 1800 population estimate (persons)
C = {
 # --- settler / European ---
 "yankee":          ("american_cultures","protestant","settler",   2560000),
 "dixie":           ("american_cultures","protestant","planter",   1700000),
 "anglo_canadian":  ("neo_european_cultures","protestant","settler",140000),
 "french_canadian": ("neo_european_cultures","catholic","settler",  220000),
 "french_creole":   ("neo_european_cultures","catholic","settler",   45000),
 "british":         ("british","protestant","urban",                 90000),
 "irish":           ("british","catholic","settler",                180000),
 "scottish":        ("british","protestant","settler",               70000),
 "french":          ("french","catholic","urban",                    25000),
 "spanish":         ("iberian","catholic","peninsular",             110000),
 "portuguese":      ("iberian","catholic","urban",                    6000),
 "russian":         ("russian","orthodox","urban",                     800),
 "north_german":    ("germanic","protestant","settler",             250000),
 # --- Latin American ---
 "criollo":         ("latin_american_cultures","catholic","criollo",1500000),
 "mestizo":         ("latin_american_cultures","catholic","mestizo",2350000),
 # --- African diaspora ---
 "afro_american":   ("african_diaspora_cultures","protestant","enslaved",1000000),
 "afro_caribbean":  ("african_diaspora_cultures","catholic","enslaved",1450000),
 # --- Mesoamerican (Catholic) ---
 "nahua":     ("mesoamerican","catholic","settled_native",1200000),
 "maya":      ("mesoamerican","catholic","settled_native",1100000),
 "zapotec":   ("mesoamerican","catholic","settled_native", 220000),
 "mixtec":    ("mesoamerican","catholic","settled_native", 180000),
 "otomi":     ("mesoamerican","catholic","settled_native", 180000),
 "purepecha": ("mesoamerican","catholic","settled_native", 100000),
 "totonac":   ("mesoamerican","catholic","settled_native",  80000),
 "huastec":   ("mesoamerican","catholic","settled_native",  50000),
 # --- Aridoamerican ---
 "tarahumara":("aridoamerican","animist","settled_native", 25000),
 "yaqui":     ("aridoamerican","animist","settled_native", 25000),
 "apache":    ("aridoamerican","animist","nomad_native",    8000),
 "navajo":    ("aridoamerican","animist","settled_native", 10000),
 "pueblo":    ("aridoamerican","animist","settled_native", 10000),
 "piman":     ("aridoamerican","animist","settled_native", 18000),
 # --- Eastern woodlands ---
 "cherokee":      ("eastern_woodlands","animist","settled_native",16000),
 "creek":         ("eastern_woodlands","animist","settled_native",20000),
 "seminole":      ("eastern_woodlands","animist","settled_native", 5000),
 "choctaw":       ("eastern_woodlands","animist","settled_native",15000),
 "chickasaw":     ("eastern_woodlands","animist","settled_native", 4000),
 "haudenosaunee": ("eastern_woodlands","animist","settled_native", 8000),
 "anishinaabe":   ("eastern_woodlands","animist","nomad_native",  35000),
 "algonquian":    ("eastern_woodlands","animist","nomad_native",  15000),   # ADDED
 # --- Plains ---
 "sioux":          ("plains_nations","animist","nomad_native",25000),
 "osage":          ("plains_nations","animist","nomad_native", 6000),
 "pawnee":         ("plains_nations","animist","settled_native",10000),
 "comanche":       ("plains_nations","animist","nomad_native",25000),
 "mandan_arikara": ("plains_nations","animist","settled_native",8000),
 "blackfoot":      ("plains_nations","animist","nomad_native",15000),
 "crow":           ("plains_nations","animist","nomad_native", 4000),
 "cheyenne":       ("plains_nations","animist","nomad_native", 3500),   # ADDED
 "arapaho":        ("plains_nations","animist","nomad_native", 3000),   # ADDED
 "caddo":          ("plains_nations","animist","settled_native",2500),  # ADDED
 "ute":            ("plateau_northwest","animist","nomad_native",8000), # ADDED
 # --- Plateau / Northwest ---
 "shoshone":  ("plateau_northwest","animist","nomad_native",  8000),
 "salish":    ("plateau_northwest","animist","settled_native",25000),
 "nez_perce": ("plateau_northwest","animist","nomad_native",   6000),
 "chinook":   ("plateau_northwest","animist","settled_native",20000),
 "california_nations": ("plateau_northwest","animist","settled_native",250000),  # ADDED
 # --- Arctic / Subarctic ---
 "tlingit": ("arctic_nations","animist","settled_native",10000),
 "aleut":   ("arctic_nations","animist","nomad_native",   8000),
 "yupik":   ("arctic_nations","animist","nomad_native",  25000),
 "inuit":   ("arctic_nations","animist","nomad_native",  25000),
 "cree":    ("arctic_nations","animist","nomad_native",  25000),   # ADDED back
 "dene":    ("arctic_nations","animist","nomad_native",  20000),   # ADDED
 "metis":   ("arctic_nations","catholic","nomad_native",  5000),   # ADDED back
 # --- Circum-Caribbean ---
 "miskito":       ("circumcaribbean","animist","settled_native",20000),
 "taino_remnant": ("circumcaribbean","animist","settled_native", 8000),
}

PRETTY = {"french_creole":"FrenchCreole","mandan_arikara":"MandanArikara","nez_perce":"NezPerce",
          "taino_remnant":"TainoRemnant","california_nations":"CaliforniaNations",
          "anglo_canadian":"AngloCanadian","french_canadian":"FrenchCanadian",
          "afro_american":"AfroAmerican","afro_caribbean":"AfroCaribbean"}

# ------------------------------------------------- pop-type mix per archetype
ARCH = {
 "settler":        {"farmers":.70,"artisans":.11,"labourers":.07,"soldiers":.035,"clergymen":.025,
                    "aristocrats":.02,"bureaucrats":.012,"clerks":.008,"officers":.005,"capitalists":.005},
 "planter":        {"farmers":.66,"artisans":.09,"labourers":.06,"aristocrats":.055,"soldiers":.04,
                    "clergymen":.025,"bureaucrats":.012,"clerks":.008,"officers":.006,"capitalists":.004},
 "peninsular":     {"aristocrats":.22,"bureaucrats":.20,"artisans":.14,"clerks":.12,
                    "clergymen":.12,"capitalists":.08,"officers":.06,"soldiers":.04,"farmers":.02},
 "urban":          {"artisans":.33,"clerks":.11,"bureaucrats":.11,"aristocrats":.10,"farmers":.14,
                    "clergymen":.06,"soldiers":.06,"officers":.03,"capitalists":.03,"labourers":.03},
 "criollo":        {"farmers":.52,"artisans":.14,"aristocrats":.09,"bureaucrats":.06,"clergymen":.05,
                    "soldiers":.05,"labourers":.04,"clerks":.025,"officers":.015,"capitalists":.01},
 "mestizo":        {"farmers":.58,"labourers":.24,"artisans":.10,"soldiers":.04,"clergymen":.015,
                    "aristocrats":.01,"clerks":.01,"officers":.005},
 "enslaved":       {"slaves":.90,"labourers":.07,"artisans":.025,"farmers":.005},
 "settled_native": {"farmers":.90,"artisans":.045,"clergymen":.02,"aristocrats":.02,"soldiers":.015},
 "nomad_native":   {"farmers":.80,"soldiers":.12,"aristocrats":.04,"clergymen":.025,"artisans":.015},
}

# --------------------------------------------------- territory: region -> weights
R = {
 # Alaska & the north
 "USA_1":   {"aleut":3,"yupik":4,"inuit":1,"tlingit":2,"dene":2,"russian":1},
 "ENG_9":   {"dene":6,"inuit":3,"cree":1},
 "CAN_60":  {"inuit":4,"cree":5,"algonquian":1},
 "CAN_13":  {"salish":5,"tlingit":2,"chinook":2,"dene":1},
 "ENG_22":  {"blackfoot":6,"cree":4},
 "ENG_30":  {"cree":5,"blackfoot":3,"sioux":2},
 "ENG_36":  {"cree":5,"metis":3,"anishinaabe":2},
 "CAN_50":  {"cree":5,"anishinaabe":5},
 "CAN_46":  {"anglo_canadian":5,"anishinaabe":3,"haudenosaunee":2},
 "CAN_58":  {"french_canadian":9,"anglo_canadian":1},
 "ENG_68":  {"anglo_canadian":5,"scottish":2,"algonquian":2,"irish":1},
 "ENG_74":  {"anglo_canadian":4,"irish":3,"inuit":2,"algonquian":1,"portuguese":1},
 # United States
 "USA_247": {"yankee":8,"algonquian":2},
 "USA_243": {"yankee":10},
 "USA_232": {"yankee":8,"haudenosaunee":2},
 "USA_231": {"yankee":10},
 "USA_223": {"yankee":5,"north_german":3,"irish":2},
 "USA_219": {"dixie":5,"afro_american":5},
 "USA_218": {"dixie":9,"afro_american":1},
 "USA_211": {"dixie":5,"afro_american":5},
 "USA_2556":{"dixie":5,"afro_american":4,"cherokee":1},
 "USA_205": {"dixie":4,"afro_american":6},
 "USA_201": {"dixie":4,"afro_american":3,"creek":2,"cherokee":1},
 "USA_200": {"seminole":55,"spanish":25,"afro_american":20},
 "USA_196": {"creek":5,"choctaw":2,"dixie":2,"afro_american":1},
 "USA_194": {"choctaw":5,"chickasaw":2,"dixie":2,"afro_american":1},
 "USA_188": {"dixie":5,"cherokee":3,"chickasaw":2},
 "USA_185": {"dixie":8,"afro_american":2},
 "USA_178": {"yankee":6,"anishinaabe":4},
 "USA_176": {"anishinaabe":7,"french_creole":3},
 "USA_170": {"anishinaabe":6,"yankee":4},
 "USA_168": {"anishinaabe":5,"french_creole":3,"yankee":2},
 "USA_162": {"anishinaabe":10},
 "USA_158": {"anishinaabe":6,"sioux":4},
 "USA_151": {"sioux":6,"anishinaabe":4},
 "USA_148": {"osage":5,"french_creole":3,"dixie":2},
 "USA_144": {"osage":5,"choctaw":3,"french_creole":2},
 "USA_139": {"french_creole":4,"afro_american":4,"choctaw":2},
 "USA_129": {"osage":4,"comanche":4,"pawnee":2},
 "USA_126": {"osage":3,"pawnee":4,"comanche":3},
 "USA_124": {"pawnee":6,"sioux":4},
 "USA_121": {"sioux":10},
 "USA_118": {"mandan_arikara":5,"sioux":5},
 "USA_116": {"blackfoot":6,"crow":4},
 "USA_111": {"shoshone":6,"crow":4},
 "USA_106": {"pueblo":4,"navajo":2,"apache":2,"criollo":1,"mestizo":1},
 "USA_91":  {"nez_perce":6,"shoshone":4},
 "USA_81":  {"chinook":6,"nez_perce":4},
 "USA_78":  {"salish":6,"chinook":4},
 "TEX_132": {"comanche":5,"apache":2,"mestizo":2,"criollo":1},
 # Mexico
 "MEX_85":  {"california_nations":8,"criollo":1,"mestizo":1},
 "MEX_94":  {"shoshone":10},
 "MEX_97":  {"shoshone":10},
 "MEX_100": {"piman":5,"apache":3,"navajo":2},
 "MEX_103": {"apache":6,"piman":4},
 "MEX_2138":{"yaqui":4,"piman":3,"mestizo":2,"criollo":1},
 "MEX_2142":{"tarahumara":4,"apache":1,"mestizo":3,"criollo":2},
 "MEX_2151":{"mestizo":5,"criollo":4,"tarahumara":1},
 "MEX_2149":{"mestizo":5,"criollo":4,"comanche":1},
 "MEX_2161":{"mestizo":4,"criollo":2,"purepecha":2,"nahua":2},
 "MEX_2159":{"huastec":3,"totonac":3,"nahua":2,"mestizo":2},
 "MEX_2170":{"purepecha":2,"mixtec":3,"zapotec":3,"nahua":2},
 "MEX_2172":{"nahua":5,"otomi":2,"criollo":2,"mestizo":1},
 "MEX_2181":{"maya":5,"zapotec":3,"nahua":2},
 "MEX_2183":{"maya":10},
 # Central America
 "UCA_2186":{"maya":58,"mestizo":30,"criollo":10,"spanish":2},
 "UCA_2191":{"nahua":5,"mestizo":5},
 "UCA_2193":{"mestizo":5,"maya":3,"miskito":2},
 "UCA_2197":{"mestizo":5,"miskito":3,"criollo":2},
 "UCA_2201":{"criollo":5,"mestizo":5},
 "CLM_1723":{"mestizo":5,"afro_caribbean":3,"criollo":2},
 # Caribbean
 "SPA_2209":{"criollo":4,"afro_caribbean":4,"spanish":2,"taino_remnant":1},
 "HAI_2213":{"afro_caribbean":7,"criollo":2,"french_creole":1,"taino_remnant":1},
 "ENG_203": {"afro_caribbean":8,"british":2},
 "ENG_2224":{"afro_caribbean":62,"criollo":20,"spanish":8,"british":7,"taino_remnant":2,"portuguese":1},
 "ENG_2228":{"afro_caribbean":7,"british":2,"french":1},
 # Hawaii left alone
 "HAW_658": {},
}

# NO name-based overrides. Six North American provinces carry northern place names
# (Arviat, Baffin Island, Attawapiskat, Fort Chimo, Echo Bay, Nunavut) while sitting in
# Texas, the Lesser Antilles, Guatemala, Pennsylvania and Cuba. The names are wrong in
# HPM's definition.csv; the region assignments are right. Keying overrides off the names
# put Inuit in Texas and Cree in Guatemala.
STRAY = {}

# Province-level culture weights. Several HPM regions span completely different cultural
# zones -- USA_106 runs from Santa Fe to Denver, MEX_2170 from Michoacan to Oaxaca -- so
# a single weight set per region smears peoples across country they never occupied.
PROV = {
 # New Mexico / Colorado: Hispanic in the south, Plains and Ute in the north
 103:{"criollo":4,"mestizo":3,"pueblo":3},             # Santa Fe
 106:{"arapaho":5,"cheyenne":3,"ute":2},               # Denver
 108:{"ute":6,"pueblo":2,"criollo":2},                 # Alamosa
 109:{"ute":4,"arapaho":3,"comanche":2,"criollo":1},   # Pueblo
 # Wyoming / western Colorado
 107:{"ute":8,"shoshone":2},                           # Grand Junction
 110:{"arapaho":5,"cheyenne":3,"sioux":2},             # Cheyenne
 111:{"crow":6,"shoshone":4},                          # Cody
 112:{"arapaho":4,"crow":3,"shoshone":3},              # Casper
 # Texas: Caddo in the east, Comanche on the plains, Tejanos on the Rio Grande
 43: {"caddo":5,"comanche":3,"mestizo":2},             # "Arviat", east Texas
 132:{"caddo":4,"comanche":3,"mestizo":3},             # Houston
 133:{"comanche":6,"mestizo":3,"criollo":1},           # Austin
 134:{"comanche":7,"caddo":3},                         # Dallas
 135:{"comanche":10},                                  # Lubbock
 136:{"mestizo":4,"criollo":3,"apache":3},             # El Paso
 137:{"mestizo":5,"criollo":3,"comanche":2},           # San Antonio
 138:{"mestizo":6,"criollo":3,"comanche":1},           # Laredo
 # Oklahoma
 129:{"comanche":5,"osage":3,"pawnee":2},
 130:{"osage":5,"choctaw":3,"caddo":2},
 131:{"osage":5,"caddo":3,"comanche":2},
 # Cherokee and Creek heartlands -- essentially no white settlement before the 1810s
 2556:{"cherokee":8,"dixie":2},                        # Asheville
 207:{"dixie":5,"afro_american":5}, 208:{"dixie":6,"afro_american":4},
 209:{"dixie":6,"afro_american":4}, 210:{"dixie":4,"afro_american":6},
 190:{"cherokee":6,"dixie":4},                         # Knoxville
 191:{"cherokee":7,"dixie":3},                         # Chattanooga
 188:{"dixie":7,"afro_american":2,"chickasaw":1},      # Nashville
 189:{"chickasaw":6,"choctaw":2,"dixie":2},            # Memphis
 201:{"creek":5,"cherokee":4,"dixie":1},               # Atlanta
 2555:{"dixie":5,"afro_american":4,"creek":1},         # Augusta
 204:{"dixie":4,"afro_american":6},                    # Savannah
 202:{"creek":5,"seminole":2,"dixie":2,"afro_american":1},  # Valdosta
 # Michoacan is Purepecha; Oaxaca is Zapotec and Mixtec; Guerrero is Nahua and Mixtec
 2170:{"purepecha":8,"mestizo":2},                     # Morelia
 2171:{"purepecha":7,"nahua":1,"mestizo":2},           # Los Alaniles
 2177:{"zapotec":58,"mixtec":29,"mestizo":10,"spanish":3},  # Oaxaca
 2178:{"zapotec":5,"mixtec":4,"mestizo":1},            # Collataro
 2179:{"nahua":29,"mixtec":19,"mestizo":29,"afro_caribbean":19,"spanish":4},  # Acapulco, Manila trade
 2180:{"nahua":5,"mixtec":3,"mestizo":2},              # Chilpancingo
 # Bajio and the west
 2166:{"mestizo":50,"criollo":27,"nahua":19,"spanish":4},  # Guadalajara
 2167:{"mestizo":39,"criollo":29,"otomi":19,"purepecha":4,"spanish":9},  # Guanajuato
 2161:{"mestizo":4,"nahua":3,"purepecha":2,"criollo":1},  # Tepic
 2168:{"mestizo":4,"nahua":3,"purepecha":2,"criollo":1},  # Puerto Vallarta
 2169:{"mestizo":4,"purepecha":3,"nahua":2,"criollo":1},  # Colima
 # Alaska: the Aleutians are Unangax, the Yukon delta Yup'ik, the panhandle Tlingit,
 # the interior Dene. One mix for all of Alaska made Dutch Harbor 59% Yup'ik.
 1:{"tlingit":8,"russian":2},                         # Sitka, the Russian capital
 2:{"tlingit":9,"russian":1},                         # Yakutat
 3:{"dene":5,"aleut":3,"yupik":1,"russian":1},        # Kenai
 4:{"aleut":9,"russian":1},                           # Dutch Harbor
 5:{"yupik":10},                                      # Unalakleet
 2599:{"dene":10}, 2630:{"dene":10}, 2631:{"dene":9,"yupik":1},
 # Great Basin: Utah is Ute country, Nevada is Western Shoshone and Paiute
 97:{"ute":7,"shoshone":3}, 98:{"ute":6,"shoshone":4}, 99:{"ute":7,"shoshone":3},
 # The Caribbean was not one place. Spanish, British, French and Danish islands had
 # wholly different populations, and a single regional mix gave Puerto Rico, Antigua
 # and Saint Kitts identical percentages to the point.
 2222:{"criollo":52,"afro_caribbean":44,"spanish":4},  # Puerto Rico, largely free
 2223:{"afro_caribbean":8,"british":1,"criollo":1},              # Saint Thomas (Danish)
 2224:{"afro_caribbean":9,"british":1},                          # Antigua
 2225:{"afro_caribbean":9,"british":1},                          # Montserrat
 2226:{"afro_caribbean":9,"british":1},                          # Tortola
 2227:{"afro_caribbean":9,"british":1},                          # Saint Kitts
 2230:{"afro_caribbean":9,"french":1},                           # Guadeloupe
 2236:{"afro_caribbean":8,"french":1,"british":1},               # Saint Martin
 45:{"afro_caribbean":8,"british":1,"criollo":1},                # "Baffin Island"
 2228:{"afro_caribbean":9,"french":1},                           # Martinique
 2229:{"afro_caribbean":8,"british":2},                          # Barbados
 2231:{"afro_caribbean":9,"french":1}, 2232:{"afro_caribbean":9,"british":1},
 2233:{"afro_caribbean":9,"british":1}, 2409:{"afro_caribbean":9,"british":1},
 2234:{"afro_caribbean":7,"criollo":3}, 2235:{"afro_caribbean":6,"criollo":4},
 2237:{"afro_caribbean":72,"spanish":20,"british":8},            # Trinidad
 2238:{"afro_caribbean":9,"british":1},                          # Tobago
 203:{"british":6,"afro_caribbean":4},                           # Bermuda
 2217:{"afro_caribbean":9,"british":1},                          # Jamaica
 2218:{"afro_caribbean":6,"british":4}, 2219:{"afro_caribbean":6,"british":4},
 2220:{"afro_caribbean":6,"british":4},
 2209:{"criollo":44,"afro_caribbean":40,"spanish":16},           # Havana
 2210:{"criollo":52,"afro_caribbean":45,"spanish":3},
 2211:{"criollo":52,"afro_caribbean":45,"spanish":3},
 2212:{"criollo":42,"afro_caribbean":54,"spanish":4},
 44:{"criollo":52,"afro_caribbean":45,"spanish":3},              # "Echo Bay", Cuba
 2213:{"afro_caribbean":9,"french_creole":1},                    # Port-au-Prince
 2215:{"afro_caribbean":9,"french_creole":1},                    # Cap-Haitien
 2214:{"criollo":5,"afro_caribbean":4,"taino_remnant":1},        # Santo Domingo
 2216:{"criollo":5,"afro_caribbean":4,"taino_remnant":1},        # La Vega
 # Central Mexico. Spanish here means peninsulares -- the audiencia, the Consulado,
 # the higher clergy and the mining houses -- not the criollo population they governed.
 2172:{"nahua":50,"criollo":17,"mestizo":13,"otomi":9,"spanish":11},   # Mexico City
 2173:{"nahua":42,"otomi":22,"criollo":17,"mestizo":16,"spanish":3},   # Queretaro
 2174:{"nahua":58,"otomi":14,"mestizo":16,"criollo":11,"spanish":1},   # Toluca
 2175:{"nahua":52,"otomi":20,"mestizo":16,"criollo":11,"spanish":1},   # Tulancingo
 2176:{"nahua":55,"mestizo":17,"criollo":20,"spanish":8},              # Puebla
 # mining country: Guanajuato and Zacatecas drew the largest European concentrations
 # outside the capital
 2158:{"mestizo":50,"criollo":36,"spanish":9,"tarahumara":5},          # Zacatecas
 2153:{"mestizo":54,"criollo":38,"spanish":3,"tarahumara":5},          # Durango
 2160:{"mestizo":56,"criollo":40,"spanish":4},                         # Aguascalientes
 # Huasteca and the Gulf
 2159:{"huastec":3,"otomi":2,"mestizo":3,"criollo":2}, # San Luis Potosi
 2162:{"totonac":28,"nahua":19,"mestizo":28,"afro_caribbean":9,"criollo":9,"spanish":7},  # Veracruz, port of entry
 2163:{"huastec":5,"mestizo":3,"criollo":2},           # Tampico
 2164:{"nahua":4,"maya":2,"mestizo":3,"criollo":1},    # Minatitlan
}

# Within a region, how settler population was actually spread in 1800. Without this the
# 25,000 Hispanic New Mexicans get shared out by HPM's 1836 city sizes, which hands a
# third of them to Denver -- a place with no Hispanic settlement whatsoever in 1800.
PSHARE = {
 103:0.90, 106:0.01, 108:0.05, 109:0.04,               # Santa Fe holds New Mexico
 107:0.25, 110:0.25, 111:0.25, 112:0.25,
 137:0.45, 138:0.25, 136:0.20, 133:0.05, 132:0.03, 134:0.01, 135:0.005, 43:0.005,
 2556:0.05, 207:0.30, 208:0.25, 209:0.25, 210:0.15,
 190:0.10, 191:0.08, 188:0.52, 189:0.30,
 201:0.12, 2555:0.33, 204:0.40, 202:0.15,
}

# ------------------------------------------------------------------ distribute
claims = collections.defaultdict(dict)      # prov -> {culture: weight}
for p, v in NA.items():
    w = PROV.get(p) or R.get(v["rg"])
    if w: claims[p] = dict(w)

unassigned = [p for p in NA if p not in claims or not claims[p]]
print("provinces with no culture assignment:", len(unassigned),
      [NA[p]["n"] for p in unassigned][:10])

# 1800 settler population by region, in thousands (US census of 1800; British North
# America from colonial returns). HPM's 1836 distribution is useless for this: it puts
# the Midwest on a par with the seaboard, when in 1800 Ohio held 45,000 people and
# Illinois about 2,000. Settler weight = regional 1800 total x the province's share of
# its region in HPM's data (a proxy for which spots inside a region were settled first).
F1800 = {
 "USA_247":490,"USA_243":743,"USA_232":589,"USA_231":211,"USA_223":602,"USA_219":406,
 "USA_218":60,"USA_211":820,"USA_2556":478,"USA_205":346,"USA_201":163,"USA_200":5,
 "USA_196":1,"USA_194":8,"USA_188":106,"USA_185":221,"USA_178":45,"USA_176":4,
 "USA_170":5,"USA_168":2,"USA_162":1,"USA_158":1,"USA_151":1,"USA_148":10,
 "USA_144":1,"USA_139":50,"USA_129":1,"USA_126":1,"USA_124":1,"USA_121":1,
 "USA_118":1,"USA_116":1,"USA_111":1,"USA_106":25,"USA_91":1,"USA_81":1,"USA_78":1,
 "TEX_132":5,"CAN_58":220,"CAN_46":60,"ENG_68":80,"ENG_74":20,"ENG_36":3,"ENG_30":2,
 "ENG_22":2,"CAN_13":2,"CAN_50":2,"CAN_60":2,"ENG_9":1,"USA_1":1,
 "MEX_85":18,"MEX_94":1,"MEX_97":1,"MEX_100":2,"MEX_103":4,
}
# settler cultures follow 1800 settlement; natives follow land area
hpm_pop = collections.Counter()
for pid, t, c, r, sz in D["pops"]:
    if pid in NA: hpm_pop[pid] += sz
SETTLER = {"yankee","dixie","anglo_canadian","french_canadian","british","irish","scottish",
           "french","spanish","portuguese","russian","north_german","criollo","mestizo",
           "afro_american","afro_caribbean","french_creole"}

share = collections.defaultdict(dict)       # culture -> {prov: raw weight}
for p, w in claims.items():
    for cu, k in w.items():
        if cu in SETTLER:
            rg = NA[p]["rg"]
            if rg in F1800:
                if p in PSHARE:
                    sh = PSHARE[p]
                else:
                    rtot = sum(hpm_pop[q] for q in NA if NA[q]["rg"] == rg and q not in PSHARE) or 1
                    rem = 1.0 - sum(PSHARE[q] for q in NA if NA[q]["rg"] == rg and q in PSHARE)
                    sh = max(rem, 0.0) * hpm_pop[p] / rtot
                base = F1800[rg] * 1000 * sh
            else:
                base = hpm_pop[p]
        elif C[cu][0] == "mesoamerican":
            # Settled agriculturalists cluster where the good land is, and HPM's 1836
            # pattern is a fair proxy for that. Weighting them by province area instead
            # starved the dense central basin -- Nahua were being pushed out of small
            # Puebla-sized provinces into whatever large one was adjacent.
            base = max(hpm_pop[p], 1)
        else:
            base = NA[p]["px"]
        share[cu][p] = k * max(base, 1)

# ---------------------------------------------------------------- two margins
# The weights say what the mix inside a province should look like; the culture
# estimates say what each people's national total must be. Distributing each culture
# independently satisfies the second and ignores the first, which is why Morelia came
# out Nahua rather than Purepecha: Nahua is a large nation and its spill dwarfed the
# local weighting. Iterative proportional fitting satisfies both margins at once.
prov_total = collections.Counter()
for cu, (grp, rel, arch, real) in C.items():
    ps = share.get(cu)
    if not ps: continue
    tgt = real * SCALE
    tot = sum(ps.values())
    for q, wv in ps.items():
        prov_total[q] += tgt * wv / tot

cells = {}                                   # (prov, culture) -> people
for q, w in claims.items():
    tw = sum(w.values()) or 1
    for cu, k in w.items():
        if cu in C: cells[(q, cu)] = prov_total[q] * k / tw

col_t = {cu: C[cu][3] * SCALE for cu in C if any(c == cu for _, c in cells)}
row_t = dict(prov_total)
for _ in range(60):
    cs = collections.Counter()
    for (q, cu), v in cells.items(): cs[cu] += v
    for key in cells:
        f = col_t.get(key[1], 0) / cs[key[1]] if cs[key[1]] else 0
        cells[key] *= f
    rs = collections.Counter()
    for (q, cu), v in cells.items(): rs[q] += v
    for key in cells:
        f = row_t[key[0]] / rs[key[0]] if rs[key[0]] else 0
        cells[key] *= f

err = max(abs(sum(v for (q, cu), v in cells.items() if cu == c) - col_t[c]) / max(col_t[c], 1)
          for c in col_t)
print(f"IPF: worst culture-total error {err*100:.2f}%")

by_prov = collections.defaultdict(dict)
for (q, cu), v in cells.items():
    if v >= 10: by_prov[q][cu] = v

out_pops = []
summary = collections.Counter()
for q, mix in by_prov.items():
    for cu, v in mix.items():
        grp, rel, arch, real = C[cu]
        n = int(round(v))
        if n < 10: continue
        rows = [(ty, n * fr) for ty, fr in ARCH[arch].items()]
        placed = 0
        for i, (ty, raw) in enumerate(rows):
            sz = int(round(raw)) if i < len(rows) - 1 else n - placed
            placed += sz
            if sz < 5: continue
            out_pops.append({"province": q, "type": ty, "culture": PRETTY.get(cu, cu),
                             "religion": rel, "size": sz})
            summary[cu] += sz

# any claimed province that still ended up with nothing gets a token population of its
# top-weighted culture, so the merge overwrites it rather than leaving 1836 data behind
have = set(r["province"] for r in out_pops)
filled = 0
for p, w in claims.items():
    if p in have or not w: continue
    cu = max(w, key=lambda c: w[c])
    grp, rel, arch, real = C[cu]
    ty = max(ARCH[arch], key=lambda t: ARCH[arch][t])
    out_pops.append({"province": p, "type": ty, "culture": PRETTY.get(cu, cu),
                     "religion": rel, "size": 20})
    summary[cu] += 20; filled += 1
print("\ntoken populations written for", filled, "frontier provinces")
print("NA provinces covered:", len(set(r['province'] for r in out_pops)), "of", len(NA))

# Primary and accepted cultures. Pops of the primary or an accepted culture never
# assimilate; everyone else drifts toward the dominant accepted culture of their
# province. Mexico is deliberately primary Mestizo with Criollo accepted: that makes
# Europeans in criollo cities become Criollo, Europeans and Indigenous pops in mestizo
# country become Mestizo, and criollos stay criollo -- three of the four rules for free.
# Colonial tags begin as the crown governed them -- peninsular Spanish primary, criollo
# accepted -- and the independence event rewrites them to the people who actually lived
# there. "independence" below is emitted as a country event; see WP02a section 16.
# Colonial administrations get their own tags so the viceroyalty and the republic that
# replaces it are never the same object. Independence fires change_tag_no_core_switch
# into the successor, then rewrites the cultures. Colonial colours are the successor's
# blended halfway to the metropole's, so they read as colonies but stay distinct.
SPA_COL = (170, 50, 50)
POR_COL = (40, 110, 60)

def blend(a, b, t=0.5):
    return [int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)]

import json as _json
_C = _json.load(open(f"{W}/world_data.json"))["countries"]
def col_for(succ, metro):
    base = _C.get(succ, {}).get("color", [130, 130, 130])
    return blend(base, metro, 0.45)

COLONIES = [
 # tag, name, successor, overlord, accepted after independence
 ("NSP", "Viceroyalty of New Spain",             "MEX", "SPA", ["criollo","nahua","maya"],  "mestizo"),
 ("CGG", "Captaincy General of Guatemala",       "UCA", "SPA", ["criollo","maya"],          "mestizo"),
 ("VNG", "Viceroyalty of New Granada",           "CLM", "SPA", ["criollo"],                 "mestizo"),
 ("CGV", "Captaincy General of Venezuela",       "VNZ", "SPA", ["criollo"],                 "mestizo"),
 ("QIT", "Presidency of Quito",                  "ECU", "SPA", ["criollo"],                 "mestizo"),
 ("VPE", "Viceroyalty of Peru",                  "PEU", "SPA", ["criollo"],                 "mestizo"),
 ("CHQ", "Royal Audiencia of Charcas",           "BOL", "SPA", ["criollo"],                 "mestizo"),
 ("VRP", "Viceroyalty of the Rio de la Plata",   "LPL", "SPA", ["criollo"],                 "criollo"),
 ("CGC", "Captaincy General of Chile",           "CHL", "SPA", ["criollo"],                 "criollo"),
 ("CBA", "Captaincy General of Cuba",            "CUB", "SPA", ["AfroCaribbean"],           "criollo"),
 ("PTR", "Puerto Rico",                          "PRI", "SPA", ["AfroCaribbean"],           "criollo"),
 ("EBR", "State of Brazil",                      "BRZ", "POR", ["criollo"],                 "criollo"),
]

COUNTRY_CULTURES = {
 "USA": {"primary":"yankee", "accepted":["dixie"]},
 "SPA": {"primary":"spanish", "accepted":["criollo","basque","catalan"]},
 "POR": {"primary":"portuguese", "accepted":["criollo"]},
 "HAI": {"primary":"AfroCaribbean", "accepted":["FrenchCreole"]},
 "CAN": {"primary":"AngloCanadian", "accepted":["FrenchCanadian","scottish","irish"]},
 "ENG": {"primary":"british", "accepted":["AngloCanadian","scottish","irish","australian"]},
 "FRA": {"primary":"french", "accepted":["FrenchCanadian","FrenchCreole","breton","occitan"]},
 "RUS": {"primary":"russian", "accepted":["aleut","tlingit"]},
 "DEN": {"primary":"danish", "accepted":["AfroCaribbean"]},
 "NET": {"primary":"dutch", "accepted":["AfroCaribbean"]},
 "TEX": {"primary":"mestizo", "accepted":["criollo","comanche"]},
 # the republics as they stand once free, for the case where they are released the
 # ordinary way rather than through the colonial tag
 "MEX": {"primary":"mestizo", "accepted":["criollo","nahua","maya"]},
 "UCA": {"primary":"mestizo", "accepted":["criollo","maya"]},
 "CLM": {"primary":"mestizo", "accepted":["criollo"]},
 "VNZ": {"primary":"mestizo", "accepted":["criollo"]},
 "ECU": {"primary":"mestizo", "accepted":["criollo"]},
 "PEU": {"primary":"mestizo", "accepted":["criollo"]},
 "BOL": {"primary":"mestizo", "accepted":["criollo"]},
 "LPL": {"primary":"criollo", "accepted":["mestizo"]},
 "CHL": {"primary":"criollo", "accepted":["mestizo"]},
 "CUB": {"primary":"criollo", "accepted":["AfroCaribbean"]},
 "PRI": {"primary":"criollo", "accepted":["AfroCaribbean"]},
 "BRZ": {"primary":"criollo", "accepted":["AfroCaribbean"]},
}
for tag, name, succ, metro, iacc, iprim in COLONIES:
    COUNTRY_CULTURES[tag] = {
        "primary": "spanish" if metro == "SPA" else "portuguese",
        "accepted": ["criollo"],
        "becomes": succ,
        "create": {"name": name, "overlord": metro, "relationship": "colony",
                   "color": col_for(succ, SPA_COL if metro == "SPA" else POR_COL)},
        "independence": {"primary": iprim, "accepted": iacc},
    }

json.dump({"country_cultures": COUNTRY_CULTURES,
           "pops": out_pops,
           "culture_groups": {PRETTY.get(c, c): v[0] for c, v in C.items()},
           "religion_hint": {PRETTY.get(c, c): v[1] for c, v in C.items()}},
          open(f"{W}/na1800.json", "w"))
