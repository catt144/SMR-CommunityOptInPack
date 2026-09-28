# Train hub reactor flash — dust write prevented; rendered cause unconfirmed

Brief 17, 2026-09-28. Base HEAD `77f62ca6113e3e4c0212bd10ce91eee0ab303897`.
Executed model: GPT-6 / Codex as identified in this session; finer model id and effort
are not exposed in the transcript. No subagents. No attended measurement.

**SOURCE:** the previous no-dust override let vanilla write positive dust to the reactor,
then wrote zero immediately afterward. The smallest repair is to prevent that first
write. Implemented on the reactor instance only. **Dust as the cause of the owner's
observed flash remains a hypothesis, not a SOURCE-proven or MEASURED cause.** Both writes
were synchronous; source does not establish that a frame renders between them, or how
the native renderer handles successive material updates when time factor changes.

## Evidence and other leads

Game citations below are from archived **1.1.1.405907**, under
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`.
`python tools/doccheck.py --emit-fingerprint` on the base HEAD returned installed
Steam build `25390750`, matching that version. These are Lua-source findings, not a
search of decoded shipping assets or a claim about native rendering internals.

| Lead | Finding |
|---|---|
| Owner's dust lead | `RequiresMaintenance.lua:169-177` reapplies dust when maintenance points change. `Buildings/Building.lua:3481-3486` applies the building guards; `Buildings/BuildingComponents.lua:326-337` normalizes dust and recurses through attachments. `Buildings/Building.lua:1731-1739` implements the recursion; `SupplyGrid.lua:257-263` dispatches `obj:SetDust` on eligible objects. Our former `20_TrainHub.lua:1291-1298` delegated first, then cleared the reactor. |
| What object is it? | Base-HEAD `20_TrainHub.lua:1265-1281` prefers `SMROptInTrainHubReactor`, falling back to `FusionReactor`; both use `ShapeshifterAutoAttach`, scale 75, default palette P4. The brief's vanilla-entity description is only the fallback. Which entity is loaded in the owner's game remains unmeasured. |
| Recreation / periodic repaint | The explicit recreation paths in `20_TrainHub.lua` are `GameInit`, `heal_after_load`, and the manual `Floor.SetHubReactorPalette` helper. `apply_hub_reactor_palette` runs during creation after `ChangeEntity`, before attachment. The inspected path contains no yield or periodic reset/repaint loop. |
| Speed change | `CommonLua/Features/GameSpeed.lua:49-85` emits `SetGameSpeed`, calls native `SetTimeFactor`, and emits `ChangeGameSpeed`. `Lua/X/HUD.lua:506-519` handles hint/gossip, sound FX and buttons. These inspected bodies do not explain a reactor palette reset. Native time-factor/render behavior remains outside this result. |
| State / animation | Our `set_hub_reactor_working` changes working/idle state, FX and custom-entity SI. `CommonLua/Classes/AutoAttach.lua:2598-2618` supplies the shapeshifter class/entity path. This is an entity on a shapeshifter, not a `FusionReactorBase` building with that class's gameplay. Native state/material behavior is unmeasured. |
| TestKit slot 6 | Read `train_row`, `stream_tick` and binding in the current `Code/80_AgentSlots.lua`: it reads train/station state and logs differences; its inspected bodies do not paint, dust or recreate the reactor. Its game-time polling interval changes in real time with speed; that alone does not establish causation. |

Reproduce the local call-site read with
`rg -n 'InitHubReactorVisual|apply_hub_reactor_palette|set_hub_reactor_working|SetDustVisuals|SetGameSpeed|ChangeGameSpeed' tools/devmods/train_hub/Code/20_TrainHub.lua`.
The other-lead conclusions are bounded to these inspected call paths, not an engine-wide absence proof.
TestKit source read at `19824aea686deb4c780e81b2af411f9b7e02510b`.

## Change and desk checks

`InitHubReactorVisual` now calls `visual:SetDust(0, const.DustMaterialExterior)` and sets
`visual.SetDust = empty_func` before attachment. Vanilla uses the same no-op setter for
visual helpers (`Lua/Construction/Construction.lua:3886-3897`). This keeps the existing
owner no-dust decision (2026-09-23) while rejecting transient positive writes. The
old post-pass cleanup stays useful for an already-created, unprotected helper.

Only the reactor root is protected, matching the existing cleanup's scope. No new class,
mod function reference, persisted name or thread: the assigned function is vanilla's,
and the existing `DeleteOnLoadGame`/recreation lifecycle remains. Descendant rendering,
direct native calls and engine-internal state changes are not covered by the Lua setter.
Other attachments still receive vanilla dust. Palette, assets and cargo code are unchanged.

Checks on base HEAD plus this working diff:

- `python tools/devmods/train_hub/tests/look_smoke.py`: PASS. The mocked native setter
  records its peak dust, so this observes intermediate writes as well as the final zero.
  Imported and fallback reactors are covered; other attaches still receive dust.
- `python tools/devmods/train_hub/tests/look_smoke.py --mutate-reactor-dust`: expected
  exit 1, `reactor received transient dust`. The mutation removes the instance no-op
  in memory and leaves the old post-pass zeroing intact.
- `python tools/devmods/train_hub/tests/reactor_dust_slot_smoke.py`: PASS. Fixture
  refusals, timed cleanup, cancellation, deleted object and stale timer covered.
- `python tools/parsecheck.py --dir tools/devmods/train_hub/Code --quiet`: PASS.
- `python tools/doccheck.py`: GREEN; existing archive CRLF warnings remain.

A desk result cannot show what renders on screen. This fixes the demonstrated dust
write sequence; it does not establish that the reported flash is gone.

## One short attended check — staged, not loaded

The attending agent's next action is to preload
[`82_ReactorDustSlot.lua.txt`](../../../tools/devmods/train_hub/tests/82_ReactorDustSlot.lua.txt)
as slot 2 after the current cargo sitting, following `tools/SMRTK.md` and restarting.
The game was running during preparation; no TestKit binding was overwritten. Its current
slot 2 fills Metals. This build link supplies the staged binding, not a claim that the
owner can press it now. Once preloaded, route the ready test to the fix pack's owner list.

**Owner:** select the hub, pause, frame its reactor, and press **Reactor: show dust reference
for 2 seconds** once. Compare that held brown appearance with the flash you reported.
It restores itself without a second press. No recording or frame stepping is required.

**Prediction, not evidence:** `SMRTK_ARM action=slot_2 status=OK`; the reference DUMP
names the actual entity/handle and reads `dust=255`. After 2000 real milliseconds,
`SMRTK_DISARM action=slot_2 status=OK` and the restoration DUMP read `dust=0`; the
reactor is back to blue. The setter is bypassed deliberately only for this visual
reference; maintenance, stock and palette are untouched. Save/load/map change or
manual disarm also restores it. If still armed after 6000 real milliseconds, press
the slot to disarm and stop on any error. No resource provisioning is needed.

A match supports the dust appearance hypothesis; it does not prove the speed trigger
or the candidate fix's rendered success. A mismatch reopens state/material/asset
investigation. If asset evidence establishes the cause,
report it and stop under brief 17's scope. Keep brief 17 until owner acceptance.
