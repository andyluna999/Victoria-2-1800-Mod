#!/bin/bash
# Reproducible build: always start from a pristine HPM, then apply every tool in order.
set -e
# Run from anywhere: the root is wherever this script's parent directory is,
# unless HPM1800_ROOT says otherwise.
ROOT="${HPM1800_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SRC="${HPM1800_SRC:-$ROOT/hpm/HPM - Copy}"
DST="${HPM1800_BUILD:-$ROOT/build/HPM}"
WORK="${HPM1800_WORK:-$ROOT/work}"
export HPM1800_ROOT HPM1800_SRC HPM1800_BUILD HPM1800_WORK

if [ ! -d "$SRC" ]; then
  echo "No pristine HPM found at: $SRC"
  echo "Put an unmodified copy of the Historical Project Mod there, or set HPM1800_SRC."
  exit 1
fi

cd "$ROOT"
mkdir -p "$WORK"
rm -rf "$DST"; mkdir -p "$(dirname "$DST")"; cp -r "$SRC" "$DST"
cd "$ROOT"
python3 tools/write_world.py
python3 tools/fix_parties.py
python3 tools/strip_1861.py
python3 tools/split_colonies.py
python3 tools/fix_louisiana.py
python3 tools/write_export.py
python3 tools/apply_export2.py   # the hand edits land here, so every
                                 # historical correction after this wins
python3 tools/apply_province_vars.py
python3 tools/apply_sa_layer.py
python3 tools/apply_europe_1800.py
python3 tools/europe_pops_1800.py
python3 tools/world_1800_political.py
# A country needs a party for every ideology its Upper House can turn. This must
# follow world_1800_political, which writes these country files from scratch.
python3 tools/colonial_parties.py
python3 tools/corrections_1800.py
# Venezuela has not been governed from Bogota since 1777. This must follow
# apply_sa_layer, which rewrites South America wholesale.
python3 tools/venezuela.py
python3 tools/venezuela_wars.py
python3 tools/gran_colombia.py
python3 tools/world_pops_1800.py
python3 tools/scotland_1800.py
python3 tools/british_isles_1800.py
python3 tools/world_demographics_1800.py
python3 tools/europe_poptypes_1800.py
python3 tools/fix_1800_governments.py
# follow every pass that writes common/countries, or those passes overwrite it.
python3 tools/country_layer_1800.py
python3 tools/accepted_cultures.py
python3 tools/industry_reforms_1800.py
python3 tools/tech_1800.py
python3 tools/tech_years.py
python3 tools/asia_1800_states.py
python3 tools/barbary_states.py
python3 tools/dependencies_1800.py
python3 tools/australia_1800.py
python3 tools/hejaz.py   # after dependencies_1800, whose file it edits
python3 tools/fix_1800_powers.py
python3 tools/treasuries_1800.py
python3 tools/capital_flight.py
python3 tools/americas_choices.py
python3 tools/brazil.py
python3 tools/divergence_nodes.py
python3 tools/apply_palette.py
python3 tools/second_coalition.py
# Hispaniola moves Santo Domingo to France, so it runs before the order of battle
# is placed: oob_relocate reads ownership from the map, and a pass that changes
# ownership afterwards leaves Spanish regiments recruiting from French soil.
python3 tools/hispaniola.py
# Hispaniola cannot be sold, because by 1803 France did not have it to sell.
python3 tools/hispaniola_not_for_sale.py
python3 tools/oob_new_tags.py
python3 tools/successor_armies.py
python3 tools/california_oob.py
python3 tools/leaders_1800.py
# Southeast Asia, corrected from a player report. This must follow leaders_1800,
# which rewrites every order of battle.
python3 tools/vietnam.py
# The Central Highlands were Jarai, not Vietnamese.
python3 tools/jarai.py
# The patterns behind the player reports, applied everywhere.
python3 tools/global_fixes.py
python3 tools/spheres_1800.py
python3 tools/navies_1800.py
python3 tools/oob_relocate.py
python3 tools/oob_unit_types.py
python3 tools/flags.py
python3 tools/bourbon_decisions.py
python3 tools/constitutional_track.py
python3 tools/louisiana.py
python3 tools/american_claims.py
python3 tools/peninsular_war.py
python3 tools/iturrigaray.py
python3 tools/latin_independence.py
python3 tools/yermo.py
python3 tools/separatism.py
python3 tools/civil_wars.py
python3 tools/independence_war.py
python3 tools/the_unredeemed.py
# Reform earns the loyalty the revolution did not.
python3 tools/the_reckoning.py
python3 tools/mexico_late.py
python3 tools/reclaim_cb.py
python3 tools/autonomous_kingdom.py
python3 tools/event_pictures.py
python3 tools/reconquest_cb.py
python3 tools/haiti_untouchable.py
python3 tools/war_names.py
python3 tools/restoration.py
# Settlers must be on the ground at the start: the engine cannot create a pop.
python3 tools/settler_seed.py
python3 tools/filibusters.py
python3 tools/american_expansion.py
python3 tools/filibuster_republics.py
python3 tools/coalitions.py
python3 tools/grande_armee.py
python3 tools/napoleonic_arc.py
# From Moscow to Waterloo: the three years the arc was missing.
python3 tools/napoleonic_fall.py
python3 tools/kingdoms.py
python3 tools/national_question.py
python3 tools/haiti_after.py
python3 tools/debug_tools.py
python3 tools/playtest_fixes.py
python3 tools/rebels_1800.py
python3 tools/spain_balance.py
# After every order-of-battle pass: it reads the final regiment homes.
python3 tools/soldier_pops.py
# twice: the first pass musters, the second covers provinces the re-homing moved
# regiments onto.
python3 tools/soldier_pops.py
# Written after the generic passes, which are the wrong tool for small nations.
python3 tools/native_warbands.py
python3 tools/haitian_army.py
python3 tools/bolivar.py
python3 tools/la_plata.py
# A country only gets the army its own file names.
python3 tools/declare_oob.py
# No army larger than a corps: a 200-regiment stack crashes the game.
python3 tools/split_armies.py
# Restore every harbour HPM shipped, and add the ports the period ran on.
python3 tools/ports.py
python3 tools/fix_navies.py
# Last of the content passes: it rewrites event windows, so anything that writes
# events after it would undo the widening. haiti_after.py did exactly that.
python3 tools/picture_mapping.py
# One key, one value: two passes were disagreeing and the filename decided.
python3 tools/dedupe_loc.py
# fire_only_once on a shared event fires it once for the world, not once each.
python3 tools/fire_once_per_country.py
# A decision is a standing policy; an event is a moment that arrives.
python3 tools/decision_cleanup.py
python3 tools/the_four_moments.py
python3 tools/widen_windows.py
python3 tools/demographic_audit.py
python3 tools/chain_audit.py
