# coding: latin_1

import uiscriptlocale

BOARD_WIDTH=333

window = {
	"name":"PvpTournamentFightsWindow",
	"x":10,
	"y":0,
	"style":("float",),
	"width":BOARD_WIDTH,
	"height":0,
	"children":
	(
		{
			"name":"BoardUI",
			"type":"window",
			"style":("attach","not_pick"),
			"x":0,
			"y":0,
			"width":BOARD_WIDTH,
			"height":0,
		},
	),
}
