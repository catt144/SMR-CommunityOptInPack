return PlaceObj('ModDef', {
	'title', "DEV ONLY - Train Hub (Module B build)",
	'description', "Development build of the Relaunched Fix Pack: Opt-In Modules train hub: six connectors, the imported hub body, a built-in drone controller and a Metals maintenance reserve. Test colonies only until it ships inside the Opt-In Modules mod.",
	'short_description', "DEV ONLY: six-connector train hub with its own drones and a maintenance reserve.",
	'id', "SMR_TrainHubDev_20260918",
	'author', "catt144",
	'version', 40,
	'lua_revision', 350453,
	'saved_with_revision', 403908,
	'optional_mod', true,
	'entities', {
		"SMROptInTrainHub6",
	},
	'code', {
		"Code/20_TrainHub.lua",
		"Code/30_TrainHubDrones.lua",
		"Code/10_TrainFloor.lua",
		"Code/BuildingTemplate/SMROptInTrainHub6.generated.lua",
		"Code/_EntityData.generated.lua",
	},
	'has_data', true,
	'saved', 1790119142,
	'code_hash', 8148640099385970650,
	'affected_resources', {
		PlaceObj('ModResourcePreset', {
			'Class', "BuildingTemplate",
			'Id', "SMROptInTrainHub6",
			'ClassDisplayName', "Building Template",
		}),
	},
	'TagGameplay', true,
	'TagBuildings', true,
})
