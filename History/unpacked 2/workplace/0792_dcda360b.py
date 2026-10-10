# coding: utf-8

import uiscriptlocale

BOARD_WIDTH = 190
BOARD_HEIGHT = 193

window = {
	"name" : "ChangeChannel_Dialog",
	"style" : ("movable", "float",),
	"x" : (SCREEN_WIDTH - 190) / 2,
	"y" : (SCREEN_HEIGHT - 100) / 2,
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "board_ui",
			"type" : "board",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			(
				{
					"name" : "title_bar_ui",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 7,
					"width" : 190 - 13,
					"children" :
					(
						{
							"name" : "title_text_ui",
							"type" : "text",
							"x" : 0,
							"y" : -1,
							"text": uiscriptlocale.CHANNEL_SWITCH_TITLE,
							"all_align":"center",
						},
					),
				},
				{
					"name" : "subboard_ui",
					"type" : "thinboard_circle",
					"x" : 13,
					"y" : 36,
					"width" : BOARD_WIDTH - (13 * 2),
					"height" : BOARD_HEIGHT - (36 * 2),
				},
			),
		},
	),
}
