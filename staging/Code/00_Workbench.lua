-- DEV ONLY. Native required dependency loads the production core first.
-- Options use the production page and AccountStorage namespace from day one.
-- No ModItem is inserted into production.items: SaveDef still sees launch files only.
-- Source: archived 1.1.1.406343, CommonLua/Modding/Mod.lua:
-- GetOptionItems :479, LoadOptions :680, ApplyModOptions :753, GetProperties :2647.
local production = Mods.SMR_CommunityOptInPack
local workbench = Mods.SMR_CommunityOptInPack_Workbench
if not production or not workbench then error("Workbench needs Opt-In Modules") end
if not (SMROptInPack and SMROptInPack.Register) then error("Workbench dependency did not load first") end

-- A direct Lua reload can run us again without unloading the ModDef objects.
local old = rawget(_G, "SMROptInWorkbench")
if old and old.Detach then old.Detach() end
local original_items = production.GetOptionItems
local original_has_options = workbench.HasOptions
local bridge = {}
SMROptInWorkbench = bridge

local function clear_cache()
    production.options.properties = nil
    production.options.__defaults = nil
end

local function get_options(self, test)
    local result = original_items(self, test)
    if test and result then return result end
    local extra = workbench:GetOptionItems(test)
    if test then return extra end
    for _, item in ipairs(extra) do result[#result + 1] = item end
    return result
end
local function hidden_options() return false end
production.GetOptionItems = get_options
workbench.HasOptions = hidden_options

-- LoadOptions copied even keys absent from production.default_options. Thus an
-- existing account value survives staging, promotion and a later full restart.
for name, default in pairs(workbench.default_options) do
    if production.default_options[name] ~= nil then error("Duplicate workbench option: " .. name) end
    if rawget(production.options, name) == nil then production.options[name] = default end
end
CurrentModOptions = production.options
clear_cache()

function bridge.Detach()
    if production.GetOptionItems == get_options then production.GetOptionItems = original_items end
    if workbench.HasOptions == hidden_options then workbench.HasOptions = original_has_options end
    clear_cache()
end
-- Items load after code. Rebuild the UI metadata once those items exist.
function OnMsg.ModItemsLoaded() clear_cache() end
function OnMsg.ModsReloading() bridge.Detach() end
SMROptInPack.Log("DEV workbench loaded; staged options share the Opt-In Modules page")
