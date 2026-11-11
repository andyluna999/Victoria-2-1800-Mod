"""Starting technology for 1800.

HPM's grants describe 1836. Ninety-three countries begin with post-Napoleonic military
thought, in a world where Napoleon has been First Consul for seven weeks. Ninety-six
have the piston steam engine, sixty-four the hot blast — which was invented in 1828.

Victoria II's tech tree is gated at 1836 throughout, so there is no pre-1836 tier to
drop into; the only lever is which level-one technologies a country starts holding.
That is enough. The rule below keeps what genuinely existed by 1800, gives the
industrial and naval techs only to the handful of states that actually had them, and
strips the rest.
"""
import re, glob, os, collections

MOD = "/home/claude/build/HPM"

# existed by 1800 and may be held by anyone who had an army, a press or a guild
UNIVERSAL = {
 "flintlock_rifles",                  # the standard musket for a century
 "bronze_muzzle_loaded_artillery",
 "the_command_principle",
 "army_command_principle",
 "guild_based_production",            # the pre-factory workshop
 "enlightenment_thought",
 "classicism_n_early_romanticism",
 "no_standard",
 "nonstate_consciousness",
}
# existed by 1800 but only in the places that had the institutions
ADVANCED = {
 "late_enlightenment_philosophy": {"ENG","FRA","PRU","AUS","NET","SWE","DEN","USA","SWI","LIG","SAR","TUS","PAP","SPA","POR","RUS"},
 "private_banks":        {"ENG","NET","FRA","USA","SWE","LIG","HAM","LUB","BRE"},
 "piston_steam_engine":  {"ENG","FRA","NET","USA","PRU"},
 "mechanical_production":{"ENG","FRA","NET","USA"},
 "post_nelsonian_thought":{"ENG","FRA","NET","DEN","SWE","SPA","USA","POR","RUS"},
 "military_staff_system":{"PRU","FRA","AUS","RUS","ENG"},
 "clipper_design":       {"ENG","USA","NET","FRA","DEN","SWE","POR","SPA"},
 "naval_design_bureaus": {"ENG","FRA","SPA","NET","RUS","DEN","SWE"},
 "alphabetic_flag_signaling": {"ENG","FRA","NET","DEN","SWE","SPA","USA","POR","RUS"},
 "early_classical_theory_and_critique": {"ENG","FRA","NET","USA","PRU","AUS"},
 "freedom_of_trade":     {"ENG","NET","USA"},
 "basic_chemistry":      {"ENG","FRA","PRU","AUS","SWE","NET"},
 "malthusian_thought":   {"ENG","FRA","NET","USA","PRU"},
}
# invented after 1800, or describing a world that has not happened yet
FORBIDDEN = {
 "post_napoleonic_thought",      # the campaigns it is named for are in the future
 "hot_blast",                    # 1828
 "experimental_railroad", "high_pressure_steam_engine", "steamers", "iron_steamers",
 "interchangeable_parts", "stock_exchange", "market_structure",
 "late_classical_theory", "introspectionism", "romanticism", "ideological_thought",
 "muzzle_loaded_rifles", "breech_loaded_rifles",
 "iron_muzzle_loaded_artillery", "iron_breech_loaded_artillery",
 "battleship_column_doctrine", "naval_professionalism", "army_professionalism",
 "fire_control_systems", "point_defense_system", "strategic_mobility",
 "military_plans", "military_statistics", "army_decision_making",
 "medicine", "state_n_government", "ad_hoc_money_bill_printing",
 "private_bank_money_bill_printing", "market_determined_prices",
}

stripped = collections.Counter(); kept = 0; files = 0
for f in glob.glob(f"{MOD}/history/countries/*.txt"):
    tag = os.path.basename(f)[:3]
    s = open(f, encoding="cp1252", errors="replace").read()
    parts = re.split(r"\n(?=\s*\d{3,4}\.\d{1,2}\.\d{1,2}\s*=)", s)
    head, tail = parts[0], ("\n" + "\n".join(parts[1:]) if len(parts) > 1 else "")
    before = head
    def keepit(name):
        if name in FORBIDDEN: return False
        if name in UNIVERSAL: return True
        if name in ADVANCED: return tag in ADVANCED[name]
        return True            # anything unlisted is left alone
    out = []
    for line in head.split("\n"):
        m = re.match(r"^\s*([a-z_]+)\s*=\s*1\s*$", line)
        if m and (m.group(1) in FORBIDDEN or m.group(1) in ADVANCED or m.group(1) in UNIVERSAL):
            if keepit(m.group(1)):
                out.append(line); globals()["kept"] = kept + 1
            else:
                stripped[m.group(1)] += 1
            continue
        out.append(line)
    head = "\n".join(out)
    if head != before:
        open(f, "w", encoding="cp1252", errors="replace", newline="\n").write(head + tail)
        files += 1

print(f"  country files adjusted            {files}")
print(f"  technology grants removed         {sum(stripped.values())}")
for k, v in stripped.most_common(10):
    print(f"    {k:<36}{v}")
