# coding: latin_1

import uiscriptlocale

BOARD_WIDTH=350
BOARD_HEIGHT=210

window = {
	"name":"AdminPanelWindow",
	"x":(SCREEN_WIDTH-BOARD_WIDTH)/2,
	"y":(SCREEN_HEIGHT-BOARD_HEIGHT)/2,
	"style":("movable", "float",),
	"width":BOARD_WIDTH,
	"height":BOARD_HEIGHT,
	"children":
	(
		{
			"name":"BoardUI",
			"type":"board",
			"style":("attach",),
			"x":0,
			"y":0,
			"width":BOARD_WIDTH,
			"height":BOARD_HEIGHT,
			"children":
			(
				{
					"name":"TitleBarUI",
					"type":"titlebar",
					"style":("attach",),
					"x":8,
					"y":7,
					"width":BOARD_WIDTH-16,
					"color":"yellow",
					"children":
					(
						{
							"name":"TitleNameUI",
							"type":"text",
							"x":(BOARD_WIDTH-16)/2,
							"y":3,
							"text":uiscriptlocale.PVP_TOURNAMENT_PANEL_TITLE,
							"text_horizontal_align":"center"
						},
					),
				},
				{
					"name":"ThinBoardUI",
					"type":"thinboard_circle",
					"style":("attach",),
					"x":8,
					"y":30,
					"width":BOARD_WIDTH-16,
					"height":BOARD_HEIGHT-38,
				},
			),
		},
	),
}
