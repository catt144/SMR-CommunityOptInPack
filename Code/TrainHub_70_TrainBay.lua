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

-- FIX_POLICY §8: per-event dev lines print only under SMROptInPack.TrainTrace (00_Core.lua).
local function trace(...)
    local pack = rawget(_G, "SMROptInPack")
    if pack and pack.TrainTrace then print(...) end
end

SMROptInTrainBay = {}
local B = SMROptInTrainBay
B.stats = { refused = 0 }
B.error = false
B.Require = { { "TrackBase", "AssignTrain" } }
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
-- caller at once: a station card's two buttons (the hub's card never shows them:
-- sectionCustom looks up "custom<class>" by exact name and the hub is no
-- Station by name, XDef/sectionCustom.generated.lua:16-21), the Transportation
-- overview's row (XDef/CommandCenterTransportationOverviewRow.generated.lua:
-- 477-483), the station-side auto-assign after construction (Station.lua:
-- 590-606) and any console or mod call. Vanilla's own early returns (Track.lua:430-435) already
-- make a refused call a silent no-op, so no caller expects a result.
local assign = TrackBase.AssignTrain
function TrackBase:AssignTrain(station, ...)
    if is_hub(station) then
        B.stats.refused = B.stats.refused + 1
        trace(string.format("[TrainBay] refused hub=%s track=%s t=%d", h(station), h(self), GameTime()))
        return
    end
    return assign(self, station, ...)
end

B.active = true
print("[TrainBay] loaded: the hub refuses add-train; legacy HubTrain compatibility")
