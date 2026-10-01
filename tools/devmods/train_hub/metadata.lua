return PlaceObj('ModDef', {
	'title', "DEV ONLY - Train Hub (Module B build)",
	'description', "Development build of the Relaunched Fix Pack: Opt-In Modules train hub: six connectors, the imported hub body, a built-in drone controller and a Metals maintenance reserve. Connected stations use vanilla storage rows with a Balanced / Export / Import / Not accepted cycle and per-resource sliders. Removing the mod can leave vanilla drone desired amounts at their last setting until a vanilla dial, storage toggle or capacity change rewrites them. Newly connected stations can auto-fill a vanilla train from the colony pool. Existing extra trains from earlier dev builds keep vanilla behavior and count toward the normal route limit; a legacy route may remain over that limit until trains are stored. Placed hubs retain their existing removal limitations. Test colonies only until it ships inside the Opt-In Modules mod.",
	'short_description', "DEV ONLY: six-connector train hub with its own drones and a maintenance reserve.",
	'id', "SMR_TrainHubDev_20260918",
	'author', "catt144",
	'version', 62,
	'lua_revision', 350453,
	'saved_with_revision', 406343,
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
		"Code/40_TrainDistribution.lua",
		"Code/45_TrainDistributionUI.lua",
		"Code/60_StationSpoilage.lua",
		"Code/70_TrainBay.lua",
		"Code/BuildingTemplate/SMROptInTrainHub6.generated.lua",
		"Code/_EntityData.generated.lua",
	},
	'has_data', true,
	'saved', 1790878811,
	'code_hash', 5737714824027890281,
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