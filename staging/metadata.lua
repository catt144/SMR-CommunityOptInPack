return PlaceObj('ModDef', {
	'title', "DEV ONLY - Opt-In Modules Workbench (never upload)",
	'description', "Local workbench for modules in progress. Requires Opt-In Modules. Its switches appear on the Opt-In Modules options page. Never upload this mod.",
	'id', "SMR_CommunityOptInPack_Workbench",
	'author', "catt144",
	'version', 0,
	'version_major', 1,
	'version_minor', 0,
	'lua_revision', 350453,
	'optional_mod', false,
	'dependencies', {
		PlaceObj('ModDependency', {
			'id', "SMR_CommunityOptInPack",
			'title', "Relaunched Fix Pack: Opt-In Modules",
			'version_major', 1,
			'version_minor', 0,
			'required', true,
		}),
	},
	'ignore_files', {
		"*",
	},
	'default_options', {
		Arboretum = false,
	},
	'code', {
		"Code/00_Workbench.lua",
		"Code/Opt_Arboretum.lua",
		"Code/BuildingTemplate/SMROptInArboretum.generated.lua",
	},
	'has_data', true,
})
