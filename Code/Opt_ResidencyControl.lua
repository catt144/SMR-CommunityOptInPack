-- D03 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix.
--
-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles
-- take effect immediately, both directions — the gates below consult
-- SMROptInPack.IsActive per call and pass through while off; the infopanel row
-- stops being appended to newly opened panels). Gate 1 (the class-method wrap
-- on Community:CanAcceptNewColonists) is installed at FILE SCOPE, classdef
-- time, so it propagates through class flattening and the FIRST mid-session
-- enable works too — an apply()-time install ran after flattening and left
-- that gate silently dead until restart (audit A2, fixed 2026-07-29; the
-- Opt_DroneOverhaul pattern). The ChooseDome global wrap and the two UI Init
-- wraps resolve at call time and stay in apply() — they are live-enable-safe
-- as installed. Other mods / power users can also pre-seed
-- SMROptInPack_Optional = { ResidencyControl = true } before this mod loads.
-- `SMROptInPack.ListFixes()` reports it as inactive until enabled.
--
-- Why it exists: the community's long-standing ask — stop new residents from
-- moving into a dome while its CURRENT residents keep commuting and using
-- services normally. The shipped game offers only blunt instruments: the
-- accept-colonists toggle is a QUARANTINE by design ("Colonists are not allowed
-- to enter or leave", T365/T7660; enforced with the literal comment
-- "quarantine, no one enters or leaves", Colonist.lua:2632-2634) and scripted
-- content depends on that seal (Wildfire's dome-local spread, TheRogueDome's
-- forced quarantine — the F61 entry records the survey; the pack's earlier F61
-- "fix" subverted it and was deleted for exactly that reason). The trait filter
-- is indirect and REMOVES a quarantine when set. This module adds the missing
-- middle setting as a new per-dome policy, leaving quarantine untouched.
--
-- WHAT THIS SHIPS: a per-dome / per-habitat "closed to new residents" policy.
--
--   * A new toggle row on the dome and MicroG-habitat infopanels (left-click
--     toggles, Ctrl+click broadcasts to all domes — the shipped
--     Community:TogglePolicy/SetPolicyState machinery, Community.lua:77-100,
--     which also plays the policy FX and respects the rogue-dome UI lock).
--   * Voluntary resettlement: post-wrapper on Community:CanAcceptNewColonists
--     (Community.lua:61-63) — a closed dome stops being offered to colonists
--     looking to move (its only caller is Colonist:FindEmigrationDome's
--     candidate filter, Colonist.lua:2658 — verified the only caller in Src).
--   * Arrivals choosing a FIRST home: post-wrapper on the global ChooseDome
--     (_GameUtils.lua:426-446) filtering closed domes out of the candidate
--     list. ChooseDome is the single choose-a-new-home funnel: rocket
--     disembark/arrivals (RocketBase.lua:1985/:2068/:2105), lander/transporter
--     arrivals (CargoTransporterNew.lua:907/:951/:975), factory-born androids
--     (DroneFactory.lua:224) and stranded colonists re-homing
--     (Colonist.lua:1149). Deliberately NOT filtered there:
--       - the `safety_dome` argument — the last-resort dome for a colonist
--         stranded outside stays available, so the policy can never suffocate
--         anyone;
--       - tourists (traits.Tourist) — they take hotel rooms, not residency in
--         the community sense, and the spec leaves hotel-seeking alone.
--   * Untouched by design: MANUAL relocation (the player's own order overrides
--     the policy), births (in-dome), homeless within their own dome (not a
--     move-in), quarantine and both passage-use toggles (fully independent).
--
-- The home-side commute gates (Dome:GetService/ChooseTraining/ChooseWorkplace,
-- ShiftsBuilding:CanWorkTrainHereDomeCheck) never read this flag, so a closed
-- dome's residents keep working, shopping and training through passages —
-- which is the whole point.
--
-- Savegame footprint (FIX_POLICY §3): `SMRFixPack_closed_to_new_residents` on
-- the Dome/Habitat object (true/false), absent-tolerant both ways — nil means
-- vanilla behavior, the unmodded game never reads it, and a save carrying the
-- flag loads fine with the module (or the pack) removed.

SMROptInPack_Optional = rawget(_G, "SMROptInPack_Optional") or {}

local FLAG = "SMRFixPack_closed_to_new_residents"

local function module_active()
	return SMROptInPack.IsActive("ResidencyControl")
end

local function is_closed(dome)
	return type(dome) == "table" and dome[FLAG] and true or false
end

-- gate 1: voluntary resettlement (FindEmigrationDome's candidate filter).
-- Installed at FILE SCOPE (audit A2, 2026-07-29) so the wrap is baked into the
-- flattened Community subclasses; guarded by the same existence checks apply()
-- runs, so a missing target degrades to apply()'s reason string instead of
-- erroring at load. module_active makes the Mod Options toggle live: off =
-- shipped answer.
do
	local C = rawget(_G, "Community")
	if type(C) == "table" and type(C.CanAcceptNewColonists) == "function"
			and type(C.TogglePolicy) == "function" then
		local orig_can = C.CanAcceptNewColonists
		function C:CanAcceptNewColonists(...)
			if module_active() and self[FLAG] then
				return false
			end
			return orig_can(self, ...)
		end
	end
end

-- One infopanel row, cloned from the shipped accept-colonists row pattern
-- (Lua\XDef\sectionDome.generated.lua:177-217): InfopanelActiveSection with
-- everything set in OnContextUpdate. Yellow/limit styling on the closed state
-- so it cannot be mistaken for the red quarantine row above it.
--
-- Placement (playtest feedback, PT-49 first sitting 2026-07-27): the row must
-- sit WITH the policy toggle group (right after the shipped accept-colonists
-- row), not at the section's end below the stat bars. The section is a VList
-- whose children render in array order (XWindow children ARE the array part;
-- the engine itself reorders them with plain array ops, XWindow.lua:719-739),
-- and sectionDome:Init builds the toggle rows first, then the plain
-- InfopanelSection blocks (Colonists count, stats). So: create the row (lands
-- last), then move it to just before the FIRST plain InfopanelSection child —
-- i.e. directly after the last shipped toggle. Class test is unambiguous:
-- InfopanelActiveSection and InfopanelSection are siblings (both XSection).
-- If no such child exists (e.g. a differently-shaped habitat section), the
-- row simply stays at the end — the pre-feedback behavior. Init-time move:
-- the first measure/layout pass runs after Init, so no invalidation is
-- strictly needed; the InvalidateMeasure is belt-and-braces for rebuilds.
local function append_policy_row(section, context)
	local row = InfopanelActiveSection:new({
		OnContextUpdate = function(self, context, ...)
			local dome = ResolvePropObj(context)
			local closed = is_closed(dome)
			if closed then
				self:SetIcon("UI/IconsRemaster/Sections/accept_colonists_off.png")
				self:SetIconBack("UI/IconsRemaster/Sections/ip_sections_limit")
				self:SetTitle(Untranslated("Closed to new residents"))
				self:SetRolloverImageColor("yellow", true)
			else
				self:SetIcon("UI/IconsRemaster/Sections/accept_colonists_on.png")
				self:SetIconBack("UI/IconsRemaster/Sections/ip_sections_on.png")
				self:SetTitle(Untranslated("Accepts new residents"))
				self:SetRolloverImageColor("green", true)
			end
			rawset(self, "ProcessToggle", function(self, context, broadcast)
				local building = ResolvePropObj(context)
				-- shipped policy machinery: UI-interaction gate, FX, broadcast
				building:TogglePolicy(FLAG, broadcast)
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
			-- rollover
			self:SetRolloverTitle(Untranslated("Residency Policy (Relaunched Fix Pack: Opt-In Modules)"))
			self:SetRolloverText(Untranslated(closed
				and "No new Colonists will move in — voluntarily or on arrival. Current residents keep commuting, working and using services through Passages exactly as before. You can still relocate Colonists here manually, and Tourists still check in.<newline><newline>Current status: <em>Closed to new residents</em>"
				or  "Close this Dome to new residents without quarantining it: no one new moves in, while current residents keep commuting, working and using services through Passages. Manual relocation and Tourists are unaffected.<newline><newline>Current status: <em>Accepts new residents</em>"))
			if closed then
				self:SetRolloverHint(Untranslated("<left_click> Accept new residents in this Dome<newline><em>Ctrl + <left_click></em> Accept new residents in all Domes"))
				self:SetRolloverHintGamepad(Untranslated("<ButtonA> Accept new residents in this Dome<newline><ButtonY> Accept new residents in all Domes"))
			else
				self:SetRolloverHint(Untranslated("<left_click> Close this Dome to new residents<newline><em>Ctrl + <left_click></em> Close all Domes to new residents"))
				self:SetRolloverHintGamepad(Untranslated("<ButtonA> Close this Dome to new residents<newline><ButtonY> Close all Domes to new residents"))
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

SMROptInPack.Register("ResidencyControl", {
	title = 'OPTIONAL: per-dome "closed to new residents" policy — no quarantine involved',
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled("ResidencyControl") then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end

		-- Both section classes declare Init themselves (generated XDef classes),
		-- so the classdef lookup is valid at mod-load time.
		local err = SMROptInPack.Require("ResidencyControl", {
			{ class = "Community", method = "CanAcceptNewColonists",
			  reason = "Community.CanAcceptNewColonists/TogglePolicy not found (game update changed it?)" },
			{ class = "Community", method = "TogglePolicy",
			  reason = "Community.CanAcceptNewColonists/TogglePolicy not found (game update changed it?)" },
			{ global = "ChooseDome" },
			{ class = "sectionDome", method = "Init",
			  reason = "sectionDome/sectionMicroGHabitat Init not found (game update changed the infopanel?)" },
			{ class = "sectionMicroGHabitat", method = "Init",
			  reason = "sectionDome/sectionMicroGHabitat Init not found (game update changed the infopanel?)" },
		})
		if err then return err end
		local SD = sectionDome
		local SM = sectionMicroGHabitat

		-- gate 1 (the CanAcceptNewColonists wrap) is installed at file scope
		-- above — see the header; apply() only validates its targets.

		-- gate 2: arrivals / first-home choice. Filter the candidate list only;
		-- safety_dome passes through untouched (last-resort survival), and
		-- tourists keep the vanilla choice.
		local orig_choose = ChooseDome
		local function choose(traits, domes, safety_dome, dome_elevators, ...)
			if module_active() and type(domes) == "table" and not (traits and traits.Tourist) then
				local filtered
				for i, dome in ipairs(domes) do
					if is_closed(dome) then
						if not filtered then
							filtered = {}
							for j = 1, i - 1 do
								filtered[#filtered + 1] = domes[j]
							end
						end
					elseif filtered then
						filtered[#filtered + 1] = dome
					end
				end
				domes = filtered or domes
			end
			return orig_choose(traits, domes, safety_dome, dome_elevators, ...)
		end
		local err = SMROptInPack.SetGlobal("ChooseDome", choose,
			"could not install the ChooseDome wrapper (sandbox change?)")
		if err then return err end

		-- UI: append the policy row after the shipped rows (VList order). The
		-- module_active check keeps the row out of newly opened infopanels when
		-- the Mod Options toggle is off (a panel already open when the toggle
		-- flips rebuilds on the next selection).
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
