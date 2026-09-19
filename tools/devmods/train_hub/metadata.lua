return PlaceObj('ModDef', {
	'title', "DEV ONLY - Train Hub (Module B build)",
	'description', "Development build of the Relaunched Fix Pack: Opt-In Modules train hub: six connectors, a built-in drone controller and a Metals maintenance reserve, on a stand-in body. Test colonies only until it ships inside the Opt-In Modules mod.",
	'short_description', "DEV ONLY: six-connector train hub with its own drones and a maintenance reserve.",
	'id', "SMR_TrainHubDev_20260918",
	'author', "catt144",
	'version', 1,
	'lua_revision', 350453,
	'saved_with_revision', 403908,
	'optional_mod', true,
	'code', {
		"Code/10_TrainFloor.lua",
		"Code/20_TrainHub.lua",
		"Code/BuildingTemplate/SMROptInTrainHub6.generated.lua",
	},
	'has_data', true,
	'affected_resources', {
		PlaceObj('ModResourcePreset', {
			'Class', "BuildingTemplate",
			'Id', "SMROptInTrainHub6",
			'ClassDisplayName', "BuildingTemplate",
		}),
	},
	'TagBuildings', true,
	'TagGameplay', true,
})
