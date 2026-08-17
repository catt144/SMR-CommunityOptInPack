-- D07 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix.
--
-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; the
-- toggle takes effect immediately, both directions — every hook below consults
-- SMROptInPack.IsActive per call and passes through while off). Other mods /
-- power users can pre-seed SMROptInPack_Optional = { CohortHousing = true }.
--
-- Why it exists: cohort housing (Nursery — exclusive_trait "Child" via
-- children_only, Residence.lua:26-28; Seniors Residence — exclusive_trait
-- "Senior" from its template) never fills on its own. In-dome, the shipped
-- ChooseResidence scorer (Residence.lua:399-423) only relocates a housed
-- colonist on a STRICTLY better comfort score, so cohort members comfortable
-- in normal housing stay put; cross-dome, FindEmigrationDome's eval ties
-- never move anyone (Colonist.lua:2675 `new_eval >= eval` guarded to strict
-- unless work/home improves). The only vanilla lever is trait-filter
-- micromanagement. This module adds the missing rule at the COLONIST/HOUSING
-- level — no dome designation, no UI:
--
--   A cohort member (Senior or Child) living in NON-cohort housing is moved
--   into cohort-specific housing wherever a free slot exists — own dome
--   first (plain residence reassignment), any reachable dome second (the
--   shipped emigration machinery) — and is left completely alone when no
--   cohort slot exists anywhere.
--
-- WHAT THIS SHIPS (all per-call-gated, zero persisted state — saves made
-- with it ON load identically without it; nothing is written to any object):
--
--   * In-dome pass: post-wrapper on Colonist:UpdateResidence (declared on
--     Colonist, Colonist.lua:2309; runs from the Idle heavy update). After
--     the shipped logic settles, a cohort member whose residence is not
--     cohort housing is reassigned to the best free cohort slot in the SAME
--     dome (highest service_comfort, then most free space). SetResidence is
--     the shipped reassignment path — same-dome only, per its own assert.
--   * Cross-dome pass: post-wrapper on Colonist:FindEmigrationDome (declared
--     on Colonist, Colonist.lua:2581). When the colonist's own dome has no
--     free cohort slot, the NEAREST reachable community with one wins —
--     bypassing the tie rule. Reuses the shipped candidate gathering
--     (same-city Community label + elevator-linked cities) and transport
--     resolution (FindTransportationModeToCommunity — walk/passage/shuttle/
--     train/elevator; train arrival = MigrateByTrain, live-proven
--     2026-07-28). If no candidate qualifies, the shipped answer stands.
--   * Graduation nudge: additive OnMsg.ColonistBecameYouth (fired by
--     UpdateAgeTrait, Colonist.lua:1751) — an immediate UpdateResidence so
--     the freed Nursery slot opens the moment the Child trait drops instead
--     of at the next heavy update. The move-out itself is vanilla
--     (ChooseResidence rejects the now-unsuitable exclusive-trait home) and
--     the need-work migration that drains graduates to production domes is
--     the untouched shipped path.
--
-- PRECEDENCE AND EXEMPTIONS (all deliberate):
--   * Player orders win: a valid user_forced_residence suppresses the
--     in-dome pass; CheckForcedDome keeps absolute precedence cross-dome
--     (the wrapper defers before looking). A senior with a player-forced
--     workplace pending counts as employed.
--   * Employed seniors are exempt (Forever Young seniors keep their jobs).
--     Children cannot work, so no equivalent applies.
--   * Tourists are ignored entirely (hotel machinery, not residency).
--   * Cohort members already IN (or reserving) cohort housing are never
--     touched.
--   * Quarantine seals (accept_colonists false = "no one enters or leaves"),
--     and the D03 closed-to-new-residents policy composes automatically:
--     both passes consult the same CanAcceptNewColonists the shipped
--     emigration uses. Overpopulated communities are skipped, mirroring
--     HasFreeLivingSpaceFor's own gate (Community.lua:335).
--
-- Known accepted behaviors (documented for the PT):
--   * A colonist redirected cross-dome is housed by the shipped arrival
--     machinery (Dome:ReserveResidence takes the first reservable home,
--     Dome.lua:2840-2848) — possibly normal housing for a moment; the
--     in-dome pass corrects it on the next heavy update. Transient, by
--     design (zero state).
--   * If the destination's last cohort slot fills mid-transit, the colonist
--     lands in normal housing and the passes simply look again — same
--     convergence behavior as the shipped emigration ping-pong guard.

SMROptInPack_Optional = rawget(_G, "SMROptInPack_Optional") or {}

local function module_active()
	return SMROptInPack.IsActive("CohortHousing")
end

-- The colonist's cohort trait, or nil when the rule must leave them alone.
local function cohort_trait(colonist)
	local traits = colonist.traits
	if not traits or traits.Tourist then return end
	if traits.Child then return "Child" end
	if traits.Senior then
		-- employed seniors exempt (Forever Young); a pending player-forced
		-- workplace counts as employed — player intent wins
		if IsValid(colonist.workplace) or colonist.user_forced_workplace then
			return
		end
		return "Senior"
	end
end

-- Best free cohort residence in a community: highest service_comfort, then
-- most free space. Working residences only.
local function find_cohort_slot(community, trait)
	local best, best_score, best_space
	for _, r in ipairs(community and community.labels
			and community.labels.Residence or empty_table) do
		if r.exclusive_trait == trait and r.ui_working then
			local space = r:GetFreeSpace()
			if space > 0 then
				local score = r.service_comfort
				if not best or score > best_score
						or (score == best_score and space > best_space) then
					best, best_score, best_space = r, score, space
				end
			end
		end
	end
	return best
end

SMROptInPack.Register("CohortHousing", {
	title = "OPTIONAL: Seniors/Children auto-move to free Retirement Home/Nursery slots",
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled("CohortHousing") then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end

		local err = SMROptInPack.Require("CohortHousing", {
			{ class = "Colonist", method = "UpdateResidence",
			  reason = "Colonist.UpdateResidence/FindEmigrationDome not found (game update changed it?)" },
			{ class = "Colonist", method = "FindEmigrationDome",
			  reason = "Colonist.UpdateResidence/FindEmigrationDome not found (game update changed it?)" },
			{ class = "Residence", method = "GetFreeSpace",
			  reason = "Residence.GetFreeSpace/IsSuitable not found (game update changed it?)" },
			{ class = "Residence", method = "IsSuitable",
			  reason = "Residence.GetFreeSpace/IsSuitable not found (game update changed it?)" },
			{ global = "FindTransportationModeToCommunity",
			  reason = "emigration transport helpers not found (game update changed them?)" },
			{ global = "IsLRTransportAvailable",
			  reason = "emigration transport helpers not found (game update changed them?)" },
		})
		if err then return err end
		local C = Colonist

		-- In-dome pass: after the shipped residence logic settles, force a
		-- cohort member out of normal housing into a free same-dome cohort
		-- slot. Runs from the same call sites the original does (Idle heavy
		-- update, homeless re-checks), so no new scheduling is introduced.
		local orig_update = C.UpdateResidence
		function C:UpdateResidence(...)
			orig_update(self, ...)
			if not module_active() then return end
			if not self:CanChangeCommand() then return end
			local trait = cohort_trait(self)
			if not trait then return end
			if self:CheckForcedResidence() then return end -- player order wins
			if IsValid(self.reserved_residence) then return end -- mid-move
			local res = self.residence
			if IsValid(res) and res.exclusive_trait == trait then return end -- already cohort-housed
			local dome = self.dome
			if not dome then return end
			local slot = find_cohort_slot(dome, trait)
			if slot and slot:IsSuitable(self) then
				self:SetResidence(slot)
			end
		end

		-- Cross-dome pass: when the own dome has no free cohort slot, the
		-- nearest reachable community with one overrides the shipped answer.
		local orig_find = C.FindEmigrationDome
		function C:FindEmigrationDome(current_dome, ...)
			local dome, mode, dist, elevator = orig_find(self, current_dome, ...)
			if not module_active() then return dome, mode, dist, elevator end
			local trait = cohort_trait(self)
			if not trait then return dome, mode, dist, elevator end
			if self:CheckForcedDome() then return dome, mode, dist, elevator end -- player order wins
			local my_dome = self.dome
			if my_dome and not my_dome.accept_colonists then
				-- quarantine, no one enters or leaves (the original returned nil)
				return dome, mode, dist, elevator
			end
			local res = self.reserved_residence or self.residence
			if IsValid(res) and res.exclusive_trait == trait then
				return dome, mode, dist, elevator -- cohort-housed: never touched
			end
			if find_cohort_slot(my_dome, trait) then
				return dome, mode, dist, elevator -- in-dome pass will take it
			end

			-- candidate gathering mirrors the original: this city's
			-- communities plus elevator-linked cities' (Colonist.lua:2595-2618)
			local my_city = self.city
			local pos = current_dome or IsUnitInDome(self) or self:GetNavigationPos()
			local shuttles = IsLRTransportAvailable(my_city)
			local best, best_mode, best_dist, best_elev
			local function consider(community)
				if community == my_dome or not community:CanVisit(self)
						or not community:CanAcceptNewColonists()
						or community.overpopulated
						or not find_cohort_slot(community, trait) then
					return
				end
				local source_city = community.city ~= my_city and my_city
				local with_shuttles = shuttles and not source_city
				local c_mode, c_dist, c_elev =
					FindTransportationModeToCommunity(community, pos, with_shuttles, source_city)
				if c_mode and (not best or (c_dist or 0) < (best_dist or 0)) then
					best, best_mode, best_dist, best_elev = community, c_mode, c_dist, c_elev
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
			return dome, mode, dist, elevator -- no cohort slot anywhere: shipped answer stands
		end
	end,
})

-- Graduation nudge: free the Nursery slot the moment the Child trait drops.
-- Additive OnMsg, registered unconditionally, gated per call — the move-out
-- itself is the shipped ChooseResidence rejecting the unsuitable home.
OnMsg.ColonistBecameYouth = SMROptInPack.WhenActive("CohortHousing", function(colonist)
	if IsValid(colonist) then
		colonist:UpdateResidence()
	end
end)
