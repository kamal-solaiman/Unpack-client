# coding: utf-8

import uiscriptlocale

BOARD_WIDTH = 342
BOARD_HEIGHT = 244

CONTENT_WIDTH = BOARD_WIDTH - 27
CONTENT_HEIGHT = BOARD_HEIGHT - 80

IMG_PATH = "d:/ymir work/ui/game/guild/dragonlairranking/"

window = {
	"name" : "DungeonInfo_TopWindow",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
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
			"title" : "",
			"children" :
			(
				{
					"name" : "titlebar_ui",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 6,
					"width" : BOARD_WIDTH - 12,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "titlename_ui",
							"type" : "text",
							"x" : (BOARD_WIDTH - 12) / 2,
							"y" : 3,
							"text" : "",
							"text_horizontal_align" : "center"
						},
					),
				},
				{
					"name" : "content1_ui",
					"type" : "v3_thinboard",
					"style" : ("attach",),
					"x" : 10,
					"y" : 32,
					"width" : CONTENT_WIDTH,
					"height" : CONTENT_HEIGHT + 2,
					"children" :
					(
						{
							"name" : "subtitle_ui",
							"type" : "image",
							"x" : 2,
							"y" : 2,
							"image" : IMG_PATH + "ranking_list_menu.sub",
						},
						{
							"name" : "subcontent_ui",
							"type" : "window",
							"style" : ("attach", "not_pick"),
							"x" : 4,
							"y" : 26,
							"width" : CONTENT_WIDTH - 8,
							"height" : CONTENT_HEIGHT - 26,
						},
					),
				},
				{
					"name" : "content2_ui",
					"type" : "v2_thinboard",
					"style" : ("attach",),
					"x" : 10,
					"y" : 32 + CONTENT_HEIGHT + 6,
					"width" : CONTENT_WIDTH + 8,
					"height" : 24,
				},
			),
		},
	),
}
