-- D19: optional content, OFF by default. Owner 2026-10-03 requested a
-- seed-consuming Arboretum test build; category and one-per-dome are provisional.
-- ON offers new buildings; OFF (including a live toggle) hides new buildings.
-- Placed Arboretums retain native service/consumption behaviour in either state.
-- Demolish them before removing the mod. Save names and residuals: bugs/D19.md.
-- All service, consumption and logistics behaviour is inherited, not patched.

local ID = "Arboretum"
local TEMPLATE = "SMROptInArboretum"

DefineClass.SMROptInArboretumBase = {
	__parents = { "LifeSupportConsumerService", "ElectricityConsumer" },
	persist_baseclass = "LifeSupportConsumerService",
}

SMROptInPack.Register(ID, {
	title = "OPTIONAL: Arboretum, an in-dome service consuming Seeds",
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled(ID) then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end
		return SMROptInPack.Require(ID, {
			{ class = "LifeSupportConsumerService" },
			{ class = "ElectricityConsumer" },
			{ class = "HasConsumption", method = "Consume_Visit" },
			{ global = "IsSeedsResourceAvailable" },
			{ global = "IsGameRuleActive" },
		})
	end,
})

-- BuildMenu.lua:731 (archived 1.1.1.406343): additional locks hide the entry.
-- Restrict the handler to our template before inspecting any runtime state.
function OnMsg.GetAdditionalBuildingLocks(template, locks)
	if not template or (template.id ~= TEMPLATE and template.class ~= TEMPLATE
		and template.template_name ~= TEMPLATE) then return end
	if SMROptInPack_Disabled[ID] or not SMROptInPack.IsActive(ID) then
		locks.smr_arboretum_off = true
	elseif IsGameRuleActive("NoTerraforming") or not IsSeedsResourceAvailable() then
		locks.smr_arboretum_seeds = true
	end
end
