# Train hub prototype, round 2: make it placeable and visible, then finish the go/no-go

## Authority

- **Owner ruling, 2026-09-18 (OI-10):** "prototype B via 3a". This is a Module B hub prototype
  with no copied art and connectors computed in Lua, and it covers interchange only (5a). The
  ruling is the owner's word for this new code, and MODULE FREEZE does not block it.
- **Owner, same day:** *"if we can use the vanilla hub just modifying it to work for our test, we
  don't need it to be pretty at all. I think I found a way to make our asset if everything works,
  but I don't want to invest time into something that ends up not working."* The deliverable is a
  **go/no-go** on whether the owner invests in an asset.
- **Owner, 2026-09-18, after sitting 1:** send the prototype back for a new round, with the two
  defects below fixed and the sitting rerun. Round 1 was built in commit `dfb8052` and ran in
  sitting 1.
- The spec is `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`: §5 covers the hub model,
  §7.2 the measured results and §10 this prototype. The two bans in `FIX_POLICY.md` bind.

## Start

Run `git log --oneline -3` and `git pull`. This brief landed at the commit that
`git log -1 --format=%h -- docs/agent/prompts/TRAIN_HUB_PROTOTYPE_high.md` names. If
`git diff --stat <that sha>..HEAD -- tools/prototypes/train_hub docs/agent/reports/TRAIN_HUB_PROTOTYPE_20260918.md`
is empty, the facts below hold. Before any write, put the end state in the todo tool, one item per
commit-and-verify unit.

## Where round 1 stands

Round 1 is a separate dev mod, `tools/prototypes/train_hub/` (mod id
`SMR_TrainHubPrototype_20260918`, class `SMRTrainHubPrototype`). It is the vanilla large-station
body with six connectors computed in Lua, in three opposite pairs. Its pre-boot predictions and
sitting 1's result are in `docs/agent/reports/TRAIN_HUB_PROTOTYPE_20260918.md`. Treat that report
as the source for what was measured.

- **Held:** slot 2 read `connectors=6 valid_elements=6`. The spot overrides work on the placed
  object, and six track-grid elements exist.
- **Defect 1, a Lua error during placement:** `HGE::l_GetSpotBeginIndex: Invalid spot` at
  `Station.lua(620)` `CanBuildOver`. Vanilla reads spots from `cursor_obj`, and the
  `CursorBuilding` has none of the virtual spots, so index 5 failed and indices 1–4 were checked
  against the vanilla entity's hexes. Falsify with
  `rg -n "cursor_obj|Trackconnector" C:\Dev\SMR-SrcArchive\1.1.0.403908\Src\Lua\Buildings\Station.lua C:\Dev\SMR-SrcArchive\1.1.0.403908\Src\Lua\Construction\Construction.lua`.
- **Defect 2, the owner cannot use it:** the connector elements are hidden (`efVisible` is
  cleared, as it is in vanilla) and the body shows only the vanilla platforms. The owner could not
  tell where to drag track. Two of the three lines cross the station body diagonally, so the
  visible platforms point them the wrong way.
- **Not yet tested:** track attachment, trains, interchange, teardown and reload (predictions
  3–8).

## End state

1. **Fix placement.** Placing the hub raises no Lua error, and its obstruction check uses the six
   computed connector hexes. Check every other reader of connector spots on the construction path
   for the same cursor problem; the lead is the `Trackconnector` sites in `TrainTransport.lua` and
   `Station.lua`.
2. **Make the connectors visible to the owner in play.** Mark each of the six connector hexes so
   the owner can see where to start a track, and make it clear which two ends form a pair (a
   through-line). Showing the markers during placement would help too. The method is your call:
   unhidden elements, a placed marker object, a ground decal, or something better. The markers
   are for the prototype only, and ugly is fine.
3. **Rewrite the predictions before boot.** Add a round 2 block to the report with what the owner
   will see and new prediction lines for placement and markers. Keep the fixture, SMRTK slots and
   aborts unless your fixes change them. Rewriting the TestKit's `Code/80_AgentSlots.lua` is
   standing permission (`tools/SMRTK.md`).
4. **Run sitting 2 with the owner** on a disposable save through SMRTK, about five steps at a
   time. Include the probe sweep first (WORKFLOW, Probe hygiene).
5. **Record** the result in the report and in spec §10, and write the go/no-go for the owner. Put
   an ask on `docs/PLAYTEST_CHECKLIST.md` only if its next action is the owner's, such as the asset
   decision.

**Done means:** all of the following, in one colony:
- The hub places with no Lua error, and the owner can see all six connector points and their
  pairing.
- Three routes each run from the hub to their own end station, and slot 1's route DUMP shows all
  three sharing the hub.
- Cargo stocked at one end station reaches both of the others.
- Demolishing the hub with tracks and trains attached raises no Lua error or assert.
- A save and reload keeps it working.

If time runs out, drop in this order: the reload leg, then the teardown leg. Name each dropped leg
as NOT RUN, and never drop placement, markers or the interchange.

## Facts you would otherwise re-derive

All were read on 1.1.0.403908 (`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`) or measured
2026-09-18.

- **A station's line is an opposite connector pair.** A train continues through a station only on
  the opposite connector (`Station.lua:931-960`). Round 1's pairs are (1,2), (3,4) and (5,6).
- **MEASURED (spec §7.2 T2):** vanilla's large station already interchanges between two routes.
  The hub's new claim is only the **third line and beyond**.
- **The Trains rollover counts each station once** across all of its routes
  (`TrainTransport.lua:492-536`), so it cannot show route count. Slot 1's route DUMP can.
- **A class or field name becomes permanent** once a kept save sees it (ban 1). Use disposable
  saves only. The owner plays one game with both mods loaded, and the dev mod stays out of it.

## Scope

In: the two fixes, the markers, the round 2 predictions, sitting 2 and the go/no-go.
Out: routing (5c/5d), Module A, the hub's final appearance, any shipped asset, any shipping
module, and TestKit files other than `80_AgentSlots.lua`.

## Stops

- The placement fix needs a change to vanilla construction that the dev mod cannot make: stop
  and report. An error during placement alone is not a no-go, so ask the owner.
- Tracks will not attach to the computed connectors, or trains will not path through them: stop.
  That is the **no-go**, and it answers the owner's asset question.
- The hub works, but demolition or reload errors in a way the prototype cannot fix: report a
  qualified go and name the failure.

## Do not claim

- "Routing works." The true claim is that N routes exchange cargo through one hub in the tested
  colony.
- "The hub works" in general. Report the fixture: its layout, the routes, trains per route and
  the stock.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once the go/no-go is
recorded.
