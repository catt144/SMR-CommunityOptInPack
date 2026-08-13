-- D12 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix.
--
-- Enable it in-game: Options → Mod Options → Community Fix Pack: Opt-In Modules (D05; the
-- toggle takes effect immediately, both directions — every hook below consults
-- SMROptInPack.IsActive per call and passes through while off, and the infopanel
-- row stops being appended to newly opened panels). Other mods / power users
-- can pre-seed SMROptInPack_Optional = { NoHomeless = true } before this mod
-- loads. `SMROptInPack.ListFixes()` reports it as inactive until enabled.
--
-- Why it exists (BUGS.md D12, found in play 2026-07-30): a specialist dome
-- STRANDS the colonists it can never house. A nursery-only child dome was
-- observed with 68 free Child slots and 28 homeless Youths/Adults sitting in
-- it, quarantine off. The cause is a vanilla TIE, not a mod defect: the
-- shipped emigration eval explicitly permits a homeless colonist to move to a
-- dome with no free housing (Colonist.lua:2676, comment "if homeless, try
-- changing community even if doesn't have living space available"), but the
-- gate above it requires a STRICTLY better score unless home or work improves
-- (:2675, :2680-2681). With zero non-cohort free slots colony-wide
-- `better_home` is false everywhere and with unemployment saturated
-- `better_work` is false too — every candidate ties, and ties never move
-- anyone. Verified byte-verbatim against the pinned 1.0.7.396349 Src on
-- 2026-08-02; no 1.0.x pass touched it.
--
-- It also compounds: the stranded homeless push the dome over IsOverpopulated
-- (Dome.lua:1026-1035) and D07's cross-dome consider() skips
-- `community.overpopulated` (Opt_CohortHousing.lua:196), so the child dome is
-- permanently excluded as a destination and no new Children ever arrive. The
-- entry's design rationale is that draining the homeless clears the flag and
-- D07 resumes unaided. ⚠️ That unwind is NOT verified — it is the reason the
-- design was chosen, and it stays a prediction until a playtest observes it.
--
-- WHAT THIS SHIPS: a per-dome / per-habitat "no homeless residents" policy.
--
--   * A new toggle row on the dome and MicroG-habitat infopanels (left-click
--     toggles, Ctrl+click broadcasts to all domes — the shipped
--     Community:TogglePolicy/SetPolicyState machinery, Community.lua:77-100,
--     which also plays the policy FX and respects the rogue-dome UI lock).
--     Same row idiom as D03, which is the DONOR PATTERN ONLY: the two modules
--     share no gate and no code (user decision, 2026-07-30).
--   * A post-wrapper on Colonist:FindEmigrationDome (declared on Colonist,
--     Colonist.lua:2581) that supplies a destination when the shipped answer
--     was EMPTY — i.e. exactly when the tie stranded them.
--
-- ⛔ HARD CONSTRAINT 1 (the trap that killed the first design): this flag has
-- its own field and its own gate and NEVER routes through
-- Community:CanAcceptNewColonists. D03's "closed to new residents" row wraps
-- that method (Opt_ResidencyControl.lua:88-93) and D07's consider() calls it
-- (Opt_CohortHousing.lua:195), so reusing D03's gate would block the cohort
-- delivery this module exists to protect. The two controls must be able to act
-- in OPPOSITE directions on the same dome at the same time:
--
--     SMRFixPack_closed_to_new_residents (D03) off → children can still migrate in
--     SMRFixPack_no_homeless             (D12) on  → graduates are pushed out
--
-- ⛔ HARD CONSTRAINT 2: NEVER expel to the surface. This wrapper can only ever
-- return a Community drawn from the city's own Community label — it has no
-- code path that returns a position, and when nothing qualifies it returns the
-- shipped answer byte-for-byte and the colonist simply stays. A colonist put
-- outside with no dome dies (F53 territory); that failure mode is made
-- structurally impossible rather than guarded against.
--
-- THE OPEN QUESTION IN THE ENTRY IS DECIDED, AND THE ANSWER IS NEITHER OF THE
-- TWO IT OFFERED. The entry asked: ALL homeless, or only colonists the dome can
-- never house (no residence IsSuitable for them)? ⛔ Both are wrong, and the
-- owner's account of how the feature is actually USED is what settles it
-- (2026-08-02):
--
--   "This is a player control toggle specifically because no automated system
--   can fully tell. Generally when people get to the size they want a child /
--   senior dome, they set up 2 domes out of the way of their resources and
--   major production domes … one to either be a retirement dome + services or
--   nursery + services … It keeps the minimal amount of housing to staff those
--   services, because you expect your retirement dome and the nursery to
--   eventually be filled with non-workforce people. So you also need to keep
--   homeless out of both, because if either gets filled with homeless they
--   cannot do their job any more, because migration turns off."
--
-- ⛔ The NARROW reading fails that outright. "Minimal housing to staff the
-- services" means the dedicated dome HAS ordinary residences by design, so
-- every colonist in it is housable-in-principle and the narrow test never
-- fires. It was chosen off the entry's own line that narrow "is what the
-- child-dome case actually needs" — true of a nursery dome with zero ordinary
-- housing, and false of the retirement+services half of the same pattern. The
-- owner's own colony had one of each, and narrow covered exactly one of them.
--
-- ⛔ The BROAD reading fails too, for a reason no source read would have found:
-- **a homeless Senior in a retirement dome is INFORMATION, not a defect.** It
-- tells the player to build more Retirement Homes. Pushing them out deletes the
-- signal and hides the shortage. The same holds for a homeless Child in a
-- nursery dome.
--
-- ⛔ AND "PUSH THE NON-WORKFORCE" IS THE TRAP INSIDE THE BROAD READING, which
-- the owner caught before a line of it was written: **"outside the workforce"
-- is a real status Children and Seniors carry BY DEFINITION**, not a failure
-- state. The game prints it as such — `T(4364, "Outside the workforce
-- (Child)")` / `T(4365, "Outside the workforce (Senior)")`,
-- `Colonist.lua:3146-3148` — and distinguishes it from `T(4366, "Unemployed")`
-- three lines later. Targeting non-workforce would sweep up exactly the cohorts
-- these domes exist to hold.
--
-- ⭐ THE RULE, THEREFORE, IN VANILLA'S OWN PREDICATE: a flagged dome pushes out
-- a homeless colonist IF AND ONLY IF `need_work` is true for them —
--
--     can_work  = self:CanWork()
--     need_work = can_work and not IsValid(self.workplace)
--                          and not self.user_forced_workplace
--
-- which is `Colonist.lua:2623-2624`, computed by the very function this module
-- wraps, two lines above the tie it exists to break. `CanWork()`
-- (`Colonist.lua:2114-2126`) is false for **Children**, for **Seniors unless
-- `g_SeniorsCanWork`**, for Tourists, and for the Earthsick / StressedOut /
-- UnableToWork / unfit. So the rule reads, in the game's own vocabulary:
--
--     move the UNEMPLOYED. Never move the employed, and never move anyone the
--     game itself calls outside the workforce.
--
-- Against the pattern the owner described, that is exactly right:
--   * the service staff the dome's minimal ordinary housing exists for are
--     EMPLOYED → never moved, so the dome keeps working;
--   * a homeless Senior in a retirement dome is OUTSIDE THE WORKFORCE → never
--     moved, so the signal survives — ⭐ *"homeless senior in the dome is
--     actually useful information to the player. It signals to them that they
--     need to build more retirement homes"*;
--   * a homeless Child in a nursery dome, likewise;
--   * the graduates and leftovers — workforce-age, jobless, housed by nothing
--     — are what is left, and they are the pile-up that drives the dome over
--     `IsOverpopulated` and switches its migration off.
--
-- ⚠️ NOT DUPLICATED HERE, DELIBERATELY: relocating a homeless Senior or Child
-- toward cohort housing that exists ELSEWHERE is **D07 `Opt_CohortHousing`'s**
-- job and it already does it, automatically and with no toggle. D12 must not
-- compete for those colonists; the two modules divide cleanly as "move the
-- cohort toward its housing" (D07) versus "move the workforce-age unemployed
-- out of a dedicated dome" (D12).
--
-- The toggle IS the judgment (owner: "no automated system can fully tell"), so
-- the module does not try to re-derive from building composition whether a dome
-- is dedicated. The player already said so by flipping the row.
--
-- ⚠️ Two honest notes on `CanWork()`, since it is doing the load-bearing work.
--   * It is not purely structural — it also excludes the momentarily ill,
--     stressed-out or mid-command. So a Youth who is sick is not pushed until
--     they recover. That is a delay, never a wrong answer, and it errs in the
--     conservative direction: do not relocate someone who cannot act.
--   * It reads `g_SeniorsCanWork`, so a colony that has unlocked senior work
--     (Forever Young / "Put Them To Work") makes its Seniors workforce, and an
--     UNEMPLOYED one in a flagged dome then becomes movable. That follows the
--     game's own definition rather than second-guessing it, and it is the
--     correct reading: in such a colony a jobless Senior is not a retirement
--     signal, they are unemployed.
--
-- ⚠️ What this costs versus the narrow reading, stated rather than buried: the
-- narrow reading was immune to the CAPACITY-CHURN mechanism (BUGS.md C40) — a
-- law can shrink Residence.capacity colony-wide while a Ministry is down, and
-- Residence:OnModifiableValueChanged (Residence.lua:224-235) EVICTS the tail
-- residents when it does. The employed exemption recovers most of it on a
-- better key: the service staff a churn eviction would hit are employed, so
-- they are exempt anyway. The residual exposure is an UNEMPLOYED workforce-age
-- resident of a flagged dome, transiently evicted, moved out for good over an
-- outage that ends by itself. Narrow window, in a dome the player deliberately
-- dedicated to non-workforce cohorts, and recorded here rather than guarded —
-- the guard would need per-colonist dwell state and the exposure does not
-- justify it.
--
-- COMPOSITION AND PRECEDENCE (all deliberate):
--   * The wrapper acts ONLY when the composed answer below it is EMPTY. That
--     makes it order-independent with respect to D07, which wraps the same
--     method: whichever installs outermost, a positive answer from the other
--     module (or from the shipped code) is never overridden. It is also
--     exactly the D12 case — the tie returns false (PickEmigrationCommunity
--     over an empty best_matches, Colonist.lua:2576).
--   * Quarantine wins absolutely: accept_colonists false means "no one enters
--     or leaves" (the shipped early-out, Colonist.lua:2632-2635) and this
--     module defers to it on both sides — a sealed source dome releases
--     nobody, and a sealed destination fails CanAcceptNewColonists.
--   * A player-forced dome (CheckForcedDome) wins over the policy.
--   * The D03 row composes automatically: a closed destination already fails
--     CanAcceptNewColonists through D03's own wrapper.
--   * Ping-pong guard: destinations carrying this same flag are never
--     considered, so two flagged domes can never trade a colonist back and
--     forth.
--   * Tourists are ignored entirely (hotel machinery, not residency).
--   * A colonist with a reserved residence is mid-move and is left alone.
--
-- Destination choice, in order: a community that (a) does not carry the flag,
-- (b) CanVisit and CanAcceptNewColonists, and (c) HAS A SUITABLE RESIDENCE AT
-- ALL for this colonist. Among those, one that can house them RIGHT NOW wins
-- over one that cannot; then the nearest. Note (c) is a suitability test, not
-- a free-space test — deliberately. In the origin scenario free non-cohort
-- slots colony-wide were ZERO, so requiring free space would have made the
-- module inert in the exact case it was built for; the shipped eval has the
-- same shape for the same reason. `community.overpopulated` is NOT filtered
-- (D07 does filter it): draining an overpopulated dome is the point, and the
-- entry names only two destination filters. The free-space preference already
-- steers away from full domes.
--
-- Savegame footprint (FIX_POLICY §3): `SMRFixPack_no_homeless` on the
-- Dome/Habitat object (true/false), absent-tolerant both ways — nil means
-- vanilla behaviour, the unmodded game never reads it, and a save carrying the
-- flag loads fine with the module (or the whole pack) removed. No threads, no
-- GameVars, no globals.

SMROptInPack_Optional = rawget(_G, "SMROptInPack_Optional") or {}

local FLAG = "SMRFixPack_no_homeless"

-- ⛔ BOTH surfaces, and the second one was missing until 2026-08-02.
-- `IsActive` reads the registry status, which the Mod Options toggle flips.
-- `SMROptInPack_Disabled` is the CONSOLE/other-mod veto, and it is what
-- `PLAYTEST_CHECKLIST.md` PT-62 documents as this module's within-session A/B
-- lever — but nothing here read it, so `SMROptInPack_Disabled.NoHomeless = true`
-- was silently ignored and the A/B half of the leg would have run with the
-- module still live. ⚠️ That is the PT-61 trap exactly: the failure would not
-- have looked like a broken command, it would have looked like an ANSWER
-- (colonists still moving, read as the fix misbehaving). Caught when the owner
-- asked whether the line was correct, before the leg leaned on it.
-- `Fix_DustDevilSpawnGate` checks both (`:332-334`), which is why its A/B
-- worked; `SMROptInPack.WhenActive` does the same for OnMsg handlers.
local function module_active()
	if not SMROptInPack.IsActive("NoHomeless") then return false end
	local disabled = rawget(_G, "SMROptInPack_Disabled")
	if type(disabled) == "table" and disabled.NoHomeless then return false end
	return true
end

local function is_flagged(community)
	return type(community) == "table" and community[FLAG] and true or false
end

-- Every residence a community can house colonists in: the Residence label its
-- own residences are added to (Residence:SetDome, Residence.lua:171-182) PLUS
-- the community ITSELF when it is a Residence. That second clause is the
-- MicroG habitat: MicroGHabitatBase parents both LivingBase (which parents
-- Residence, Residence.lua:462-466) and Community, and its ChooseResidence
-- returns `self` (MicroGHabitat.lua:139-148). It has no parent_dome, so its
-- Residence label is empty and a label-only test would read "this community
-- can never house anyone" and evacuate every habitat.
local function each_residence(community, fn)
	if not community then return end
	if IsKindOf(community, "Residence") then
		local r = fn(community)
		if r then return r end
	end
	local list = community.labels and community.labels.Residence or empty_table
	for _, res in ipairs(list) do
		if IsValid(res) then
			local r = fn(res)
			if r then return r end
		end
	end
end

-- Does this community contain housing this colonist could EVER occupy?
-- Suitability only (Residence:IsSuitable = the exclusive_trait test) — no
-- free-space, no working-state condition. See the header for why.
local function has_suitable_home(community, colonist)
	return each_residence(community, function(res)
		return res:IsSuitable(colonist) or nil
	end) and true or false
end

-- Could this community house them RIGHT NOW? Destination ranking only.
local function has_free_suitable_home(community, colonist)
	return each_residence(community, function(res)
		return (res:IsSuitable(colonist) and res.ui_working
			and res:GetFreeSpace() > 0) or nil
	end) and true or false
end

-- ⛔ THE DOME PRECONDITION (owner, 2026-08-02): the policy exists — and applies
-- — only where a **Nursery or a Retirement Home is actually built**. *"Instead
-- of saying it can't have ordinary housing, make it say it must have either a
-- nursery OR a retirement home built in the dome. That gives us some safety,
-- while giving us the flexibility we need."*
--
-- Tested through `exclusive_trait` rather than by class name, so it needs no
-- enumeration to keep in step. Verified against the shipped set 2026-08-02 —
-- exactly three residences carry a cohort trait, and the property route catches
-- all three without naming any of them:
--     Nursery              `children_only`            -> "Child"
--     LargeNurseryCCP1     `children_only`            -> "Child"   (the large one)
--     SeniorsResidenceCCP1 `exclusive_trait "Senior"`             (the only one)
-- `children_only` becomes `exclusive_trait = "Child"` at `Residence:GameInit`
-- (`Residence.lua:25-27`), so both nurseries resolve to the same field by the
-- time anything reads it. Playground / School / SchoolSpireCCP1 also carry
-- `children_only`, but they are services and training buildings rather than
-- Residences, so iterating `labels.Residence` excludes them by construction.
--
-- ⛔ EXCEPT THE HOTEL, and this is why the exclusion is explicit rather than
-- assumed. `Hotel` ships `exclusive_trait = "Tourist"` and **is a Residence** —
-- `HotelBase` parents `LivingBase` (`Hotel.lua:1-4`), which parents `Residence`
-- (`Residence.lua:462-466`). Without this clause every dome with a Hotel would
-- have qualified as a "Nursery / Retirement Dome", shown the row, and applied
-- the policy to a tourist dome. Caught 2026-08-02 when the owner asked whether
-- the test followed class or name and whether it covered both nurseries; it
-- covered both nurseries and one building it should never have touched.
--
-- ⚠️ AND THE HOTEL'S TRAIT IS NOT A FIXED TEMPLATE VALUE — it is a live player
-- toggle, which the owner flagged as common practice: *"a hotel can be a
-- residence, it is very commonly flagged for colonists to not be allowed to
-- move into by players."* `HotelBase:SetTouristOnly` writes
-- `exclusive_trait = "Tourist"` when restricted and **`false`** when not
-- (`Hotel.lua:6-27`), driven by the infopanel's Tourists-Only / Any-Colonist
-- button (`:29-52`). So a Hotel is EITHER tourist-exclusive OR plain ordinary
-- housing, and this predicate is correct in both states rather than only the
-- default one: restricted → excluded by the `"Tourist"` clause; unrestricted →
-- `exclusive_trait` is `false`, so it never reaches the clause at all and the
-- Hotel counts as the ordinary housing it has become. Nothing here caches the
-- field, so flipping that button mid-game is picked up on the next read.
--
-- ⛔ AND THE CONSEQUENCE OF THAT IS DELIBERATELY UNGUARDED — do not "fix" it.
-- An open Hotel in a flagged dome quietly cancels this policy: an arriving
-- jobseeker gets a ROOM there, so they are no longer homeless, so this module
-- has no subject to move. They stay, they use the services, and they occupy a
-- room meant for a tourist. That is a real outcome, and it is left to the
-- player, because the Tourists-Only button is THEIR control and the same
-- principle governs this module's own toggle — *"no automated system can fully
-- tell"* (owner, 2026-08-02). The answer is explanation, not interception:
-- `MOD_DESCRIPTION.md` carries it as `[FAQ]` usage guidance under this module.
-- A future session that adds a guard here is overriding a player decision this
-- module exists to respect.
--
-- STRUCTURAL: a switched-off Nursery still counts, because the player built one
-- — this asks what the dome IS, not what it is doing this minute.
--
-- It buys three things at once:
--   * safety — the toggle cannot be flipped onto a production dome by someone
--     who read the row as a "get rid of homeless" button, which is the exact
--     misread the owner flagged;
--   * honesty — the row's title claims "Nursery / Retirement Dome", and with
--     this gate that claim is true wherever the row appears. Without it the
--     title was a lie on every other dome;
--   * a self-neutralising policy — demolish the last cohort home and the flag
--     stops doing anything, because the WRAPPER checks the same predicate the
--     UI does. The two can never disagree about where the policy applies.
local function has_cohort_housing(community)
	return each_residence(community, function(res)
		local t = res.exclusive_trait
		return (t and t ~= "" and t ~= "Tourist") and true or nil
	end) and true or false
end

-- Is this colonist the class the policy moves? Vanilla's own `need_work`
-- (Colonist.lua:2623-2624) plus the tourist carve-out. Used on BOTH sides now:
-- who gets pushed out, and who must not be routed in.
local function is_push_subject(colonist)
	local traits = colonist.traits
	if traits and traits.Tourist then return false end
	if not colonist:CanWork() then return false end
	if IsValid(colonist.workplace) or colonist.user_forced_workplace then return false end
	return true
end

-- ⭐⭐ THE DOOR IN THE WALL (owner, 2026-08-03). Added BEFORE PT-62's re-run
-- rather than after, so the leg tests the shape we intend to ship.
--
-- ⛔ THE OVER-CORRECTION IT REPAIRS, derived from Src and never yet observed.
-- The symmetric veto below refuses the class this policy pushes out — and that
-- class is `need_work`, which is EXACTLY the set vanilla moves toward an open
-- job. `better_work = not work_available and new_work_available`
-- (`Colonist.lua:2679`) fires only when `need_work` is true (`:2623-2624`), so a
-- flagged dome vetoing every `need_work` arrival is a flagged dome that **can
-- never be staffed from outside**. `ChooseDome` closed the other entrance. For
-- the pattern this module exists for — the owner's *"2 domes out of the way of
-- their resources and major production domes"* — there is no passage, so
-- migration is the ONLY staffing route. Flag such a dome and its service staff
-- age out or die with no replacement: the services go dark and the player sees
-- *"my retirement dome isn't working"*, which is the exact confusion this
-- module's row was designed to prevent, reached from the opposite direction.
--
-- ⭐ SO THE WALL OPENS WHEN THERE IS A JOB: a colonist is neither pushed out of
-- nor refused entry to a flagged dome while that dome has a free workplace THEY
-- could take. Vanilla computes this — `Workforce:HasFreeWorkplacesAround`
-- (`Workforce.lua:43-51`): `ui_working and CanWorkHere(colonist) and
-- HasFreeWorkSlots()`. Reachable on every community this module touches, since
-- `Community.__parents = { "Workforce" }` (`Community.lua:8-9`) and both `Dome`
-- (`Dome.lua:376-377`) and `MicroGHabitatBase` (`MicroGHabitat.lua:3-4`) parent
-- Community.
--
-- ⛔ IT MUST BE ON BOTH SIDES, AND THAT IS THE WHOLE DESIGN — an entry-only
-- door re-opens the PT-62 loop in miniature: let them in for the job, they lose
-- the slot to someone else, they are now a push subject and go straight back
-- out, the slot is still free so the entry door is still open, vanilla offers
-- the dome again. Bounded by work slots rather than the ~97-scoring cohort
-- slots, but the same defect shape we just spent a sitting finding.
--
-- With the SAME predicate on both sides it closes itself, and every branch
-- terminates:
--   * a free slot they qualify for exists → they are not pushed, so they stay
--     and remain a candidate for it;
--   * they win it → employed → `is_push_subject` false forever → dome staffed;
--   * someone else wins it → no free slot → the entry door shuts AND they
--     become pushable → pushed out ONCE, with no re-offer possible.
-- Race (two colonists admitted for one slot) resolves the same way: the loser
-- is pushed once when the slot closes. One-way, terminating.
--
-- This is the module's existing idiom — one predicate shared by both halves, so
-- the two can never disagree, exactly as `is_push_subject` is shared by push and
-- veto and `has_cohort_housing` is shared by the wrapper and the UI.
--
-- ⚠️ THE COST, STATED RATHER THAN BURIED, and it is PT-62's to measure: N
-- homeless jobseekers in a flagged dome with ONE open slot means ALL N are
-- held, because each of them individually sees a free slot. The expectation is
-- that this is short-lived — colonists seek work in their own dome first, so
-- "unemployed resident + a slot they qualify for" should resolve quickly — but
-- that is an ASSUMPTION and it is not verified. PT-62's re-run reads whether
-- the slot actually fills. If it does not, this door needs a dwell bound.
--
-- ⚠️ Defensive by necessity: a missing method returns FALSE (door shut, i.e.
-- the pre-2026-08-03 behaviour) rather than erroring. The stand-in tables that
-- drive this wrapper in the D07 probe carry no Workforce methods, and a method
-- call on them is what ERRORed that whole probe on 2026-08-02. apply() Requires
-- the method as well, so a game update that removes it reports a reason string
-- instead of silently reverting to the sealed-dome behaviour.
local function has_free_work_for(community, colonist)
	if type(community) ~= "table" then return false end
	if type(community.HasFreeWorkplacesAround) ~= "function" then return false end
	return community:HasFreeWorkplacesAround(colonist) and true or false
end

-- The same question at the ARRIVAL seam, where there is no colonist to ask
-- `CanWorkHere` about — see the ChooseDome wrapper. Vanilla's own colonist-
-- independent count (`GetFreeWorkplacesAround`, `_GameUtils.lua:443-455`)
-- returns free slots in WORKING buildings; the second return (closed slots) is
-- deliberately ignored, since a switched-off workplace is not recruiting.
-- Coarser than the emigration side on purpose: that seam is already trait-based
-- by necessity, and erring toward LETTING PEOPLE IN is the safe direction there.
-- ⚠️ Nil-safe on the label because the shipped helper is not.
local function has_free_work_slots(community)
	if type(community) ~= "table" then return false end
	local labels = community.labels
	if not labels or not labels.Workplace then return false end
	local get_free = rawget(_G, "GetFreeWorkplacesAround")
	if type(get_free) ~= "function" then return false end
	local on = get_free(community)
	return (on or 0) > 0
end

-- The push. Installed at FILE SCOPE (the A2 lesson, FIX_POLICY §5) so the wrap
-- is in place before class flattening and a FIRST mid-session Mod Options
-- enable works without a relaunch; guarded by the same existence check apply()
-- runs, so a missing target degrades to apply()'s reason string instead of
-- erroring at load. module_active() makes the toggle live in both directions.
do
	local C = rawget(_G, "Colonist")
	if type(C) == "table" and type(C.FindEmigrationDome) == "function"
			and type(C.IsHomeless) == "function" then
		local orig_find = C.FindEmigrationDome
		function C:FindEmigrationDome(current_dome, ...)
			local dome, mode, dist, elevator = orig_find(self, current_dome, ...)
			if not module_active() then return dome, mode, dist, elevator end
			-- ⛔ THE SYMMETRIC HALF — a flagged dome must not RECEIVE the class
			-- it is set to move out. Without this the policy and the shipped
			-- eval fight each other: we push a jobseeker out, the dome drops
			-- below `IsOverpopulated`, its free cohort slots start scoring
			-- ~97 again in `Community:GetScoreFor`, vanilla offers the same
			-- dome straight back, and the colonist shuttles. **Observed live
			-- 2026-08-02 during PT-62: six colonists en route INTO flagged
			-- domes while those domes were draining**, arriving by train and
			-- walking back in.
			--
			-- ⚠️ This is the ONE case where the wrapper overrides a positive
			-- shipped answer, and the narrowness is what keeps it legal:
			--   * it fires only for a colonist the policy would immediately
			--     push out again, so it removes a round trip rather than a
			--     choice;
			--   * it NEVER touches cohort members — `is_push_subject` is false
			--     for anyone outside the workforce — so Children and Seniors
			--     keep arriving normally. That is what makes it compatible with
			--     HARD CONSTRAINT 1: we still do not route through
			--     `CanAcceptNewColonists`, and cohort delivery is untouched;
			--   * returning nothing is the shipped "stay put" answer, and
			--     `TryToEmigrate` clears any pending transport request with it
			--     (`Colonist.lua:1604-1609`).
			-- It also stays order-independent with D07, which only ever moves
			-- cohort members and therefore never trips this clause.
			--
			-- ⭐ …UNLESS THE DOME HAS A JOB FOR THEM (2026-08-03). Vanilla is
			-- moving this colonist toward that dome precisely BECAUSE it has an
			-- open workplace (`better_work`, Colonist.lua:2679, which fires only
			-- for `need_work` — the same set this clause vetoes). Refusing them
			-- is refusing the dome its own staff. Tested LAST because it walks
			-- the Workplace label; every cheaper gate has already run.
			if dome and is_flagged(dome) and has_cohort_housing(dome)
					and is_push_subject(self)
					and not has_free_work_for(dome, self) then
				return
			end
			-- otherwise only ever ADD a destination; never override one
			if dome then return dome, mode, dist, elevator end

			-- ⛔ GUARD ORDER IS LOAD-BEARING — the FLAG IS TESTED FIRST, before
			-- any method call on the colonist, and it must stay that way.
			-- Two reasons, and the second was paid for:
			--   1. Hot path. This wrapper runs for every colonist on every heavy
			--      update, and for almost every colonist in almost every game the
			--      answer is "their dome does not carry the flag". That is a plain
			--      field read on a table we already have; doing method calls ahead
			--      of it spends work on the 99% case to learn nothing.
			--   2. ⚠️ It keeps the module inert for anything that is not a real
			--      Colonist. The first ordering asked `self:IsHomeless()` up here
			--      and ERRORed the whole D07 CohortHousing probe — that probe
			--      drives this same wrapped method with plain-table stand-ins,
			--      which carry no `IsHomeless` (observed 2026-08-02, log
			--      `Mars.exe-20260802-20.36.57`: `attempt to call a nil value
			--      (method 'IsHomeless')`). A real Colonist always has it, so this
			--      is not reachable in play — but a module that only behaves when
			--      handed a perfect object is one an unlucky mod interaction turns
			--      into a log full of errors, and PT-62's P11 forbids exactly that.
			local my_dome = self.dome
			if not is_flagged(my_dome) then return dome, mode, dist, elevator end
			if not has_cohort_housing(my_dome) then
				-- the dome precondition, checked HERE and not only in the UI so
				-- the two can never disagree: a flag left on a dome whose last
				-- Nursery/Retirement Home was demolished is inert, and a flag
				-- broadcast onto a dome that never had one does nothing
				return dome, mode, dist, elevator
			end
			if not my_dome.accept_colonists then
				return dome, mode, dist, elevator -- quarantine: no one enters or leaves
			end
			if not is_push_subject(self) then return dome, mode, dist, elevator end
			if not self:IsHomeless() then return dome, mode, dist, elevator end
			if IsValid(self.reserved_residence) then
				return dome, mode, dist, elevator -- mid-move
			end
			if self:CheckForcedDome() then
				return dome, mode, dist, elevator -- player order wins
			end
			-- ⭐ THE DOOR, PUSH SIDE (2026-08-03) — and it is what makes the
			-- entry-side door terminate rather than oscillate; see the header.
			-- While this dome has a free workplace THIS colonist could take,
			-- they are a candidate for it, not a subject to move: pushing them
			-- out empties the dome of the very people who would staff it. Once
			-- the slot is gone — to them (employed → exempt for good) or to
			-- someone else — this gate stops holding and the normal push runs.
			-- Placed last of the gates deliberately: it is the only one that
			-- walks a label, so it is paid for only by colonists who have
			-- already passed every cheap test.
			if has_free_work_for(my_dome, self) then
				return dome, mode, dist, elevator
			end

			-- ⛔ THE SUBJECT TEST — vanilla's own `need_work`, verbatim from
			-- Colonist.lua:2623-2624, which this very function computes a few
			-- lines above the tie we are breaking. Move the UNEMPLOYED; never
			-- move the employed, and never move anyone the game itself calls
			-- OUTSIDE THE WORKFORCE. See the header: CanWork() is false for
			-- Children, for Seniors unless g_SeniorsCanWork, for Tourists and
			-- for the Earthsick/StressedOut/UnableToWork/unfit, so a homeless
			-- Senior in a retirement dome survives to be the build-more-housing
			-- signal it is, and the service staff the dome's ordinary housing
			-- exists for are employed and never touched.
			-- (the workforce / outside-the-workforce test is is_push_subject,
			-- applied above so both halves of the policy share one predicate)

			-- Candidate gathering mirrors the shipped function: this city's
			-- communities plus every elevator-linked city's
			-- (Colonist.lua:2595-2618).
			local my_city = self.city
			local pos = current_dome or IsUnitInDome(self) or self:GetNavigationPos()
			local shuttles = IsLRTransportAvailable(my_city)
			local best, best_mode, best_dist, best_elev, best_free
			local function consider(community)
				if community == my_dome or is_flagged(community) then return end
				if not community:CanVisit(self) then return end
				if not community:CanAcceptNewColonists() then return end
				if not has_suitable_home(community, self) then return end
				local source_city = community.city ~= my_city and my_city
				local with_shuttles = shuttles and not source_city
				local c_mode, c_dist, c_elev =
					FindTransportationModeToCommunity(community, pos, with_shuttles, source_city)
				if not c_mode then return end
				local free = has_free_suitable_home(community, self)
				if not best
						or (free and not best_free)
						or (free == best_free and (c_dist or 0) < (best_dist or 0)) then
					best, best_mode, best_dist, best_elev, best_free =
						community, c_mode, c_dist, c_elev, free
				end
			end
			for _, community in ipairs(my_city.labels.Community or empty_table) do
				consider(community)
			end
			local seen = { [my_city] = true }
			for _, elev in ipairs(my_city.labels.Elevator or empty_table) do
				if ValidateBuilding(elev) then
					local other_city = elev.other and elev.other.city
					if other_city and not seen[other_city] then
						seen[other_city] = true
						for _, community in ipairs(other_city.labels.Community or empty_table) do
							consider(community)
						end
					end
				end
			end
			if best then
				return best, best_mode, best_dist, best_elev
			end
			-- nowhere to send them: the shipped answer stands and they stay put
			return dome, mode, dist, elevator
		end
	end
end

-- One infopanel row, same construction as D03's (see Opt_ResidencyControl.lua
-- for the full derivation of the placement rule): InfopanelActiveSection with
-- everything set in OnContextUpdate, then moved up to sit with the shipped
-- toggle group instead of below the stat blocks. The section is a VList whose
-- children render in array order, and sectionDome:Init builds the toggle rows
-- first and the plain InfopanelSection blocks after — so a row created last is
-- moved to just before the FIRST plain InfopanelSection child. If no such
-- child exists the row simply stays at the end.
--
-- Strings are Untranslated (F98, 2026-08-02): re-using a shipped translation id
-- is a NO-OP in retail — T(id, text) returns LocIdToLightUserdata(id) and
-- discards the literal (CommonLua\Core\localization.lua:250-252). Every string
-- below is new text, so Untranslated is the correct route; nothing here appends
-- to a shipped T.
--
-- Icons: the `service_in_connected_domes_*` pair is a shipped Sections asset
-- (sectionDome.generated.lua:141-147), chosen over D03's accept_colonists pair
-- so the two pack rows are not identical at a glance. Look-check is on the
-- playtest item.

-- How many colonists in THIS community the policy currently applies to — the
-- same subject test the wrapper uses, so the number on the row cannot disagree
-- with the behaviour. Drives TitleRight (see below).
local function count_movable(community)
	local n = 0
	for _, c in ipairs(community and community.labels
			and community.labels.Homeless or empty_table) do
		if IsValid(c) and not (c.traits and c.traits.Tourist)
				and not IsValid(c.reserved_residence)
				and c:CanWork()
				and not IsValid(c.workplace) and not c.user_forced_workplace
				-- ⭐ the free-work door counts here TOO (2026-08-03), or the row
				-- lies: a dome with an open service slot moves NOBODY, and a row
				-- reading "5 moving out" while five people stay is exactly the
				-- disagreement between number and behaviour this function exists
				-- to prevent. On a dome that is recruiting it now reads
				-- "0 would move", which is both true and informative.
				and not has_free_work_for(community, c) then
			n = n + 1
		end
	end
	return n
end

local function append_policy_row(section, context)
	-- ⛔ The dome precondition, UI side: no Nursery and no Retirement Home means
	-- no row at all. Build one and the row appears the next time the panel is
	-- opened (infopanel sections are constructed in Init, so an already-open
	-- panel picks it up on re-selection — acceptable, and noted on PT-62's
	-- look-check rather than papered over).
	if not has_cohort_housing(ResolvePropObj(context)) then return end

	-- ⛔ TitleRight IS DELIBERATELY NOT USED, after trying it twice.
	-- `InfopanelActiveSection:Init` decides the title's alignment ONCE, from
	-- whether TitleRight is empty at construction
	-- (`InfopanelActiveSection.generated.lua:157-159`): empty -> the title is
	-- CENTRED, like every sibling row on this panel. Setting TitleRight only in
	-- OnContextUpdate left the title centred AND the value right-aligned, so the
	-- two rendered on top of each other ("Nursery / Retirement D(28 would
	-- move)"). Seeding it at construction fixed the overlap but split the row
	-- into two hard-butted columns with no gap ("Nursery / Retirement Dome28
	-- would move"), because this panel is narrow. Both observed live 2026-08-02.
	-- The count therefore lives INSIDE the title, which centres like the shipped
	-- rows and reads as one sentence.
	local row = InfopanelActiveSection:new({
		OnContextUpdate = function(self, context, ...)
			local community = ResolvePropObj(context)
			local on = is_flagged(community)

			-- ⭐ THE TITLE NAMES THE DOME TYPE AND NEVER CHANGES; the STATE and
			-- the CONSEQUENCE both live on the right. Two owner notes drove
			-- this (2026-08-02):
			--   * "this could easily be mistaken for just hitting a button to
			--     get rid of homeless … not all players will look at a tooltip,
			--     they will just be confused why their retirement dome isn't
			--     working" — so the count is ON THE ROW. On a retirement dome
			--     full of homeless Seniors it reads "0 would move", which
			--     answers that confusion in place, before the click.
			--   * "I would like to see something about nursery / retirement in
			--     the label, so I instantly know what it could be talking
			--     about … if I am a new player working on a retirement home or
			--     a nursery that jumps out at me, jobseeker doesn't" — so the
			--     recognition words lead, and they lead in BOTH states rather
			--     than only when the policy is set.
			-- The icon colour carries on/off as well (green permissive, yellow
			-- restriction), so the state is encoded twice.
			local n = count_movable(community)

			-- ⛔ ICON POLARITY MIRRORS D03's, and the first build had it
			-- inverted: the OFF state — which is VANILLA — rendered red, so a
			-- player who had never touched the row saw what looked like an
			-- alarm and would press it to clear it. Permissive state reads
			-- green/on; the restriction reads yellow/limit. Same pairing as
			-- Opt_ResidencyControl, which playtested correctly.
			self:SetTitle(Untranslated(string.format(
				on and "Nursery / Retirement Dome (%d moving out)"
				   or  "Nursery / Retirement Dome (%d would move)", n)))
			if on then
				self:SetIcon("UI/IconsRemaster/Sections/service_in_connected_domes_off.png")
				self:SetIconBack("UI/IconsRemaster/Sections/ip_sections_limit")
				self:SetRolloverImageColor("yellow", true)
			else
				self:SetIcon("UI/IconsRemaster/Sections/service_in_connected_domes_on.png")
				self:SetIconBack("UI/IconsRemaster/Sections/ip_sections_on")
				self:SetRolloverImageColor("green", true)
			end
			rawset(self, "ProcessToggle", function(self, context, broadcast)
				local building = ResolvePropObj(context)
				if broadcast then
					-- ⛔ OUR OWN BROADCAST, deliberately not the shipped one.
					-- Community:SetPolicyState's broadcast arm writes the field
					-- onto EVERY community in the city (Community.lua:86-94),
					-- which would leave the flag on production domes where the
					-- row is not even shown — inert today, but it would switch
					-- itself on the day someone built a Nursery there. Ctrl+click
					-- therefore means "every Nursery/Retirement Dome", which is
					-- what the row claims to be about. Each dome still goes
					-- through the shipped per-dome path, so the policy FX and
					-- ObjModified are vanilla's.
					if not building:GetUIInteractionState() then return end
					local state = not building[FLAG]
					for _, c in ipairs(building.city and building.city.labels
							and building.city.labels.Community or empty_table) do
						if has_cohort_housing(c) and c[FLAG] ~= state then
							c:SetPolicyState(FLAG, false, state)
						end
					end
				else
					-- shipped policy machinery: UI-interaction gate + FX
					building:TogglePolicy(FLAG, false)
				end
				RebuildInfopanel(building)
			end)
			self.OnActivate = function(self, context, gamepad)
				self:ProcessToggle(context, not gamepad and IsMassUIModifierPressed())
			end
			self.OnAltActivate = function(self, context, gamepad)
				if gamepad then
					self:ProcessToggle(context, true)
				end
			end
			self:SetRolloverTitle(Untranslated("Dedicated Dome Policy (Community Fix Pack: Opt-In Modules)"))
			self:SetRolloverText(Untranslated(
				"For <em>Nursery</em> and <em>Retirement</em> Domes. Those Domes keep only enough ordinary housing to staff their services, so unhoused jobseekers pile up in them — and once a Dome holds enough homeless it counts as overcrowded and stops receiving anyone, including the Children or Seniors it was built for.<newline><newline>"
				.. "When this is on, <em>unemployed</em> Colonists with no home here move to the nearest Dome that has housing they can use.<newline><newline>"
				.. "<em>Nobody else is touched.</em> Colonists who work here stay — they are who this Dome's ordinary housing is for. Seniors and Children stay too, even while homeless: that is the Dome telling you to build more Retirement Homes or Nurseries, and hiding it would not help you.<newline><newline>"
				.. "<em>While this Dome has a job opening, nobody moves and jobseekers may still arrive</em> — otherwise it could never replace the staff its services need.<newline><newline>"
				.. "Nobody is ever put outside. If there is nowhere suitable to send someone they simply stay, a quarantined Dome releases no one, and your manual Dome assignments always win.<newline><newline>"
				.. "Current status: <em>" .. (on and "moving out homeless jobseekers" or "homeless jobseekers may stay") .. "</em>"))
			if on then
				self:SetRolloverHint(Untranslated("<left_click> Let homeless jobseekers stay in this Dome<newline><em>Ctrl + <left_click></em> Let them stay in all Domes"))
				self:SetRolloverHintGamepad(Untranslated("<ButtonA> Let homeless jobseekers stay in this Dome<newline><ButtonY> Let them stay in all Domes"))
			else
				self:SetRolloverHint(Untranslated("<left_click> Move homeless jobseekers out of this Dome<newline><em>Ctrl + <left_click></em> Do this in all Domes"))
				self:SetRolloverHintGamepad(Untranslated("<ButtonA> Move homeless jobseekers out of this Dome<newline><ButtonY> Do this in all Domes"))
			end
		end,
	}, section, context)

	local target
	for i, child in ipairs(section) do
		if child ~= row and IsKindOf(child, "InfopanelSection")
				and not IsKindOf(child, "InfopanelActiveSection") then
			target = i
			break
		end
	end
	local from = table.find(section, row)
	if target and from and from > target then
		table.remove(section, from)
		table.insert(section, target, row)
		section:InvalidateMeasure()
	end
end

SMROptInPack.Register("NoHomeless", {
	-- ⚠️ title corrected 2026-08-03: it still described the NARROW reading
	-- ("colonists the dome cannot house"), which was built first and falsified
	-- live the same evening — the rule is vanilla's `need_work`. `ListFixes()`
	-- prints this string, so a stale one misreports the module to the leg that
	-- reads it as account truth.
	title = 'OPTIONAL: per-dome Nursery/Retirement policy — moves out homeless UNEMPLOYED colonists, unless the dome has a job opening',
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled("NoHomeless") then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end

		local err = SMROptInPack.Require("NoHomeless", {
			{ class = "Colonist", method = "FindEmigrationDome",
			  reason = "Colonist.FindEmigrationDome/IsHomeless not found (game update changed it?)" },
			{ class = "Colonist", method = "IsHomeless",
			  reason = "Colonist.FindEmigrationDome/IsHomeless not found (game update changed it?)" },
			{ class = "Colonist", method = "CheckForcedDome",
			  reason = "Colonist.CheckForcedDome not found (game update changed it?)" },
			{ class = "Colonist", method = "CanWork",
			  reason = "Colonist.CanWork not found (game update changed the workforce test?)" },
			-- the free-work door (2026-08-03). Required rather than merely
			-- probed for, because its absence would not error — it would
			-- silently seal every flagged dome to workforce-age entrants and
			-- the dome would quietly lose its services. Say so instead.
			{ class = "Community", method = "HasFreeWorkplacesAround",
			  -- F100: the old string said "game update changed the Workforce mixin?"
			  -- and that is not what happens. This check names Community while
			  -- Workforce DECLARES the method, so on the first load pass — mod code
			  -- runs before the class hierarchy is built (agent/facts/EF-001) — the
			  -- inherited method is not there to find, the check fails, and the
			  -- module applies cleanly on the second pass. The preceding
			  -- "authoring error, not a game update" line (00_Core.lua) is the
			  -- correct diagnosis; this string now agrees with it instead of
			  -- contradicting it. Owner decision 2026-08-10: reason string ONLY —
			  -- the Require target does not move until D12's review settles.
			  reason = "Community.HasFreeWorkplacesAround not found — expected on the FIRST load pass and NOT a game update: this check names Community while Workforce declares the method (authoring error — see the preceding line), and mod code loads before the class hierarchy is built, so the module applies cleanly on the second pass. If no 'NoHomeless: applied' line follows this one, the method is genuinely gone — without it a flagged dome could never be staffed" },
			{ global = "GetFreeWorkplacesAround",
			  reason = "GetFreeWorkplacesAround not found (game update changed it?) — the arrival seam needs it to keep a flagged dome staffable" },
			{ class = "Residence", method = "IsSuitable",
			  reason = "Residence.IsSuitable/GetFreeSpace not found (game update changed it?)" },
			{ class = "Residence", method = "GetFreeSpace",
			  reason = "Residence.IsSuitable/GetFreeSpace not found (game update changed it?)" },
			{ class = "Community", method = "TogglePolicy",
			  reason = "Community.TogglePolicy/CanAcceptNewColonists not found (game update changed it?)" },
			{ class = "Community", method = "CanAcceptNewColonists",
			  reason = "Community.TogglePolicy/CanAcceptNewColonists not found (game update changed it?)" },
			{ global = "FindTransportationModeToCommunity",
			  reason = "emigration transport helpers not found (game update changed them?)" },
			{ global = "ChooseDome" },
			{ global = "IsLRTransportAvailable",
			  reason = "emigration transport helpers not found (game update changed them?)" },
			-- the row states its own consequence through TitleRight; if that
			-- setter ever goes, say so instead of silently dropping the row
			-- (shipped precedent: sectionFactionTarget.lua:40)
			{ class = "InfopanelActiveSection", method = "SetTitleRight",
			  reason = "InfopanelActiveSection.SetTitleRight not found (game update changed the infopanel row?)" },
			{ class = "sectionDome", method = "Init",
			  reason = "sectionDome/sectionMicroGHabitat Init not found (game update changed the infopanel?)" },
			{ class = "sectionMicroGHabitat", method = "Init",
			  reason = "sectionDome/sectionMicroGHabitat Init not found (game update changed the infopanel?)" },
		})
		if err then return err end
		local SD = sectionDome
		local SM = sectionMicroGHabitat

		-- the FindEmigrationDome wrapper is installed at file scope above —
		-- see the header; apply() only validates its targets.

		-- ⛔ THE SECOND ENTRY PATH. The FindEmigrationDome veto only covers
		-- colonists who RESETTLE. Arrivals choose a first home through the
		-- global `ChooseDome` instead — rocket disembark, lander/transporter
		-- arrivals, factory-born androids, and stranded colonists re-homing
		-- (`Colonist.lua:1149`) — and nothing above touches it. That is how a
		-- landing can drop jobseekers straight into a dome the policy is
		-- draining, which is what PT-62 caught on 2026-08-02.
		--
		-- The owner's instinct here was to make vanilla treat a flagged dome as
		-- QUARANTINED for these colonists, because `accept_colonists` is a gate
		-- vanilla honours everywhere. ⛔ That cannot be done at its own seam:
		-- `Community:CanAcceptNewColonists()` takes NO colonist argument
		-- (`Community.lua:61-63`), so it cannot distinguish a jobseeker from a
		-- Senior — which is precisely why HARD CONSTRAINT 1 forbids this module
		-- from using it. `ChooseDome` DOES receive `traits`, so the same intent
		-- lands here instead, per-colonist and without touching quarantine.
		--
		-- Trait-based by necessity: at this seam there is no workplace to read,
		-- so the test is "could this colonist be workforce" rather than the
		-- full `need_work`. Children, Seniors and Tourists are never filtered,
		-- so cohort delivery and hotel-seeking are untouched. ⚠️ `safety_dome`
		-- passes through UNFILTERED — the last-resort dome for a colonist
		-- stranded outside must always remain available, so this can never
		-- suffocate anyone (the D03 lesson, Opt_ResidencyControl.lua:45-50).
		local orig_choose = ChooseDome
		local function choose(traits, domes, safety_dome, dome_elevators, ...)
			if module_active() and type(domes) == "table" and traits
					and not traits.Tourist and not traits.Child and not traits.Senior then
				-- ⭐ …AND THE SAME DOOR HERE (2026-08-03): a flagged dome with a
				-- free workplace is still a valid landing site, because an
				-- arrival who takes that job is staff, not a jobseeker to be
				-- kept out. Without this the dome is sealed to workforce-age
				-- entrants at BOTH seams and can never be restaffed — see the
				-- header. Colonist-independent here of necessity (no colonist
				-- exists yet to ask CanWorkHere about), which errs toward
				-- letting people in; that is the safe direction at this seam.
				local filtered
				for i, dome in ipairs(domes) do
					if is_flagged(dome) and has_cohort_housing(dome)
							and not has_free_work_slots(dome) then
						if not filtered then
							filtered = {}
							for j = 1, i - 1 do filtered[#filtered + 1] = domes[j] end
						end
					elseif filtered then
						filtered[#filtered + 1] = dome
					end
				end
				-- never hand back an EMPTY list: if every candidate was flagged,
				-- the shipped choice stands rather than leaving an arrival with
				-- nowhere to go at all
				if filtered and #filtered > 0 then domes = filtered end
			end
			return orig_choose(traits, domes, safety_dome, dome_elevators, ...)
		end
		local fail = SMROptInPack.SetGlobal("ChooseDome", choose,
			"could not install the ChooseDome wrapper (sandbox change?)")
		if fail then return fail end

		local orig_sd_init = SD.Init
		function SD:Init(parent, context)
			local r = orig_sd_init(self, parent, context)
			if module_active() and IsContextOfKind(context, "Dome") then
				pcall(append_policy_row, self, context)
			end
			return r
		end
		local orig_sm_init = SM.Init
		function SM:Init(parent, context)
			local r = orig_sm_init(self, parent, context)
			if module_active() and IsContextOfKind(context, "MicroGHabitatBase") then
				pcall(append_policy_row, self, context)
			end
			return r
		end
	end,
})
