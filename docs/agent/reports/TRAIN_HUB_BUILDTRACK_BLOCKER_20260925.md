# Train hub build 5 — construction-group stop

**Historical stop, resolved by owner ruling `d230bd4`.** Implementation and remaining smoke:
`TRAIN_HUB_BUILDTRACK_20260925.md`. This report records the source audit only.
Build 5's original brief said to report and stop if sequential
completion conflicts with the construction group's leader logic. It does. No build-track code,
smoke, sitting, or timing measurement was made. The existing repair path and dev-mod metadata
were not changed by this audit.

Source: archived installed game tree, **1.1.1.405907 / installed build 25390750**,
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua/`.

| Field or operation | Source finding | Conflict with build 5 |
|---|---|---|
| `construction_group` | `Buildings/ConstructionSite.lua:32` says the leader adds requests and all members complete together. `Tracks.lua:329-383,419-438` puts adjacent new track sites in a group; `construction_group[1]` is the leader. | A placed line is not a series of independent sites with independent costs. |
| `construction_cost_multiplier` | `Buildings/ConstructionSite.lua:2499,2548-2549` puts cost on the leader. `Tracks.lua:460-474` sets the new-track leader's multiplier to 100 (or halves it for Transport Tycoon). | The group's request is priced as a group, not one normal element cost on every member. The brief's old `Track.lua:646` pointer is a repair-site placement line on this build; the new-track multiplier is in `Tracks.lua:460-474`. |
| `construction_resources`, `construct_request` | `Buildings/ConstructionSite.lua:701-728` lets only the leader create resource and work requests; `:1262-1273` directs a member's command-center registration to the leader. | The existing `SMROptIn_track_work` payment path reads the leader's outstanding request. It cannot infer a particular member's unpaid share from that request. |
| `Complete()` | `Buildings/ConstructionSite.lua:2671-2717` walks and completes every live member, then removes the leader. `Buildings/TrackElement.lua:860-943` defines an individual track site's completion, but does not allocate the group request to that site. | Calling the leader completes a group in one step. Calling a member directly would bypass the leader's normal accounting and leave its shared request/work and remaining members to reconcile; this is not a proven safe substitute. |

Build 4's persisted list **does** have `kind` (`tools/devmods/train_hub/Code/20_TrainHub.lua`,
`track_work` and `discover_breaks`), so the other stop does not apply. The obstacle is the group's
shared cost and completion semantics. OI-28 asked whether to retain sequential,
per-element normal-cost construction and commission a group-accounting design, or change build 5's
order and cost requirements. The owner chose native group completion in `d230bd4`; brief 04
records the ruling and OI-28 was removed in that commit.

The original audit did not implement or test the feature. The current build report tracks
drones-chain QA C1–C6 and D14(g,h); this source audit closes none of those checks.
