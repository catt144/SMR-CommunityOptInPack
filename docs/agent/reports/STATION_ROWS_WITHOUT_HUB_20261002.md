# Station rows without a hub — brief 30, 2026-10-02

**Built; attended smoke NOT RUN.** This is the design pass authorized by the owner's
2026-10-02 ruling in the train spec §4.7. The depot infotip and the sitting are recorded
below as their units land. Brief 30 stays live until the owner passes the sitting.

Started at `ea6d43fb93ea2bf669be564229c414c713476455`; `git log --oneline -5` and
`git pull` ran first (already current). Executed model: Codex (GPT-6 per session
instructions; an exact backend model id is not exposed in this transcript).
`python tools/doccheck.py --emit-fingerprint` read installed build **25579348**.
Source tree: `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`.

## Design calls delegated by the brief

Every ordinary `Station` gets the existing native row and inline slider. The hub and
Elevator Depot keep their own panels. The states are Balanced → Export → Import →
Not accepted → Balanced. Ctrl+click copies the current mode and percentage to other
ordinary stations in the same city, including hubless stations, without advancing
the source. Not accepted still uses vanilla's flags and remembers the slider.

| Hubless state | Trains | Local drones |
|---|---|---|
| Balanced | Supply excess above the selected amount; receive up to it | Use it as the desired amount |
| Export | Supply stock above the minimum; refuse deliveries | Fill to capacity |
| Import | Receive up to the cap; never supply | May drain to zero |
| Not accepted | Vanilla disabled-resource drain | Vanilla disabled storage |

These are targets and bounds, not promises that stock exists elsewhere. Untouched
Balanced rows use the live absolute vanilla dial; an edited slider is a percentage
of live capacity and follows upgrades. The hubless tooltip describes other stations
as suppliers/receivers, without promising a hub or a central surplus sink.

Joining a hub switches to that hub's existing settings and default Balanced pin.
The station's independent settings remain dormant. Leaving resumes them; a station
never configured outside a hub resumes the vanilla dial as its Balanced target.
Rejoining restores the hub's table. Neither set is copied into the other. Baselines
from resources present only in the old set are cleared at this change of ownership.

## Mechanism and save footprint

SOURCE: `40_TrainDistribution.lua` keeps the existing hub allocation function and adds
a separate line-local allocation view. No hub object or hub implementation is needed
for this path. It wraps native `Train:TransferCargo` / `UnloadAll`, uses the existing
temporary-claim helper and synchronous capacity/enabled answers, and leaves native
code to write cargo and reservations. It uses the native should-move input to find
an empty pickup trip, as the hub path already does; no scheduler or movement changes.

SOURCE: native cargo bodies are `Lua/Units/Train.lua:744-831,862-1043` on archived
**1.1.1.406343 / build 25579348**. The hubless smoke checks byte parity of that file,
Station, MultiResourceDepot and MultiResourceCubeVisuals against the older archive
consumed by the existing harness. Late assignments exceeding a changed cap stay aboard
whole; vanilla may unload them at another accepting stop. No hub overflow exception
applies to a hubless row. A depot endpoint retains its own row writers and native
storage; its exchange is bounded by the ordinary station's row.

New persisted name, also in FIX_POLICY's inventory: **`SMROptIn_station_rows`**, on a
vanilla station, containing only resource keys and `{mode, percent}` data. This is
the inert-field rung: settings must survive a save in a colony with no mod-owned hub,
while vanilla has no field that represents per-resource percentages without changing
its removal behavior. It contains no object references, callbacks, custom classes or
threads. The old hub field `SMROptIn_distribution` is unchanged.

SOURCE / desk-checked: `transport_policy` is never written. Claims are synchronous and
released after evaluation, on genuine errors, and at SaveGameStart. At SaveGameStart,
hubless stations with applied settings regain vanilla's own desired amounts before
the snapshot; SaveGameDone and LoadGame reapply the saved inert rows. Native disabled
flags remain player-reversible through vanilla's controls. The hub's existing save
behavior stays as before. **Actual serialization and mod-removal loading are NOT RUN**;
the desk snapshot check does not claim either.

## Desk verification

Commands run on the working change based on `ea6d43f` (2026-10-02):

| Command | Evidence and limit |
|---|---|
| `python tools/devmods/train_hub/tests/hubless_smoke.py` | Archived native bodies with request doubles: caps/floors, Balanced pin, reservations, native rewrites, simulated save baseline and hub transitions; no hub class loaded. Engine behavior remains unobserved. |
| `python tools/devmods/train_hub/tests/distribution_smoke.py` | Existing hub allocation smoke passes, including chain routing, full-hub refusal and save hooks. |
| `python tools/devmods/train_hub/tests/distribution_departure_smoke.py` | Existing native departure/watchdog smoke passes. |
| `python tools/devmods/train_hub/tests/station_visuals_smoke.py` | Existing physical-capacity drawing smoke passes. |
| `python tools/devmods/train_hub/tests/distribution_ui_smoke.py` | Compiled native row/slider callbacks with window doubles: hubless cycle, slider, Ctrl copy and tooltip; existing hub layout checks pass. No pixels or hit-testing claim. |

PROBE SWEEP: `rg -n 'TEMPORARY' Code/ ../SMR-BugFixPack-TestKit/Code/` and doccheck's
matching sweep found no markers before testing. `tasklist /FI "IMAGENAME eq Mars.exe"`
found the game closed before Code writes. TestKit has unrelated working changes in
`Code/72_SMRTK_World.lua` and `README.md`; they are outside this task.

## Attended smoke

NOT RUN. The owner must see the hubless row draw and act, and the repaired twinless
infotip in game. OI-38's replacement-surface-depot adoption check remains owed. The
full shipping battery and shipping split are outside this design pass.
