# Future ideas — a parking lot, NOT a backlog

⛔ **Nothing in this file is work.** An item here has not been decided, scoped,
costed or promised. Moving something out of this file means writing it up as an
entry in `docs/agent/bugs/` (with the intent + reachability discipline
`docs/agent/FIX_POLICY.md` §4 requires) or a spec in
`docs/agent/reports/` — and, for anything that changes what a player sees, an
owner decision on the fix pack's `docs/PLAYTEST_CHECKLIST.md`.

Created 2026-08-12 with the repo, empty on purpose. ⭐ **Populated 2026-08-14 by
owner ruling:** *"move anything that's possible opt ins to only the opt in
future ideas doc … want [the fix pack's] folder reserved for only bug related
items."* The six entries below moved here whole from the fix pack's
`docs/FUTURE_IDEAS.md`, histories and owner quotes preserved; that file keeps
only bug-related parking. **The fix pack file's HARD RULE travels with them
verbatim: nothing here gets built, speced, researched or prototyped until after
launch; un-parking is an explicit owner decision, one item at a time; adding to
this file is not progress.**

---

# Parked items (all moved 2026-08-14 from the fix pack's FUTURE_IDEAS.md)

## 1. Seniors in workshops — "vocation in retirement"

**What.** Let Seniors work the three vocation Workshops (Art / VR /
Biorobotics), which they currently cannot.

**Why it is a good idea.** The Workshops are the designed late-game
employment-and-morale sink, and Seniors are exactly the population with nothing
to do and a Comfort problem. Thematically it is the strongest fit in the game.

**Why it is parked.** Two real costs, neither small. It needs
**work-eligibility surgery** (not a knob), and it **collides with D07's
employed-senior exemption** — a senior who takes a workshop job would stop
cohort-migrating, which is the behaviour D07 exists to provide. So it is not an
addition to D10; it is a change to D07's contract.

**Where the material lives.** D10 entry in the FIX PACK's `agent/bugs/` (the
"Deferred (recorded, NOT in this module)" bullet); D07 entry in THIS repo's
`agent/bugs/` for the exemption it collides with.

**Cost.** Own module or an explicit D07 amendment + own decision + own
playtest. Not a rider on D10's PT-57.

**To un-park.** Owner decides the D07 interaction first — does an employed
senior still cohort-migrate, or not? Everything else follows from that answer.

---

## 2. D01 `on_activate` demand refresh — parked 2026-07-31  **[FAQ]**

**What.** Make a mid-session enable of `ClassicRockets` take effect on a rocket
that is **already parked**, instead of only on rockets that land after the flip.
Today the wrap sits on `GetFuelResourceRequest`, which is only consulted when
`CargoTransporterNew:UpdateCargoResourceRequests` runs — and nothing re-triggers
that for an already-parked rocket; the landing path is what does. The hook
answers correctly, nobody asks it. An `on_activate` would re-run it on parked,
destination-less player rockets.

**Why it is a good idea.** It would make the toggle feel instant instead of
"works from the next landing".

**Why it is parked.** Owner, 2026-07-31: *"its not a high priority, the mod
functions flawlessly, besides a already parked rocket when activated… Touching
it just invites a regression."* The limitation was already **accepted by owner
decision on 2026-07-30** and is self-correcting — the rocket picks the behaviour
up on its next landing. **Documented instead of built:** the player-facing note
now lives on this mod's card/site material (originally `MOD_DESCRIPTION.md`,
since superseded).

**Where the material lives.** D01 entry in THIS repo's `agent/bugs/` (PT-55
found it; cause confirmed in source).

**Cost.** Small — but it touches a working module's activation path, which is
the regression surface the owner named.

**To un-park.** Only if the limitation actually grates in play.

---

## 3. D11 — shuttle same-pair passenger batching — parked 2026-07-31

**What.** Let one shuttle carry several colonists on a trip when they share the
same origin→destination dome pair. Today the limit is **1 passenger per shuttle
and it is structural, not a tunable**: one `ColonistTransportTask` per colonist,
`transport_task.colonist` singular (`ShuttleHub.lua:635+`). For contrast, the
limits that ARE modifiable are cargo/shuttle (3) and shuttles/hub (10) — neither
is the constraint here.

**Why it is a good idea.** Owner, 2026-07-31: *"I love this idea."* Shuttle
passenger throughput is a real late-game pinch, and no breakthrough, law or tech
in the game touches it.

**Why it is parked.** Owner, same message: *"I think its something that has
decent risk."* Correct — because the 1-passenger limit is **structural**, this is
not a knob change; it means reworking the transport task model that colonist
movement depends on.

**Where the material lives.** D11 entry in the FIX PACK's `agent/bugs/` (full
shuttle-limits research, all source-verified).

**To un-park.** Post-launch, and only with a clear-eyed look at the task-model
rework first.

⚠️ **Multi-hop passenger routing is REJECTED, not parked** — refused by the
owner 2026-07-30. Do not re-propose it as part of this.

---

## 4. Dome infopanel row labels — this mod's rows read too close to vanilla's — parked 2026-08-02

**What.** The dome infopanel now carries vanilla's quarantine row plus this
mod's policy rows, and in their permissive states they read almost alike —
vanilla's *"Accepts Colonists"* against D03's *"Accepts new residents"*. The
owner's ask was to relabel vanilla's row to say **quarantine** outright. Two
separable pieces: (a) rename **our** D03 row so the collision disappears
(candidate: *"Open to move-ins" / "Closed to move-ins"*), and (b) clarify
**vanilla's** row.

**Why it is a good idea.** A new player reads two near-identical rows and cannot
tell which one seals the dome. Vanilla's row only names itself once it is SET —
it flips to `T(8736, "Quarantined")`, `sectionDome.generated.lua:189` — so the
ambiguity sits exactly where a first-time reader meets it.

**Why it is parked.** (a) is cheap but edits **D03, which is `tested`** (PT-49 in
full plus PT-55), so it wants its row re-checked and it is outside the D12
prompt's scope fence. (b) is gated on a capability we do not have: ⛔ **a shipped
string cannot be replaced** — re-using its id discards the replacement (**F98**,
source-verified and **live-confirmed 2026-08-02: `type(T(8821,"ZZZ"))` printed
`userdata`**), so the only replacement route is `Untranslated(...)`, which
**deletes that row's translation for every non-English player**. The fix for that
is our own `ModItemLocTable` — the F84/D10 work already parked to post-release.

**Where the material lives.** F98 and F84 entries in the FIX PACK's
`agent/bugs/` (that half of the material stays fix-pack-side); the append route
that *is* safe (`shipped_T .. Untranslated("…")` via `TMeta.__concat`, retail
light-userdata form, shipped precedent `Workplace.lua:293`) is recorded on F98.
D03's row is `Opt_ResidencyControl.lua:116-175`; the shipped row is
`sectionDome.generated.lua:177-217`.

**Rough cost.** (a) minutes plus a visual re-check on any attended sitting.
(b) small once the loc pipeline exists; unshippable before it.

**What it would need to un-park.** (a) an owner decision to touch a `tested`
module for a cosmetic reason. (b) `ModItemLocTable` landing first — and even
then, prefer the **append** route over replacement so translations survive.

---

## 5. Dev/cheat tooling that actually works on retail — parked 2026-08-10; ⚖️ destination re-ruled HERE 2026-08-14

**What.** Expose the game's own dev affordances to players on a retail build and
repair the ones that throw there. Originally framed as a separate mod; ⚖️ **the
owner re-ruled 2026-08-14:** *"dev/cheat tool would be opt in territory though
since its not a bug fix"* — if ever built, it is a module (or module family) in
THIS mod, not a separate product.

**Why it is a good idea.** The affordances already exist and are already drawn —
`InfopanelObj:CreateCheatActions` (`Infopanel.lua:22-52`) builds a toolbar button
for every `Cheat*`/`AsyncCheat*` method on the selected object's class, and
`CheatToggleInfopanelCheats()` (`Cheats.lua:290`) is a shipped, localized
cheat-menu entry. A toolkit would surface shipped functionality, not invent it.

**Why it is parked.** Different audience from everything shipped so far, and
two honest costs recorded with the 08-14 re-ruling: this mod's card promises
"eight opt-in gameplay modules" (a cheat surface changes what the product is),
and the gate it must widen — `AreCheatsEnabled() = Platform.cheats or
AreModdingToolsActive()` (`gamelib.lua:1035`, `Mod.lua:145`) — is the first
design decision and the first ethical one: on PC, mods do not block Steam
achievements.

**Where the material lives.** `F101.md` (`wontfix`) in the FIX PACK's
`agent/bugs/` holds the whole derivation: the gate; the two shipped buttons that
throw once it opens (`TestMeteor` defined only under `Platform.cheats`,
`Meteors.lua:1086-1088`, with ungated callers incl. `Building:CheatMeteorHit`;
`GetSpotNameColor` absent on retail, called by `GedGameObjectEditor.lua:104`);
both repair sketches incl. the no-new-global route; and the working instrument
to copy (`CheatBreakElement`, `TrackElement.lua:436-438`, ungated, works).

**Rough cost.** The two repairs are ~60-80 lines; the gate/UX design is the
real work.

**To un-park.** Launch first, then an explicit owner decision. F101 stays
`wontfix` in the fix pack either way — the fix pack never grows a cheat surface.

---

## 6. D01 export half — standing PreciousMetals demand (+ F56 auto-offload)

**What.** Restores the ORIGINAL game's behaviour where every landed rocket
carries a standing `PreciousMetals` export demand up to its
`max_export_storage`, gated by a per-rocket `allow_export` toggle — so drones
fill a parked rocket with rare metals without the player driving the payload
dialog. It also **owns F56** (auto RC Transports never offload into rockets),
which must be decided in the same pass so a player can't get emptying without
refilling. Rides the same `ClassicRockets` flag as the shipped fuel half.

**What it relates to.** `Opt_ClassicRockets` (this repo); F56 (fix pack
`agent/bugs/`, `wontfix` with the belongs-here note); the same machinery as
F50/F68/F70/F71.

**Why it is parked.** By D01's own verdict this is **not a defect** — it is
fidelity to the original. It needs three research questions answered (the
`allow_export` UI mapping; whether the modern Earth-arrival path actually SELLS
unrequested metals aboard; what the original did about RC auto-offload), a
build, a probe and a playtest, and it edits a busy shared system. The *design*
call is already made (owner 2026-07-26: match the original, no invented
thresholds). *(In the fix pack file this sat under "proposed for parking,
awaiting yes/no" — the owner's 2026-08-14 move order supersedes: it parks
here.)*

**Where the material lives.** D01 entry in THIS repo's `agent/bugs/` (research
questions listed, legacy loader citation `RocketBase.lua:1729-1736`).

**To un-park.** Post-launch owner decision; answer research question (2) — the
sell path — before anything is written, since it decides whether the feature is
even coherent.
