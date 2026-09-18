return PlaceObj('ModDef', {
	'title', "DEV ONLY - Train Hub Prototype",
	'description', "Disposable-save prototype for the Relaunched Fix Pack: Opt-In Modules train-hub go/no-go. Do not enable for a kept colony.",
	'short_description', "DEV ONLY: six-connector train-station prototype.",
	'id', "SMR_TrainHubPrototype_20260918",
	'author', "catt144",
	'version', 1,
	'lua_revision', 350453,
	'saved_with_revision', 403908,
	'optional_mod', true,
	'code', {
		"Code/00_TrainHubPrototype.lua",
		"Code/BuildingTemplate/SMRTrainHubPrototype.generated.lua",
	},
	'has_data', true,
	'affected_resources', {
		PlaceObj('ModResourcePreset', {
			'Class', "BuildingTemplate",
			'Id', "SMRTrainHubPrototype",
			'ClassDisplayName', "BuildingTemplate",
		}),
	},
	'TagBuildings', true,
	'TagGameplay', true,
})
