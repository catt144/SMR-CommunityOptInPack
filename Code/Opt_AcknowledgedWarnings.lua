-- D02 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix.
--
-- Enable it in-game: Options → Mod Options → Community Fix Pack: Opt-In Modules (D05; toggles
-- take effect immediately, both directions — the wrappers below consult
-- SMROptInPack.IsActive per call and pass through while off). Other mods /
-- power users can also pre-seed SMROptInPack_Optional = { AcknowledgedWarnings
-- = true } before this mod loads. `SMROptInPack.ListFixes()` reports it as
-- inactive until enabled.
--
-- Why it exists: dismissing a "Building Not Working" warning only silences the
-- whole notification id for 120,000 GAME-ms = 4 game hours (SuppressTime, with
-- GameTime defaulting true — NotificationPreset.lua:65-66/:126-128; measured
-- live, PT-38: three dismissal→return pairs at 120,000 + time-to-next-attempt,
-- every in-window re-add attempt BLOCKED). That is designed behavior, not a bug
-- (the D02 entry in docs/BUGS.md records the full trace), but the design has no
-- answer for a PERMANENTLY broken building: an unfixable wreck — the archetype
-- is a building entombed by a landscaping lake (F30) — re-nags every 4 game
-- hours for the rest of the game, which at ultra speed is every few REAL
-- seconds. And the window is per notification ID, so while it runs, a FRESHLY
-- broken building is silenced too — arguably backwards.
--
-- WHAT THIS SHIPS: dismissal means "I have seen THESE buildings".
--
--   * Dismissing the warning stamps every building it currently lists with an
--     acknowledgment flag; those buildings stay quiet until they RECOVER
--     (ShouldShowNotWorkingNotification() turning false clears the stamp on the
--     next remove attempt — BaseBuilding.lua:121-139 funnels both directions
--     through UpdateObjectInNotification). A later, separate breakage of the
--     same building notifies again.
--   * The shipped 4-game-hour whole-id window is NOT armed for this one id, so
--     a NEW building breaking right after a dismissal warns immediately.
--     Strictly better than the shipped window on both axes.
--   * Only `NotWorkingBuildings` is touched. DestroyedInfrastructure /
--     RoverDamaged etc. keep their shipped dismissal semantics (they are
--     one-shot adds where dismissal already holds — F32 trace).
--
-- Mechanism — three chained wrappers on the notification helper GLOBALS
-- (CommonLua\Libs\Notifications\Notifications.lua; none of the three is
-- captured as a file-local there, so replacement globals are seen — the F22
-- precedent, and every call site resolves them through _G at call time):
--   * SuppressNotification (:141-146) — its ONLY caller is RemoveNotification,
--     and only under `notification.dismissed` (:86-88), so it IS the dismissal
--     hook; `notification.objects` (an array_set — objects in the array part)
--     is still intact at that point. For this id we stamp and skip the shipped
--     whole-id window; every other id falls through untouched.
--   * AddObjectToNotification (:231-249) — the single re-add funnel for this id
--     (BaseBuilding:UpdateNotWorkingBuildingsNotification via
--     UpdateObjectInNotification, plus the direct RequiresMaintenance.lua:234
--     call). An acknowledged building's re-add is dropped; anything else passes
--     through.
--   * RemoveObjectFromNotification (:275-290) — the recovery direction of the
--     same funnels (and RequiresMaintenance.lua:274). A remove attempt for an
--     acknowledged building clears the stamp BEFORE the shipped body runs, so
--     recovery (or destruction, Building.lua:1487) re-arms future warnings.
--     RemoveNotification also calls this with a notification TABLE as `id` for
--     parent bookkeeping — the wrapper acts only on the exact id string.
--
-- Savegame footprint (FIX_POLICY §3): `SMRFixPack_ack_notworking = true` on
-- acknowledged Building objects, absent-tolerant in both directions — the
-- unmodded game never reads it, and a save carrying stamps loads fine with the
-- module (or the whole pack) removed. Stale stamps left by disabling the module
-- are inert (nothing reads the flag when the wrappers are gone) and clear
-- themselves on the building's next recovery if the module returns.

SMROptInPack_Optional = rawget(_G, "SMROptInPack_Optional") or {}

local ID = "NotWorkingBuildings"
local FLAG = "SMRFixPack_ack_notworking"

local function module_active()
	return SMROptInPack.IsActive("AcknowledgedWarnings")
end

SMROptInPack.Register("AcknowledgedWarnings", {
	title = 'OPTIONAL: dismissing "Building Not Working" acknowledges those buildings until they recover',
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled("AcknowledgedWarnings") then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end

		local err = SMROptInPack.Require("AcknowledgedWarnings", {
			{ global = "SuppressNotification",
			  reason = "SuppressNotification not found (game update changed the notification library?)" },
			{ global = "AddObjectToNotification",
			  reason = "AddObjectToNotification not found (game update changed the notification library?)" },
			{ global = "RemoveObjectFromNotification",
			  reason = "RemoveObjectFromNotification not found (game update changed the notification library?)" },
			{ global = "FindNotification",
			  reason = "FindNotification not found (game update changed the notification library?)" },
		})
		if err then return err end
		-- NOTE: NotificationPresets is a preset GlobalMap and exists EMPTY at
		-- mod-load time (the F75 lesson) — do not "verify" the preset here. The
		-- wrappers key on the id string alone, which is safe either way.

		local orig_suppress = SuppressNotification
		local function suppress(notification, ...)
			if module_active() and notification and notification.id == ID and notification.dismissed then
				-- D02: dismissal = per-object acknowledgment. Stamp what the
				-- player looked at; skip the shipped whole-id quiet window so a
				-- NEW breakage still warns immediately.
				for _, obj in ipairs(notification.objects or empty_table) do
					if type(obj) == "table" then
						obj[FLAG] = true
					end
				end
				return
			end
			return orig_suppress(notification, ...)
		end

		local orig_add = AddObjectToNotification
		local function add(object, object_params, id, ...)
			if module_active() and id == ID and type(object) == "table" and object[FLAG] then
				-- acknowledged and still broken: stay quiet. Mirror the shipped
				-- "nothing to do" answer (the existing notification, if any).
				return FindNotification(id, ...)
			end
			return orig_add(object, object_params, id, ...)
		end

		local orig_remove = RemoveObjectFromNotification
		local function remove(object, id, ...)
			if module_active() and id == ID and type(object) == "table" and object[FLAG] then
				-- the building recovered (or was destroyed): re-arm its warnings
				object[FLAG] = nil
			end
			return orig_remove(object, id, ...)
		end

		local WRAP_FAIL = "could not install the notification wrappers (sandbox change?)"
		return SMROptInPack.SetGlobal("SuppressNotification", suppress, WRAP_FAIL)
			or SMROptInPack.SetGlobal("AddObjectToNotification", add, WRAP_FAIL)
			or SMROptInPack.SetGlobal("RemoveObjectFromNotification", remove, WRAP_FAIL)
	end,
})
