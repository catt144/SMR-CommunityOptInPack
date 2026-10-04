return {
	PlaceObj('ModItemCode', {
		'name', "00_Workbench",
		'CodeFileName', "Code/00_Workbench.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_Arboretum",
		'CodeFileName', "Code/Opt_Arboretum.lua",
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "Arboretum",
		'DisplayName', "Arboretum",
		'Help', "Adds an indoor <em>Arboretum</em> that consumes Seeds for Comfort and relaxation. Turning it off stops new construction; demolish all Arboretums before removing the mod.",
		'DefaultValue', false,
	}),
}
