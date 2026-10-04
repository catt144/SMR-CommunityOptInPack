# Opt-In Modules workbench

This is a dev-only sibling mod, never uploaded. Its required dependency loads
Opt-In Modules first. Enable both in the Mod Manager and fully restart the game.
Staged switches appear on the existing Opt-In Modules options page. Their account
keys, classes and save names are already the production names.

Local install (PowerShell):

```powershell
New-Item -ItemType Junction -Path "$env:APPDATA\Surviving Mars Relaunched\Mods\SMR-OptInPack-Workbench" -Target "B:\Dev\SMR\SMR-OptInPack\staging"
```

`modules.json` declares each resident's complete file ownership, code order,
option names and optional regeneration command. Paths are relative to this mod;
code and defaults remain in `metadata.lua`, and editor items in `items.lua`.
`python tools/workbench.py` from the repo root checks these surfaces and package
exclusion. The bridge adds option metadata at runtime without changing the
production editor item list or writing a second account namespace.

For a module already authorized to ship:

```text
python tools/promote_module.py Arboretum --check
python tools/promote_module.py Arboretum
```

The first command prints the plan without writes. The second moves owned files
and registrations, regenerates declared outputs, runs the workbench guard,
Lua parsing and doccheck, and restores touched bytes on failure. It neither
commits nor uploads. Review module documentation and the release outbox as part
of the authorized release. Arboretum is held until after launch (owner,
2026-10-03); its category and footprint decisions remain in D19/OI-47/OI-48.

The current promote route handles owned Code/Data/tools/UI files. It refuses
custom imported models: merging their shared ArtSpec and entity registrations
needs a specific extension to the tool. Destination collisions also stop before
any move. Both mods' editor files use the ordinary tab-indented serialization;
an unfamiliar layout is refused rather than guessed.

Content already placed is retained when a module switch is off. Before removing
the workbench, promote that content with its final class names or follow the
module's removal instructions. The engine can still show a missing-workbench
warning for an older save after promotion; resaving updates the enabled-mod list.
Promotion is not a missing-mod-warning bypass.
