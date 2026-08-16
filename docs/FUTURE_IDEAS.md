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

---

## 7. Drone seed-supply routing pair — the "gleaner" + the scattered-source brake — parked 2026-08-15, ⚖️ destination ruled by owner the same day

**What.** Two complementary drone-judgment options born out of the fix pack's
`C47`/`C48` farm investigation: **(I) a seeds-only cargo top-up** — after a
drone picks up one plant's 280-seed offer, let it claim more nearby offers
until full before delivering (~10× fewer trips for the same flow on a
+2-carry rig), and **(J) the developers' own 150 distance brake** applied to
vegetation seed offers (`supply_dist_modifier = 150`, the exact number and
comment they gave surface deposits).

⚖️ **Why it is parked HERE and may never touch the fix pack — owner ruling
2026-08-15, verbatim:** *"I am not going to manipulate drone behavior on a bug
fix mod."*

**Why it is a good idea.** Measured, not argued: 134 deliveries on the owner's
own colony, not one a full drone trip, 84% exactly one bush's yield, while
12.4M stored seeds sat untouched — every landscape trip wastes ~90% of the
drone's capacity. The full design with verified seams, guards, save-safety
shape and the known limit of the brake: **`agent/reports/
DRONE_OVERHAUL_OPTIONS.md` §I+J** (added 2026-08-15).

**Where the material lives.** That report section; fix pack `agent/bugs/C47.md`
+ `C48.md` (the measurements); this repo's `D02.md` (the flapping boundary from
the same sitting).

**To un-park.** Post-launch owner decision, one option at a time. ⚠️ J's fate
also hangs on the fix pack's brake-intervention leg — if that refutes the
distance knob, only I survives.
⛔⛔ **It did, the same evening: J is REFUTED by measurement** (the leg applied
the brake at 100% and the routing did not move — see the report §J amendment
and fix pack `agent/bugs/C48.md`).

⭐⭐ **AMENDED 2026-08-16 — THE WHOLE FARM CASE IS NOW THIS HOUSE'S, by owner
ruling** (*"it is bug territory in practice even if not logic … has to be in
opt in as its tinkering with drone logic"*): the mechanism was closed by the
pairing-log leg (985 witnessed decisions; storage depots are a strict last
resort, categorically — full report `agent/reports/SEED_LOGISTICS_HANDOFF.md`),
and the parked set here is now **I (gleaner) + K (pairing policy: bank crumbs
to depots, feed consumers from depots, farm-only or all-consumer scope) + the
K-probe (flag-brand experiment, runs FIRST)** — designs in
`DRONE_OVERHAUL_OPTIONS.md` §I/§K. J stays dead as a tombstone.

## 8. "Open Domes" discoverability — the endgame law the game says you have and you cannot find — parked 2026-08-16

**What.** QoL options for the moment terraforming turns the atmosphere
breathable and the *Planet Habitable* popup announces *"The Open Domes law has
been unlocked"* — while the policy itself can still be an unnamed **?** in the
Politics grid with no route to it. Candidate shapes, cheapest first:
**(L) reveal-on-unlock** — force the `OpenDomes` policy slot to `visible` once
`BreathableAtmosphere` is true, leaving the prepare-chain untouched for every
other policy; **(M) honest popup** — append the real remaining requirement to
the `AtmosphereBreathable` popup text; **(N) name the "?"** — let a locked hex's
rollover name the policy it hides instead of the generic *"Prepare more laws in
the category to unlock this law"*.

**Why it is a good idea.** Owner hit it live on their own campaign 2026-08-16 —
two full sessions cycled, no dome option anywhere, and read the grid as broken.
It is not; it is **two independent gates and the game only announces one**.
⭐ **The cost is player-confirmed, not estimated:** the owner then reached the
law organically and *"had to work my way down the row"*, exactly as the chain
predicts (`EF-058`).

- **Gate 1, announced.** The law's `DisableConditions`, *"Must have Breathable
  Atmosphere"* — Atmosphere ≥ 95% **and** Temperature ≥ 50%
  (`Data/LawDef/LawDef-Research.lua:632-644`; `Data/TerraformingParam.lua:86`
  + `:143`).
- **Gate 2, silent.** The policy grid's sequential prepare-chain. `OpenDomes` is
  `SortKey 900` — **10th of 11** in **Research & Ecology** (`ResearchAndSafety`)
  — and a slot only turns `visible` when *every* earlier slot in the row has
  been **prepared**; visible-but-unprepared blocks the rest of the row exactly
  as hard as locked (`Lua/Factions/Legislature.lua:1085-1140`, `are_prev_prepared`
  `:1075-1084`). A Martian Assembly lifts the 3-per-category cap but not this.
- **Nothing links them, and nothing is broken.** `SetAtmosphereBreathable`
  (`Lua/Terraforming.lua:304-366`) never touches the Legislature — there is no
  reveal path failing to fire, no dead branch to repair. That absence is
  precisely why this is not a fix-pack item.
- **The game's own two variants disagree.** `AtmosphereBreathable` and
  `AtmosphereBreathableNoPoliticsRule` share title and body and diverge in one
  line: with politics off the player gets an *"Open the Domes"* button on the
  spot (`Data/PopupNotifications/PopupNotificationPreset-GreenMars.lua:15-19`);
  with politics on they get "unlocked" and no route.
- **The locked hex never names what it hides** (`Data/XDef/LawEntry.lua:155`
  + `:212`), so the announced law is undiscoverable by inspection.
- **Player cost when it bites:** 8 further preparations, one per session,
  sessions 1 Sol apart (`LegislatureBetweenSessions` = 1440000ms = 1 Sol).
  Accelerators exist and blunt the severity — Efficient Assembly's instant
  prepare (`Legislature.lua:767-781`) and a Law Office auto-preparing a random
  visible policy every ~3 Sols (`DLC/thomas/Code/LawOffice.lua:41-63`).

⚖️ **Why it is parked HERE — ruled on the spot 2026-08-16.** No shipped-Lua
defect: every line behaves as written and the mechanic *is* generically
explained in-UI. A reveal or a reword is a design change, not a repair, so it
cannot enter the fix pack. Severity is feel, not function — the law is
reachable the whole time.

**Where the material lives.** ✅ **The fact debt is PAID (2026-08-16, same
day):** the mechanism is `agent/facts/EF-057` (breathability is a
two-parameter quorum; which effects belong to the atmosphere and which to the
law) + `EF-058` (the policy grid's prepare-chain, its caps and bypasses, the
session economy, and why a locked hex can never name itself). Mirrored in the
fix pack as `EF-061`/`EF-062` — amend both or neither. This entry keeps only
the QoL shapes and the ruling.

**Rough cost.** Unscoped. M and N look like text/rollover work; L needs a seam
on the policy-state recalc plus a save-safe way to hold the override — **no
seam has been verified**, and `RecalcPoliciesState` is a plain `Legislature`
method, so the flattened-class trap does not obviously apply but has not been
checked either.

**To un-park.** Post-launch owner decision, one shape at a time. The one item
that was worth doing even if all three die is already done (the facts above),
so un-parking starts cold at seam work: L needs `RecalcPoliciesState` wrapped
and a save-safe home for the override; M and N need the loc-string discipline
any player-visible text change carries.

## 9. Per-fix player toggles for the FIX PACK — a Mod Options page like the one we admired — parked 2026-08-16

**What.** A player-facing on/off switch per fix in the **fix pack** (not this
mod), reached the way every other setting is: Main Menu → Options → a page
listing the modules with checkboxes. Parked HERE and not in the fix pack's own
`FUTURE_IDEAS.md` per the 2026-08-14 ruling that reserves that file for
bug-related items only — same routing as #5 (dev/cheat tooling).

**Why it is a good idea.** Owner, 2026-08-16, on seeing the parallel community
fix mod's options page: *"I genuinely like that he allows people to turn off
fixes in his pack as well."* And the gap it exposes is real and currently
total — **a player cannot disable a single fix of ours by any route:**
- the `SMRFixPack_Disabled` veto is read at mod load (`00_Core.lua:384-388`),
  so it only works from **a companion mod that loads before ours** — a modder's
  tool, not a player's;
- ⛔ the developer console cannot do it — by the time anyone can type, the fixes
  are applied;
- ⛔ the fix pack has **no Mod Options page at all**, and the reason matters:
  not a decision against toggles, but a consequence of the opt-in split leaving
  it with nothing left to configure, so the engine correctly stops listing it
  (checklist, 2026-08-12 build notes).
⇒ The argument gets stronger as the pack grows: 75 modules today, and the
"one mod fixes all" direction (`agent/prompts/COVERAGE_SWEEP_SMRCF.md`) points
at more. A player who dislikes exactly one fix currently has one remedy —
uninstall all of them.

**Where the material lives.** ⭐ **The capability is already built and shipped
in THIS mod:** the opt-in pack's own Mod Options page gates its 7 modules, so
the template, the persistence and the gamepad surface all exist and work. Fix
pack `FIX_POLICY` §7 carries the surface rules (*"Mod Options is the one
universal surface (gamepad-native) — anything a console player must be able to
steer goes there or nowhere"*, and the note that every log/console surface is
invisible on console).

**Rough cost.** Unscoped, and bigger than it looks — the page itself is the
easy part. Real questions: what a mid-save toggle means for a fix that has
already changed state; whether toggling needs the full restart a Mod-Manager
disable needs (`D13`); how 75+ entries stay navigable (their page has search
and version grouping, which is why it works); and a save-safety pass under
`FIX_POLICY` §3a for anything that can now be switched off at runtime.

**To un-park.** Post-launch owner decision. ⛔ Not a pre-release change — the
ship line was frozen 2026-08-12 and this touches every module. ⚠️ **Unrelated
but adjacent, and NOT parked:** the frozen `MOD_DESCRIPTION.md` tells players
to set the veto *"in the console"*, which is false and is already logged as a
correction release prep must make. Confirm that landed before upload; it is a
release item, not a future idea.
