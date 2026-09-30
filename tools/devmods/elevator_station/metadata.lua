return PlaceObj('ModDef', {
	'title', "DEV ONLY - Elevator Depot (look prototype)",
	'description', "Look prototype for the Relaunched Fix Pack: Opt-In Modules Elevator Depot (brief 25, 2026-09-29). One placeable stand-in in the Stations menu, on the surface and underground: vanilla's Space Elevator at 75% with a smaller vanilla tunnel as the train mouth, on our own base entity. A working station: trains drive in, stop inside and come back out. Its cabin runs for show; no cargo crosses maps, no drone crew, no twin. Console: SMRElevatorDepotDev.Report(), .Measure(), .Set(). Demolish every stand-in before removing this mod.",
	'short_description', "DEV ONLY: the Elevator Depot's look, a working station placeable on both maps.",
	'id', "SMR_ElevatorStationDev_20260929",
	'author', "catt144",
	'version', 5,
	'lua_revision', 350453,
	'saved_with_revision', 405907,
	'optional_mod', true,
	'entities', {
		"SMROptInElevatorDepot",
	},
	'code', {
		"Code/10_ElevatorDepotDev.lua",
		"Code/_EntityData.generated.lua",
		"Code/BuildingTemplate/SMROptInElevatorDepotDev.generated.lua",
	},
	'has_data', true,
	'saved', 1790748485,
	'code_hash', 5524373636416358041,
	'affected_resources', {
		PlaceObj('ModResourceEntity', {
			'Entity', "SMROptInElevatorDepot",
		}),
		PlaceObj('ModResourcePreset', {
			'Class', "BuildingTemplate",
			'Id', "SMROptInElevatorDepotDev",
			'ClassDisplayName', "Building Template",
		}),
	},
	'TagGameplay', true,
	'TagBuildings', true,
})