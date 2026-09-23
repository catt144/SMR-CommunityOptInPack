return {
	PlaceObj('ModItemCode', {
		'name', "20_TrainHub",
		'CodeFileName', "Code/20_TrainHub.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "30_TrainHubDrones",
		'CodeFileName', "Code/30_TrainHubDrones.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "10_TrainFloor",
		'CodeFileName', "Code/10_TrainFloor.lua",
	}),
	PlaceObj('ModItemRef', {1} --[[SMROptInTrainHub6 SMROptInTrainHub6Base]]),
	PlaceObj('ModItemRef', {2} --[[SMROptInTrainHub6]]),
	PlaceObj('ModItemRef', {3} --[[SMROptInTrainHub6 refs: 1]]),
	PlaceObj('ModItemRef', {4} --[[SMROptInTrainHub6Glass refs: 1]]),
	PlaceObj('ModItemRef', {5} --[[SMROptInTrainHub6Glass]]),
	PlaceObj('ModItemRef', {6} --[[SMROptInTrainHub6DomeGlass refs: 1]]),
	PlaceObj('ModItemRef', {7} --[[SMROptInTrainHub6DomeGlass]]),
}