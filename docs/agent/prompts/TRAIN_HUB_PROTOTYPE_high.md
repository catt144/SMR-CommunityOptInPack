# Train hub prototype: can one hub carry three or more routes? A go/no-go build

## Authority

- **Owner ruling, 2026-09-18 (OI-10):** "prototype B via 3a". Build the Module B hub prototype on
  option 3a (no copied art; connectors computed in Lua), interchange only (5a). This ruling is the
  owner's word for this new code. MODULE FREEZE does not block it.
- **Owner, same day:** *"if we can use the vanilla hub just modifying it to work for our test, we
  don't need it to be pretty at all. I think I found a way to make our asset if everything works,
  but I don't want to invest time into something that ends up not working."* Appearance is out of
  scope. The deliverable is a **go/no-go** that tells the owner whether to invest in an asset.
- **Owner target (spec §6, OPTION 5):** a routing network whose hubs each meet three or four
  lines. 5d and 5c (routing) are later decisions and are not this build.
- The spec is `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`: §5 is the hub model, §7.2
  the measured results, §10 this prototype's shape. The two bans in `FIX_POLICY.md` bind.

## Start

`git log --oneline -3`, `git pull`. This brief landed with the spec at the commit that
`git log -1 --format=%h -- docs/agent/prompts/TRAIN_HUB_PROTOTYPE_high.md` names. If
`git diff --stat <that sha>..HEAD -- docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` is
empty, the facts below hold. Put the end state in the todo tool before any write, one item per
commit-and-verify unit.

## End state

1. **Spike (§7 item 6, §10 step 0).** Can a class present more than four track connectors to all
   twelve spot-reading sites (§5.4)? The lead is overriding `GetSpotBeginIndex` / `GetSpotPos`, and
   the fallback is the six `TrackConnectedObjBase` methods plus wrapping the two external readers
   (`TrackElement.lua:345`, `Train.lua:660`). Neither is prescribed.
2. **Build the hub.** A `Station` subclass, so it keeps storage and the balancer, with **at least
   six connectors (three lines)**. Your call is the cheapest body that works: PassageHub's entity,
   a vanilla station's entity with computed extra connectors, or anything else. It must not look
   finished.
3. **Test it with the owner in game** on a disposable save through SMRTK. Rewriting the TestKit's
   `Code/80_AgentSlots.lua` is standing permission (`tools/SMRTK.md`). Slot 1 of the last sitting
   already DUMPs station stock and every route's station path (TestKit `adfe3ee`).
4. **Record** the result in spec §10 and the go/no-go for the owner in a short report under
   `docs/agent/reports/`. Put an ask on `docs/PLAYTEST_CHECKLIST.md` only if its next action is
   the owner's, such as the asset decision.

**Done means:** in one colony, the hub is buildable. Three routes each run from the hub to their
own end station, and slot 1's route DUMP shows three routes sharing the hub. Cargo stocked at one
end station reaches both of the others. Demolishing the hub with tracks and trains attached raises
no Lua error or assert (`PassageHub.lua:50-55` warns that teardown is where hubs break). A save and
reload of the disposable save keeps it working. If time runs out, stop after the spike and report
it: the spike alone answers most of the go/no-go.

## Facts you would otherwise re-derive

All were read on 1.1.0.403908 (`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`) or measured
2026-09-18.

- **Vanilla stations have connectors 1–4,** in pairs (1,2) and (3,4). A train continues through a
  station only on the directly opposite connector, so each pair is one line. Falsify with
  `rg -n "last_connector_idx|for i = #spots - 1, 1, -2" Lua/Buildings/Station.lua` and
  `Station.lua:931-960`.
- **MEASURED (spec §7.2 T2):** a large station whose two parallel lines carry two routes
  interchanges cargo between them, and balancing settles at network-wide capacity shares. The
  hub's new claim is only the **third line and beyond**.
- **The Trains rollover counts each station once** across all of a station's routes
  (`TrainTransport.lua:492-536`), so it cannot show route count. Slot 1's route DUMP can.
- **A new class or field name is permanent** once a kept save sees it (ban 1). Only disposable
  saves until the owner rules otherwise. The owner plays one game with both mods loaded, so the
  prototype must not reach that game.

## Your call

Where the code lives and how it stays out of a release and out of the owner's game: an
off-by-default option the release excludes, a separate local dev mod, or something better. Also
the body, the connector geometry, and whether the spike needs a throwaway first. Record each call
in its commit message.

## Scope

In: the spike, the prototype hub, its SMRTK sitting, and recording the go/no-go.
Out: routing (5c/5d), Module A, any shipped asset, any shipping module, and TestKit files other
than `80_AgentSlots.lua`.

## Stops

- The spike and its fallback both fail: stop and report. That is a **no-go**, and the owner's
  asset question is answered.
- Anything needs a shipped asset or an edit to a shipping module: stop. That is an owner call.
- The hub works but demolition or reload errors in a way that is not fixable inside the
  prototype: report it as a qualified go, with the failure named.

## Do not claim

- "Routing works." This is interchange (5a). The true claim is that N routes exchange cargo
  through one hub in the tested colony.
- "The hub works" in general. Report the fixture: its layout, the routes, trains per route and
  the stock.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once the go/no-go is
recorded.
