# Drone surfaces and save boundary — link 1 survey

**Scope.** Read-only survey of archived `Src` for game `1.1.0.403908`, Steam build `24995074`. `python tools/doccheck.py --emit-fingerprint` reports the `game 1.1.0.403908 build 24995074` fact group **HOLDS**. No game probe was run; `MEASURED` below means arithmetic or an existing cited probe, not a new play observation.

## 1. Work animation and FX names

**SOURCE — dispatch is polymorphic.** The function at `Src/Lua/Units/Drone.lua:983` is `Drone:Work`, not `Drone:DroneWork`. It assigns the request and the fields `w_request`, `request_amount`, `resource`, `amount`, `target`, and `override_ui_status`, approaches and fulfils the request, then delegates to the target with `building:DroneWork(self, request, resource, amount)` at `:1021`. Its destructor clears those fields and unassigns the request at `:1013-1020`. Therefore `Drone.lua:983-1021` itself contains no fixed animation or FX name; the target class chooses them.

**SOURCE — the exact vanilla broken-track path is construction, not generic building repair.** `TrackBase:BreakTrackElement` creates a `TrackGridElement` construction group and calls `PlaceConstructionSite(..., "TrackGridElement", ...)` (`Src/Lua/Buildings/Track.lua:623-645`). `ConstructionSite:DroneWork` calls:

```lua
drone:ContinuousTask(request, amount, g_Consts.DroneConstructBatteryUse,
  "constructStart", "constructIdle", "constructEnd", "Construct", ...)
```

at `Src/Lua/Buildings/ConstructionSite.lua:1465-1476`. Thus the source-exact visual names for an ordinary drone repairing a broken track site are animation states **`constructStart` → `constructIdle` → `constructEnd`** and FX id **`Construct`**.

**SOURCE — generic malfunction/clear repair is a different path.** `RequiresMaintenance:DroneWork` passes **`repairBuildingStart`**, **`repairBuildingIdle`**, **`repairBuildingEnd`**, FX id **`Repair`** (`Src/Lua/RequiresMaintenance.lua:655-680`). `Building:DroneWork` uses the same four names for `clear_work_request` (`Src/Lua/Buildings/Building.lua:1892-1905`). Those are valid vanilla repair visuals, but they are not the broken-track construction site's own `DroneWork` choice.

**SOURCE — exact calls/actions and cleanup.** `Drone:ContinuousTask` (`Src/Lua/Units/Drone.lua:798-829`) performs:

1. `self:StartFX(fx, building)`;
2. `self:PlayState(anim_start)`;
3. `self:SetState(anim_idle)`;
4. work loop;
5. `self:StopFX()`;
6. `self:PlayState(anim_end)`.

`Unit:StartFX` turns that into `PlayFX(fx, "start", actor, target)` with default actor `self`; `Unit:StopFX` emits `PlayFX(fx, "end", same_actor, same_target)` and clears `fx`, `fx_actor`, and `fx_target` (`Src/Lua/Units/Unit.lua:79-101`). Every next command also calls `StopFX()` in `Unit:OnCommandStart` (`:104-118`). When a command returns, `CommandThreadProc` chooses/sets `Idle` (`Src/CommonLua/Classes/CommandObject.lua:262-283`); `Drone:Idle` then resets interaction state, color modifier, and calls `SetState("idle")` (`Drone.lua:653-666`).

**INFERRED — link 2 call shape.** To imitate the broken-track vanilla visual without assigning/faking a task request, use `StartFX("Construct", site)`, `PlayState("constructStart")`, `SetState("constructIdle")`, then on normal exit `StopFX()`, `PlayState("constructEnd")`, and let the custom command return so the command machinery enters `Idle`. On interruption, ensure `StopFX()` is in cleanup; the next command also stops a surviving FX and `Idle` restores `idle`. Do not call `Drone:Work`/`ContinuousTask` with a fake request merely for visuals: both mutate request amounts and battery. If the settled design intentionally means generic *repair* visuals rather than the site's native visuals, substitute the three `repairBuilding*` states and FX `Repair`; source does not make those the native broken-track choice.

## 2. Battery property and thresholds

**SOURCE.** `battery_max` is a modifiable `Drone` property whose default is `const.DroneBatteryMax` and whose property scale is `100` (`Src/Lua/Units/Drone.lua:9-11`). The constant is `800*100`, i.e. **80,000 stored units / 800 scaled units** (`Src/Lua/_GameConst.lua:81`). `FlyingDrone` inherits `Drone` and does not override the property (`Src/Lua/Units/FlyingDrone.lua:11-21`).

**SOURCE.** `g_Consts.DroneEmergencyPower` defaults to **6,000 stored units** (`Src/Lua/__const.lua:632-637`). The same declaration says drones seek recharge while looking for work at twice this limit and drop current work at the limit.

- Charge-seek boundary: `battery <= DroneEmergencyPower * 2`, inclusive, i.e. **12,000 stored / 120 scaled units**. At this boundary `CanTakeTaskOnTheWay` returns false (`Drone.lua:618-635`), and `Idle` issues `SetCommand("EmergencyPower")` (`:653-699`).
- Emergency interruption: each `UseBattery` computes `battery = Max(self.battery - adjusted_amount, 0)` and, at `battery <= DroneEmergencyPower`, inclusive, changes command to `EmergencyPower`; at `battery <= 0` it uses `NoBattery` (`Drone.lua:1760-1783`). Exceptions are `DespawnAtHub`, `Charge`, `Dead`, and (for nonzero emergency) `RecallToRover`. A command centre providing remote charging makes `UseBattery` return before consumption (`:1761-1763`).

**MEASURED (arithmetic).** Against the default 80,000 maximum, emergency is **7.5%** and idle charge-seek is **15%**. The thresholds are absolute `g_Consts` values, not fractions of `battery_max`; increasing `battery_max` does not move them. Holding `battery = battery_max` keeps a Wasp above both.

## 3. Palette/recolour callable surface

**SOURCE.** The callable is exactly:

```lua
Building.SetPalette(object, cm1, cm2, cm3, cm4)
```

`Building:SetPalette(cm1, cm2, cm3, cm4)` first rejects an invalid object, then calls `SetObjectPaletteRecursive(self, cm1, cm2, cm3, cm4)` (`Src/Lua/Buildings/Building.lua:736-748`). `ColorizableObject:SetObjectPaletteRecursive(...)` applies `SetColorizationMaterials(...)` to the object and recursively to attaches (`Src/CommonLua/Classes/Colorization.lua:846-858`).

**SOURCE — vanilla recharge-platform precedent.** `AttachedRechargeStations.Init` gets the palette with:

```lua
local cm1, cm2, cm3, cm4 =
  GetBuildingColors(GetCurrentColonyColorScheme(), BuildingTemplates.RechargeStation)
```

and calls `Building.SetPalette(platform, cm1, cm2, cm3, cm4)` when `cm1` is non-nil (`Src/Lua/Buildings/AttachedRechargeStations.lua:2-7,24-27`). The target is the **`RechargeStationPlatform` attach**, not the spawned `NotBuildingRechargeStation` object.

**SOURCE/INFERRED.** `Drone:OnSkinChanged(skin, palette)` ignores `palette`; it changes entity and reinitializes the night light (`Drone.lua:3173-3187`). Therefore `ChangeSkin(..., palette)` is not evidence of drone recolouring. Calling `Building.SetPalette(drone, cm1, cm2, cm3, cm4)` is structurally supported because its non-life-support branch only requires a valid colorizable object and the recursive helper, but vanilla source does not demonstrate that call on a Wasp. A live visual probe must confirm which `DroneJapanFlying` materials respond.

## 4. Control and the two reassign buttons

**SOURCE.** `Drone:CanBeControlled()` is exactly:

```lua
return not self:IsDisabled()
   and not self.rogue
   and self.command ~= "Embark"
   and not self.disappeared
```

(`Src/Lua/Units/Drone.lua:2171-2173`).

Both reassign buttons use the same enabled predicate:

```lua
local tutorial2_enable = not g_Tutorial
  or ((g_Tutorial.Id == "Tutorial2")
      and g_Tutorial.DisableReassignButtons
      and NumberOfUnassignedDrones() > 0)
  or false
local enabled = self:CanBeControlled() and tutorial2_enable
button:SetEnabled(enabled)
```

Single reassign: `Drone.lua:1988-1991`; reassign-all: `:2016-2020`. Thus a false `CanBeControlled()` greys both regardless of their mode icon.

**INFERRED/policy-bound wrapper.** `FIX_POLICY.md` §1 requires a chain that calls the captured original and passes its result through for other drones. The compatible one-result shape is: call `local allowed = orig(self, ...)`; return `false` when `self.command_center` is a train hub; otherwise return `allowed`. Identify by the live controller relationship, not by sweeping all Wasps.

## 5. Save hook, persisted command, and deadline re-arm

**SOURCE/MEASURED (existing EF-024/EF-030).** Mods receive `OnMsg.SaveGameStart` and `OnMsg.SaveGameDone`; neither name is in `ModMsgBlacklist` (`Src/CommonLua/Modding/Mod.lua:1443-1453`). `DoSaveGame` sets `SavingGame = true`, synchronously calls `Msg("SaveGameStart", params)`, writes the save, sets `SavingGame = false`, then calls `Msg("SaveGameDone", name, autosave, err, metadata)` (`Src/CommonLua/Savegame.lua:1035-1060`). `Msg` invokes static handlers synchronously under `procall`, wakes `WaitMsg` threads, then invokes reactions (`Src/CommonLua/Core/cthreads.lua:12-31`); a handler error is reported, not a veto/unwind. Autosave sets `params.autosave = true` and calls the same `DoSaveGame` (`Savegame.lua:1448-1451`); EF-030 measured both events on that path.

**MEASURED (existing EF-023/EF-027), with current-source support.** A sleeping game-time command thread is serialized by value with its blocked stack, function bytecode, locals, and upvalues. `CommandObject` stores `command`, `command_destructors`, and `command_thread`, and creates commands with `CreateGameTimeThread` (`Src/CommonLua/Classes/CommandObject.lua:82-101`). A vanilla drone blocked in `Drone:Work` therefore carries its command thread plus the live source/request/amount locals and the drone's request/target fields shown at `Drone.lua:983-1022`; a mod-authored track command blocked below a yield additionally carries that mod function by value. Source alone does not enumerate the engine serializer; the by-value claim is the measured/documented EF-023/EF-027 result.

**SOURCE caveat (EF-070 applies in this build).** `SaveGameStart` is not immediately adjacent to `EngineSaveGame`: saving enters `Savegame._Wrap`, waits on a new real-time thread (`Savegame.lua:337-343`), and only later reaches `PersistGame`/`EngineSaveGame` (`:853-866`). The autosave screen has `game_blocking = false` (`Src/CommonLua/Classes/XDef/SilentSaveScreen.generated.lua:15-21`). Game-time code can therefore run between teardown and the persist walk. Also `InMemSaveGame` and `SaveGameBugReportPStr` call `PersistGame` without the start/done messages (`Savegame.lua:1117-1127,1141-1154`).

**INFERRED — required layer-1 shape.** For a persisted absolute game-time deadline:

1. Keep the pending record as plain persisted data with one permanent field name and an absolute `deadline`, never a stored function/thread.
2. `OnMsg.SaveGameStart`: set/sustain a saving gate, remove track-mode visual drones and their mod command threads, and do not alter the pending deadline.
3. Every dispatcher/spawner must refuse to create a replacement while `SavingGame` (or the module's explicit save gate) is true; otherwise an autosave can respawn a track drone before the persist walk.
4. `OnMsg.SaveGameDone`: clear the gate and rebuild/re-arm from `remaining = Max(0, deadline - GameTime())`; do this even when `err` is non-nil so failed saves do not leave runtime visuals torn down.
5. `OnMsg.LoadGame`/`PostLoadGame`: perform the same validation and re-arm from the persisted deadline. If overdue, complete/drop once after validating the site; never add a fresh full travel duration.

This is `FIX_POLICY.md` §3a layer 1: `SaveGameStart` teardown / `SaveGameDone` rebuild, with autosaves included and **re-arm from a persisted deadline, never restart blind**. Policy also requires its own A/B and long-interval soak. The source does **not** prove that `DoneObject` has eliminated every command frame before the actual persist walk—`CommandObject:Done` says command destructors run in another thread (`CommandObject.lua:124-142`)—so the A/B must inspect a save made mid-track command, and the autosave race/gate must be tested. The two hook-skipping internal paths remain an explicit limitation unless a probe establishes they are irrelevant to player saves.

## Exact falsifiers

Run from the Opt-In repo in PowerShell:

```powershell
python tools/doccheck.py --emit-fingerprint |
  rg -F 'game 1.1.0.403908 build 24995074' |
  rg -F 'HOLDS'

$src = 'B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src'
$checks = @{
  'Lua\Units\Drone.lua' = @(
    'default = const.DroneBatteryMax, scale = 100',
    'self.battery <= g_Consts.DroneEmergencyPower * 2',
    'building:DroneWork(self, request, resource, amount)',
    'return not self:IsDisabled() and not self.rogue and self.command ~= "Embark" and not self.disappeared',
    'local enabled = self:CanBeControlled() and tutorial2_enable'
  )
  'Lua\Buildings\ConstructionSite.lua' = @(
    '"constructStart", "constructIdle", "constructEnd", "Construct"'
  )
  'Lua\RequiresMaintenance.lua' = @(
    '"repairBuildingStart", "repairBuildingIdle", "repairBuildingEnd", "Repair"'
  )
  'Lua\Buildings\AttachedRechargeStations.lua' = @(
    'Building.SetPalette(platform, cm1, cm2, cm3, cm4)'
  )
  'CommonLua\Savegame.lua' = @(
    'Msg("SaveGameStart", params)',
    'Msg("SaveGameDone", name, autosave, err, metadata)',
    'params.autosave = true'
  )
}
foreach ($rel in $checks.Keys) {
  $path = Join-Path $src $rel
  foreach ($needle in $checks[$rel]) {
    rg -n -F -- $needle $path
    if ($LASTEXITCODE -ne 0) { throw "missing: $rel :: $needle" }
  }
}

$batteryMax = 800 * 100
$emergency = 6000
$seek = $emergency * 2
if ($batteryMax -ne 80000 -or $emergency -ne 6000 -or $seek -ne 12000 -or
    (100 * $emergency / $batteryMax) -ne 7.5 -or
    (100 * $seek / $batteryMax) -ne 15) { throw 'battery arithmetic moved' }
```

## What source does not prove

- It does not prove the custom Wasp entity visibly responds to the chosen four palette values; probe `DroneJapanFlying`.
- It does not make `repairBuilding*` the broken-track site's native visual; that site uses `construct*`/`Construct`.
- It does not prove save teardown is race-free or that object deletion has drained the command thread before persistence; test manual save, autosave, reload, failed-save rebuild, and a long deadline.
- It does not prove the hook-skipping in-memory/bug-report save paths are user save formats that the module must support.
