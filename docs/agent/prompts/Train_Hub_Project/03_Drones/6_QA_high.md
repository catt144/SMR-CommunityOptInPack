# Drones chain, link 6 — terminal adversarial QA, fresh context

**Link 6, the last link of the `03_Drones` chain** (`README.md`). **Fresh context, and the owner
runs it on a different model from the links it audits.** Trust nothing forward: every earlier link's
report is a claim until you check it against the code, the commits and the logs.

Read `DESIGN.md`, this folder's `README.md`, and your `## Notes from upstream`. `git log`,
`git pull` both repos first.

## Authority

The chain method (`docs/agent/support/CHAIN_METHOD.md`): the terminal link audits every handoff that
landed, sweeps owed work, checks consistency, samples verdicts against primary evidence, and holds
the folder-empty gate. Its value on a clean run is certification plus residue, not rescue.

## End state

1. **Every handoff landed.** Each earlier link's notes reached the link that needed them, and what
   shipped matches what its report claims. Sample the strongest claim of each link against the code.
2. **The bans.** The persisted name is in the inventory, spelled the same in code and record, with
   its kind field for build 5; no executable reference crosses to the fix pack.
3. **`DESIGN.md` against the build:** each owner ruling either implemented, or explicitly recorded
   as overtaken with the owner's word behind it. The pad-to-pit change is the known one.
4. **Owed work swept:** what the smoke did not cover (both configurations, both toggle directions),
   anything routed to the owner still open, and every drift instance the links logged.
5. **The gate:** this folder holds only `DESIGN.md` and `README.md` when you are done. A link file
   still here means that link did not finish; say so rather than deleting it for them.
6. A verdict of PASS, PASS WITH CORRECTIONS or FAIL, with the corrections listed as work, and the
   kickoff line for whatever the owner has queued next, or a line saying nothing is queued.

⚠️ **The game patched mid-chain**, 1.1.0.403908 → **1.1.1.405907** (installed build 25390750), and
`doccheck --emit-fingerprint` reports every fact group MOVED. Every chain report written before
2026-09-23 cites a tree that is no longer installed. Judge those citations on that basis: a claim
whose line number moved is not thereby wrong, but it is unverified until re-read, and the queued
sweep (`prompts/perma/gamepatch/`) is where that work belongs, not silently inside your audit.

**Two flight implementations exist:** engine mode (`9a540dd`) and the scripted flight preserved at
tag `drones-scripted-flight-20260923`. Check that the one link 3 chose is the one link 4 built
against, that the other is either removed or knowingly kept, and that `OI-26`'s ruling (the 7 m
engine ride) is recorded where the obeying role reads it, not only in a report.

## Live work list

One todo item per commit-and-verify unit.

## Scope

In: auditing this chain's work and records. Out: building, redesigning, or fixing what you find
beyond a one-line records correction — those become listed work, not your edits.

## Stops

1. A claim cannot be checked because its evidence was never committed: record it as unverifiable,
   which is a finding, not a blocker.
2. You find a fault that makes the build unsafe to keep: stop and route it to the owner with the
   evidence.

## Do not claim

Do not certify what you only read a report about. Name the command, or the file and line, behind
each verdict.

## Notes from upstream

### L5 handoff, 2026-09-25 — the smoke closed; audit it against the report

The report is `docs/agent/reports/drones_chain/L5_SMOKE_20260925.md`; the hub report's "Build 4
smoke" and spec §10's "Drones L5" carry the rulings. Treat each as a claim and sample it against its
commit and the named log. The L5 commits are `git log --grep="Drones chain L5"`, plus `ca586d1`
(storage).

**Left for you, or for the owner through you:**
- Never seen in play: the reassign buttons greyed on hub Wasps; a rocket refusing a hub Wasp as
  cargo; whether `Idle`'s go-home distance bounces a far fleet Wasp home repeatedly; the absence of
  cube hauling between stations; `SMROptInHubFlight.Lost` read after a long run, including a Wasp
  left past the 60 s hold timeout (end state 3); a dead grid (only the malfunction ran); OI-27, the
  cross-map drone policy, never asked; the storage cap (`ca586d1`) in play.
- The door route's mesh clearance is unmeasured. The committed receipt bounds only the tagged
  scripted flight. `DoorRideHeight` 200 and `DoorOutDistance` 3000 are guesses the owner has not
  dialled.
- Deferred by the owner to the import/export and dials work: `DESIGN.md` §6 train construction (the
  report holds the 1.1.1 source reading and a ready test) and cargo kept aboard at a full hub.
- Moved: the Wasp palette default, to brief 05 (its "Handed over" section).
- The ship test: neither configuration and neither toggle direction was run.

**Drift since "L5 drift" below:**
- The owner backtracked the pit swarm launch (`dba55af`, never seen) to a train-door launch within
  the sitting (`3c47ce2`). The chunk steps `7ddb822` (5/10/20/30) were replaced by 5/15/25 with a
  5-slot repair reserve (`cf14791`).
- L5 shipped `3c47ce2` with a door count that crashed the flight driver in the game (36 errors, log
  `Mars.exe-20260925-13.34.56`). The mock returned -1 for a missing spot where the engine raises;
  `ad5113b` fixed both. The first in-game run stranded every launched Wasp until a restart.
- Item 9 ran on a demolish, not a salvage: a salvage cannot remove a hub. The owner's earlier
  demolish-and-rebuild used the TestKit's `CheatDelete` and quick-build, which deleted the dropped
  pile (vanilla's cheat path).
- The autosave was closed by argument, not by a run: the slot save shares `DoSaveGame` and the
  unpaused window (the report cites the lines).
- The storage change (`ca586d1`) came at close-out, outside the smoke's scope, on an owner ask. It
  overrides vanilla's `RecalculateDerivedMaxZ` with vanilla's own body, sized from min(storage,
  150000); no mock covers it.
- The spot-name finding is filed as **EF-117** (fix pack `c41ccb1`, mirrored here). Two `< 0` checks
  after `GetSpotBeginIndex` remain in `30_TrainHubDrones.lua` and are dead code under it: the pit
  spots in `F.PitPoints` (:131) and `Enter1`/`Enter2` in `tunnel_inner` (:251). They cannot fire on
  today's bodies, and they were left unchanged.
- The clearance receipt was re-pinned twice (`3c47ce2`, `ad5113b`) with identical geometry. The
  2026-09-25 session ran `claude-opus-5-5[1m]`.

### L5 drift, 2026-09-24 (the attended sitting, fixes built in-link under the owner's ruling)

- L3's accepted fix `HandoffAt="outside"` was never made the file default: `1b32bc8`.
- The hub dispatched before a new site's requests existed; the claim held nothing (`68ad91b`, found by the short-stock case).
- The runtime XTemplate panel section never rendered in play, although every smoke passed it (`c73a286`). The mocks could not see it.
- `DESIGN.md` §2's "the timer is the only authority" is overtaken: the flight is the authority and a lost Wasp is relaunched (`c764ea4`, `89330ed`). `MinVisualTime` is gone.
- The L4 fleet tiers on vanilla's load word are replaced (`3955ab5`, `7ddb822`).
- L5's own error: it told the owner the persist error was vanilla's and came with 1.1.1, from logs that held no saves. The audit found it was ours (`99a8cd9`'s global `WaitWakeup`).
- L5's console lines twice failed to parse or indexed nil (a method reference without a call, `MapGet` absent in the console).

### Audit drift, 2026-09-24

`reports/TRAIN_HUB_AUDIT_111_20260923.md` consumed brief 07 under its no-game-state
stop. The later owner sitting resolved the stall as D14(f)'s siding reservation
deadlock and confirmed trains unstuck after the guard correction (§9). The old
guard fails the paired-siding regression; incoming/moving/crossing controls remain.
Native visual clearance was not explicitly confirmed. Exhaustive source-field/citation resolution remains OPEN;
the recursive inventory is lexical candidate evidence, not certification. D14(a)'s
`3a0faff` passed its source test but the owner then hit loader assertions and CTD
on the old autosave and known-good templates. That repair is withdrawn; the legacy
dwell closure was restored exactly. Read §8:
the test missed the Lua→C permanent transition when loading an old save. Require
old→new→save→reload controls for a replacement; native template and autosave
rollback loads passed while that pre-guard process still logged C-function persist errors.
Neither a matching source copy nor a same-version collector test proves migration.
The subsequent snapshot guard `102f5f0` (§10) preserves that legacy wrapper body,
temporarily restores the native waiter around PersistGame and adds an explicit
metadata marker for new loads. Updated mocked tests pass; native controls in
§§11–12 now cover legacy loading, a 128× autosave/reload cycle, a new manual save
and its fresh-process reload. The closed writer log and fresh-load prefix contain
no persist/load/crash failure markers; the existing ArtSpec/Braze startup errors
remain. ck215 is consumed. Autosave-specific cold reload was not separately run;
pre-wrapper unmarked hub saves remain ambiguous, and drone-flight adoption was
not exercised by that general colony run.
Repair smoke had incorrectly removed each completed repair group immediately;
it now keeps groups until the final unfinished site completes, with a failing
old-fixture control. Traffic smoke remains red on the known obsolete geometry
expectation. Flight code/receipt were unchanged. No native game ran in the initial audit;
the first later owner loads failed, followed by the successful rollback controls. No clearance
or both-configuration result was earned. OI-27 carries the cross-map policy;
D14(b-e) carry cross-map, nanite, track-split and editor-load residue. The report
lists read-command failures and the unavailable todo tool. The peer icon edit
and UI files were left outside the commits.

- **L1 evidence commits:** verbatim reports `ac32389`; shared EF allocation Fix Pack `38022d1`;
  Opt-In mirror `079a347`; synthesis/lifecycle commit is the one deleting link 1. Sample claims
  against those commits, not chat.
- **OI-25:** approved by the owner on 2026-09-22; L2 records the offset floor/rim column in
  this chain's README and spec §10, and removes the answered checklist item.
- **Design drift:** `DESIGN.md` names generic `ConstructionSite:Complete`; source says the concrete
  track path is `ConstructionGroupLeader:Complete` → `TrackConstructionSite:Complete` (`EF-112`).
  The design reference was intentionally left unchanged.
- **Source/runtime residue:** physical graph BFS, Wasp palette response, arbitrary-distance manual
  approach, save teardown/race and pit flight are source or geometry conclusions only; later links'
  native smokes must not promote them without the named probes.
- **Command drift:** SMR-Assets has no remote, so its requested pull could not run. The pit report
  pins Assets HEAD and input hashes; verify again if any fingerprinted file moves.
- **Report drift:** `agents/drone_surfaces.md`'s `rg -F` exact-literal loop loses embedded quotes in
  Windows PowerShell 5.1. Parent verification passed with `Select-String -SimpleMatch`; use that
  equivalent when auditing, and keep the failed command as evidence rather than silently rewriting
  the verbatim report.

L2 evidence: `docs/agent/reports/drones_chain/L2_FLIGHT_20260922.md` and its drift inventory.
Its actual Lua is exercised by `tools/devmods/train_hub/tests/flight_smoke.py`, with mocked
objects/clock only. L3 owns live clearance and import survival; L4 owns persisted deadlines.
The metadata registration line entered the shared history in `24ffa82` during this link,
alongside a changed mesh, so L1's old margins do not certify the current geometry. No art was
edited by L2. L2 removes its spent row rather than striking it because the map gate rejects
tombstones. Read-command mistakes and initial mock expectation failures are preserved in the
report; they are not native failures or successful flight evidence.

### L2E handoff, 2026-09-23

Engine mode landed in `9a540dd` on `16a69e3`; report `L2E_ENGINEFLIGHT_20260923.md`. Audit: the
static gate (only `STOCK_LEG`/`STOCK_HOLD`/`false` reach `SetCommand`/`QueueCommand`; no class
assignment) and the mocked command machinery, which is the whole basis of the "never Idle" claim —
a real `Idle` in link 3's sitting falsifies the model, not the mock. Drift: HEAD moved mid-link
(`16a69e3`, Spec 9) and two peer files sat modified in the tree at commit time, committed by
pathspec; a pre-existing spawn-instant recall error was fixed in passing; `DespawnNow` was declined
against the brief's preference with `KillDrone`'s membership assert as the reason; Blender wrote
the receipt CRLF and it was normalised before commit; the smoke's solver spy moved from the 1.1.0
to the 1.1.1 archive. The receipt bounds the scripted chords only; engine legs are unbounded.
`OI-26` asks the 7 m ride ruling. No game ran.

### L2R handoff, 2026-09-22

Read `docs/agent/reports/drones_chain/L2R_EXITROUTE_20260922.md` and its drift table. The actual
route is checked by `flight_smoke.py`; `exit_clearance.py` measures swept level-Wasp envelopes
against evaluated Blender geometry and optional panels. Its committed receipt pins inputs,
counts, per-leg bounds and worst triangles; none establishes native clearance.
The route keeps OI-25's +1000 crest before lowering into the under-deck lane: audit this explicit
interpretation against L3's visual result. Track height is a stated guess, awaiting a train pass.

Scope extension: the first smoke failed because `d48871e` deleted the flight metadata entry;
L2R restored that single entry, without claiming import survival. Shared geometry changed
between measurement runs; the final receipt was re-measured and hash-checked. No art changed
in this link. Initial nonexistent-path / escaped-underscore / wildcard reads failed without
writes. Spent row removal follows the map gate instead of the brief's literal strikethrough.
Review L3 for all native obligations and L4 for unchanged save/deadline authority.

### L2M handoff, 2026-09-22

Motion build `74b1e4a`; report `docs/agent/reports/drones_chain/L2M_MOTION_20260922.md` has the
leg-by-leg decision, commands/hashes, tuners, measured clearance and complete drift table.
The native claim is timed ComponentInterpolation only; native curvature/FlightGoto are unused.
The archived FlightGoto body ran with a solver spy, not with C++ Flight_Step or in the game.
Do not turn that source-contract test into native evidence. L3 still owns the visual verdict.

Audit the drift: coarse-prism clearance first failed at RingClamp_1 (−0.053805 m); conservative
time subdivision resolved the false-positive hull without changing safety allowances. Reverse
sampling caught a duplicate-waypoint timing asymmetry, now shared equally. Old axis-only smoke
expectations were replaced. Early recall necessarily changed to curved braking/retrace; normal
deadlines remain asserted. The final receipt proves positive source-mesh bounds including bank
and interpolation; its smallest is 0.123799 m at Ring, not a measured native closest distance.

Scope extension is the existing clearance instrument and a new receipt, needed to measure the
new motion. No art, hub implementation, dispatch or persisted state changed. Concurrent
`08bca5b`, `061d6cb`, `63790bc` are separate diffs; `061d6cb` restores the flight code-list entry
after another import. Import survival is still owed. Assets had no pull target. The report
retains failed read/patch attempts, initial long-running-tool handling and discarded measurements.
L2M deletes its spent file and removes its row together, and clears the parent map's block.
Review the fresh L3 handoff for every native obligation, and L4 for economic/save integration.

### L2M2 handoff, 2026-09-22

Motion build `d77efa4` plus `6d89b1a` and `b84f106`; report
`docs/agent/reports/drones_chain/L2M2_FLUIDITY_20260922.md` has the three faults, their causes
read from the code, the leg-by-leg mechanism, commands, hashes and the drift table. Audit these:
the driver is a game-time thread (a mod-owned thread under FIX_POLICY §3a layer 1, gated and
deleted at SaveGameStart; a departure from L2's "REAL-time driver" header); `Speed`/`ClimbRate`
changed meaning from deadline budgets to speed caps, so the console deadlines now move with every
dial (the L2M smoke's "deadline independence" assertion was replaced on purpose); six tuners were
retired and one added; `TurnRadius` kept its name but its default grew fivefold; `BankAngle` may
be negative. The clearance instrument gained two export fields (`chord_horizon_ms`, per-span
`bank_minutes`) and reads them with the old defaults as fallback; the receipt was re-measured
after a line-ending normalisation because its first hash was of a CRLF working copy. FlightGoto
was again not adopted, this time with the class-static parameter reason (Flight.lua:149-160);
ComponentCurvature stays off with the reason that no shipped Lua calls it. Peer commits
`8e2c827`, `2b64304`, `1fbdf49` landed during the link and touch no flight code. **Mock-green,
game-red:** the owner's first console run of `d77efa4` raised `HGE::l_SetAcceleration: Expected
integer`; the cause is the engine's integer division of integers (EF-116, fix pack `2812098`,
mirror `de8a92b`), which a lupa mock cannot show, and which most likely also explains L2M's
stutter (its sampler's `u` could only be 0 or 1 in game). `b84f106` routes every division through
`div()`, every engine number through `int()`, and gates the source in the smoke; audit that the
gate holds (`grep -n "[^/]/[^/]"` on the flight file finds only `div`'s body) and that the
owner's control line `*r print(7/2, 7*1.0/2, math.type(7/2))` was run before link 3 tuned
anything. No game ran in this link beyond that one failed console line; the smoke's chord
contract is mocked Lua, and the claim of fluidity is left to the owner.

### L4 handoff, 2026-09-23

The hub half landed in `b556035` on `b1f62be`; report `L4_HUB_20260923.md`, whose drift inventory
is the audit list. Sample: the persisted shape against the section's header and inventory row 11;
the four dispatch gates and the 50 %/100 % arithmetic in `repair_smoke.py` against
`Track.lua:651-656` and `ConstructionSite.lua:731-760`; the claim (`AssignUnit` at dispatch,
`UnassignUnit` then `AddResource(-n)` at completion) against `10_TrainFloor.lua`'s reserve; the
`Station:ShouldAddRequestToCommandCenter` override's scope (out of range only, maintenance
requests only, the original always called); `Finalize`'s callers (`DroneControl.lua:341-352`).
Drift to weigh: the flight file was edited although the brief scoped its internals out (`F.Adopt`
and the load sweep's move, both named by the brief's own handoff text; 53 lines); `flight_smoke.py`
was red at HEAD before this link from L3's dial commits landing without a smoke run, and its
receipt hash had not matched the source since `7e02763` (both fixed in `b1f62be`, the scripted
suite now pinned under the tagged dials); the Blender clearance at the settled lane FAILS
(`Platform_6` −0.637 m, `RingPillar_4` −0.052 m) and the committed receipt bounds the tagged
flight only, stated in its `mode` field; the owner saw resource balancing in play from the
uncommitted tree and the fix landed before commit; `EF-115`'s 1.1.0 `CanBeControlled` body is
corrected in the fact; the fleet does not launch from the pit (declared, link 5 asks). The peer's
brief 06 committed twice mid-link with files left modified in the tree; committed by pathspec.
No game ran.

## Lifecycle

Your report is the chain's close-out. **Delete this file and strike its row in `README.md` in the
same commit**, leaving the folder at `DESIGN.md` + `README.md`.
