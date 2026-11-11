# Installing HPM 1800

You do not need Python, git or any of the build system to play this. You need
*Victoria II*, a copy of the Historical Project Mod, and the patch from the
[Releases page](https://github.com/andyluna999/Victoria-2-1800-Mod/releases).

## What you need first

- **Victoria II** with *A House Divided* and *Heart of Darkness*
- **HPM 0.4.6.3**, installed as a mod and working. Start it once at the 1836 date
  and confirm it loads before going any further — if HPM is broken, this will be
  broken in ways that are much harder to diagnose.

## Installing

**1. Back up your HPM folder.** The patch overwrites several thousand files and
there is no uninstaller. Copy the whole thing somewhere safe:

```
Victoria 2\mod\HPM  ->  Victoria 2\mod\HPM_backup
```

**2. Start from an unmodified HPM.** If you have made your own changes to HPM, or
have another patch applied over it, remove the mod folder and reinstall HPM
cleanly. The patch assumes it is landing on stock HPM, and the first thing that
breaks otherwise will not look like it has anything to do with the cause.

**3. Extract `HPM_1800_patch.zip` over the mod folder**, so that the `HPM` folder
inside the zip merges into `Victoria 2\mod\HPM`. Say yes to replacing files.

**4. Start a new game.** Not a save. Orders of battle, party lists, pop data and
accepted cultures are all read once when a game begins, so an existing save will
load and behave strangely.

The start date should read **1 January 1800**.

## Checking it worked

Pick **Spain**. You should see the Viceroyalty of New Spain, the Viceroyalty of
Peru, New Granada, Río de la Plata and the Captaincy General of Chile on the map,
and France should be a Republic under Bonaparte.

Pick **the Viceroyalty of New Spain**. It should have around eighteen regiments,
a decisions tab with eight entries, and a treasury that is not zero.

If the game crashes at country selection or the map is empty, the patch has landed
on something other than stock HPM. Restore your backup and start again from step 2.

## Reporting a problem

The game log is far more useful than a description, and it is at:

```
Documents\Paradox Interactive\Victoria II\HPM\logs\game.log
```

It records every event that fired and when. Most of the bugs found so far were
invisible from inside the game and obvious from one line of that file.

Please say which country you were playing, what year it was, and what you expected
instead.

## Known limits

- **Saves do not survive a patch.** Every update needs a fresh start.
- **The 1836 content is still there** and much of it assumes a world that this
  start date has not produced yet. Expect oddities after about 1850.
- **The AI plays the period better than it plays the aftermath.** The wars of
  independence and the Napoleonic arc are scripted closely; what happens
  afterwards is much more open, and much less tested.
