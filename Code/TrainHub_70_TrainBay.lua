-- Module TrainHub, part 70 (Code/Opt_TrainHub.lua lists it). Brief 34b, owner
-- 2026-10-02 (spec section 4.8 ruling 10): no train ever appears in the hub,
-- auto-filled or player-assigned. Auto-fill is cut; the player adds trains with
-- vanilla's own Construct Train and Send out Train on any station (archived
-- 1.1.1.406343 Lua/XDef/customStation.generated.lua:11-40,
-- Buildings/Station.lua:707-745, :796-803, :861-868). The cut bytes and their
-- tests: docs/archive/train_bay_autofill_20261002/. The earlier extras:
-- docs/archive/train_bay_extras_20260928/.
-- Keep the saved class name: existing HubTrain objects inherit vanilla Train
-- behavior, including Idle, route counting and storage. No new HubTrain is spawned.
-- The old snapshot's delete-on-load list and prepaid pool use vanilla's loader.
DefineClass.HubTrain = {
    __parents = { "Train" },
    persist_baseclass = "Train",
}

SMROptInTrainBay = {}
local B = SMROptInTrainBay
B.stats = { refused = 0 }
B.error = false
B.Require = { { "TrackBase", "AssignTrain" }, { "Station", "ToggleCreateRouteMode_Update" } }
for _, pair in ipairs(B.Require) do
    local class = rawget(_G, pair[1])
    if not class or type(class[pair[2]]) ~= "function" then
        B.error = pair[1] .. "." .. pair[2] .. " unavailable"
        print("[TrainBay] inactive: " .. B.error)
        return
    end
end
if type(rawget(_G, "SMROptInTrainHubBase")) ~= "table" then
    B.error = "SMROptInTrainHubBase unavailable"
    print("[TrainBay] inactive: " .. B.error)
    return
end

local function h(o) return IsValid(o) and tostring(o.handle) or "none" end
local function is_hub(o) return IsValid(o) and IsKindOf(o, "SMROptInTrainHubBase") end

-- The one spawn in the game: TrackBase:AssignTrain(station) places the Train in
-- the station it is passed (archived 1.1.1.406343 Buildings/Track.lua:428-457,
-- the only PlaceObjectIn("Train") under Lua/). Refusing a hub here closes every
-- caller at once: both card buttons, the Transportation overview's row
-- (XDef/CommandCenterTransportationOverviewRow.generated.lua:477-483), the
-- station-side auto-assign after construction (Station.lua:590-606) and any
-- console or mod call. Vanilla's own early returns (Track.lua:430-435) already
-- make a refused call a silent no-op, so no caller expects a result.
local assign = TrackBase.AssignTrain
function TrackBase:AssignTrain(station, ...)
    if is_hub(station) then
        B.stats.refused = B.stats.refused + 1
        print(string.format("[TrainBay] refused hub=%s track=%s t=%d", h(station), h(self), GameTime()))
        return
    end
    return assign(self, station, ...)
end

-- The hub's card shows vanilla's Construct Train and Send out Train, because
-- sectionCustom resolves customStation up the class chain
-- (XDef/sectionCustom.generated.lua:14-38). InfopanelButton:OnContextUpdate
-- calls context:<OnPressParam>_Update(button) when the method exists
-- (XDef/InfopanelButton.generated.lua:59-64): disable both with the reason, and
-- make the presses themselves do nothing, which also covers the Transportation
-- overview's row and a gamepad press.
local REASON = "Trains are built and sent out from a <em>Train Station</em>, never from the hub."
local function refuse_button(button, title)
    button:SetEnabled(false)
    button:SetRolloverTitle(title)
    button:SetRolloverText(Untranslated(REASON))
    if button.SetRolloverDisabledText then button:SetRolloverDisabledText(Untranslated(REASON)) end
end
function SMROptInTrainHubBase:ConstructTrain_Update(button)
    refuse_button(button, T(14474, "Construct Train"))
end
function SMROptInTrainHubBase:ToggleCreateRouteMode_Update(button)
    refuse_button(button, T(14381, "Send out Train"))
end
function SMROptInTrainHubBase:ConstructTrain() end
function SMROptInTrainHubBase:ToggleCreateRouteMode() end

B.active = true
print("[TrainBay] loaded: the hub refuses add-train; legacy HubTrain compatibility")
