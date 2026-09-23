return PlaceObj('ModDef', {
	'title', "DEV ONLY - Rail Shaft (cross-map train tunnel prototype)",
	'description', "Throwaway prototype for the Relaunched Fix Pack: Opt-In Modules. Lets a Universal Tunnel be built underground, cross-links one mouth on each map into a rail shaft, and replaces the hop with a map transfer that logs every stage. Throwaway saves only: it writes vanilla's DisabledInEnvironment GameVar and re-links finished buildings by hand.",
	'short_description', "DEV ONLY: cross-map train tunnel, instrumented. Throwaway saves only.",
	'id', "SMR_RailShaftDev_20260923",
	'author', "catt144",
	'version', 1,
	'lua_revision', 350453,
	'saved_with_revision', 405907,
	'optional_mod', true,
	'code', {
		"Code/10_RailShaft.lua",
	},
	'TagGameplay', true,
})
