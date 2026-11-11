# HPM 1800

A conversion of the **Historical Project Mod** for *Victoria II* that moves the start
date from 1836 to **1 January 1800** — the last year of the Directory, three years
before the Louisiana Purchase, eight before Bayonne, and the beginning of the period
that produced every country in the Americas.

This is not a reskin of 1836. The world is rebuilt: Spain still holds an empire from
California to Tierra del Fuego, Saint-Domingue is in revolt, Bonaparte is First Consul,
and the technology tree starts where 1800 actually started.

## What it adds

**The Spanish American question.** Five viceroyalties, each with its own road out — a
junta in the King's name, a constitutional province of Cádiz, an autonomous kingdom, or
a republic. A separatism figure that every Bourbon reform moves, so a viceroy who
governs well for eight years arrives at the crisis of 1808 with credit banked and one
who enforces the Consolidación does not. Iturrigaray's night, Yermo's coup, the Grito,
Morillo's expedition, Riego's mutiny, and a Spain that gives up on a timer set by how
much it still holds.

**The Napoleonic arc.** Austerlitz, Jena, Wagram and the treaties that followed them,
each settlement waiting on its own battle. Then the retreat from Moscow, Tauroggen,
Leipzig, the abdication, Golfe-Juan and Waterloo — every one a fork that can go the
other way. Three endings: a Congress of Vienna, a Congress of Paris, or a peace of
exhaustion.

**The American tide.** Eleven frontier bands opening from 1805 to 1848 on two roads —
Dixie up from Louisiana into Texas, Yankee out of Ohio across the plains to Oregon.
Settlers are walked west province by province rather than left to the engine's
migration, so the frontier fills in the order it actually filled. Adams-Onís, the
empresario grants, the presidio line, and republics that declare when the settlers hold
the ground.

**Haiti, Brazil and the Plata.** Toussaint's army and the expeditions sent against it.
The Portuguese court's flight to Rio and the Empire that came out of it. The Congress of
Tucumán, San Martín's crossing of the Andes, and Bouchard taking Monterey under the flag
of a country four years old.

## Playing it

You do not need any of this to play. Download the patch from
[Releases](https://github.com/andyluna999/Victoria-2-1800-Mod/releases), extract it
over a clean install of HPM, and start a new game. Full instructions, including what
to do when it goes wrong, are in [docs/INSTALLING.md](docs/INSTALLING.md).

## Building

The mod is generated, not hand-edited. Put an unmodified copy of HPM at
`hpm/HPM - Copy`, then:

```sh
bash tools/make.sh
```

117 passes run over the pristine copy and write a complete mod to `build/HPM`. The
source is never modified. `data/` holds derived tables — the province index, the 1836
pop census, the colour map — that were produced once from HPM's own files and its map
images; the build copies them into `work/` on a fresh checkout.

Each pass is a single Python file that does one thing and explains why in its docstring.
The build is deterministic: running it twice produces byte-identical output.

## The audits

Five audit suites run at the end of every build and must pass:

| | |
|---|---|
| `lint.py` | 32 checks — syntax, keys, references, scope |
| `sweep.py` | 56 checks — balance, manpower, localisation |
| `deep_audit.py` | structural integrity against a recorded baseline |
| `chain_audit.py` | 38 checks — event chains, flags, reachability |
| `demographic_audit.py` | population, cultures, pop types |

They exist because this mod has been broken in every way a Paradox mod can be broken,
usually silently. Most checks were written the day a specific bug was found, and the
comment above each one says what it was.

## Requirements

*Victoria II* with **A House Divided** and **Heart of Darkness**, and a copy of the
**Historical Project Mod** to build against.

## Licence

See `LICENSE`. HPM and *Victoria II* are the property of their respective authors and
Paradox Interactive; nothing here redistributes either.
