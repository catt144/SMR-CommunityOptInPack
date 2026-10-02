-- Train stations do not spoil food; the hub does (owner, 2026-09-28).
-- Relaunched spoils Food and every delicacy by g_Consts.FoodDecay (4) percent of
-- each stored amount per sol, rounded to whole units at random (Lua/Spoilage.lua).
-- Stations inherit it from StorageDepot: BuildingDailyUpdate is a combined method
-- (Buildings/Building.lua:2), so StorageDepot:BuildingDailyUpdate runs for every
-- Station and calls self:SpoilStoredResources() (Buildings/StorageDepot.lua:116-132,
-- archived 1.1.1.405907). Trains never spoil (Units/Train.lua has no call). A
-- station holding a row target then drops a unit now and then and a train carries
-- one unit back; a station's stock is cargo in transit, so it keeps.
-- The hub is a 480-per-resource warehouse and its losses send no trains: it keeps
-- vanilla spoilage. Other depots are untouched: the method is replaced on Station
-- only. No persisted state; without the mod stations spoil again.
-- Shipping (brief 34; owner 2026-10-02, OI-41): this goes with the TrainHub module, so a
-- station keeps its food only while that module is on; off, it spoils as vanilla, per call.
-- StorageDepot declares the method (StorageDepot.lua:116-132); it is read at call time.
function Station:SpoilStoredResources(...)
	local P = rawget(_G, "SMROptInPack")
	if type(P) == "table" and type(P.IsActive) == "function" and not P.IsActive("TrainHub") then
		return StorageDepot.SpoilStoredResources(self, ...)
	end
end

SMROptInTrainHubBase.SpoilStoredResources = StorageDepot.SpoilStoredResources
