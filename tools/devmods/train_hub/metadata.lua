return PlaceObj('ModDef', {
	'title', "DEV ONLY - Train Hub (Module B build)",
	'description', "Development build of the Relaunched Fix Pack: Opt-In Modules train hub: six connectors, the imported hub body, a built-in drone controller and a Metals maintenance reserve. Test colonies only until it ships inside the Opt-In Modules mod.",
	'short_description', "DEV ONLY: six-connector train hub with its own drones and a maintenance reserve.",
	'id', "SMR_TrainHubDev_20260918",
	'author', "catt144",
	'version', 49,
	'lua_revision', 350453,
	'saved_with_revision', 405907,
	'optional_mod', true,
	'entities', {
		"SMROptInTrainHub6",
		"SMROptInTrainHub6Glass",
		"SMROptInTrainHub6DomeGlass",
	},
	'code', {
		"Code/20_TrainHub.lua",
		"Code/30_TrainHubDrones.lua",
		"Code/10_TrainFloor.lua",
		"Code/BuildingTemplate/SMROptInTrainHub6.generated.lua",
		"Code/_EntityData.generated.lua",
	},
	'has_data', true,
	'saved', 1790198858,
	'code_hash', -8008577484182597929,
	'affected_resources', {
		PlaceObj('ModResourcePreset', {
			'Class', "BuildingTemplate",
			'Id', "SMROptInTrainHub6",
			'ClassDisplayName', "Building Template",
		}),
		PlaceObj('ModResourceEntity', {
			'Entity', "SMROptInTrainHub6",
		}),
		PlaceObj('ModResourceEntity', {
			'Entity', "SMROptInTrainHub6Glass",
		}),
		PlaceObj('ModResourceEntity', {
			'Entity', "SMROptInTrainHub6DomeGlass",
		}),
	},
	'TagGameplay', true,
	'TagBuildings', true,
})