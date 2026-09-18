# Module revalidation against game 1.1.0.403908 + DLC — the other seven modules

**Question asked (owner, 2026-09-17):** *have the opt-in modules been overtaken by the
game?* `ClassicRockets` (D01) was answered on 2026-09-17 and is `OVERTAKEN` — the record
is D01's final section and the ask is `docs/DECISIONS_OWED.md` **OI-01**. This report
answers the same question for the other seven.

**Method.** Desk only. Every claim below is read off the two archived source trees —
`C:\Dev\SMR-SrcArchive\1.0.7.396349\Src` and `C:\Dev\SMR-SrcArchive\1.1.0.403908\Src` —
and every citation is build-qualified as `<build>/Src/<path>:<lines>`. **The game was not
launched and no playtest was run.** Every section names a falsifier: an in-game check that
would prove the reading wrong. The live `ModTools\Src` was not used; it is 1.1.0 today and
can move again.

**No code was changed.** MODULE FREEZE holds; no `status:` word and no heading tag was
touched, because nothing here was tested. Findings that belong to a module's own record
were appended to its `docs/agent/bugs/D##.md` entry; the owner-facing asks are
`DECISIONS_OWED.md` **OI-03 … OI-07**.

⚠️ Reports are not authority. Where this disagrees with `agent/bugs/`, `agent/facts/`,
`WORKFLOW.md` or `FIX_POLICY.md`, those win.

**The one mechanical fact this builds on** (established 2026-09-17, `DECISIONS_OWED.md`
OI-02): every `class`+`method` pair named in every module's `SMROptInPack.Require` block
still exists in 1.1.0, so **no module is hard-broken at load**. What follows is about
semantics, and semantics is where four of the seven moved.

---

## 1 · Summary

| module | verdict | one line |
|---|---|---|
| **D02** `AcknowledgedWarnings` | **PARTLY OVERTAKEN** | The 4-game-hour whole-id window is byte-unchanged, so the complaint stands — but 1.1.0 split `NotWorkingBuildings` across **seven-plus** notification ids with the same window, and the module hardcodes the one id its own archetype probably no longer lands on. |
| **D03** `ResidencyControl` | **STILL NEEDED — with a silent regression** | Vanilla still ships no "closed to new residents" middle setting. But `ChooseDome`'s first parameter changed from a **traits table** to the **colonist**, so the module's tourist carve-out is dead code on 1.1.0 and the row's own promise ("Tourists still check in") is now false. |
| **D04** `MultipleSuns` | **STILL NEEDED** | `build_once = true` is still on the Artificial Sun and `SolarPanelBase:GameInit` still only tests `labels.ArtificialSun[1]`. Both halves still do work vanilla does not. One NEW uncovered case: 1.1.0 unbinds panels when a sun is removed and never re-tests the other sun. |
| **D06** `DroneOverhaul` | **NEEDS A PLAYTEST TO TELL** | The cross-hub WORK-locality hole it was built for is untouched, but 1.1.0 rebuilt the surrounding machinery: a second `FindTask` path (on-the-way tasks), task **swapping**, a redefined `GetIdleDronesCount`, and the removal of `CalcLapTime` — which makes `SMROptInPack.DroneReport()` throw. |
| **D07** `CohortHousing` | **OVERTAKEN (in-dome) + INERT (both halves)** | 1.1.0 deleted `exclusive_trait` outright, so the module's `find_cohort_slot` can never match and **the whole module is a no-op**. And it is moot anyway for the in-dome half: 1.1.0's `ChooseResidence` added a **tier** that puts matching cohort housing above any comfort score. |
| **D09** `DroneStatDials` | **STILL NEEDED** | Every piece of the machinery is unchanged: the `Drone`/`Consts` labels, `move_speed`, `DroneResourceCarryAmount`, `SetLabelModifier`, `Modifier`, and the Mod Options choice-value contract. Vanilla ships no drone speed/carry dial. |
| **D12** `NoHomeless` | **STILL NEEDED IN PRINCIPLE — INERT IN PRACTICE** | The tie that strands the homeless survives verbatim (relocated into `GetBestReachableCommunities`), so the defect is real on 1.1.0. But the module's dome precondition reads the deleted `exclusive_trait`, so **the row never draws and the wrapper never fires**. |

**What could not be settled from source, and why.** Three things, stated plainly:

1. **D06 is not settleable at a desk.** Its value was always a measured claim (the A/B save,
   the 88 %-of-repair-time hauling figure) and 1.1.0 replaced the instrument that produced
   those numbers. Whether the claim gate still helps, hurts, or is now drowned by vanilla's
   on-the-way tasks is an experiment, not a read.
2. **D02's archetype.** Which of the new notification ids an *unfixably* broken building
   lands on in 1.1.0 depends on the runtime reason string (`GetNotWorkingNotificationReason`),
   and reason strings are produced by `GetUIWarning` implementations across dozens of
   classes. The routing table is plain in source; which branch the F30 lake case takes is not.
3. **Whether D12's origin scenario still reproduces.** The tie logic is identical, but the
   surrounding eval numbers were re-based (`CommunityEvalNone`, `CommunityEvalOverpopulated`
   −500 → −200, an explicit life-support tier). The defect is *available* on 1.1.0; whether
   the owner's 68-free-Child-slots / 28-stranded-Youths colony still produces it is a game
   question.

Everything else below is settled from source with a named falsifier.

---

## 2 · D02 `AcknowledgedWarnings` — PARTLY OVERTAKEN

**The vanilla mechanism it depends on.** Three notification-library globals
(`SuppressNotification`, `AddObjectToNotification`, `RemoveObjectFromNotification`) and
one hardcoded notification id, `NotWorkingBuildings`, whose preset carries
`SuppressTime = 120000` + `Suppressable = true` — the whole-id 4-game-hour quiet window
the module exists to replace with per-object acknowledgment.

**What 1.0.7 did.** `NotWorkingBuildings` was the generic catch-all: `ShouldShowNotWorkingNotification`
returned true for essentially any stopped, work-permitted, non-demolishing building
(`1.0.7.396349/Src/Lua/Buildings/BaseBuilding.lua:121-135`), with a single special case for
`NotEnoughWorkers` before any colonists exist. One id, one window, everything in it.

**What 1.1.0 does.** Two changes, in opposite directions.

*The window itself did not move.* The preset is byte-identical where it matters —
`SuppressTime = 120000`, `Suppressable = true`, no `Parent`
(`1.1.0.403908/Src/Data/NotificationPreset.lua:1198-1216`, against
`1.0.7.396349/Src/Data/NotificationPreset.lua:637-655`). ⇒ **The D02 complaint is not fixed.
A permanently broken building still re-nags every 4 game hours, and the window is still
per-id, so a freshly broken building is still silenced by an unrelated dismissal.**

*But the id was split.* `ShouldShowNotWorkingNotification` is now a router
(`1.1.0.403908/Src/Lua/Buildings/BaseBuilding.lua:306-313`):

```lua
local reason = self:GetNotWorkingNotificationReason()
if reason and (ReasonNotification[reason] or SuppressedReasons[reason]) then
	return false -- shown in a dedicated notification, or covered by a separate system
end
return self:IsStoppedAndWorkPermitted()
```

`ReasonNotification` (`:243-266`) routes stopped buildings to **`DepositExhausted`,
`PowerShortage`, `WaterShortage`, `OxygenShortage`, `NoDroneService`, `UnreachableBuilding`
and `EnvironmentalProblem`**; `SuppressedReasons` (`:268-278`) drops another dozen reasons
out of the id entirely, including `Malfunction`/`MalfunctionRes`, which 1.1.0 moved to a
brand-new **`MaintenanceStuckBuildings`** notification
(`1.1.0.403908/Src/Lua/RequiresMaintenance.lua:341-343`, preset at
`1.1.0.403908/Src/Data/NotificationPreset.lua:1101-1121`; the migration fixup at
`RequiresMaintenance.lua:345-352` says so in its own comment).

**Every one of those new ids carries the same `SuppressTime = 120000` + `Suppressable = true`**
(`MaintenanceStuckBuildings` `:1110-1111`, `UnreachableBuilding` `:1503-1504`,
`NoDroneService` `:1148-1149`, `EnvironmentalProblem` `:866-867`, `DepositExhausted`
`:731-732`). The module hardcodes `local ID = "NotWorkingBuildings"`
(`Code/Opt_AcknowledgedWarnings.lua:74`) and every wrapper tests `id == ID`, so on 1.1.0
it fixes one of at least seven instances of the same defect — and the D02 archetype, an
*unfixable* wreck, is precisely the kind of case most likely to route away
(`TooFarFromWorkforce → UnreachableBuilding`, `NoCommandCenter/NoDroneHub → NoDroneService`).

**Two smaller things, recorded so the next session does not rediscover them.**

* `SuppressNotification` gained a recursive child-suppression branch for
  `ParentNotificationPreset` (`1.1.0.403908/Src/CommonLua/Libs/Notifications/Notifications.lua:165-181`).
  It resolves the global by name at call time, so a replaced global is reached — the module's
  wrapper is still on the dismissal path. Its only caller is still `RemoveNotification` under
  `notification.dismissed` (`:109-110`), which is the premise the module's dismissal hook rests on.
* 1.1.0 added a new object funnel, `SetNotificationObjects` (`:358-371`), which routes through
  `AddObjectsToNotification` (plural, `:285`) — **not** the singular `AddObjectToNotification`
  the module wraps — and calls `RemoveObjectFromNotification(obj, notification)` with a
  notification **table** as `id`, which the module's `id == ID` string test will not match.
  Nothing in the shipped `NotWorkingBuildings` path uses it today
  (`UpdateObjectInNotification` at `:349-356` still uses the singular pair), so this is a
  latent exposure rather than a live one.

**Verdict: PARTLY OVERTAKEN.** Not by a fix — by a split. The module still does something
vanilla does not, for the id it names. It does not fight a new deliberate rule. Its reach
shrank without anyone touching it.

**Falsifier.** On 1.1.0, break a building in a way that cannot be repaired (the F30
entombed-by-lake archetype), dismiss its warning, and read which notification the warning
came from. If it says "Building Not Working", the coverage gap is narrower than claimed
here. Then dismiss a `MaintenanceStuckBuildings` warning with the module ON and check
whether a *different* building's maintenance warning is silenced for the next 4 game hours:
if it is not, the shipped whole-id window is not reaching that id and this reading is wrong.

---

## 3 · D03 `ResidencyControl` — STILL NEEDED, with a silent regression

**The vanilla mechanism it depends on.** Three seams: `Community:CanAcceptNewColonists`
(voluntary resettlement), the global `ChooseDome` (first-home choice on arrival), and
`sectionDome`/`sectionMicroGHabitat` `Init` (the infopanel row). Plus the shipped policy
machinery `Community:TogglePolicy`/`SetPolicyState`.

**What 1.0.7 did, and what 1.1.0 does — the feature question first.** Vanilla still offers
no middle setting. The dome infopanel's toggle rows on 1.1.0 are birth policy,
`allow_work_in_connected`, `allow_service_in_connected` and `accept_colonists`
(`1.1.0.403908/Src/Lua/XDef/sectionDome.generated.lua:34, 92, 133, 174`), and
`accept_colonists` is still the quarantine seal (`Community:CanAcceptNewColonists` is
`self.ui_working and self.accept_colonists`, `1.1.0.403908/Src/Lua/Buildings/Community.lua:96-98`,
unchanged from `1.0.7.396349/Src/Lua/Buildings/Community.lua:61-63`). The two **new** 1.1.0
policies are the *outbound* direction — whether residents may leave through passages to work
or use services elsewhere — which is exactly the home-side commute the D03 header says it
deliberately never touches. ⇒ **D03's feature is not overtaken; if anything vanilla moved
toward the same design space from the other side.**

**The regression.** `ChooseDome`'s first parameter changed meaning:

```lua
-- 1.0.7.396349/Src/Lua/_GameUtils.lua:426
function ChooseDome(traits, domes, safety_dome, dome_elevators)
-- 1.1.0.403908/Src/Lua/_GameUtils.lua:486
function ChooseDome(colonist, domes, safety_dome, dome_elevators)
```

and **every caller** was updated to pass the colonist/applicant rather than its `.traits`
(1.0.7: `ChooseDome(unit.traits, …)` / `ChooseDome(applicant.traits, …)` at
`RocketBase.lua:1985/:2068/:2105`, `CargoTransporterNew.lua:907/:951/:975`,
`DroneFactory.lua:224`, `Colonist.lua:1149`; 1.1.0: `ChooseDome(unit, …)` /
`ChooseDome(applicant, …)` at `RocketBase.lua:1978/:2064/:2103`,
`CargoTransporterNew.lua:996/:1045/:1088`, `DroneFactory.lua:230`, `Colonist.lua:1452`,
and a NEW ninth site `ColonistTransport.lua:870`).

The module's wrapper is

```lua
-- Code/Opt_ResidencyControl.lua:216-217
local function choose(traits, domes, safety_dome, dome_elevators, ...)
	if module_active() and type(domes) == "table" and not (traits and traits.Tourist) then
```

On 1.1.0 the first argument is a Colonist (or an applicant table), and `Tourist` is only
ever a key of `colonist.traits` — never a direct member; every vanilla read is
`self.traits.Tourist` or `colonist.traits["Tourist"]`
(`1.1.0.403908/Src/Lua/Units/Colonist.lua:2671, :2675, :2705, :3906`). ⇒ **`traits.Tourist`
is `nil` for every caller, the carve-out never fires, and a closed dome is now filtered out
for tourists too.** The module's own rollover text still promises the opposite:
*"Manual relocation and Tourists are unaffected"* (`Code/Opt_ResidencyControl.lua:159`).

This is a behaviour change to a frozen module and needs the owner's line — the ask is
`DECISIONS_OWED.md` **OI-03**. The fix is one line (`traits.traits and traits.traits.Tourist`,
tolerant of both shapes), but it is still a module edit.

**A second reach the module never claimed.** `CanAcceptNewColonists` had exactly one caller
in 1.0.7 (`Colonist.lua:2658`, and the module header says so, having verified it). On 1.1.0
it has two: the same emigration filter, relocated to `GetBestReachableCommunities`
(`1.1.0.403908/Src/Lua/Units/Colonist.lua:3458`), **and** `FindStopoverDomeForRocket`
(`1.1.0.403908/Src/Lua/UniversalRocket.lua:2226`), which picks a waiting dome for a colonist
booked to leave Mars. There it is a *preference*, not a gate — the nearest dome still wins if
nothing can house the colonist — so a D03-closed dome becomes a less-preferred stopover.
That is arguably in keeping with the policy, but nobody decided it and nobody has seen it.

**Everything else validated.** `TogglePolicy`/`SetPolicyState` still exist and still play the
FX and respect the UI-interaction lock (`Community.lua:100-135`); `SetPolicyState`'s broadcast
path gained a `community[policy_member .. "_disabled"]` skip (`:117`) which the module's flag
never sets, so Ctrl+click is unaffected. The infopanel row's placement rule still holds: the
section is still four `InfopanelActiveSection` toggles followed by plain `InfopanelSection`
blocks (`1.1.0.403908/Src/Lua/XDef/sectionDome.generated.lua:34/92/133/174` then `:216`), so
"insert before the first plain `InfopanelSection`" still lands the row with the toggle group.
`sectionMicroGHabitat` still exists and is still the only other `Community` infopanel section;
`MicroGHabitatBase` is still the only other `Community` subclass
(`1.1.0.403908/Src/Lua/Buildings/MicroGHabitat.lua:4`). The icons the row uses
(`accept_colonists_on/off.png`, `ip_sections_limit`) are still referenced by the shipped section.

**Verdict: STILL NEEDED.** The module does something vanilla does not, and it does not fight a
new deliberate rule. It carries one dead guard that silently broke a promise it makes to the
player in its own tooltip.

**Falsifier.** On 1.1.0, close a dome to new residents, then land a rocket carrying a Tourist
with that dome the only sensible choice. If the Tourist checks in anyway, the traits-argument
reading is wrong. Separately: close a dome and confirm its current residents still commute out
through passages (they should — the two new `allow_*_in_connected` policies are the only thing
that gates that, and the module never touches them).

---

## 4 · D04 `MultipleSuns` — STILL NEEDED

**The vanilla mechanism it depends on.** Two, one per half: the `build_once` flag on the
`ArtificialSun` building template (limit lift), and `SolarPanelBase:GameInit`'s one-sun-only
binding test plus `TestSunPanelRange`/`SetArtificialSun` (binding fix).

**What 1.0.7 did.** `build_once = true` on the template; `SolarPanelBase:GameInit` read
`self.city.labels.ArtificialSun[1]` and nothing else
(`1.0.7.396349/Src/Lua/Buildings/SolarPanel.lua:8-14`), so a panel built in range of sun #2
only never registered.

**What 1.1.0 does.** Both are unchanged where it counts:

* `build_once = true` is still on the template
  (`1.1.0.403908/Src/Lua/BuildingTemplate/ArtificialSun.generated.lua:16`, and the data form
  at `1.1.0.403908/Src/Data/BuildingTemplate/ArtificialSun.lua:7`), and `wonder = true` with
  it (`:15`). The colony-wide enforcement is still `Building:CanBuildOnlyOnce`
  (`1.1.0.403908/Src/Lua/Buildings/Building.lua:3893`) consulted live by the build menu
  (`1.1.0.403908/Src/Lua/X/BuildMenu.lua:731`) and by construction
  (`Construction.lua:212`), so the module's live `on_activate`/`on_deactivate` template flip
  still works with no UI refresh.
* `SolarPanelBase:GameInit` still reads only `labels.ArtificialSun[1]`
  (`1.1.0.403908/Src/Lua/Buildings/SolarPanel.lua:11-16`). **The binding bug is unfixed on 1.1.0.**
  `TestSunPanelRange` (`1.1.0.403908/Src/Lua/Buildings/ArtificialSun.lua:18`) and
  `SolarPanelBase:SetArtificialSun` (`SolarPanel.lua:69`) are both intact.

⇒ Both halves still do work vanilla does not do.

**What is NEW, and is an uncovered case rather than a conflict.** 1.1.0 gave the sun its own
re-link pass and a teardown:

```
ArtificialSunBase:LinkPanelsInRange()        1.1.0.403908/Src/Lua/Buildings/ArtificialSun.lua:42-57
ArtificialSunBase:OnModifiableValueChanged() :59-63   -- re-links when effect_range changes
ArtificialSunBase:Done(done_map)             :65-73   -- clears artificial_sun on every panel bound to it
```

`Done` unbinds every panel that pointed at the removed sun and does **not** re-test whether
another sun still covers them. With the limit lifted and two overlapping suns standing,
demolishing one leaves panels in the survivor's range dark until something re-runs the test —
and the module's only sweep is `OnMsg.LoadGame` (`Code/Opt_MultipleSuns.lua:196-215`). So on
1.1.0 the module's own feature has a hole its 1.0.7 design could not have had, because on
1.0.7 two suns could not coexist without a third-party mod and `Done` did not unbind. This is
the same *shape* as D01's parked limitation (state that nothing re-evaluates), not a new
defect class. It is recorded in D04's entry; whether to close it is `DECISIONS_OWED.md` **OI-04**.

`effect_range` also became `modifiable = true` (`ArtificialSun.lua:7`), which is what the new
`OnModifiableValueChanged` hook exists for — no interaction with the module.

**Verdict: STILL NEEDED.** Neither half is overtaken and neither fights a new rule.

**Falsifier.** On 1.1.0 with the module ON: build two Artificial Suns with overlapping
coverage, then build a solar panel in range of the second one only. If it lights up without
the module, the binding fix is redundant and this reading is wrong. Then demolish the first
sun and watch the panels that were bound to it but are also in the survivor's range: if they
stay lit, the `Done` gap is not real.

---

## 5 · D06 `DroneOverhaul` — NEEDS A PLAYTEST TO TELL

**The vanilla mechanism it depends on.** `TaskRequestHub:FindTask` (the claim gate),
the fall-through tail of `Drone:Idle` reaching `Drone:CleanUnreachables` (moonlighting),
`TaskRequester:FindDroneNodes` + `GetCommandCenter` (the coverage walk), and
`DroneControl:GetIdleDronesCount` + `hub.priority_queue` (both the gate and the scan).
Telemetry additionally uses `DroneControl:CalcLapTime` and the `DroneLoad*Threshold` consts.

**What 1.0.7 did.** Pull-only assignment: an idle drone polled only its own hub, from the
single `command_center:FindTask(self)` call inside `Drone:Idle`
(`1.0.7.396349/Src/Lua/Units/Drone.lua:621`); requests were posted into every covering hub's
queues; the claim was first-poller-wins and held for the trip; nothing reassigned it. Hub load
was a **lap time** (`DroneControl:CalcLapTime`, `1.0.7.396349/Src/Lua/Buildings/DroneControl.lua:955`)
compared against `const.DroneLoadLowThreshold` / `DroneLoadMediumThreshold`.

**What 1.1.0 does.** The hole the module was built for is still there — and the machinery
around it was rebuilt.

*Still there.* `TaskRequestHub:FindTask` is byte-identical
(`1.1.0.403908/Src/Lua/_TaskRequest.lua:74-85`). The registration layer is unchanged: a
building still connects to **every** covering hub via `FindDroneNodes` + `GetCommandCenter`
(`1.1.0.403908/Src/Lua/_TaskRequest.lua:286-317`; `FindDroneNodes` gained an optional
`building` argument that defaults to `self`, so the module's `src:FindDroneNodes()` still
works). `DroneHubExtenderBase:GetCommandCenter` is unchanged
(`1.1.0.403908/Src/Lua/Buildings/DroneHubExtender.lua:166-170`). **There is still no
cross-hub locality anywhere for WORK requests.**

*The tail the moonlight hook rides is still intact.* `Drone:Idle`'s last two statements are
still `Sleep(2000)` then `self:CleanUnreachables()`
(`1.1.0.403908/Src/Lua/Units/Drone.lua:653-712`), every found-work branch still `SetCommand`s
before reaching it, and `Drone:CleanUnreachables` is still declared
(`:971`) with its other two call sites still inside `Deliver` (`:1454`) and
`PickRechargeStation` (`:1491`) — so the `self.command == "Idle"` gate still selects exactly
the fall-through. The F86 tier-2 repair still holds on 1.1.0.

*Four things moved.*

1. **A second `FindTask` path.** The `FindTask` call moved into a new
   `Drone:TryTakeTask(command_center)` (`1.1.0.403908/Src/Lua/Units/Drone.lua:593-615`), and
   that has **two** callers: `Idle` (`:707`) and the new
   `Drone:TryTakeTaskOnTheWay` (`:638-651`, called from `:730` and `:1756`), a travelling drone
   grabbing a request that appears mid-trip, polled every `const.DroneTaskOnTheWayInterval`
   = 1000 ms (`1.1.0.403908/Src/Lua/_GameConst.lua:86-87`). The module's header states
   *"its ONLY caller is the drone auto-Idle path, so player orders are structurally untouched"*
   (`Code/Opt_DroneOverhaul.lua:23-25`). **That claim is false on 1.1.0.** The claim gate now
   also vetoes on-the-way polls. It is not a correctness break — vetoes are strike-bounded —
   but strikes burn at up to one per second per request now, so `STRIKES_MAX = 4` may expire
   in ~4 seconds and the gate's whole effect could be washed out.
2. **`GetIdleDronesCount` changed meaning.** It is now an alias for a new
   `GetFreeDronesCount`, which counts drones in `Idle`, in `WaitingCommand`, **and** any
   travelling drone eligible for an on-the-way task
   (`1.1.0.403908/Src/Lua/Buildings/DroneControl.lua:992-1005`). The module uses it twice, in
   opposite directions: `closest:GetIdleDronesCount() > 0` decides whether to veto
   (`Opt_DroneOverhaul.lua:189`), and `hub:GetIdleDronesCount() == 0` decides whether a hub is
   *saturated* and therefore worth moonlighting for (`:235`). The first gets more eager; the
   second gets much harder to satisfy, so **moonlighting may effectively stop firing** on a
   busy colony.
3. **Vanilla added task reassignment — for hauling only.** `Drone:TryTaskSwap`
   (`1.1.0.403908/Src/Lua/Units/Drone.lua:1065-1114`) trades two drones' tasks when one is much
   closer to the other's target, gated by `const.DroneTaskSwapDistancePct` / `MinGain`
   (`_GameConst.lua:89-92`). It is **PickUp-only** (`self.command ~= "PickUp"` and a required
   `s_request`) and **same-hub-only** (`other.command_center == command_center`). ⇒ It does
   **not** touch WORK requests and does **not** cross hubs, so it does not overtake the module's
   part 1. What it does overtake is the half D06 deliberately declared out of scope
   ("PickUp/Deliver hauling — deliberately out of v1 scope"). That is a design input for the
   D06 rebuild, not a verdict on the shipped module.
4. **Hub load measurement was replaced, and the module's telemetry now throws.**
   `DroneControl:CalcLapTime`, `const.DroneLoadLowThreshold` and `const.DroneLoadMediumThreshold`
   **do not exist anywhere in the 1.1.0 tree**; 1.1.0 measures load as a sampled idle percentage
   over a window (`const.DroneLoadSampleInterval`, `DroneLoadWindow`, `DroneLoadHighPct`,
   `DroneLoadMediumPct`, `1.1.0.403908/Src/Lua/_GameConst.lua:94-98`).
   `SMROptInPack.DroneReport()` calls `hub:CalcLapTime()` unconditionally
   (`Code/Opt_DroneOverhaul.lua:293`) and is registered **whether or not the module is enabled**,
   so on 1.1.0 invoking it raises `attempt to call a nil value (method 'CalcLapTime')`. It is
   console-invoked only, so it cannot fire by itself — but it is the module's only instrument
   and the D06 rebuild's measurement plan leans on it.

Also noted, harmless: `Drone:Idle` now gates on `command_center:CanCommandDrones()`
(`1.1.0.403908/Src/Lua/Buildings/DroneHub.lua:150-153`) rather than `.working` — a hub with no
power still commands drones. The module still tests `.working` in three places, so it is now
*narrower* than vanilla's own notion of a working hub. And `const.DroneRestrictRadius` gained an
underground sibling, `const.DroneRestrictRadiusUnderground = CommandCenterMaxRadius * 3 * GridSpacing`
(`_GameConst.lua:73`), selected by a new `GetDroneRestrictRadius(map)`
(`1.1.0.403908/Src/Lua/Units/Drone.lua:232-237`); the module hardcodes the surface constant in
both its reach tests, so on an underground map it under-states drone reach by a third.

**Verdict: NEEDS A PLAYTEST TO TELL.** The defect is still present, so the module is not
overtaken; but three of its four load-bearing assumptions were re-based and its instrument is
broken. Nothing here can be settled by reading. The owner ask is `DECISIONS_OWED.md` **OI-05**,
and it matters more than the others because the D06 **rebuild spec**
(`reports/DRONE_REBUILD_DESIGN_20260901.md`, ratification gated on checklist item 94) was
written entirely against 1.0.7.

**Falsifier.** On 1.1.0 with the module ON and telemetry patched or replaced: park idle drones
beside a building that a distant hub also covers, break it, and watch which fleet claims the
repair. If the near fleet already wins without the module, vanilla acquired locality somewhere
this read missed. Then read `vetoed` versus `veto_expired`: if `veto_expired` dominates, the
on-the-way polls are burning the strike budget as predicted here. Then check `moonlighted`: if
it stays at 0 across a session where a hub is visibly saturated, the `GetIdleDronesCount`
redefinition has disabled part 2.

---

## 6 · D07 `CohortHousing` — OVERTAKEN in-dome, and INERT in both halves

**The vanilla mechanism it depends on.** The `exclusive_trait` field on `Residence` —
`"Child"` on nurseries (set from `children_only` at `Residence:GameInit`) and `"Senior"` on
the Seniors Residence — plus `ChooseResidence`'s comfort scorer and `FindEmigrationDome`'s
tie rule, which between them never move a comfortable cohort member into cohort housing.

**What 1.0.7 did.**

```lua
-- 1.0.7.396349/Src/Lua/Buildings/Residence.lua:11
{ template = true, modifiable = true, id = "exclusive_trait", … default = false, … }
-- :26-27
if self.children_only and not self.exclusive_trait then
	self.exclusive_trait = "Child"
end
```

and `ChooseResidence` ranked purely on comfort, with a matching `exclusive_trait` giving a
`score * 2` bonus but no precedence — a housed colonist only moved on a **strictly better**
score (`1.0.7.396349/Src/Lua/Buildings/Residence.lua:382-422`). That is the module's stated
reason for existing.

**What 1.1.0 does. Two independent things, either of which is decisive.**

*First: `exclusive_trait` no longer exists.* `grep -rn "exclusive_trait" 1.1.0.403908/Src/`
returns **nothing** — and neither does `children_only`. It was replaced by a named-predicate
filter, `filter_residents`, with the values `Everyone | Children | Seniors | Tourists | Adults`
(`1.1.0.403908/Src/Lua/Buildings/Residence.lua:15`; predicates at
`1.1.0.403908/Src/Lua/Stats.lua:192-197`). The cohort buildings now declare it directly —
`NurseryBase.filter_residents = "Children"` (`Residence.lua:551-556`),
`SeniorsResidence.filter_residents = "Seniors"` (`:573-585`), `Hotel` → `"Tourists"`
(`1.1.0.403908/Src/Lua/BuildingTemplate/Hotel.generated.lua:47`) — and `Residence:IsSuitable`
is now `ColonistFilterFunc[self.filter_residents]` (`:198-201`).

The module's only way of recognising cohort housing is

```lua
-- Code/Opt_CohortHousing.lua:104
if r.exclusive_trait == trait and r.ui_working then
```

⇒ `nil == "Child"` is false for every residence, `find_cohort_slot` returns `nil`
unconditionally, and **both passes become no-ops**: the in-dome pass finds no slot and does
nothing; the cross-dome pass's `consider()` rejects every candidate and falls through to the
shipped answer. The module is inert, and it is inert *quietly* — its `Require` block only
names `Colonist.UpdateResidence/FindEmigrationDome` and `Residence.GetFreeSpace/IsSuitable`,
all of which still exist, so `apply()` succeeds and `ListFixes()` reports it **active**.
Harmless, but a status word that is not true.

*Second, and this is the OI-01 shape: vanilla adopted the in-dome half.* 1.1.0's
`ChooseResidence` introduced a **tier** above score:

```lua
-- 1.1.0.403908/Src/Lua/Buildings/Residence.lua:416-435 (GetResidenceComfort)
local pred = ColonistFilterFunc[residence.filter_residents]
if pred then
	local match = pred(colonist.traits)
	return match and score * 2, match and 1 or 0     -- second return: the TIER
end
…
-- :437-467 (ChooseResidence)
if tier > best_tier
	or tier == best_tier and score > best_score
	or tier == best_tier and score == best_score and space > best_space and best_home ~= current_home then
```

⇒ **A matching filtered residence now beats any unfiltered one outright, at any comfort
score.** A Senior comfortable in ordinary housing is moved into a free Seniors Residence in
the same dome by vanilla, which is precisely what D07's in-dome pass was built to add
(`Code/Opt_CohortHousing.lua:31-38`). Vanilla ships the module's in-dome feature.

*The cross-dome half is not adopted.* `FindEmigrationDome`'s tie rule survives (see §8), and
`Community:GetScoreFor` still only adds the matching residence's comfort as a score term
(`1.1.0.403908/Src/Lua/Buildings/Community.lua:442-459`) — there is no cross-dome tier. So
the cross-dome pass would still do something vanilla does not, **if it could recognise a
cohort slot at all.** It cannot.

**Verdict: OVERTAKEN (in-dome) + INERT (both halves).** It does not fight a new deliberate
rule — it simply cannot see the world any more. Three honest options (retire; port to
`filter_residents` and keep only the cross-dome half, since vanilla now owns the in-dome
half; or port whole and accept redundancy) are `DECISIONS_OWED.md` **OI-06**.

**Falsifier.** On 1.1.0 with the module OFF: put a comfortable Senior in ordinary housing in a
dome that also has a free Seniors Residence, and wait one heavy update. If vanilla does **not**
move them, the tier reading is wrong and the in-dome half is still needed. Then turn the module
ON with a Child in ordinary housing and a free Nursery **in another dome**: if the Child
emigrates, `find_cohort_slot` is matching something after all and the inertness claim is wrong.

---

## 7 · D09 `DroneStatDials` — STILL NEEDED

**The vanilla mechanism it depends on.** Label modifiers, exactly as the game's own techs
use them: a percent `Modifier` on label `"Drone"`, prop `move_speed`, applied to `UIColony`
via `LabelContainer:SetLabelModifier`; and an amount `Modifier` on label `"Consts"`, prop
`DroneResourceCarryAmount`. Plus the Mod Options contract — `CurrentModOptions`, the
`ApplyModOptions` message, and `ModItemOptionChoice`'s "the choice text IS the value".

**What 1.0.7 did / what 1.1.0 does.** Unchanged, every piece:

* `const.DroneResourceCarryAmount` is still defined with `value = 1` in the `Drone` group
  (`1.1.0.403908/Src/Lua/__const.lua:683-687`, identical to
  `1.0.7.396349/Src/Lua/__const.lua:637-641`) and is still consumed at
  `runits[res] = (Resources[res].carry_amount or const.ResourceScale) * g_Consts.DroneResourceCarryAmount`
  (`1.1.0.403908/Src/Lua/Units/Drone.lua:790`), still rebuilt on `OnMsg.ConstValueChanged`
  (`:793`). The tech that uses the same prop is still there
  (`1.1.0.403908/Src/Data/Tech.lua:478` — the preset file was renamed from `TechPreset.lua`
  to `Tech.lua`, which is a citation move, not a behaviour change) and so is the
  Ancient Artifact upgrade route (`AncientArtifactInterface.generated.lua:24`).
* `Drone.move_speed` is still a plain member (`1.1.0.403908/Src/Lua/Units/Drone.lua:28`,
  applied at `:90`).
* `LabelContainer:SetLabelModifier` is unchanged — the only diff in the whole file is a
  varargs pass-through on the unrelated `UpdateFilteredLabel`
  (`1.1.0.403908/Src/Lua/LabelContainer.lua:80-97`).
* `Modifier`, `HasModifiablePropScale` and `GetModifiablePropScale` all still live in
  `1.1.0.403908/Src/CommonLua/Classes/Modifiers.lua`.
* The Mod Options API moved file (`CommonLua/Classes/Mod.lua` →
  `1.1.0.403908/Src/CommonLua/Modding/Mod.lua`) but is otherwise intact: `CurrentModOptions`
  is still injected into the mod env (`:1634`), `Msg("ApplyModOptions", mod.id)` still fires
  on apply and on load (`:697, :753-759, :2199`), and `ModItemOptionChoice:GetOptionMeta`
  still builds `{ text = T(item), value = item }` — **the choice string is still the value**
  (`:2781-2789`, byte-identical to `1.0.7.396349/Src/CommonLua/Classes/Mod.lua:2764-2771`).
  This last point underwrites every module's toggle, not just D09's.

Vanilla ships no drone speed or carry-capacity dial; the only levers remain the techs, which
is the module's whole premise (breakthrough-lottery insurance).

**Verdict: STILL NEEDED.** Nothing overtaken, nothing fought. This is the one module of the
seven whose every cited mechanism survived the version unchanged.

**Falsifier.** On 1.1.0, set "Drone speed" to 5x, hit Apply, and read a drone's
`move_speed`. If it does not rise, either the modifier is not landing or the prop lost its
modifiable scale — and `ReapplyDials`' `HasModifiablePropScale` guard would have silently
returned instead of erroring, which is exactly the shape that looks like "the dial does
nothing" rather than a crash.

---

## 8 · D12 `NoHomeless` — STILL NEEDED IN PRINCIPLE, INERT IN PRACTICE

**The vanilla mechanism it depends on.** Two: the emigration tie in
`Colonist:FindEmigrationDome` (the defect), and `Residence.exclusive_trait` (the dome
precondition — the policy applies only where a Nursery or a Retirement Home is actually built,
owner ruling 2026-08-02).

**What 1.0.7 did.** The tie, at `1.0.7.396349/Src/Lua/Units/Colonist.lua:2668-2685`: a
candidate must score `new_eval >= eval`, and then must clear a **strictly-better** gate
unless home or work improves. With zero free non-cohort slots colony-wide and unemployment
saturated, every candidate ties and nobody moves — the stranding the module exists to break.

**What 1.1.0 does — the defect first.** `FindEmigrationDome` was rewritten and split
(`1.1.0.403908/Src/Lua/Units/Colonist.lua:3497-3527`): it now builds a reachability graph
(`BuildReachableGraph`, `:3400-3422`) and delegates scoring to a new
`Colonist:GetBestReachableCommunities(reachable, force_leave)` (`:3425-3495`). **Inside that
function the tie is verbatim:**

```lua
-- 1.1.0.403908/Src/Lua/Units/Colonist.lua:3474-3492
if new_eval >= eval then
	if not home_available or new_home_available then -- if homeless, try changing community even if doesn't have living space available.
		local better_home = not home_available and new_home_available
		local better_work = not work_available and new_work_available
		local better_home_work = better_home or (need_work and better_work)
		local better_eval = beat_threshold and new_eval >= eval or new_eval > eval
		if better_eval or better_home_work then
```

— the same comment, the same guard, the same `need_work` definition two dozen lines above
(`:3428-3429`) that the module's `is_push_subject` is copied from. ⇒ **The D12 defect is
available on 1.1.0.** The function still returns nothing when nothing qualifies, so the
module's "act only when the shipped answer is EMPTY" composition rule still holds, and the
signature change (`current_dome` → `current_dome, force_leave`) is absorbed by both wrappers'
`(current_dome, ...)` pass-through.

**But the module cannot run.** Its dome precondition is

```lua
-- Code/Opt_NoHomeless.lua:305-310
local function has_cohort_housing(community)
	return each_residence(community, function(res)
		local t = res.exclusive_trait
		return (t and t ~= "" and t ~= "Tourist") and true or nil
	end) and true or false
end
```

and `exclusive_trait` does not exist in 1.1.0 (§6). ⇒ `has_cohort_housing` is **always
false**, which means:

* `append_policy_row` returns on its first line (`Opt_NoHomeless.lua:658`) — **the infopanel
  row never appears at all**, on any dome. The module has no control surface on 1.1.0.
* the push half's precondition fails (`:524`) — nobody is ever moved;
* the symmetric entry veto fails its second clause (`:484`) — it never fires either.

The module is a complete no-op, and — as with D07 — it reports `active`, because its `Require`
block names only methods that still exist. `has_suitable_home`'s reliance on
`Residence:IsSuitable` is fine in itself (the method survives, re-implemented over
`filter_residents`, `1.1.0.403908/Src/Lua/Buildings/Residence.lua:198-201`); it is simply
never reached.

**Three more 1.1.0 changes that bear on the module's design, recorded for whoever ports it.**

1. **The candidate set is now reachability-filtered.** 1.0.7 considered every `Community` in
   the city label plus every elevator-linked city's; 1.1.0 walks a graph of walk/passage/
   station/elevator/shuttle-reachable nodes (`BuildReachableGraph`, `:3400-3422`). Both D12's
   `consider()` loop (`Opt_NoHomeless.lua:582-595`) and D07's (`Opt_CohortHousing.lua:207-220`)
   still mirror the **1.0.7** gathering. They each gate on `FindTransportationModeToCommunity`
   returning a mode, and that function's signature and semantics are unchanged
   (`1.1.0.403908/Src/Lua/Units/Colonist.lua:3170`), so they cannot propose an unreachable
   destination — but they no longer mirror vanilla's own candidate set, which is what the
   comments in both modules claim they do.
2. **The eval ladder was re-based.** `CommunityEvalNone = -700`, `CommunityEvalLifeSupport = 100`,
   `CommunityEvalNoLifeSupport = -400`, `CommunityEvalFreeSpaceForHomeless = 20`, and the
   overpopulation penalty softened from a hardcoded **-500** to
   `CommunityEvalOverpopulated = -200` (`1.1.0.403908/Src/Lua/Buildings/Community.lua:436-440`,
   applied at `1.1.0.403908/Src/Lua/Buildings/Dome.lua:4200-4210`, against
   `1.0.7.396349/Src/Lua/Buildings/Dome.lua:3575-3585`). The devs' own comment says the penalty
   *"pushes the homeless out and deters newcomers"* — i.e. vanilla now leans, weakly, in D12's
   direction. Whether that alone unsticks the origin scenario is not readable from source.
3. **The row's icon is no longer distinctive.** D12 picked the
   `service_in_connected_domes_on/off` pair specifically so its row would not look like D03's
   (`Opt_NoHomeless.lua:620-624`). On 1.1.0 vanilla uses that exact pair for its **own** new
   `allow_service_in_connected` row on the same panel
   (`1.1.0.403908/Src/Lua/XDef/sectionDome.generated.lua:138-144`). Cosmetic, but the reason the
   icon was chosen is gone.

**Verdict: STILL NEEDED IN PRINCIPLE, INERT IN PRACTICE.** The defect survived; the module's
recognition of the world did not. It does not fight a new deliberate rule. The port question
is `DECISIONS_OWED.md` **OI-07**, filed jointly with D07 because they share the deleted field.

**Falsifier.** On 1.1.0, open a dome that contains a Nursery with the module ON. If the
"Nursery / Retirement Dome" row appears, `has_cohort_housing` is matching something and the
inertness claim is wrong. Separately, and independent of the module: build the origin
scenario — a nursery-only dome with free Child slots and a pile of homeless Youths, zero free
non-cohort slots colony-wide — and see whether the Youths still sit there. If 1.1.0 drains them
by itself, the softened overpopulation penalty has done what the module was written to do and
the defect half of this verdict is wrong too.

---

## 9 · Cross-cutting notes

**The `Require` blocks are now a weak test, and that is the lesson of this pass.** All seven
modules pass their own existence checks on 1.1.0 (OI-02), and two of them — D07 and D12 — are
nevertheless complete no-ops, because what broke was a **data field on a class**, not a method.
`Require` only checks classes, methods and globals (`Code/00_Core.lua`). A field a module keys
its whole behaviour on (`exclusive_trait`) is invisible to it. Whatever is done about D07 and
D12, the general repair is worth considering: a module whose reason for existing depends on a
field should assert that field, and report a reason string when it is gone, the way a missing
method does. Raised here; not filed as its own owner ask, because it only becomes actionable
once OI-06/OI-07 are ruled.

**The DLC (`DLC/norman`, the food DLC) touches none of the seven directly.** Its content is
farms, restaurants and food storage — no new `Community` subclass, no new `Residence`, no new
drone carrier, no new solar building. It does, however, add a large number of
`ServiceWorkplace` buildings with a Food demand (Bakery, BaristaCafe, PanoramicRestaurant,
GourmetRestaurant, FastFoodRestaurant, FoodStand, Replicator, …). That is a direct input to the
**parked** `DECISIONS_OWED.md` item **95** ("food-service default priority 3 … exactly four
buildings — Diner, Mega Mall, Grocer, Small Grocer"). That enumeration is no longer four.
Recorded here; item 95 is not reopened by this pass.

**Citations in older records.** Nothing in this report edits an existing entry's text. Where a
module header or an entry cites a 1.0.7 line, that citation is still correct **for 1.0.7** and
should be read that way; the 1.1.0 equivalents are all given above with their build prefix.

---

## 10 · ⚖️ 2026-09-17 — what the owner ruled on this report, and the two consequences of it

**The ruling (owner, 2026-09-17).** On the asks this report raised: **`Opt_DroneOverhaul` (D06)
archived as PARKED**, **`Opt_CohortHousing` (D07) and `Opt_NoHomeless` (D12) archived as DEAD**,
**`Opt_DroneStatDials` (D09) kept**. That lifted MODULE FREEZE for exactly those three and for
nothing else. ⛔ **OI-01 (`ClassicRockets`), OI-03 (D03's dead tourist guard) and OI-04 (D04's
sun-removal gap) were NOT ruled on and stay open** in `docs/DECISIONS_OWED.md`.

All three modules were **deleted** — file, `items.lua` `ModItemCode` + `ModItemOptionToggle`, and
`metadata.lua` `code` entry + `default_options` key. Counts after: **6 `Code/*.lua` files,
5 registered modules** (1 default-active, 4 carrying `optional = true`), the two sets agree;
**1 allowlisted wrap site** (was 3 — D06's two left with its file); **0 shared-symbol load-order
constraints** (both retired rules named `NoHomeless`; the pair is preserved verbatim as a comment in
`tools/doccheck.py`). Pull them, never type them: `python tools/doccheck.py --emit-counts`.

Shipping modules are now `ClassicRockets` (D01), `AcknowledgedWarnings` (D02), `ResidencyControl`
(D03), `MultipleSuns` (D04), `DroneStatDials` (D09). ⛔ **Git is the record** — restore sha
**`cc846e4`**, the last commit in which all three still shipped
(`git show cc846e4:Code/Opt_DroneOverhaul.lua`). The untracked convenience copies at
`C:\Dev\SMR-OptInPack-archive\` sit deliberately OUTSIDE the mod root, so the Mod Editor cannot
sweep a retired module into an upload pack and the junctioned game folder cannot see it.

### 10.1 · A stale Mod-Options key is INERT — removing a toggle is safe

Removing a `ModItemOptionToggle` leaves its key behind in
`AccountStorage.ModOptions[mod.id]` forever. That residue **does nothing**, and this is the engine
answer to the account-state worry raised under OI-01 (*"check what a stale `ClassicRockets` key in
`AccountStorage.ModOptions` does before promising it is clean"*). Read off
`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src\CommonLua\Modding\Mod.lua`:

- `ModDef:LoadOptions` (`:680-699`) does `table.overwrite(self.options, options_in_storage)` and
  **then** seeds defaults for the properties the mod currently declares. An extra key in storage is
  copied into `self.options` and never looked at again.
- The write path (`:755-770`) iterates the **current** `options:GetProperties()`. It never
  enumerates, never clears and never errors on a key that no longer has a property.

⇒ A removed toggle's key lingers, is read by nothing, and the Mod Options UI simply does not render
it — no crash, no reset of the player's other toggles, no migration needed. **Source-read, not run
in the game**; the falsifier is to enable a retired toggle on 1.1.0, remove it, and reopen Mod
Options expecting the surviving toggles to hold their values.

⛔ **This deserves an `EF-` fact and does not have one.** `EF-` ids are **allocated by the FIX
PACK** (`../WORKFLOW.md` reading path 2; fix pack checklist item 86) — file it there first, then
mirror it here at the same id and say so in both. **No `EF-` number was minted for it in this
repo.** Until then, this section is its home.

### 10.2 · `SMRFixPack_no_homeless` residue — real, inert, and NOT renameable

D12 wrote `SMRFixPack_no_homeless` as a **real field** onto `Dome` / `MicroGHabitatBase` objects,
through `TogglePolicy`, in any save where the policy was switched on. It is row 3 of the
persisted-name inventory (`../FIX_POLICY.md` §3) and **stays there with its exact bytes**: retiring
a module does not retire save contract, and the inventory is history as well as contract.

Scope: this mod is **UNPUBLISHED**, so the only saves that can carry the field are the owner's own
test saves. The fix pack's **Save Rescue** (its `D13`) already targets these keys, so there is a
route if one is ever wanted. With the module gone, nothing in this pack reads the field, so the
residue is **inert** — stated rather than assumed, because "stale = harmless" is exactly the kind of
claim this project files a control for. The control: load an affected test save with the current
pack and confirm no `[CommunityOptInPack]` line and no `[LUA ERROR]` mentions the field. Not run.

### 10.3 · Three TestKit probes are now orphaned — ⛔ FLAGGED, NOT EDITED

`C:\Dev\SMR-BugFixPack-TestKit\Code\60_Probes_Opt.lua` still registers `CohortHousing` (`:215`) and
`NoHomeless` (`:392`) against modules that no longer ship, and `OptionsMenuOptIn`'s `WANT` list
(`:892-901`) names all three of `DroneOverhaul`, `CohortHousing` and `NoHomeless` — so that probe
will assert toggles the pack no longer declares. D06 never had a probe of its own.

⛔ **The kit is SHARED with the fix pack and kit edits are owner-gated** — fix pack checklist item
**83**, which deliberately stayed on the fix pack's list because kit changes land in ITS tree
(`docs/DECISIONS_OWED.md`, the table at the top). Nothing in the kit was touched. **This is the
owner's call and it is the one piece of fallout from the ruling that is still outstanding.**
