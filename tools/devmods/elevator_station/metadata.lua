return PlaceObj('ModDef', {
	'title', "DEV ONLY - Elevator Station (look prototype)",
	'description', "Look-only prototype for the Relaunched Fix Pack: Opt-In Modules Elevator Station (brief 25, 2026-09-29). One placeable stand-in in the Stations menu, on the surface and underground: a small train-hub dome with a store at its centre, a cargo-lift column and a rail with a vanilla station's two connectors. No storage, no range rule, no twin. Its dome glass and, underground only, its lift shaft are attached visuals. Console: SMRElevatorStationDev.Report(), .Measure(). Demolish every stand-in before removing this mod.",
	'short_description', "DEV ONLY: the Elevator Station's look, placeable on both maps.",
	'id', "SMR_ElevatorStationDev_20260929",
	'author', "catt144",
	'version', 1,
	'lua_revision', 350453,
	'saved_with_revision', 405907,
	'optional_mod', true,
	'code', {
		"Code/10_ElevatorStationDev.lua",
		"Code/BuildingTemplate/SMROptInElevatorStationDev.generated.lua",
	},
	'has_data', true,
	'affected_resources', {
		PlaceObj('ModResourcePreset', {
			'Class', "BuildingTemplate",
			'Id', "SMROptInElevatorStationDev",
			'ClassDisplayName', "Building Template",
		}),
	},
	'TagGameplay', true,
	'TagBuildings', true,
})
